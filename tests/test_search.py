import sys
import datetime as dt
from pathlib import Path
from zoneinfo import ZoneInfo

from fastapi.testclient import TestClient

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

import main
from main import search_knowledge_base


def _create_user_and_token(client: TestClient, monkeypatch, tmp_path: Path, username: str):
    monkeypatch.setenv("APP_DB_PATH", str(tmp_path / "app.db"))
    monkeypatch.setenv("INVITE_CODE", "abc123")
    r = client.post("/api/auth/register", json={"invite_code": "abc123", "username": username, "password": "pw"})
    if r.status_code == 200:
        user_id = r.json()["user"]["id"]
    else:
        user_id = None
    token = client.post("/api/auth/login", json={"username": username, "password": "pw"}).json()["token"]
    return user_id, token


def test_search_matches_filename_and_content(tmp_path: Path):
    kb = tmp_path / "knowledge_base"
    (kb / "语文").mkdir(parents=True)
    (kb / "语文" / "语文.md").write_text("这是文言文复习资料", encoding="utf-8")
    (kb / "语文" / "古诗.txt").write_text("古诗文言文", encoding="utf-8")
    (kb / "语文" / "古诗.txt.meta.json").write_text("{}", encoding="utf-8")
    (kb / "数学").mkdir(parents=True)
    (kb / "数学" / "函数.md").write_text("二次函数", encoding="utf-8")

    res = search_knowledge_base(
        base_dir=kb,
        q="文言文",
        category=None,
        limit=20,
        context=6,
    )

    assert res["query"] == "文言文"
    assert len(res["results"]) == 2
    filenames = {r["filename"] for r in res["results"]}
    assert "语文.md" in filenames
    assert "古诗.txt" in filenames


def test_api_search_returns_results(tmp_path: Path, monkeypatch):
    client = TestClient(main.app)
    user_id, token = _create_user_and_token(client, monkeypatch, tmp_path, "alice")

    kb_root = tmp_path / "knowledge_base"
    kb_root.mkdir(parents=True, exist_ok=True)
    main.KNOWLEDGE_BASE_DIR = kb_root
    (kb_root / f"u_{user_id}" / "语文").mkdir(parents=True)
    (kb_root / f"u_{user_id}" / "语文" / "语文.md").write_text("这是文言文复习资料", encoding="utf-8")

    r = client.get("/api/search", params={"q": "文言文"}, headers={"Authorization": "Bearer " + token})
    assert r.status_code == 200
    data = r.json()
    assert data["query"] == "文言文"
    assert data["results"][0]["filename"] == "语文.md"


def test_root_redirects_to_pages():
    client = TestClient(main.app, follow_redirects=False)
    r = client.get("/")
    assert r.status_code in [301, 302, 307, 308]
    assert r.headers.get("location") == "https://zhongkao-kb.pages.dev/"


def test_api_daily_quote_has_required_fields():
    tz = ZoneInfo("Asia/Shanghai")
    client = TestClient(main.app)

    def set_now(y, m, d, hh, mm):
        main._now_shanghai = lambda: dt.datetime(y, m, d, hh, mm, tzinfo=tz)

    set_now(2026, 5, 1, 12, 3)
    r = client.get("/api/daily_quote")
    assert r.status_code == 200
    data = r.json()
    assert set(["slot", "expires_at_ts", "text", "source", "summary"]).issubset(set(data.keys()))
    assert data["slot"] == "2026-05-01 12:00"
    assert data["expires_at_ts"] == int(dt.datetime(2026, 5, 1, 12, 10, tzinfo=tz).timestamp())

    set_now(2026, 5, 1, 12, 9)
    r2 = client.get("/api/daily_quote")
    data2 = r2.json()
    assert data2["slot"] == "2026-05-01 12:00"
    assert data2["text"] == data["text"]
    assert data2["source"] == data["source"]

    set_now(2026, 5, 1, 12, 10)
    r3 = client.get("/api/daily_quote")
    data3 = r3.json()
    assert data3["slot"] == "2026-05-01 12:10"


