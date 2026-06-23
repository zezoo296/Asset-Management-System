from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from core.security import create_access_token, hash_password, verify_password
from crud.organization import create_organization, get_organization_by_email
from models.organization import Organization
from schemas.auth import LoginRequest, Token
from schemas.organization import OrganizationCreate


def signup(db: Session, data: OrganizationCreate) -> Organization:
    if get_organization_by_email(db, data.email):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered",
        )

    hashed_password = hash_password(data.password)
    return create_organization(db, data.name, data.email, hashed_password)


def authenticate(db: Session, email: str, password: str) -> Organization:
    organization = get_organization_by_email(db, email)
    if organization is None or not verify_password(password, organization.password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return organization


def login(db: Session, data: LoginRequest) -> Token:
    organization = authenticate(db, data.email, data.password)
    access_token = create_access_token(organization.id)
    return Token(access_token=access_token, token_type="bearer")
