from uuid import UUID

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session

from core.database import get_db
from core.security import decode_access_token
from models.organization import Organization

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/login")


def get_current_organization(
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db),
) -> Organization:
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )

    subject = decode_access_token(token)
    if subject is None:
        raise credentials_exception

    try:
        organization_id = UUID(subject)
    except ValueError as exc:
        raise credentials_exception from exc

    organization = db.get(Organization, organization_id)
    if organization is None:
        raise credentials_exception

    return organization
