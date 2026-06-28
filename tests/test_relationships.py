from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from tests.helpers import create_asset_via_api
from models.enums import RelationType
from models.relation import Relation


def test_create_relationship(
    client: TestClient,
    auth_headers: dict[str, str],
    db: Session,
):
    create_asset_via_api(
        client,
        auth_headers,
        asset_id="domain-example-com",
        asset_type="domain",
        value="example.com",
    )
    create_asset_via_api(
        client,
        auth_headers,
        asset_id="subdomain-www",
        asset_type="subdomain",
        value="www.example.com",
    )

    response = client.post(
        "/api/v1/relations/",
        json={
            "from_id": "subdomain-www",
            "to_id": "domain-example-com",
            "type": "parent",
        },
        headers=auth_headers,
    )

    assert response.status_code == 201
    body = response.json()
    assert body["from_id"] == "subdomain-www"
    assert body["to_id"] == "domain-example-com"
    assert body["type"] == "parent"

    relation = (
        db.query(Relation)
        .filter(
            Relation.from_id == "subdomain-www",
            Relation.to_id == "domain-example-com",
            Relation.type == RelationType.PARENT,
        )
        .first()
    )
    assert relation is not None


def test_get_related_assets(client: TestClient, auth_headers: dict[str, str]):
    create_asset_via_api(
        client,
        auth_headers,
        asset_id="domain-example-com",
        asset_type="domain",
        value="example.com",
    )
    create_asset_via_api(
        client,
        auth_headers,
        asset_id="subdomain-www",
        asset_type="subdomain",
        value="www.example.com",
    )
    create_asset_via_api(
        client,
        auth_headers,
        asset_id="ip-203",
        asset_type="ip_address",
        value="203.0.113.10",
    )

    client.post(
        "/api/v1/relations/",
        json={
            "from_id": "subdomain-www",
            "to_id": "domain-example-com",
            "type": "parent",
        },
        headers=auth_headers,
    )
    client.post(
        "/api/v1/relations/",
        json={
            "from_id": "subdomain-www",
            "to_id": "ip-203",
            "type": "resolves_to",
        },
        headers=auth_headers,
    )

    response = client.get(
        "/api/v1/assets/domain-example-com/graph",
        headers=auth_headers,
    )

    assert response.status_code == 200
    body = response.json()
    assert len(body["nodes"]) == 3
    assert len(body["edges"]) == 2
