import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_follow_unfollow_flow(client: AsyncClient, test_users):
    user1_headers = {"api-key": "api-key-1"}

    # Тест подписки
    follow_response = await client.post("/api/users/2/follow", headers=user1_headers)
    assert follow_response.status_code == 200
    assert follow_response.json() == {"result": True}

    # Проверяем дублирующую подписку
    duplicate_follow = await client.post("/api/users/2/follow", headers=user1_headers)
    assert duplicate_follow.status_code == 400
    assert "already following" in duplicate_follow.json()["detail"]

    # Проверяем подписку на несуществующего пользователя
    invalid_follow = await client.post("/api/users/999/follow", headers=user1_headers)
    assert invalid_follow.status_code == 400
    assert "User not found" in invalid_follow.json()["detail"]

    # Тест отписки
    unfollow_response = await client.delete(
        "/api/users/2/follow", headers=user1_headers
    )
    assert unfollow_response.status_code == 200


@pytest.mark.asyncio
async def test_user_profiles(client: AsyncClient, test_users):
    user1_headers = {"api-key": "api-key-1"}

    # Проверяем профиль текущего пользователя
    my_profile = await client.get("/api/users/me", headers=user1_headers)
    assert my_profile.status_code == 200
    assert my_profile.json()["user"]["id"] == 1
    assert my_profile.json()["user"]["name"] == "Test User 1"

    # Проверяем чужой профиль
    other_profile = await client.get("/api/users/2", headers=user1_headers)
    assert other_profile.status_code == 200
    assert other_profile.json()["user"]["name"] == "Test User 2"


@pytest.mark.asyncio
async def test_followers_logic(client: AsyncClient, test_users):
    user1_headers = {"api-key": "api-key-1"}
    user2_headers = {"api-key": "api-key-2"}

    await client.post("/api/users/2/follow", headers=user1_headers)

    # Проверяем подписчиков User2
    profile = await client.get("/api/users/2", headers=user2_headers)
    followers = profile.json()["user"]["followers"]
    assert len(followers) == 1
    assert followers[0]["id"] == 1

    # Проверяем подписки User1
    my_profile = await client.get("/api/users/me", headers=user1_headers)
    following = my_profile.json()["user"]["following"]
    assert len(following) == 1
    assert following[0]["id"] == 2

    # User2 подписывается на User1
    await client.post("/api/users/1/follow", headers=user2_headers)

    # Проверяем взаимные подписки
    profile_user1 = await client.get("/api/users/1", headers=user1_headers)
    assert len(profile_user1.json()["user"]["followers"]) == 1
