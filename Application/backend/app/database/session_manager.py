"""Simple JWT session helpers backed by the auth_sessions table.

Flow this module implements:
    1. Caller (a future Flask login route) verifies the user's password
       with Werkzeug first.
    2. generate_and_store_token(user_id) asks Flask-JWT-Extended for one
       real JWT access token, valid for exactly 1 hour, stores that exact
       token string in auth_sessions, and returns it.

A future Flask login route only needs:

    token = generate_and_store_token(user.id)
    return {"access_token": token}

No JTI bookkeeping, refresh-token complexity, or blocklist architecture.

Every function below accepts an optional `session` argument. Pass one in
(e.g. from a test fixture, or a request-scoped session) to use it
directly; omit it and each call opens and closes its own session via
`database.get_session()` — the shape a real Flask route would use.

Run cleanup from Application/backend/app/ (see README):

    python -m database.session_manager
"""

import os
from contextlib import nullcontext
from datetime import datetime, timedelta

from flask import Flask
from flask_jwt_extended import JWTManager, create_access_token

from .database import get_session
from .models.auth import AuthSession

# Exactly 1 hour, per the simplified session design.
ACCESS_TOKEN_EXPIRES = timedelta(hours=1)

# Dev-only fallback secret so this module works out of the box for tests
# and local development. The real Flask app must set JWT_SECRET_KEY via
# environment/config in any non-dev environment — never rely on this
# fallback for production.
_DEV_JWT_SECRET = "dev-only-insecure-secret-do-not-use-in-production"


def _jwt_app() -> Flask:
    """Build a minimal Flask app configured for Flask-JWT-Extended.

    This database package doesn't own the real Flask app, so it builds a
    throwaway one purely to reuse Flask-JWT-Extended's token encoding with
    the correct secret and expiry settings.
    """
    app = Flask(__name__)
    from app.config import Config
    app.config.from_object(Config)
    JWTManager(app)
    return app


def _session_scope(session):
    """Use the given session as-is, or open/close a new one."""
    return nullcontext(session) if session is not None else get_session()


def generate_and_store_token(user_id: int, session=None) -> str:
    """Generate a real 1-hour JWT for user_id, store it, and return it."""
    app = _jwt_app()
    with app.app_context():
        token = create_access_token(identity=str(user_id))

    now = datetime.utcnow()
    with _session_scope(session) as db:
        auth_session = AuthSession(user_id=user_id, token=token, expires_at=now + ACCESS_TOKEN_EXPIRES)
        db.add(auth_session)
        db.commit()
    return token


def get_active_token(user_id: int, session=None) -> str | None:
    """Return an active (non-expired) stored token for user_id, if any."""
    with _session_scope(session) as db:
        auth_session = (
            db.query(AuthSession)
            .filter(AuthSession.user_id == user_id, AuthSession.expires_at > datetime.utcnow())
            .order_by(AuthSession.expires_at.desc())
            .first()
        )
        return auth_session.token if auth_session else None


def validate_stored_token(token: str, session=None) -> bool:
    """True if the exact token exists in auth_sessions and hasn't expired. Slides expiration by 1 hour."""
    with _session_scope(session) as db:
        auth_session = db.query(AuthSession).filter_by(token=token).one_or_none()
        if auth_session is None:
            return False
        
        if auth_session.expires_at > datetime.utcnow():
            # Sliding expiration: extend token by 1 hour from now
            auth_session.expires_at = datetime.utcnow() + ACCESS_TOKEN_EXPIRES
            db.commit()
            return True
        return False


def delete_token(token: str, session=None) -> bool:
    """Delete the auth_sessions row for token (logout). Returns True if found."""
    with _session_scope(session) as db:
        auth_session = db.query(AuthSession).filter_by(token=token).one_or_none()
        if auth_session is None:
            return False
        db.delete(auth_session)
        db.commit()
        return True


def cleanup_expired_tokens(session=None) -> int:
    """Delete every expired auth_sessions row. Returns rows deleted."""
    with _session_scope(session) as db:
        deleted = (
            db.query(AuthSession)
            .filter(AuthSession.expires_at < datetime.utcnow())
            .delete(synchronize_session=False)
        )
        db.commit()
        return deleted


def main() -> None:
    deleted = cleanup_expired_tokens()
    print(f"Removed {deleted} expired auth session(s).")


if __name__ == "__main__":
    main()
