import os
from api.config import YandexConfig


def test_correct_config_env():
    try:
        os.environ["YNDX_CLIENT_ID"] = 'client_id'
        os.environ["YNDX_CLIENT_SECRET"] = 'client_secret'
        config = YandexConfig()
        assert config.client_id == 'client_id'
        assert config.client_secret.get_secret_value() == 'client_secret'
    finally:
        del os.environ["YNDX_CLIENT_ID"]
        del os.environ["YNDX_CLIENT_SECRET"]


def test_correct_config_file():
    assert "YNDX_CLIENT_ID" not in os.environ
    assert "YNDX_CLIENT_SECRET" not in os.environ

    try:
        with open('.env', 'w') as f:
            f.writelines(["YNDX_CLIENT_ID=client_id", "\n", "YNDX_CLIENT_SECRET=client_secret"])
        config = YandexConfig()
        assert config.client_id == 'client_id'
        assert config.client_secret.get_secret_value() == 'client_secret'
    finally:
        try:
            os.unlink('.env')
        except FileNotFoundError:
            pass
