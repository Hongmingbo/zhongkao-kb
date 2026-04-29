import sys
from pathlib import Path

from fastapi.testclient import TestClient

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

import main
from main import search_knowledge_base


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


def test_api_search_returns_results(tmp_path: Path):
    kb = tmp_path / "knowledge_base"
    (kb / "语文").mkdir(parents=True)
    (kb / "语文" / "语文.md").write_text("这是文言文复习资料", encoding="utf-8")

    main.KNOWLEDGE_BASE_DIR = kb
    client = TestClient(main.app)

    r = client.get("/api/search", params={"q": "文言文"})
    assert r.status_code == 200
    data = r.json()
    assert data["query"] == "文言文"
    assert data["results"][0]["filename"] == "语文.md"


def test_root_redirects_to_pages():
    client = TestClient(main.app, follow_redirects=False)
    r = client.get("/")
    assert r.status_code in [301, 302, 307, 308]
    assert r.headers.get("location") == "https://zhongkao-kb.pages.dev/"
