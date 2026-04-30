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
    assert "nickname" in data
    assert "has_avatar" in data


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
    (kb_root / "u_1" / "_profile").mkdir(parents=True)
    (kb_root / "u_1" / "_profile" / "avatar.png").write_bytes(b"\x89PNG\r\n\x1a\n")

    r1 = client.get("/api/stats", headers={"Authorization": "Bearer " + t1})
    r2 = client.get("/api/stats", headers={"Authorization": "Bearer " + t2})
    assert r1.status_code == 200 and "语文" in r1.json()
    assert "_profile" not in r1.json()
    assert r2.status_code == 200 and r2.json() == {}


def test_set_nickname(tmp_path: Path, monkeypatch):
    db_path = tmp_path / "app.db"
    monkeypatch.setenv("APP_DB_PATH", str(db_path))
    monkeypatch.setenv("INVITE_CODE", "abc123")
    client = TestClient(main.app)
    client.post("/api/auth/register", json={"invite_code": "abc123", "username": "alice", "password": "pw"})
    token = client.post("/api/auth/login", json={"username": "alice", "password": "pw"}).json()["token"]

    r = client.post("/api/profile/nickname", json={"nickname": "小明"}, headers={"Authorization": "Bearer " + token})
    assert r.status_code == 200
    assert r.json()["nickname"] == "小明"

    r2 = client.get("/api/auth/me", headers={"Authorization": "Bearer " + token})
    assert r2.status_code == 200
    assert r2.json()["nickname"] == "小明"


def test_avatar_default_and_upload(tmp_path: Path, monkeypatch):
    db_path = tmp_path / "app.db"
    monkeypatch.setenv("APP_DB_PATH", str(db_path))
    monkeypatch.setenv("INVITE_CODE", "abc123")
    client = TestClient(main.app)
    client.post("/api/auth/register", json={"invite_code": "abc123", "username": "alice", "password": "pw"})
    token = client.post("/api/auth/login", json={"username": "alice", "password": "pw"}).json()["token"]

    r0 = client.get("/api/profile/avatar", headers={"Authorization": "Bearer " + token})
    assert r0.status_code == 200
    assert r0.headers.get("content-type", "").startswith("image/")
    assert len(r0.content) > 0

    png = (
        b"\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR\x00\x00\x00\x01\x00\x00\x00\x01\x08\x06\x00\x00\x00\x1f\x15\xc4\x89"
        b"\x00\x00\x00\x0cIDATx\x9cc\xf8\xff\xff?\x00\x05\xfe\x02\xfeA\xd9\xdd\xa6\x00\x00\x00\x00IEND\xaeB`\x82"
    )
    files = {"file": ("avatar.png", png, "image/png")}
    r1 = client.post("/api/profile/avatar", files=files, headers={"Authorization": "Bearer " + token})
    assert r1.status_code == 200

    r2 = client.get("/api/profile/avatar", headers={"Authorization": "Bearer " + token})
    assert r2.status_code == 200
    assert r2.headers.get("content-type", "").startswith("image/png")
    assert r2.content[:8] == b"\x89PNG\r\n\x1a\n"


def test_admin_users_count(tmp_path: Path, monkeypatch):
    db_path = tmp_path / "app.db"
    monkeypatch.setenv("APP_DB_PATH", str(db_path))
    monkeypatch.setenv("INVITE_CODE", "abc123")
    monkeypatch.setenv("ADMIN_TOKEN", "admintoken")
    client = TestClient(main.app)

    client.post("/api/auth/register", json={"invite_code": "abc123", "username": "u1", "password": "pw"})
    client.post("/api/auth/register", json={"invite_code": "abc123", "username": "u2", "password": "pw"})

    r1 = client.get("/api/admin/users_count")
    assert r1.status_code in [403, 503]

    r2 = client.get("/api/admin/users_count", headers={"X-Admin-Token": "admintoken"})
    assert r2.status_code == 200
    assert r2.json()["user_count"] == 2


