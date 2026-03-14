"""Google OAuth with email allowlist."""

from typing import Any

import httpx
from loguru import logger

from fastmcp.server.auth.providers.google import GoogleProvider


class RestrictedGoogleProvider(GoogleProvider):
    """GoogleProvider that only allows specific email addresses."""

    def __init__(self, *, allowed_emails: list[str], **kwargs):
        kwargs.setdefault("required_scopes", ["openid", "https://www.googleapis.com/auth/userinfo.email"])
        super().__init__(**kwargs)
        self._allowed_emails = {e.lower() for e in allowed_emails}

    async def _extract_upstream_claims(self, idp_tokens: dict[str, Any]) -> dict[str, Any] | None:
        access_token = idp_tokens.get("access_token")
        if not access_token:
            return None

        async with httpx.AsyncClient(timeout=10) as client:
            resp = await client.get(
                "https://www.googleapis.com/oauth2/v2/userinfo",
                headers={"Authorization": f"Bearer {access_token}"},
            )
            if resp.status_code != 200:
                raise ValueError("Failed to fetch Google user info")

            email = resp.json().get("email", "").lower()
            if email not in self._allowed_emails:
                logger.warning(f"auth.rejected email={email}")
                raise ValueError(f"Email {email} is not authorized")

            return {"email": email}
