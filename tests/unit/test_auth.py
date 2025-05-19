import pytest
from datetime import datetime, timedelta
from jose import jwt
from unittest.mock import AsyncMock, MagicMock
import bcrypt
import base64

from freezegun import freeze_time

from app.users.service import AuthService


def test_create_jwt():
    mock_settings = MagicMock()
    mock_settings.TOKEN_TYPE_FIELD = 'type'
    mock_settings.JWT_ENCODE_ALGORITHM = 'HS256'
    mock_settings.PRIVATE_KEY_PATH.read_text.return_value = 'secret'
    mock_google_client = MagicMock()
    mock_yandex_client = MagicMock()
    mock_repo = MagicMock()

    auth_service = AuthService(
        user_repository=mock_repo,
        setting=mock_settings,
        google_client=mock_google_client,
        yandex_client=mock_yandex_client
    )
    payload = {'user_id': 123}
    token = auth_service.create_jwt(token_type='access', token_data=payload)

    decoded = jwt.decode(token, 'secret', algorithms=['HS256'])
    assert decoded['type'] == 'access'
    assert decoded['user_id'] == 123

@pytest.mark.asyncio
async def test_generate_access_token():
    mock_user = MagicMock()
    mock_user.id = 1
    mock_user.email = 'test@example.com'
    mock_repo = MagicMock()
    mock_repo.get_user = AsyncMock(return_value=mock_user)

    mock_settings = MagicMock()
    mock_settings.ACCESS_TOKEN_TYPE = 'access'
    mock_settings.TOKEN_TYPE_FIELD = 'type'
    mock_settings.PRIVATE_KEY_PATH.read_text.return_value = 'secret'
    mock_settings.JWT_ENCODE_ALGORITHM = 'HS256'

    mock_google_client = MagicMock()
    mock_yandex_client = MagicMock()


    auth_service = AuthService(
        user_repository=mock_repo,
        setting=mock_settings,
        google_client=mock_google_client,
        yandex_client=mock_yandex_client
    )

    with freeze_time("2025-01-01 12:00:00"):
        token = await auth_service.generate_access_token(user_id=1)
        decoded = jwt.decode(token, 'secret', algorithms=['HS256'])

        assert decoded['sub'] == 'test@example.com'
        assert decoded['user_id'] == 1
        assert decoded['type'] == 'access'
        assert decoded['iat'] == datetime(2025, 1, 1, 12, 0).timestamp()
        assert decoded['exp'] == (datetime(2025, 1, 1, 12, 0) + timedelta(minutes=15)).timestamp()


def test_generate_refresh_token():
    mock_user = MagicMock()
    mock_user.id = 99

    mock_settings = MagicMock()
    mock_settings.REFRESH_TOKEN_TYPE = 'refresh'
    mock_settings.TOKEN_TYPE_FIELD = 'type'
    mock_settings.PRIVATE_KEY_PATH.read_text.return_value = 'secret'
    mock_settings.JWT_ENCODE_ALGORITHM = 'HS256'

    mock_google_client = MagicMock()
    mock_yandex_client = MagicMock()
    mock_repo = MagicMock()

    auth_service = AuthService(
        user_repository=mock_repo,
        setting=mock_settings,
        google_client=mock_google_client,
        yandex_client=mock_yandex_client
    )

    with freeze_time("2025-01-01 00:00:00"):
        token = auth_service.generate_refresh_token(mock_user)
        decoded = jwt.decode(token, 'secret', algorithms=['HS256'])

        assert decoded['user_id'] == 99
        assert decoded['type'] == 'refresh'
        assert decoded['iat'] == datetime(2025, 1, 1).timestamp()
        assert decoded['exp'] == (datetime(2025, 1, 1) + timedelta(days=30)).timestamp()


def test_validate_password_success():
    password = "my_secure_password"
    hashed = bcrypt.hashpw(password.encode(), bcrypt.gensalt())
    hashed_b64 = base64.b64encode(hashed).decode()

    result = AuthService.validate_password(password, hashed_b64)
    assert result is True

def test_validate_password_failure_wrong_password():
    password = "my_secure_password"
    wrong_password = "wrong"
    hashed = bcrypt.hashpw(password.encode(), bcrypt.gensalt())
    hashed_b64 = base64.b64encode(hashed).decode()

    result = AuthService.validate_password(wrong_password, hashed_b64)
    assert result is False

def test_validate_password_failure_invalid_hash():
    invalid_hash = "not-a-valid-base64"

    with pytest.raises(Exception):
        AuthService.validate_password("password", invalid_hash)
