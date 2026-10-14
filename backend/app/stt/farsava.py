import httpx
import logging
import os

from app.core.config import settings


async def transcribe_audio_farsava(audio_file_path: str) -> str:
    """
    فایل صوتی را به فارس‌آوا می‌فرستد و متن پیاده‌سازی شده را برمی‌گرداند.
    """
    if not os.path.exists(audio_file_path):
        raise FileNotFoundError(f"Audio file not found: {audio_file_path}")
    if not settings.farsava_api_key:
        raise RuntimeError("FARSAVA_API_KEY is not configured")

    headers = {
        "Authorization": f"Bearer {settings.farsava_api_key}"
    }

    try:
        async with httpx.AsyncClient(timeout=120.0) as client:
            with open(audio_file_path, "rb") as audio_file:
                # ارسال فایل به صورت Multipart
                files = {"file": (os.path.basename(audio_file_path), audio_file, "audio/wav")}
                
                logging.info("Sending audio to FarsAva...")
                response = await client.post(settings.farsava_url, headers=headers, files=files)
                response.raise_for_status()
                
                data = response.json()
                
                # استخراج متن (بسته به فرمت دقیق خروجی فارس‌آوا، این بخش متغیر است)
                # معمولاً ساختاری شامل transcript یا لیستی از segments با مشخصات گوینده دارد
                transcript = data.get("transcription", "").strip()
                if not transcript:
                    raise RuntimeError("FarsAva returned an empty transcription")
                
                logging.info("FarsAva transcription completed successfully.")
                return transcript
                
    except httpx.HTTPStatusError as exc:
        logging.error("FarsAva API error: %s", exc.response.status_code)
        raise RuntimeError(
            f"FarsAva request failed with status {exc.response.status_code}"
        ) from exc