def test_filters_options(tmp_path: Path, monkeypatch):
    client = TestClient(main.app)
    user_id, token = _create_user_and_token(client, monkeypatch, tmp_path, "u1")

    kb_root = tmp_path / "knowledge_base"
    kb_root.mkdir(parents=True, exist_ok=True)
    main.KNOWLEDGE_BASE_DIR = kb_root
    base = kb_root / f"u_{user_id}"
    (base / "语文").mkdir(parents=True)
    (base / "语文" / "a.md").write_text("x", encoding="utf-8")
    (base / "语文" / "a.md.meta.json").write_text('{"year":"2023","region":"北京","type":"中考真题"}', encoding="utf-8")
    (base / "数学").mkdir(parents=True)
    (base / "数学" / "b.txt").write_text("y", encoding="utf-8")

    r = client.get("/api/filters/options", headers={"Authorization": "Bearer " + token})
    assert r.status_code == 200
    data = r.json()
    assert "语文" in data["categories"]
    assert "数学" in data["categories"]
    assert "2023" in data["years"]
    assert "北京" in data["regions"]
    assert "中考真题" in data["types"]
    assert "md" in data["exts"]
    assert "txt" in data["exts"]


def test_filter_by_meta_and_ext(tmp_path: Path, monkeypatch):
    client = TestClient(main.app)
    user_id, token = _create_user_and_token(client, monkeypatch, tmp_path, "u2")

    kb_root = tmp_path / "knowledge_base"
    kb_root.mkdir(parents=True, exist_ok=True)
    main.KNOWLEDGE_BASE_DIR = kb_root
    base = kb_root / f"u_{user_id}"
    (base / "语文").mkdir(parents=True)
    (base / "语文" / "a.md").write_text("x", encoding="utf-8")
    (base / "语文" / "a.md.meta.json").write_text('{"year":"2023","region":"北京","type":"中考真题"}', encoding="utf-8")
    (base / "语文" / "b.md").write_text("y", encoding="utf-8")
    (base / "数学").mkdir(parents=True)
    (base / "数学" / "c.txt").write_text("z", encoding="utf-8")

    r = client.get("/api/filter", params={"year": "2023", "ext": "md"}, headers={"Authorization": "Bearer " + token})
    assert r.status_code == 200
    data = r.json()
    assert "语文" in data
    assert [x["name"] for x in data["语文"]] == ["a.md"]


def test_split_questions_basic():
    from main import split_questions_from_text

    text = """一、选择题
1. 下列说法正确的是（ ）
A. 选项A
B. 选项B
C. 选项C
D. 选项D

2、这是一道没有选项的题
"""

    items = split_questions_from_text(text)
    assert len(items) == 2
    assert items[0]["id"] == "1"
    assert "下列说法正确的是" in items[0]["stem"]
    assert items[0]["options"][0].startswith("A")
    assert items[1]["id"] == "2"
    assert items[1]["options"] == []


def test_api_split_creates_questions_file(tmp_path: Path, monkeypatch):
    client = TestClient(main.app)
    user_id, token = _create_user_and_token(client, monkeypatch, tmp_path, "u3")

    kb_root = tmp_path / "knowledge_base"
    kb_root.mkdir(parents=True, exist_ok=True)
    main.KNOWLEDGE_BASE_DIR = kb_root
    base = kb_root / f"u_{user_id}"
    (base / "语文").mkdir(parents=True)
    (base / "语文" / "试卷.md").write_text(
        """1. 题目
A. a
B. b
C. c
D. d
""",
        encoding="utf-8",
    )
    r = client.post("/api/split", json={"category": "语文", "filename": "试卷.md"}, headers={"Authorization": "Bearer " + token})
    assert r.status_code == 200
    data = r.json()
    assert data["status"] == "success"
    assert data["count"] == 1

    out = base / "语文" / "试卷.questions.json"
    assert out.exists()

    r2 = client.get("/api/questions/语文/试卷.questions.json", headers={"Authorization": "Bearer " + token})
    assert r2.status_code == 200
    data2 = r2.json()
    assert data2["items"][0]["id"] == "1"
