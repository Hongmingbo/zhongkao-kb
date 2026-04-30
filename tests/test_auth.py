import sys
from pathlib import Path

from fastapi.testclient import TestClient

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

import main


def test_register_login_me(tmp_path: Path, monkeypatch):
    db_path = tmp_path / "app.db"
    monkeypatch.setenv("APP_DB_PATH", str(db_path))
    monkeypatch.setenv("INVITE_CODE", "abc123")

    client = TestClient(main.app)

    r = client.post("/api/auth/register", json={"invite_code": "abc123", "username": "alice", "password": "pw"})
    assert r.status_code == 200
    assert r.json()["status"] == "success"

    r2 = client.post("/api/auth/login", json={"username": "alice", "password": "pw"})
    assert r2.status_code == 200
    token = r2.json()["token"]
    assert token

    r3 = client.get("/api/auth/me", headers={"Authorization": "Bearer " + token})
    assert r3.status_code == 200
    data = r3.json()
    assert data["username"] == "alice"


def test_kb_isolated_by_user(tmp_path: Path, monkeypatch):
    db_path = tmp_path / "app.db"
    monkeypatch.setenv("APP_DB_PATH", str(db_path))
    monkeypatch.setenv("INVITE_CODE", "abc123")

    client = TestClient(main.app)
    client.post("/api/auth/register", json={"invite_code": "abc123", "username": "u1", "password": "pw"})
    client.post("/api/auth/register", json={"invite_code": "abc123", "username": "u2", "password": "pw"})
    t1 = client.post("/api/auth/login", json={"username": "u1", "password": "pw"}).json()["token"]
    t2 = client.post("/api/auth/login", json={"username": "u2", "password": "pw"}).json()["token"]

    kb_root = tmp_path / "knowledge_base"
    kb_root.mkdir(parents=True, exist_ok=True)
    monkeypatch.setattr(main, "KNOWLEDGE_BASE_DIR", kb_root)

    (kb_root / "u_1" / "语文").mkdir(parents=True)
    (kb_root / "u_1" / "语文" / "a.md").write_text("x", encoding="utf-8")

    r1 = client.get("/api/stats", headers={"Authorization": "Bearer " + t1})
    r2 = client.get("/api/stats", headers={"Authorization": "Bearer " + t2})
    assert r1.status_code == 200 and "语文" in r1.json()
    assert r2.status_code == 200 and r2.json() == {}

