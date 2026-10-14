import pytest
from pydantic import ValidationError

from app.api.schemas import DynamicsWebhookRequest


def test_webhook_requires_valid_http_url():
    request = DynamicsWebhookRequest(
        call_id="call-123",
        audio_url="https://media.example.test/call.wav",
    )

    assert request.call_id == "call-123"


def test_webhook_rejects_local_file_paths():
    with pytest.raises(ValidationError):
        DynamicsWebhookRequest(call_id="call-123", audio_url="/tmp/call.wav")
