import pytest
from unittest.mock import MagicMock
from app.infrastructure.database.database import Settings


@pytest.fixture(autouse=True)
def mock_settings(monkeypatch):
    # Мокируем настройки для тестов
    mock_settings = MagicMock(spec=Settings)
    mock_settings.DB_HOST = "test_host"
    mock_settings.DB_PORT = 5432
    mock_settings.DB_USER = "test_user"
    mock_settings.DB_PASSWORD = "test_password"
    # ... остальные поля

    monkeypatch.setattr("app.infrastructure.database.database.settings", mock_settings)