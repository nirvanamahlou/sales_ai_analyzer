import httpx
import msal
import logging

from app.core.config import settings

API_VERSION = "v9.2"


async def get_dynamics_access_token() -> str:
    """
    ارتباط با سرور مایکروسافت و دریافت توکن دسترسی موقت (Bearer Token)
    """
    settings.require_dynamics()
    authority = f"https://login.microsoftonline.com/{settings.dynamics_tenant_id}"
    scopes = [f"{settings.dynamics_env_url}/.default"]
    client = msal.ConfidentialClientApplication(
        settings.dynamics_client_id,
        authority=authority,
        client_credential=settings.dynamics_client_secret,
    )
    
    # ابتدا بررسی می‌کند که آیا توکن کش شده‌ای وجود دارد یا خیر
    result = client.acquire_token_silent(scopes, account=None)
    
    if not result:
        # اگر توکن نبود، یک توکن جدید از سرور می‌گیرد
        result = client.acquire_token_for_client(scopes=scopes)
        
    if "access_token" in result:
        return result["access_token"]
    else:
        logging.error(f"CRM Token Error: {result.get('error_description')}")
        raise RuntimeError("عدم موفقیت در دریافت توکن از Dynamics 365")

async def fetch_recent_calls_from_crm(limit: int = 10) -> list:
    """
    دریافت لیست آخرین تماس‌های ثبت شده در CRM که هنوز تحلیل نشده‌اند
    """
    token = await get_dynamics_access_token()
    
    headers = {
        "Authorization": f"Bearer {token}",
        "Accept": "application/json",
        "OData-MaxVersion": "4.0",
        "OData-Version": "4.0"
    }
    
    # اندپوینت مربوط به موجودیت Phone Calls در داینامیکس
    # فرض بر این است که فایل‌های صوتی به صورت Attachment (annotation) به تماس متصل شده‌اند
    endpoint = f"{settings.dynamics_env_url}/api/data/{API_VERSION}/phonecalls?$select=activityid,phonenumber,subject,createdon&$top={limit}&$orderby=createdon desc"

    async with httpx.AsyncClient(timeout=30.0) as client:
        response = await client.get(endpoint, headers=headers)
        response.raise_for_status()
        data = response.json()
        
        calls = data.get("value", [])
        logging.info(f"Fetched {len(calls)} recent calls from Dynamics 365.")
        return calls

async def download_audio_from_crm(activity_id: str, save_path: str) -> bool:
    """
    دانلود فایل صوتی ضمیمه شده به یک تماس خاص از CRM
    """
    token = await get_dynamics_access_token()
    headers = {"Authorization": f"Bearer {token}"}
    
    # جستجو در جدول annotations (یادداشت‌ها و ضمایم) برای پیدا کردن فایل صوتی متصل به این تماس
    endpoint = f"{settings.dynamics_env_url}/api/data/{API_VERSION}/annotations?$filter=_objectid_value eq {activity_id} and mimetype startswith 'audio/'&$select=documentbody,filename"

    async with httpx.AsyncClient(timeout=60.0) as client:
        response = await client.get(endpoint, headers=headers)
        response.raise_for_status()
        attachments = response.json().get("value", [])
        
        if not attachments:
            logging.warning(f"No audio attachment found for call {activity_id}")
            return False
            
        import base64
        # داینامیکس فایل‌ها را به صورت Base64 در فیلد documentbody برمی‌گرداند
        file_content = base64.b64decode(attachments[0]["documentbody"])
        
        with open(save_path, "wb") as f:
            f.write(file_content)
            
        logging.info(f"Audio file downloaded successfully for call {activity_id}")
        return True
