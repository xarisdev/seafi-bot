from ...services.web.api import APIClient

async def load_plans(client: APIClient):
    plans = await client.get_plans()
    return {plan.id: plan for plan in plans}