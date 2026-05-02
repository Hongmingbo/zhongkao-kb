import sys
from pathlib import Path

from fastapi.testclient import TestClient

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

import main


def _create_user_and_token(client: TestClient, monkeypatch, tmp_path: Path, username: str):
    monkeypatch.setenv("APP_DB_PATH", str(tmp_path / "app.db"))
    monkeypatch.setenv("INVITE_CODE", "abc123")
    client.post("/api/auth/register", json={"invite_code": "abc123", "username": username, "password": "pw"})
    token = client.post("/api/auth/login", json={"username": username, "password": "pw"}).json()["token"]
    return token


def test_favorites_toggle_and_list(tmp_path: Path, monkeypatch):
    client = TestClient(main.app)
    token = _create_user_and_token(client, monkeypatch, tmp_path, "u1")

    kb_root = tmp_path / "kb"
    kb_root.mkdir(parents=True, exist_ok=True)
    monkeypatch.setattr(main, "KNOWLEDGE_BASE_DIR", kb_root)

    r1 = client.post(
        "/api/favorites/toggle",
        headers={"Authorization": "Bearer " + token},
        json={"category": "语文", "filename": "a.pdf"},
    )
    assert r1.status_code == 200
    assert r1.json()["status"] == "success"
    assert r1.json()["favorited"] is True

    r2 = client.get("/api/favorites", headers={"Authorization": "Bearer " + token})
    assert r2.status_code == 200
    items = r2.json()["items"]
    assert any(it["category"] == "语文" and it["filename"] == "a.pdf" for it in items)

    r3 = client.post(
        "/api/favorites/toggle",
        headers={"Authorization": "Bearer " + token},
        json={"category": "语文", "filename": "a.pdf"},
    )
    assert r3.status_code == 200
    assert r3.json()["favorited"] is False
