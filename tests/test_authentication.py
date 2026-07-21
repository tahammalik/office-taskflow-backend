import pytest
from httpx import ASGITransport,AsyncClient

"""
Test cases for authentication endpoints.
These tests cover user signup, login, and duplicate checks."""

async def test_user_signup(
        client: AsyncClient,
        uusername: str = "testuser",
        uemail: str = "testuser@email.com",
        upassword: str = "testpassword",
):
    response = await client.post(
        "/v1/auth/signup",
        json={"username": uusername,
              "email": uemail,
              "password": upassword
        },
    )

    assert response.status_code == 201
    return response.json()

async def test_duplicate_user_signup(
        client: AsyncClient,
        username: str = "testuser",
        email: str = "testuser@email.com",
        password: str = "testpassword"
):
    response = await client.post(
        "/v1/auth/signup",
        json={"username": username,
              "email": email,
              "password": password
        },
    )
    response = await client.post(
        "/v1/auth/signup",
        json={"username": username,
              "email": "user@email.me",
              "password": password
        },
    )

    assert response.status_code == 409
    
async def test_duplicate_email_signup(
        client: AsyncClient,
        username: str = "testuser",
        email: str = "testuser@email.com",
        password: str = "testpassword"
):
    response = await client.post(
        "/v1/auth/signup",
        json={"username": username,
              "email": email,
              "password": password
        },
    )
    response = await client.post(
        "/v1/auth/signup",
        json={"username": "user",
              "email": email,
              "password": password
        },
    )

    assert response.status_code == 409

async def test_user_login(
        client: AsyncClient,
        username: str = "testuser",
        email: str = "testuser@email.com",
        password: str = "testpassword"
):
    signup_response = await client.post(
        "/v1/auth/signup",
        json={"username": username,
                "email": email,
                "password": password
        },
    )
    assert signup_response.status_code == 201

    response = await client.post(
        "/v1/auth/login",
        data={"username": username,
              "password": password
        }
    )

    assert response.status_code == 201
    return response.json()

async def test_user_login_invalid_credentials(
        client: AsyncClient,
        username: str = "testuser",
        email: str = "testuser@email.com",
        password: str = "testpassword"
):
    signup_response = await client.post(
        "/v1/auth/signup",
        json={"username": username,
                "email": email,
                "password": password
        },
    )
    assert signup_response.status_code == 201

    response = await client.post(
        "/v1/auth/login",
        data={"username": username,
              "password": "wrongpassword"
        }
    )

    assert response.status_code == 401