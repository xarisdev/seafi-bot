async def load_plans(client):
    plans = await client.get_plans()
    return {plan.id: plan for plan in plans}