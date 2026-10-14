from app.core.config import Settings


def test_redis_settings_are_parsed_from_url(monkeypatch):
    monkeypatch.setenv("REDIS_URL", "redis://:secret@example.test:6380/4")

    redis_settings = Settings().redis_settings()

    assert redis_settings.host == "example.test"
    assert redis_settings.port == 6380
    assert redis_settings.database == 4
    assert redis_settings.password == "secret"


def test_require_dynamics_reports_missing_values(monkeypatch):
    for name in (
        "DYNAMICS_TENANT_ID",
        "DYNAMICS_CLIENT_ID",
        "DYNAMICS_CLIENT_SECRET",
        "DYNAMICS_ENV_URL",
    ):
        monkeypatch.delenv(name, raising=False)

    try:
        Settings().require_dynamics()
    except RuntimeError as exc:
        assert "DYNAMICS_TENANT_ID" in str(exc)
        assert "DYNAMICS_CLIENT_SECRET" in str(exc)
    else:
        raise AssertionError("Missing Dynamics settings should fail")
