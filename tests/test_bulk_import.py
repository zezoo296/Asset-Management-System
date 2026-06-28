from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from tests.helpers import asset_payload, count_assets, create_asset_via_api


def test_bulk_import_success(client: TestClient, auth_headers: dict[str, str]):
    assets = [
        asset_payload(
            asset_id=f"domain-{index}",
            value=f"domain-{index}.example.com",
            source="import",
        )
        for index in range(5)
    ]

    response = client.post("/api/v1/assets/import", json=assets, headers=auth_headers)

    assert response.status_code == 200
    body = response.json()
    assert body["created"] == 5
    assert body["failed"] == 0
    assert body["updated"] == 0


def test_bulk_import_duplicate_assets(
    client: TestClient,
    auth_headers: dict[str, str],
    db: Session,
):
    create_asset_via_api(
        client,
        auth_headers,
        asset_id="domain-example-com",
        value="example.com",
    )

    response = client.post(
        "/api/v1/assets/import",
        json=[
            asset_payload(
                asset_id="domain-example-com",
                value="example.com",
                source="import",
            )
        ],
        headers=auth_headers,
    )

    assert response.status_code == 200
    body = response.json()
    assert body["created"] == 0
    assert body["updated"] == 1
    assert count_assets(db) == 1


def test_bulk_import_partial_failure(
    client: TestClient,
    auth_headers: dict[str, str],
    db: Session,
):
    assets = [
        asset_payload(
            asset_id="domain-valid-1",
            value="valid-1.example.com",
            source="import",
        ),
        {
            "id": "invalid-asset",
            "type": "domain",
            "value": "invalid.example.com",
        },
        asset_payload(
            asset_id="domain-valid-2",
            value="valid-2.example.com",
            source="import",
        ),
    ]

    response = client.post("/api/v1/assets/import", json=assets, headers=auth_headers)

    assert response.status_code == 207
    body = response.json()
    assert body["created"] == 2
    assert body["failed"] == 1
    assert count_assets(db) == 2
