from datetime import datetime, timedelta, timezone

from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from tests.helpers import create_asset_via_api
from models.asset import Asset


def seed_filter_assets(client: TestClient, auth_headers: dict[str, str]) -> None:
    fixtures = [
        ("domain-prod", "domain", "prod.example.com", "active", ["prod"]),
        ("subdomain-dev", "subdomain", "dev.example.com", "active", ["dev"]),
        ("ip-stale", "ip_address", "203.0.113.1", "stale", ["prod"]),
        ("service-archived", "service", "internal-api", "archived", ["internal"]),
    ]
    for asset_id, asset_type, value, status, tags in fixtures:
        create_asset_via_api(
            client,
            auth_headers,
            asset_id=asset_id,
            asset_type=asset_type,
            value=value,
            status=status,
            tags=tags,
        )


def test_filter_by_type(client: TestClient, auth_headers: dict[str, str]):
    seed_filter_assets(client, auth_headers)

    response = client.get("/api/v1/assets/?type=domain", headers=auth_headers)

    assert response.status_code == 200
    body = response.json()
    assert body["total"] == 1
    assert len(body["items"]) == 1
    assert body["items"][0]["type"] == "domain"


def test_filter_by_status(client: TestClient, auth_headers: dict[str, str]):
    seed_filter_assets(client, auth_headers)

    response = client.get("/api/v1/assets/?status=active", headers=auth_headers)

    assert response.status_code == 200
    body = response.json()
    assert body["total"] == 2
    assert all(item["status"] == "active" for item in body["items"])


def test_filter_by_tag(client: TestClient, auth_headers: dict[str, str]):
    seed_filter_assets(client, auth_headers)

    response = client.get("/api/v1/assets/?tag=prod", headers=auth_headers)

    assert response.status_code == 200
    body = response.json()
    values = {item["value"] for item in body["items"]}
    assert values == {"prod.example.com", "203.0.113.1"}


def test_filter_by_value_contains(client: TestClient, auth_headers: dict[str, str]):
    for asset_id, value in [
        ("subdomain-api", "api.example.com"),
        ("subdomain-mail", "mail.example.com"),
        ("domain-google", "google.com"),
    ]:
        create_asset_via_api(
            client,
            auth_headers,
            asset_id=asset_id,
            asset_type="subdomain" if "example.com" in value else "domain",
            value=value,
        )

    response = client.get("/api/v1/assets/?value=example", headers=auth_headers)

    assert response.status_code == 200
    body = response.json()
    assert body["total"] == 2
    assert len(body["items"]) == 2


def test_sorting(client: TestClient, auth_headers: dict[str, str], db: Session):
    now = datetime.now(timezone.utc)

    create_asset_via_api(
        client,
        auth_headers,
        asset_id="asset-a",
        value="a.example.com",
    )
    create_asset_via_api(
        client,
        auth_headers,
        asset_id="asset-b",
        value="b.example.com",
    )
    create_asset_via_api(
        client,
        auth_headers,
        asset_id="asset-c",
        value="c.example.com",
    )

    db.query(Asset).filter(Asset.id == "asset-a").update(
        {"first_seen": now - timedelta(days=3)}
    )
    db.query(Asset).filter(Asset.id == "asset-b").update(
        {"first_seen": now - timedelta(days=2)}
    )
    db.query(Asset).filter(Asset.id == "asset-c").update(
        {"first_seen": now - timedelta(days=1)}
    )
    db.commit()

    response = client.get(
        "/api/v1/assets/?sort_by=first_seen&sort_order=asc",
        headers=auth_headers,
    )

    assert response.status_code == 200
    items = response.json()["items"]
    assert [item["id"] for item in items] == ["asset-a", "asset-b", "asset-c"]


def test_pagination(client: TestClient, auth_headers: dict[str, str]):
    for index in range(25):
        create_asset_via_api(
            client,
            auth_headers,
            asset_id=f"asset-{index:02d}",
            value=f"asset-{index:02d}.example.com",
        )

    response = client.get(
        "/api/v1/assets/?page=2&limit=10",
        headers=auth_headers,
    )

    assert response.status_code == 200
    body = response.json()
    assert len(body["items"]) == 10
    assert body["page"] == 2
    assert body["limit"] == 10
    assert body["total"] == 25
    assert body["pages"] == 3
