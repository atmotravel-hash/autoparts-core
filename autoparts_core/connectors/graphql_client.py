"""Shared GraphQL POST client with SSRF checks and rate limiting.

Used for public catalog endpoints that the sites themselves expose
(typically POST /graphql or /apigateway/graphql). Does not bypass CAPTCHA,
auth walls, or Cloudflare challenges.
"""

from __future__ import annotations

import time
from dataclasses import dataclass, field
from typing import Any

import httpx

from autoparts_core.security.ssrf import validate_public_url


@dataclass
class GraphQLError(Exception):
    message: str
    status_code: int | None = None
    payload: Any = None

    def __str__(self) -> str:  # pragma: no cover
        return self.message


@dataclass
class RateLimiter:
    min_interval_seconds: float = 0.6
    _last: float = field(default=0.0, init=False)

    def wait(self) -> None:
        now = time.monotonic()
        delta = now - self._last
        if delta < self.min_interval_seconds:
            time.sleep(self.min_interval_seconds - delta)
        self._last = time.monotonic()


class GraphQLClient:
    def __init__(
        self,
        endpoint: str,
        *,
        origin: str | None = None,
        referer: str | None = None,
        timeout: float = 25.0,
        min_interval_seconds: float = 0.6,
        extra_headers: dict[str, str] | None = None,
    ) -> None:
        ok, reason = validate_public_url(endpoint)
        if not ok:
            raise ValueError(f"GraphQL endpoint rejected: {reason}")
        self.endpoint = endpoint
        self.timeout = timeout
        self.limiter = RateLimiter(min_interval_seconds=min_interval_seconds)
        self.headers = {
            "User-Agent": "AutoPartsCore/0.2 (+catalog GraphQL client; respectful rate limits)",
            "Accept": "application/json",
            "Content-Type": "application/json",
        }
        if origin:
            self.headers["Origin"] = origin
        if referer:
            self.headers["Referer"] = referer
        if extra_headers:
            self.headers.update(extra_headers)

    def execute(
        self,
        query: str,
        variables: dict[str, Any] | None = None,
        *,
        operation_name: str | None = None,
    ) -> dict[str, Any]:
        self.limiter.wait()
        body: dict[str, Any] = {"query": query}
        if variables is not None:
            body["variables"] = variables
        if operation_name:
            body["operationName"] = operation_name
        try:
            with httpx.Client(timeout=self.timeout, follow_redirects=True, headers=self.headers) as client:
                response = client.post(self.endpoint, json=body)
        except httpx.HTTPError as exc:
            raise GraphQLError(f"Network error: {exc}") from exc

        # Cloudflare / captcha HTML must not be treated as success
        ctype = (response.headers.get("content-type") or "").lower()
        text_head = response.text[:200].lower()
        if "text/html" in ctype and ("just a moment" in text_head or "captcha" in text_head):
            raise GraphQLError(
                "Access challenge/CAPTCHA encountered — refusing to bypass",
                status_code=response.status_code,
            )
        try:
            payload = response.json()
        except Exception as exc:
            raise GraphQLError(
                f"Non-JSON GraphQL response (HTTP {response.status_code})",
                status_code=response.status_code,
                payload=response.text[:500],
            ) from exc

        if response.status_code >= 400 and "data" not in payload:
            raise GraphQLError(
                f"HTTP {response.status_code} from GraphQL endpoint",
                status_code=response.status_code,
                payload=payload,
            )
        if payload.get("errors") and payload.get("data") is None:
            msg = payload["errors"][0].get("message", "GraphQL error")
            raise GraphQLError(msg, status_code=response.status_code, payload=payload)
        return payload
