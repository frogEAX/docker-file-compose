import sys
import json
from unittest.mock import MagicMock, patch

import pytest
from fastapi.testclient import TestClient


@pytest.fixture
def app_client():
    mock_ch = MagicMock()
    mock_redis = MagicMock()

    with patch("clickhouse_connect.get_client", return_value=mock_ch), \
         patch("redis.from_url", return_value=mock_redis):
        sys.modules.pop("main", None)
        import main

        client = TestClient(main.app)
        yield client, mock_ch, mock_redis

    sys.modules.pop("main", None)


def test_track_inserts_visit_and_increments_counter(app_client):
    client, mock_ch, mock_redis = app_client

    resp = client.get("/track", params={"path": "/pricing"})

    assert resp.status_code == 200
    assert resp.json() == {"ok": True}

    mock_ch.insert.assert_called_once()
    args, kwargs = mock_ch.insert.call_args
    assert args[0] == "visits"
    inserted_row = args[1][0]
    assert inserted_row[0] == "/pricing"
    assert kwargs["column_names"] == ["path", "ip", "ts"]

    mock_redis.incr.assert_called_once_with("total_visits")


def test_track_defaults_to_root_path_when_missing(app_client):
    client, mock_ch, _ = app_client

    resp = client.get("/track")

    assert resp.status_code == 200
    inserted_row = mock_ch.insert.call_args[0][1][0]
    assert inserted_row[0] == "/"


def test_stats_returns_cached_value_without_hitting_clickhouse(app_client):
    client, mock_ch, mock_redis = app_client

    cached_payload = {"total": 42, "top_pages": [{"path": "/", "count": 42}], "by_hour": []}
    mock_redis.get.return_value = json.dumps(cached_payload)

    resp = client.get("/stats")

    assert resp.status_code == 200
    assert resp.json() == cached_payload
    mock_ch.query.assert_not_called()


def test_stats_computes_and_caches_when_cache_is_empty(app_client):
    client, mock_ch, mock_redis = app_client

    mock_redis.get.return_value = None
    mock_ch.query.side_effect = [
        MagicMock(result_rows=[("/", 10), ("/pricing", 4)]),
        MagicMock(result_rows=[(9, 3), (10, 7)]),
    ]

    resp = client.get("/stats")
    body = resp.json()

    assert resp.status_code == 200
    assert body == {
        "total": 0,
        "top_pages": [{"path": "/", "count": 10}, {"path": "/pricing", "count": 4}],
        "by_hour": [{"hour": 9, "count": 3}, {"hour": 10, "count": 7}],
    }

    mock_redis.setex.assert_called_once()
    setex_args = mock_redis.setex.call_args[0]
    assert setex_args[0] == "stats_cache"
    assert setex_args[1] == 10
    assert json.loads(setex_args[2]) == body
