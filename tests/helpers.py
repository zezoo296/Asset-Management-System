import time
from collections.abc import Generator

from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from models.asset import Asset


def asset_payload(
    *,
    asset_id: str,
    asset_type: str = "domain",
    value: str = "example.com",
    status: str = "active",
    source: str = "manual",
    tags: list[str] | None = None,
    metadata: dict | None = None,
    **extra: str | None,
) -> dict:
    payload = {
        "id": asset_id,
        "type": asset_type,
        "value": value,
        "status": status,
        "source": source,
        "tags": tags if tags is not None else [],
        "metadata": metadata if metadata is not None else {},
    }
    payload.update({key: value for key, value in extra.items() if value is not None})
    return payload


def create_asset_via_api(
    client: TestClient,
    headers: dict[str, str],
    **kwargs,
) -> dict:
    response = client.post("/api/v1/assets/", json=asset_payload(**kwargs), headers=headers)
    assert response.status_code in (200, 201), response.text
    return response.json()


def import_assets_via_api(
    client: TestClient,
    headers: dict[str, str],
    assets: list[dict],
):
    return client.post("/api/v1/assets/import", json=assets, headers=headers)


def count_assets(db: Session) -> int:
    return db.query(Asset).count()


def get_asset_by_value(db: Session, value: str) -> Asset | None:
    return db.query(Asset).filter(Asset.value == value).first()


def pause() -> Generator[None, None, None]:
    time.sleep(0.05)
    yield
