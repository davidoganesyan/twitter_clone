import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_create_tweet(client: AsyncClient, test_users, test_tweets):
    user1_headers = {"api-key": "api-key-1"}

    # Успешное создание твита
    response = await client.post(
        "/api/tweets/",
        json={"tweet_data": "New content", "tweet_media_ids": []},
        headers=user1_headers,
    )
    assert response.status_code == 200
    assert "tweet_id" in response.json()

    # Создание с медиафайлами
    response = await client.post(
        "/api/tweets/",
        json={"tweet_data": "With media", "tweet_media_ids": [1]},
        headers=user1_headers,
    )
    assert response.status_code == 200

    # Неавторизованный запрос
    user3_headers = {"api-key": "non_valid_key"}
    response = await client.post(
        "/api/tweets/",
        json={"tweet_data": "With media", "tweet_media_ids": []},
        headers=user3_headers,
    )
    assert response.status_code == 401


@pytest.mark.asyncio
async def test_delete_tweet(client: AsyncClient, test_tweets):
    user1_headers = {"api-key": "api-key-1"}

    # Удаление своего твита
    response = await client.delete("/api/tweets/1", headers=user1_headers)
    assert response.status_code == 200

    # Удаление чужого твита
    response = await client.delete("/api/tweets/2", headers=user1_headers)
    assert response.status_code == 403


@pytest.mark.asyncio
async def test_likes(client: AsyncClient, test_tweets):
    user1_headers = {"api-key": "api-key-1"}

    # Добавление лайка
    response = await client.post("/api/tweets/1/likes", headers=user1_headers)
    assert response.status_code == 200

    # Повторный лайк
    response = await client.post("/api/tweets/1/likes", headers=user1_headers)
    assert response.status_code == 400

    # Удаление лайка
    response = await client.delete("/api/tweets/1/likes", headers=user1_headers)
    assert response.status_code == 200

    # Лайк несуществующего твита
    response = await client.post("/api/tweets/999/likes", headers=user1_headers)
    assert response.status_code == 404


@pytest.mark.asyncio
async def test_feed(client: AsyncClient, test_tweets, test_users):
    user1_headers = {"api-key": "api-key-1"}

    # Проверка ленты
    response = await client.get("/api/tweets/", headers=user1_headers)
    data = response.json()
    assert response.status_code == 200
    assert len(data["tweets"]) == 2

    # Проверка структуры ответа
    tweet = data["tweets"][0]
    assert "content" in tweet
    assert "attachments" in tweet
    assert "author" in tweet
    assert "likes" in tweet

    # Проверка медиавложений
    assert len(tweet["attachments"]) == (1 if tweet["id"] == 2 else 0)
