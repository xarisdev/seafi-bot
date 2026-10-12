import httpx
import logging

from .exceptions import (
    APIError,
    UnauthorizedError,
    ForbiddenError,
    NotFoundError,
    ConflictError,
    ServerError,
    NetworkError
)

from ...models.responses import ResponseSchema
from ...models.user import UserRead
from ...models.plan import SubscriptionPlanCreate, SubscriptionPlanRead, SubscriptionPlanUpdate
from ...models.lava import ProductSchema, PaymentSchema, InvoiceSchema
from ...models.subscription import SubscriptionSchema

from ...app.config import settings

logger = logging.getLogger("api.client")

class APIClient():
    def __init__(self):
        self._client: httpx.AsyncClient | None = None
        self._auth_header = {"X-Api-Key": settings.X_API_KEY}

    # ------------ Start/Close ------------

    def start(self):
        self._client = httpx.AsyncClient(
            base_url=settings.BASE_SERVER_URL,
            headers=self._auth_header
        )
        logger.info("APIClient started")

    async def close(self):
        await self._client.aclose()
        logger.info("APIClient closed")

    # ------------ Request to Server ------------

    async def _request(self, method: str, url: str, **kwargs) -> ResponseSchema:
        """
        ## Args

        - :url: should started with: `"/api/v1"`
        """
        try:
            response = await self._client.request(
                method=method,
                url=url,
                **kwargs
            )
            logger.info(f"HTTP Request: {method} {url} | {response.status_code}")
        except httpx.RequestError as exc:
            logger.error(f"HTTP Request: {method} {url} | {str(exc)}")
            raise NetworkError("Server Unavailable") from exc

        if 200 <= response.status_code < 300:
            return ResponseSchema(
                status_code=response.status_code,
                data=response.json() or None,
                message=response.text or None
            )

        if response.status_code == 401: raise UnauthorizedError()
        if response.status_code == 403: raise ForbiddenError()
        if response.status_code == 404: raise NotFoundError()
        if response.status_code == 409: raise ConflictError()
        if response.status_code >= 500: raise ServerError()

        logger.error(f"HTTP API Request failed")
        
        raise APIError("Request failed", response.status_code)

    # ------------ Public API methods ------------

    # ------------ API Users ------------
    
    async def create_user(self, telegram_id: int) -> UserRead:
        response = await self._request(
            "POST",
            "/api/v1/users",
            json={"telegram_id": telegram_id}
        )
        return UserRead(**response.data)

    async def get_user(self, telegram_id: int) -> UserRead:
        response = await self._request(
            "GET",
            f"/api/v1/users/{telegram_id}"
        )
        return UserRead(**response.data)

    # ------------ API Products ------------

    async def get_products(self) -> list[ProductSchema]:
        response = await self._request(
            "GET",
            f"/api/v1/products"
        )
        return [ProductSchema(**data) for data in response.data]

    # ------------ API Plans ------------

    async def create_plan(self, data: SubscriptionPlanCreate) -> SubscriptionPlanRead:
        response = await self._request(
            "POST",
            f"/api/v1/plans",
            json=data.model_dump()
        )
        return SubscriptionPlanRead(**response.data)

    async def get_plans(self) -> list[SubscriptionPlanRead]:
        response = await self._request(
            "GET",
            f"/api/v1/plans"
        )
        return [SubscriptionPlanRead(**plan) for plan in response.data]

    async def get_plan(self, plan_id: int) -> SubscriptionPlanRead:
        response = await self._request(
            "GET",
            f"/api/v1/plans/{plan_id}"
        )
        return SubscriptionPlanRead(**response.data)

    async def patch_plan(self, plan_id: int, data: SubscriptionPlanUpdate) -> SubscriptionPlanRead:
        response = await self._request(
            "PATCH",
            f"/api/v1/plans/{plan_id}",
            json=data.model_dump()
        )
        return SubscriptionPlanRead(**response.data)

    # ------------ API Payments ------------

    async def create_payment_link(self, plan_id: int, telegram_id: int, currency: str) -> PaymentSchema:
        response = await self._request(
            "POST",
            f"/api/v1/payments/create-link/{plan_id}?telegram_id={telegram_id}&currency={currency}"
        )
        return PaymentSchema(
            invoice=InvoiceSchema(
                **response.data.get("invoice")
            ),
            subscription=SubscriptionSchema(
                **response.data.get("subscription")
            )
        )

    async def check_payment(self, invoice_id: str) -> SubscriptionSchema:
        response = await self._request(
            "GET",
            f"/api/v1/payments/invoices/{invoice_id}"
        )
        return SubscriptionSchema(
            **response.data
        )

    #async def cancel_payment(self, telegram_id: int, invoice: InvoiceSchema):
    #    #placeholder
    #    pass

    # ------------ API Subscriptions ------------
    async def get_active_subscription(self, telegram_id: int) -> SubscriptionSchema | None:
        response = await self._request(
            "GET",
            f"/api/v1/subscriptions/active?telegram_id={telegram_id}"
        )
        if response.data is None:
            return None
        return SubscriptionSchema(**response.data)

    async def get_subscription(self, subscription_id: int) -> SubscriptionSchema:
        response = await self._request(
            "GET",
            f"/api/v1/subscriptions/{subscription_id}"
        )
        return SubscriptionSchema(**response.data)

api_client = APIClient()