def test_change_password_and_invalidate_sessions(tmp_path: Path, monkeypatch):
    db_path = tmp_path / "app.db"
    monkeypatch.setenv("APP_DB_PATH", str(db_path))
    monkeypatch.setenv("INVITE_CODE", "abc123")
    client = TestClient(main.app)

    client.post("/api/auth/register", json={"invite_code": "abc123", "username": "alice", "password": "oldpw"})
    token = client.post("/api/auth/login", json={"username": "alice", "password": "oldpw"}).json()["token"]

    r = client.post(
        "/api/profile/password",
        json={"old_password": "oldpw", "new_password": "newpw123"},
        headers={"Authorization": "Bearer " + token},
    )
    assert r.status_code == 200
    assert r.json()["status"] == "success"

    r2 = client.get("/api/auth/me", headers={"Authorization": "Bearer " + token})
    assert r2.status_code == 401

    r3 = client.post("/api/auth/login", json={"username": "alice", "password": "oldpw"})
    assert r3.status_code == 401
    r4 = client.post("/api/auth/login", json={"username": "alice", "password": "newpw123"})
    assert r4.status_code == 200


def test_admin_reset_password(tmp_path: Path, monkeypatch):
    db_path = tmp_path / "app.db"
    monkeypatch.setenv("APP_DB_PATH", str(db_path))
    monkeypatch.setenv("INVITE_CODE", "abc123")
    monkeypatch.setenv("ADMIN_TOKEN", "admintoken")
    client = TestClient(main.app)

    client.post("/api/auth/register", json={"invite_code": "abc123", "username": "alice", "password": "pw1"})
    token = client.post("/api/auth/login", json={"username": "alice", "password": "pw1"}).json()["token"]

    r = client.post(
        "/api/admin/reset_password",
        json={"username": "alice", "new_password": "pw2xxxxx"},
        headers={"X-Admin-Token": "admintoken"},
    )
    assert r.status_code == 200
    assert r.json()["status"] == "success"

    r2 = client.get("/api/auth/me", headers={"Authorization": "Bearer " + token})
    assert r2.status_code == 401

    r3 = client.post("/api/auth/login", json={"username": "alice", "password": "pw1"})
    assert r3.status_code == 401
    r4 = client.post("/api/auth/login", json={"username": "alice", "password": "pw2xxxxx"})
    assert r4.status_code == 200


def test_trash_delete_restore_and_clear(tmp_path: Path, monkeypatch):
    db_path = tmp_path / "app.db"
    monkeypatch.setenv("APP_DB_PATH", str(db_path))
    monkeypatch.setenv("INVITE_CODE", "abc123")
    client = TestClient(main.app)

    client.post("/api/auth/register", json={"invite_code": "abc123", "username": "u1", "password": "pw"})
    token = client.post("/api/auth/login", json={"username": "u1", "password": "pw"}).json()["token"]

    kb_root = tmp_path / "kb"
    kb_root.mkdir(parents=True, exist_ok=True)
    monkeypatch.setattr(main, "KNOWLEDGE_BASE_DIR", kb_root)

    cat_dir = kb_root / "u_1" / "语文"
    cat_dir.mkdir(parents=True, exist_ok=True)
    (cat_dir / "a.md").write_text("x", encoding="utf-8")
    (cat_dir / "a.md.meta.json").write_text('{"year":"2024"}', encoding="utf-8")

    d = client.delete("/api/file/语文/a.md", headers={"Authorization": "Bearer " + token})
    assert d.status_code == 200

    r = client.get("/api/trash", headers={"Authorization": "Bearer " + token})
    assert r.status_code == 200
    items = r.json().get("items") or []
    assert len(items) == 1
    tid = items[0]["id"]

    cat_dir.mkdir(parents=True, exist_ok=True)
    (cat_dir / "a.md").write_text("y", encoding="utf-8")
    rr = client.post("/api/trash/restore", json={"id": tid}, headers={"Authorization": "Bearer " + token})
    assert rr.status_code == 200
    restored = rr.json()["restored"]["filename"]
    assert restored != ""
    assert (cat_dir / restored).exists()

    r2 = client.get("/api/trash", headers={"Authorization": "Bearer " + token})
    assert r2.status_code == 200
    assert (r2.json().get("items") or []) == []

    d2 = client.delete("/api/file/语文/" + restored, headers={"Authorization": "Bearer " + token})
    assert d2.status_code == 200
    r3 = client.get("/api/trash", headers={"Authorization": "Bearer " + token})
    items2 = r3.json().get("items") or []
    assert len(items2) == 1

    c = client.delete("/api/trash/clear", headers={"Authorization": "Bearer " + token})
    assert c.status_code == 200
    r4 = client.get("/api/trash", headers={"Authorization": "Bearer " + token})
    assert (r4.json().get("items") or []) == []
