from fastapi.testclient import TestClient

from vision_caption.infrastructure.server.app import create_app
from vision_caption.infrastructure.settings import AppSettings, ServerSettings


def _app_with_frontend(tmp_path):
    dist_path = tmp_path / "dist"
    assets_path = dist_path / "assets"
    assets_path.mkdir(parents=True)
    (dist_path / "index.html").write_text(
        "<!doctype html><html><body>Vision Caption</body></html>",
        encoding="utf-8",
    )
    (assets_path / "app.js").write_text(
        "console.log('vision-caption')",
        encoding="utf-8",
    )
    settings = AppSettings(
        server=ServerSettings(frontend_dist_path=dist_path),
        runtime={"use_mocks": True},
    )
    return create_app(settings)


def test_frontend_health_assets_and_spa_fallback(tmp_path) -> None:
    with TestClient(_app_with_frontend(tmp_path)) as client:
        root = client.get("/")
        health = client.get("/health")
        asset = client.get("/assets/app.js")
        client_route = client.get("/impostazioni/accessibilita")

    assert root.status_code == 200
    assert root.headers["content-type"].startswith("text/html")
    assert "Vision Caption" in root.text
    assert health.status_code == 200
    assert health.json() == {"status": "ok", "mode": "mock"}
    assert asset.status_code == 200
    assert "vision-caption" in asset.text
    assert client_route.status_code == 200
    assert "Vision Caption" in client_route.text


def test_missing_backend_and_asset_paths_do_not_fall_back_to_html(tmp_path) -> None:
    with TestClient(_app_with_frontend(tmp_path)) as client:
        missing_api = client.get("/api/missing")
        missing_asset = client.get("/assets/missing.js")

    assert missing_api.status_code == 404
    assert missing_asset.status_code == 404


def test_websocket_route_precedes_frontend_mount(tmp_path) -> None:
    with TestClient(_app_with_frontend(tmp_path)) as client:
        with client.websocket_connect("/ws/vision") as websocket:
            config = websocket.receive_json()

    assert config["type"] == "stream_config"
    assert config["protocol_version"] == 1
    assert config["max_in_flight"] == 1
