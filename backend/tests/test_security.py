import pytest
from fastapi import HTTPException
from types import SimpleNamespace

from app.core import security


@pytest.mark.asyncio
async def test_api_key_rejects_invalid_value(monkeypatch):
    monkeypatch.setattr(security, "settings", SimpleNamespace(api_key="expected"))

    with pytest.raises(HTTPException) as exc:
        await security.require_api_key("wrong")

    assert exc.value.status_code == 401


@pytest.mark.asyncio
async def test_api_key_accepts_matching_value(monkeypatch):
    monkeypatch.setattr(security, "settings", SimpleNamespace(api_key="expected"))

    await security.require_api_key("expected")
