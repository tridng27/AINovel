import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_register_success(client: AsyncClient):
    res = await client.post("/api/v1/auth/register", json={
        "username": "newuser",
        "email": "new@test.com",
        "password": "Password123!",
    })
    assert res.status_code == 201
    data = res.json()
    assert data["username"] == "newuser"
    assert data["is_verified"] is False


@pytest.mark.asyncio
async def test_register_duplicate_email(client: AsyncClient):
    payload = {"username": "dup1", "email": "dup@test.com", "password": "Password123!"}
    await client.post("/api/v1/auth/register", json=payload)
    res = await client.post("/api/v1/auth/register", json={**payload, "username": "dup2"})
    assert res.status_code == 409


@pytest.mark.asyncio
async def test_login_success(client: AsyncClient):
    await client.post("/api/v1/auth/register", json={
        "username": "loginuser", "email": "login@test.com", "password": "Password123!",
    })
    res = await client.post("/api/v1/auth/login", json={
        "email": "login@test.com", "password": "Password123!",
    })
    assert res.status_code == 200
    assert res.json()["access_token"]
    assert res.json()["token_type"] == "bearer"


@pytest.mark.asyncio
async def test_login_wrong_password(client: AsyncClient):
    await client.post("/api/v1/auth/register", json={
        "username": "wrongpass", "email": "wrong@test.com", "password": "Password123!",
    })
    res = await client.post("/api/v1/auth/login", json={
        "email": "wrong@test.com", "password": "WrongPass!",
    })
    assert res.status_code == 401


@pytest.mark.asyncio
async def test_refresh_token(client: AsyncClient):
    reg = await client.post("/api/v1/auth/register", json={
        "username": "refuser", "email": "ref@test.com", "password": "Password123!",
    })
    refresh_token = reg.json()["refresh_token"]
    res = await client.post("/api/v1/auth/refresh", json={"refresh_token": refresh_token})
    assert res.status_code == 200
    assert res.json()["access_token"]
    # old refresh token is invalidated — second use should fail
    res2 = await client.post("/api/v1/auth/refresh", json={"refresh_token": refresh_token})
    assert res2.status_code == 401


@pytest.mark.asyncio
async def test_logout(client: AsyncClient):
    reg = await client.post("/api/v1/auth/register", json={
        "username": "logoutuser", "email": "logout@test.com", "password": "Password123!",
    })
    refresh_token = reg.json()["refresh_token"]
    res = await client.post("/api/v1/auth/logout", json={"refresh_token": refresh_token})
    assert res.status_code == 204
    # after logout refresh token is gone
    res2 = await client.post("/api/v1/auth/refresh", json={"refresh_token": refresh_token})
    assert res2.status_code == 401


@pytest.mark.asyncio
async def test_me_authenticated(client: AsyncClient):
    reg = await client.post("/api/v1/auth/register", json={
        "username": "meuser", "email": "me@test.com", "password": "Password123!",
    })
    token = reg.json()["access_token"]
    res = await client.get("/api/v1/auth/me", headers={"Authorization": f"Bearer {token}"})
    assert res.status_code == 200
    assert res.json()["email"] == "me@test.com"


@pytest.mark.asyncio
async def test_me_unauthenticated(client: AsyncClient):
    res = await client.get("/api/v1/auth/me")
    assert res.status_code == 401


@pytest.mark.asyncio
async def test_verify_email_invalid_token(client: AsyncClient):
    res = await client.post("/api/v1/auth/verify-email", json={"token": "not.a.valid.token"})
    assert res.status_code == 400


@pytest.mark.asyncio
async def test_resend_verification_unknown_email(client: AsyncClient):
    # Should return 204 silently (no email enumeration)
    res = await client.post("/api/v1/auth/resend-verification", json={"email": "ghost@test.com"})
    assert res.status_code == 204
