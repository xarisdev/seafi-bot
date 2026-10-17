import logging
import httpx

from typing import Literal

from .models.exceptions import (
    HTTPError,
    NetworkError,
    BadRequestError,
    UnauthorizedError,
    ForbiddenError,
    NotFoundError,
    ConflictError,
    ServerError
)
from .models.http import ResponseSchema

from ..app.config import settings

logger = logging.getLogger("client.http:_client")

class HTTPClient():
    def __init__(self):
        self.client: httpx.AsyncClient | None = None
        
        self.auth_header = {
            "X-Api-Key": settings.X_API_KEY
        }

    # ------------ Lifecycle ------------

    def start(self):
        self.client = httpx.AsyncClient(
            base_url=settings.BASE_SERVER_URL,
            headers=self.auth_header
        )
        logger.info("HTTPClient started")

    async def close(self):
        await self.client.aclose()
        logger.info("HTTPClient closed")

    # ------------ Request ------------

    async def _request(self, *args, **kwargs) -> httpx.Response:
        try:
            return await self.client.request(*args, **kwargs)

        except httpx.RequestError as exc:
            raise NetworkError("Request failed") from exc

    async def request(self,
                      method: Literal["GET", "POST", "PATCH"],
                      url: str,
                      **kwargs) -> ResponseSchema:
        response = await self._request(method=method, url=url, **kwargs)
        logger.info(
            "Request [%s]: %s %s",
            response.status_code,
            method,
            url
        )

        try: response_json = response.json()
        except ValueError: response_json = None

        status_code = response.status_code
        response_details = response.text or None

        if 200 <= response.status_code < 300:
            return ResponseSchema(
                status_code=status_code,
                response_json=response_json,
                response_details=response_details
            )

        details = response_json if response_json is not None else response_details or "Request failed"
        errors = {
            400: BadRequestError,
            401: UnauthorizedError,
            403: ForbiddenError,
            404: NotFoundError,
            409: ConflictError
        }

        error_class = errors.get(status_code)

        if error_class is not None:
            raise error_class(details)

        if status_code >= 500:
            raise ServerError(details)

        logger.error(
            "Request failed: [%s] [%s] [%s] | [%s]",
            status_code,
            method,
            url,
            kwargs
        )
        raise HTTPError(status_code, details)