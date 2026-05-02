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


def test_upload_image_keeps_original_no_md(tmp_path: Path, monkeypatch):
    client = TestClient(main.app)
    token = _create_user_and_token(client, monkeypatch, tmp_path, "u1")

    kb_root = tmp_path / "kb"
    kb_root.mkdir(parents=True, exist_ok=True)
    monkeypatch.setattr(main, "KNOWLEDGE_BASE_DIR", kb_root)

    r = client.post(
        "/upload",
        headers={"Authorization": "Bearer " + token},
        files={"file": ("a.png", b"\x89PNG\r\n\x1a\nfake", "image/png")},
    )
    assert r.status_code == 200
    data = r.json()
    assert data["status"] == "success"
    res = data["results"][0]
    assert res["saved_as"].endswith(".png")
    cat = res["category"]
    base = kb_root / "u_1" / cat
    assert (base / "a.png").exists()
    assert not (base / "a.png.md").exists()


def test_upload_pdf_keeps_original_and_creates_derived_md(tmp_path: Path, monkeypatch):
    client = TestClient(main.app)
    token = _create_user_and_token(client, monkeypatch, tmp_path, "u1")

    kb_root = tmp_path / "kb"
    kb_root.mkdir(parents=True, exist_ok=True)
    monkeypatch.setattr(main, "KNOWLEDGE_BASE_DIR", kb_root)

    fake_pdf = b"%PDF-1.4\n%fake\n1 0 obj\n<<>>\nendobj\ntrailer\n<<>>\n%%EOF\n"
    r = client.post(
        "/upload",
        headers={"Authorization": "Bearer " + token},
        files={"file": ("a.pdf", fake_pdf, "application/pdf")},
    )
    assert r.status_code == 200
    data = r.json()
    assert data["status"] == "success"
    res = data["results"][0]
    cat = res["category"]
    base = kb_root / "u_1" / cat
    assert (base / "a.pdf").exists()
    assert (base / "a.pdf.md").exists()


def test_file_raw_serves_png(tmp_path: Path, monkeypatch):
    client = TestClient(main.app)
    token = _create_user_and_token(client, monkeypatch, tmp_path, "u1")

    kb_root = tmp_path / "kb"
    kb_root.mkdir(parents=True, exist_ok=True)
    monkeypatch.setattr(main, "KNOWLEDGE_BASE_DIR", kb_root)

    base = kb_root / "u_1" / "语文"
    base.mkdir(parents=True, exist_ok=True)
    (base / "a.png").write_bytes(b"\x89PNG\r\n\x1a\nfake")

    r = client.get("/api/file/raw/语文/a.png", headers={"Authorization": "Bearer " + token})
    assert r.status_code == 200
    assert (r.headers.get("content-type") or "").startswith("image/png")
    assert "no-store" in (r.headers.get("cache-control") or "").lower()
