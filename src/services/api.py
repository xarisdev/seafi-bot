import httpx
import logging

from ..models.responses import ResponseSchema
from ..models.exceptions import (
    APIError,
    UnauthorizedError,
    ForbiddenError,
    NotFoundError,
    ConflictError,
    ServerError,
    NetworkError
)

from ..models.user import UserCreate, UserRead, UserUpdate
from ..models.subscription import SubscriptionCreate, SubscriptionRead

from ..app.config import settings

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
    
    async def create_user(self, data: UserCreate) -> UserRead:
        response = await self._request(
            "POST",
            "/api/v1/users",
            json=data.model_dump()
        )
        return UserRead(**response.data)

    async def get_user(self, telegram_id: int) -> UserRead:
        response = await self._request(
            "GET",
            f"/api/v1/users/{telegram_id}"
        )
        return UserRead(**response.data)

    async def patch_user(self, telegram_id: int, data: UserUpdate) -> UserRead:
        response = await self._request(
            "PATCH",
            f"/api/v1/users/{telegram_id}",
            json=data.model_dump()
        )
        return UserRead(**response.data)

    # ------------ API Subscriptions ------------

    async def create_subscription(self, data: SubscriptionCreate) -> SubscriptionRead:
        response = await self._request(
            "POST",
            f"/api/v1/subscriptions",
            json=data.model_dump()
        )
        return SubscriptionRead(**response.data)

    async def get_subscriptions(self) -> list[SubscriptionRead]:
        response = await self._request(
            "GET",
            f"/api/v1/subscriptions"
        )
        return [SubscriptionRead(**sub) for sub in response.data]

    async def patch_subscription(self, subscription_id: int, x_admin_key: str) -> SubscriptionRead:
        response = await self._request(
            "PATCH",
            f"/api/v1/subscriptions/{subscription_id}",
            headers={"X-Admin-Key": x_admin_key}
        )
        return SubscriptionRead(**response.data)

    # ------------ API Filters ------------

api_client = APIClient()