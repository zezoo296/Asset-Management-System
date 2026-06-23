from sqlalchemy.orm import Session

from models.organization import Organization


def get_organization_by_email(db: Session, email: str) -> Organization | None:
    return db.query(Organization).filter(Organization.email == email).first()


def create_organization(
    db: Session, name: str, email: str, hashed_password: str
) -> Organization:
    organization = Organization(
        name=name,
        email=email,
        password=hashed_password,
    )
    db.add(organization)
    db.commit()
    db.refresh(organization)
    return organization
