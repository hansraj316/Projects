import importlib.util
from pathlib import Path


def load_app():
    app_path = Path(__file__).resolve().parents[1] / "app.py"
    spec = importlib.util.spec_from_file_location("project_starlink_app", str(app_path))
    module = importlib.util.module_from_spec(spec)  # type: ignore[arg-type]
    assert spec and spec.loader
    spec.loader.exec_module(module)  # type: ignore[assignment]
    return module.app


def test_root_get_renders():
    app = load_app()
    client = app.test_client()
    resp = client.get("/")
    assert resp.status_code == 200


def test_post_with_file_id_redirects():
    app = load_app()
    client = app.test_client()
    resp = client.post("/", data={"file_id": "test-file-123"}, follow_redirects=False)
    assert resp.status_code in (302, 303)
    assert "success=True" in resp.headers.get("Location", "")
