from ...services.api import APIClient

async def load_superuser(client: APIClient, superuser_id: int):
    return await client.get_user(telegram_id=superuser_id) 