async def load_superuser(client, superuser_id: int):
    return await client.get_user(telegram_id=superuser_id)