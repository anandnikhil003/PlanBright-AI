"""Create and validate short-lived local development JWTs."""

import os
from datetime import datetime, timedelta, timezone

from jose import JWTError, jwt


DEV_ISSUER = "planbright-local-dev"
DEV_AUDIENCE = "planbright-local-api"


def _dev_secret() -> str:
    if os.getenv("AUTH_MODE", "external").strip().lower() != "development":
        raise RuntimeError("Set AUTH_MODE=development in backend/.env first")
    secret = os.getenv("DEV_TOKEN_SECRET", "").strip()
    if len(secret) < 32:
        raise RuntimeError("DEV_TOKEN_SECRET must be at least 32 characters")
    return secret


def generate_dev_token(user_id: str = "local-dev-user", ttl_minutes: int = 60) -> str:
    if ttl_minutes < 1 or ttl_minutes > 1440:
        raise ValueError("Token lifetime must be between 1 and 1440 minutes")
    now = datetime.now(timezone.utc)
    issued_at = int(now.timestamp())
    claims = {
        "sub": user_id,
        "iss": DEV_ISSUER,
        "aud": DEV_AUDIENCE,
        "iat": issued_at,
        "exp": int((now + timedelta(minutes=ttl_minutes)).timestamp()),
    }
    return jwt.encode(claims, _dev_secret(), algorithm="HS256")


def verify_dev_token(token: str) -> str | None:
    if os.getenv("AUTH_MODE", "external").strip().lower() != "development":
        return None
    try:
        claims = jwt.decode(
            token,
            _dev_secret(),
            algorithms=["HS256"],
            audience=DEV_AUDIENCE,
            issuer=DEV_ISSUER,
            options={"require_exp": True, "require_sub": True},
        )
        return claims.get("sub")
    except (JWTError, RuntimeError, TypeError, ValueError):
        return None
