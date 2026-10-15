"""HTTP layer only: parse, delegate to UserService, shape the response."""
from typing import Optional

from fastapi import APIRouter, Depends, Query, Request, status
from sqlalchemy.orm import Session

from app.schemas import ErrorResponse, UserCreate, UserList, UserOut, UserStatus, UserUpdate
from app.service import UserService

router = APIRouter(tags=["users"])

E404 = {"model": ErrorResponse, "description": "User not found"}
E409 = {"model": ErrorResponse, "description": "Business rule conflict"}
E422 = {"model": ErrorResponse, "description": "Validation error"}


def get_db(request: Request):
    db = request.app.state.session_factory()
    try:
        yield db
    finally:
        db.close()


def get_service(db: Session = Depends(get_db)) -> UserService:
    return UserService(db)


@router.post("", response_model=UserOut, status_code=status.HTTP_201_CREATED,
             responses={409: E409, 422: E422}, summary="Register a user")
def create_user(body: UserCreate, svc: UserService = Depends(get_service)):
    return svc.create(body.name, body.email, body.phone)


@router.get("", response_model=UserList, responses={422: E422}, summary="List users")
def list_users(
    limit: int = Query(20, ge=1, le=100),
    offset: int = Query(0, ge=0),
    status_filter: Optional[UserStatus] = Query(None, alias="status"),
    svc: UserService = Depends(get_service),
):
    items, total = svc.list(limit, offset, status_filter.value if status_filter else None)
    return UserList(items=items, total=total, limit=limit, offset=offset)


@router.get("/{user_id}", response_model=UserOut, responses={404: E404},
            summary="Get a user (used by other services to verify a user and read status/contact)")
def get_user(user_id: str, svc: UserService = Depends(get_service)):
    return svc.get(user_id)


@router.put("/{user_id}", response_model=UserOut,
            responses={404: E404, 409: E409, 422: E422}, summary="Update profile")
def update_user(user_id: str, body: UserUpdate, svc: UserService = Depends(get_service)):
    return svc.update(user_id, body.name, body.email, body.phone)


@router.post("/{user_id}/activate", response_model=UserOut,
             responses={404: E404, 409: E409}, summary="Activate a user")
def activate_user(user_id: str, svc: UserService = Depends(get_service)):
    return svc.activate(user_id)


@router.post("/{user_id}/deactivate", response_model=UserOut,
             responses={404: E404, 409: E409}, summary="Deactivate a user")
def deactivate_user(user_id: str, svc: UserService = Depends(get_service)):
    return svc.deactivate(user_id)
