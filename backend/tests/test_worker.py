import pytest

from app.worker import tasks


@pytest.mark.asyncio
async def test_remote_audio_requires_https():
    with pytest.raises(RuntimeError, match="HTTPS"):
        await tasks._resolve_audio_source("call-1", "http://media.example.test/call.wav")


@pytest.mark.asyncio
async def test_remote_audio_requires_allowed_host(monkeypatch):
    monkeypatch.setattr(
        tasks,
        "settings",
        type(
            "TestSettings",
            (),
            {
                "audio_url_allowed_hosts": ("allowed.example.test",),
                "audio_directory": "/tmp",
            },
        )(),
    )

    with pytest.raises(RuntimeError, match="not allowed"):
        await tasks._resolve_audio_source(
            "call-1",
            "https://blocked.example.test/call.wav",
        )
