import logging

from telegram.ext import Application

from .http_client import HTTPClient

from .models.api import (
    User,
    Plan, PlanCreate, PlanUpdate,
    Invoice,
    LavaProduct,
    Subscription
)
logger = logging.getLogger("client.api:_client")

class APIClient():
    def __init__(self):
        self._http_client: HTTPClient | None = None

        self.bot_application: Application = None

    # ------------ Lifecycle ------------

    def startup(self, application: Application):
        self.bot_application = application

        if self._http_client is None:
            self._http_client = HTTPClient()
            self._http_client.start()

    async def shutdown(self):
        if self._http_client is not None:
            await self._http_client.close()
            self._http_client = None

    # ------------ API Endpoints ------------

    # ------------ Users ------------

    async def create_user(self, telegram_id: int) -> User:
        json_data = {
            "telegram_id": telegram_id
        }
        response = await self._http_client.request(
            method="POST",
            url="/api/v1/users",
            json=json_data
        )
        return User(**response.response_json)

    async def get_user(self, telegram_id: int) -> User:
        response = await self._http_client.request(
            method="GET",
            url=f"/api/v1/users/{telegram_id}"
        )
        return User(**response.response_json)

    # ------------ Plans ------------

    async def create_plan(self, plan_create: PlanCreate) -> Plan:
        response = await self._http_client.request(
            method="POST",
            url="/api/v1/plans",
            json=plan_create.model_dump()
        )
        return Plan(**response.response_json)

    async def get_plans(self) -> list[Plan]:
        response = await self._http_client.request(
            method="GET",
            url="/api/v1/plans"
        )
        return [Plan(**plan) for plan in response.response_json]

    async def get_plan_by_id(self, plan_id: int) -> Plan:
        response = await self._http_client.request(
            method="GET",
            url=f"/api/v1/plans/{plan_id}"
        )
        return Plan(**response.response_json)

    async def patch_plan(self, plan_id: int, data: PlanUpdate) -> Plan:
        response = await self._http_client.request(
            method="PATCH",
            url=f"/api/v1/plans/{plan_id}",
            json=data.model_dump()
        )
        return Plan(**response.response_json)

    # ------------ Filters ------------

    # -------- ::PLACEHOLDER:: --------

    # ------------ Invoices ------------

    async def create_invoice(self, plan_id: int, currency: str, telegram_id: int) -> Invoice:
        url = (
            "/api/v1/payments/invoices"
            f"?plan_id={plan_id}"
            f"&currency={currency}"
            f"&telegram_id={telegram_id}"
        )
        response = await self._http_client.request(
            method="POST",
            url=url
        )
        return Invoice(**response.response_json)

    async def get_user_invoices(self, telegram_id: int, status: str | None) -> list[Invoice]:
        url = f"/api/v1/payments/invoices?telegram_id={telegram_id}"
        if status is not None:
            url += f"&status={status}"
        response = await self._http_client.request(
            method="GET",
            url=url
        )
        return [Invoice(**invoice) for invoice in response.response_json]

    async def check_invoice(self, invoice_id: int) -> Invoice:
        response = await self._http_client.request(
            method="GET",
            url=f"/api/v1/payments/invoices/{invoice_id}"
        )
        return Invoice(**response.response_json)

    async def cancel_invoice(self, invoice_id: int) -> None:
        await self._http_client.request(
            method="POST",
            url=f"/api/v1/payments/invoices/{invoice_id}/cancel"
        )

    # ------------ Products ------------

    async def get_lava_products(self) -> list[LavaProduct]:
        response = await self._http_client.request(
            method="GET",
            url="/api/v1/lava-products"
        )
        return [LavaProduct(**product) for product in response.response_json]

    # ------------ Subscriptions ------------

    async def get_all_subscriptions(self, telegram_id: int) -> list[Subscription]:
        response = await self._http_client.request(
            method="GET",
            url=f"/api/v1/subscriptions/all?telegram_id={telegram_id}"
        )
        return [Subscription(**subscription) for subscription in response.response_json]

    async def get_active_subscription(self, telegram_id: int) -> Subscription | None:
        response = await self._http_client.request(
            method="GET",
            url=f"/api/v1/subscriptions/active?telegram_id={telegram_id}"
        )
        if response.response_json is None:
            return None
        return Subscription(**response.response_json)

    async def get_subscription(self, subscription_id: int) -> Subscription:
        response = await self._http_client.request(
            method="GET",
            url=f"/api/v1/subscriptions/{subscription_id}"
        )
        return Subscription(**response.response_json)

api_client = APIClient()