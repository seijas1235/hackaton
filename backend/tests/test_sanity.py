from shared.settings import get_settings


def test_settings_defaults():
    s = get_settings()
    assert s.env == "local"
    assert s.log_level == "INFO"
    assert s.jwt_algorithm == "HS256"
