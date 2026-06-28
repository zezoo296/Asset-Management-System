from fastapi.testclient import TestClient

from tests.helpers import asset_payload, count_assets, get_asset_by_value


def test_create_asset(client: TestClient, auth_headers: dict[str, str], db):
    payload = asset_payload(
        asset_id="domain-example-com",
        asset_type="domain",
        value="example.com",
        status="active",
        tags=["root"],
        metadata={},
    )

    response = client.post("/api/v1/assets/", json=payload, headers=auth_headers)

    assert response.status_code == 201
    body = response.json()
    assert body["value"] == "example.com"
    assert body["first_seen"] is not None
    assert body["last_seen"] is not None
    assert count_assets(db) == 1
    assert get_asset_by_value(db, "example.com") is not None


def test_duplicate_asset_updates_existing(
    client: TestClient,
    auth_headers: dict[str, str],
    db,
    pause,
):
    payload = asset_payload(
        asset_id="domain-example-com",
        asset_type="domain",
        value="example.com",
    )

    first_response = client.post("/api/v1/assets/", json=payload, headers=auth_headers)
    assert first_response.status_code == 201
    first_seen = first_response.json()["first_seen"]

    pause

    second_response = client.post("/api/v1/assets/", json=payload, headers=auth_headers)
    assert second_response.status_code == 200
    second_body = second_response.json()

    assert count_assets(db) == 1
    assert second_body["first_seen"] == first_seen
    assert second_body["last_seen"] > first_seen


def test_duplicate_merges_tags(client: TestClient, auth_headers: dict[str, str], db, pause):
    existing_payload = asset_payload(
        asset_id="domain-example-com",
        asset_type="domain",
        value="example.com",
        tags=["prod"],
    )
    client.post("/api/v1/assets/", json=existing_payload, headers=auth_headers)

    pause

    import_payload = asset_payload(
        asset_id="domain-example-com",
        asset_type="domain",
        value="example.com",
        tags=["critical"],
    )
    response = client.post("/api/v1/assets/import", json=[import_payload], headers=auth_headers)
    assert response.status_code == 200

    asset = get_asset_by_value(db, "example.com")
    assert asset is not None
    assert asset.tags == ["prod", "critical"]


def test_duplicate_merges_metadata(client: TestClient, auth_headers: dict[str, str], db, pause):
    existing_payload = asset_payload(
        asset_id="domain-example-com",
        asset_type="domain",
        value="example.com",
        metadata={"issuer": "Lets Encrypt"},
    )
    client.post("/api/v1/assets/", json=existing_payload, headers=auth_headers)

    pause

    import_payload = asset_payload(
        asset_id="domain-example-com",
        asset_type="domain",
        value="example.com",
        metadata={"expires": "2026-01-01"},
    )
    response = client.post("/api/v1/assets/import", json=[import_payload], headers=auth_headers)
    assert response.status_code == 200

    asset = get_asset_by_value(db, "example.com")
    assert asset is not None
    assert asset.metadata_ == {
        "issuer": "Lets Encrypt",
        "expires": "2026-01-01",
    }


def test_stale_asset_becomes_active_when_seen_again(
    client: TestClient,
    auth_headers: dict[str, str],
    db,
    pause,
):
    stale_payload = asset_payload(
        asset_id="domain-example-com",
        asset_type="domain",
        value="example.com",
        status="stale",
    )
    first_response = client.post("/api/v1/assets/", json=stale_payload, headers=auth_headers)
    assert first_response.status_code == 201
    first_last_seen = first_response.json()["last_seen"]

    pause

    import_payload = asset_payload(
        asset_id="domain-example-com",
        asset_type="domain",
        value="example.com",
        status="active",
    )
    second_response = client.post(
        "/api/v1/assets/import",
        json=[import_payload],
        headers=auth_headers,
    )
    assert second_response.status_code == 200

    asset = get_asset_by_value(db, "example.com")
    assert asset is not None
    assert asset.status.value == "active"
    assert asset.last_seen.isoformat().replace("+00:00", "Z") >= first_last_seen.replace(
        "+00:00", "Z"
    )
