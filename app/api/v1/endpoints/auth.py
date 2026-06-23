from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from core.database import get_db
from schemas.auth import LoginRequest, Token
from schemas.organization import OrganizationCreate, OrganizationRead
from services.auth import login as login_service
from services.auth import signup as signup_service

router = APIRouter()


@router.post("/signup", response_model=OrganizationRead, status_code=201)
def signup(data: OrganizationCreate, db: Session = Depends(get_db)):
    organization = signup_service(db, data)
    return organization


@router.post("/login", response_model=Token)
def login(data: LoginRequest, db: Session = Depends(get_db)):
    return login_service(db, data)