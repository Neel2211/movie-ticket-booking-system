"""Business logic. All business rules live here (and only here).

BR-U1  Email must be unique, case-insensitive            -> 409 EMAIL_ALREADY_EXISTS
BR-U2  name/email/phone must be valid                     -> 422 (see schemas.py)
BR-U3  Status lifecycle ACTIVE <-> INACTIVE, repeating a
       transition is rejected                             -> 409 INVALID_STATE_TRANSITION
BR-U4  An INACTIVE user's profile cannot be edited
       (must be re-activated first)                       -> 409 USER_INACTIVE
"""
from sqlalchemy import func, select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.errors import (
    DuplicateEmailError,
    InvalidStateTransitionError,
    UserInactiveError,
    UserNotFoundError,
)
from app.models import User

ALLOWED_TRANSITIONS = {
    "ACTIVE": {"INACTIVE"},
    "INACTIVE": {"ACTIVE"},
}


def normalize_email(email: str) -> str:
    return email.strip().lower()


def check_transition(current: str, target: str) -> None:
    """BR-U3 as a pure function so it is trivially unit-testable."""
    if target not in ALLOWED_TRANSITIONS.get(current, set()):
        raise InvalidStateTransitionError(f"User is already {current}; cannot move to {target}")


class UserService:
    def __init__(self, db: Session):
        self.db = db

    def _commit_or_conflict(self, email: str) -> None:
        try:
            self.db.commit()
        except IntegrityError:
            # The UNIQUE constraint decides races between concurrent requests (BR-U1).
            self.db.rollback()
            raise DuplicateEmailError(f"A user with email '{email}' already exists")

    def create(self, name: str, email: str, phone: str) -> User:
        norm = normalize_email(email)
        # Fast, friendly check; the DB constraint below is the real guarantee.
        if self.db.scalar(select(User.id).where(User.email_normalized == norm)):
            raise DuplicateEmailError(f"A user with email '{email}' already exists")
        user = User(name=name, email=email, email_normalized=norm, phone=phone, status="ACTIVE")
        self.db.add(user)
        self._commit_or_conflict(email)
        return user

    def get(self, user_id: str) -> User:
        user = self.db.get(User, user_id)
        if user is None:
            raise UserNotFoundError(f"User '{user_id}' not found")
        return user

    def list(self, limit: int, offset: int, status: str | None = None):
        q = select(User)
        count_q = select(func.count()).select_from(User)
        if status:
            q = q.where(User.status == status)
            count_q = count_q.where(User.status == status)
        items = self.db.scalars(q.order_by(User.created_at, User.id).limit(limit).offset(offset)).all()
        return items, self.db.scalar(count_q)

    def update(self, user_id: str, name=None, email=None, phone=None) -> User:
        user = self.get(user_id)
        if user.status == "INACTIVE":
            raise UserInactiveError("Inactive users cannot be edited; activate the user first")
        if name is not None:
            user.name = name
        if phone is not None:
            user.phone = phone
        if email is not None:
            user.email = email
            user.email_normalized = normalize_email(email)
        self._commit_or_conflict(email or user.email)
        return user

    def _set_status(self, user_id: str, target: str) -> User:
        user = self.get(user_id)
        check_transition(user.status, target)
        user.status = target
        self.db.commit()
        return user

    def activate(self, user_id: str) -> User:
        return self._set_status(user_id, "ACTIVE")

    def deactivate(self, user_id: str) -> User:
        return self._set_status(user_id, "INACTIVE")
