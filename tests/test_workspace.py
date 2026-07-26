from httpx import AsyncClient

async def test_workspace_endpoint(
        client: AsyncClient,
        username: str = "testuser",
        email: str = "testuser@email.com",
        password: str = "testpassword",
):
    # First, create a user and get their token
    signup_response = await client.post(
        "http://localhost:8000/v1/auth/signup",
        json={"username": username, "email": email, "password": password}
    )
    assert signup_response.status_code == 201
    login_response = await client.post(
        "http://localhost:8000/v1/auth/login",
        data={"username": username, "password": password}
    )
    assert login_response.status_code == 200
    user_token = login_response.json()["access_token"]

    # Then, use the user's token to create a workspace
    
    response = await client.post(
        "http://localhost:8000/v1/workspace/create",
        headers={"Authorization": f"Bearer {user_token}"},
        json={
            "name": "Test Workspace",
            "email": email
        }
    )
    print(response.status_code, response.json())
    assert response.status_code == 201
        