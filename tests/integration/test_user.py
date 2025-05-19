import pytest
import aiohttp
import asyncio


@pytest.mark.asyncio
async def test_login_success():
    async with aiohttp.ClientSession() as session:
        # Правильные данные пользователя (должны существовать в БД)
        login_data = {
            "email": "test2@gmail.com",
            "password": "testTEST2"
        }

        async with session.post(
                "http://192.168.56.1:8000/auth/login/",
                json=login_data
        ) as response:
            assert response.status == 200
            data = await response.json()
            assert "access_token" in data
            assert data["token_type"] == "Bearer"


@pytest.mark.asyncio
async def test_login_invalid_password():
    async with aiohttp.ClientSession() as session:
        login_data = {
            "email": "test_user@example.com",
            "password": "wrong_password"
        }

        async with session.post(
                "http://192.168.56.1:8000/auth/login/",
                json=login_data
        ) as response:
            assert response.status in [400, 401, 404]


@pytest.mark.asyncio
async def test_login_validation_error():
    async with aiohttp.ClientSession() as session:
        invalid_data = [
            {"email": "not-an-email", "password": "string"},  # Невалидный email
            {"password": "string"},  # Нет email
            {}  # Пустой запрос
        ]

        for data in invalid_data:
            async with session.post(
                    "http://192.168.56.1:8000/auth/login/",
                    json=data
            ) as response:
                assert response.status == 422  # Ошибка валидации
                error = await response.json()
                assert "detail" in error