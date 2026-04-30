import os
import secrets
import sqlite3
import time
import hashlib
from contextlib import contextmanager
from dataclasses import dataclass
from pathlib import Path
from typing import Optional

from fastapi import HTTPException, Header

try:
    import psycopg2
    import psycopg2.pool
    import psycopg2.extras
except Exception:
    psycopg2 = None


@dataclass(frozen=True)
class User:
    id: int
    username: str


_PG_POOL = None


def database_url() -> str:
    return (os.getenv("DATABASE_URL") or "").strip()


def db_backend() -> str:
    return "postgres" if database_url() else "sqlite"


def db_path() -> Path:
    p = (os.getenv("APP_DB_PATH") or "").strip()
    return Path(p) if p else Path(__file__).parent / "app.db"


def _sqlite_conn():
    p = db_path()
    p.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(str(p))
    conn.row_factory = sqlite3.Row
    return conn


def _pg_pool():
    global _PG_POOL
    if _PG_POOL is not None:
        return _PG_POOL
    url = database_url()
    if not url:
        raise RuntimeError("DATABASE_URL is not set")
    if psycopg2 is None:
        raise RuntimeError("psycopg2 is not available")
    kwargs = {}
    if "sslmode=" not in url:
        kwargs["sslmode"] = "require"
    _PG_POOL = psycopg2.pool.SimpleConnectionPool(1, 8, dsn=url, **kwargs)
    return _PG_POOL


@contextmanager
def _pg_conn():
    pool = _pg_pool()
    conn = pool.getconn()
    conn.autocommit = True
    try:
        yield conn
    finally:
        pool.putconn(conn)


@contextmanager
def _pg_cursor(dict_rows: bool = True):
    with _pg_conn() as conn:
        cur = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor if dict_rows else None)
        try:
            yield cur
        finally:
            cur.close()


def init_db():
    if db_backend() == "postgres":
        with _pg_cursor(False) as cur:
            cur.execute(
                """
                CREATE TABLE IF NOT EXISTS users (
                  id BIGSERIAL PRIMARY KEY,
                  username TEXT UNIQUE NOT NULL,
                  password_salt TEXT NOT NULL,
                  password_hash TEXT NOT NULL,
                  nickname TEXT,
                  avatar_filename TEXT,
                  created_at BIGINT NOT NULL
                )
                """
            )
            cur.execute(
                """
                CREATE TABLE IF NOT EXISTS sessions (
                  token TEXT PRIMARY KEY,
                  user_id BIGINT NOT NULL REFERENCES users(id),
                  created_at BIGINT NOT NULL,
                  expires_at BIGINT NOT NULL
                )
                """
            )
            cur.execute("CREATE INDEX IF NOT EXISTS sessions_user_id_idx ON sessions(user_id)")
        return

    conn = _sqlite_conn()
    try:
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS users (
              id INTEGER PRIMARY KEY AUTOINCREMENT,
              username TEXT NOT NULL UNIQUE,
              password_salt TEXT NOT NULL,
              password_hash TEXT NOT NULL,
              created_at INTEGER NOT NULL
            )
            """
        )
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS sessions (
              token TEXT PRIMARY KEY,
              user_id INTEGER NOT NULL,
              created_at INTEGER NOT NULL,
              expires_at INTEGER NOT NULL,
              FOREIGN KEY(user_id) REFERENCES users(id)
            )
            """
        )
        cols = {r["name"] for r in conn.execute("PRAGMA table_info(users)").fetchall()}
        if "nickname" not in cols:
            conn.execute("ALTER TABLE users ADD COLUMN nickname TEXT")
        if "avatar_filename" not in cols:
            conn.execute("ALTER TABLE users ADD COLUMN avatar_filename TEXT")
        conn.commit()
    finally:
        conn.close()


def _pbkdf2(password: str, salt: str, rounds: int = 200_000) -> str:
    dk = hashlib.pbkdf2_hmac("sha256", password.encode("utf-8"), salt.encode("utf-8"), rounds)
    return dk.hex()


def _pg_unique_conflict(e: Exception) -> bool:
    pgcode = getattr(e, "pgcode", None)
    return pgcode == "23505"


def update_password_by_user_id(user_id: int, new_password: str):
    init_db()
    salt = secrets.token_hex(16)
    pw_hash = _pbkdf2(new_password, salt)

    if db_backend() == "postgres":
        with _pg_cursor(False) as cur:
            cur.execute(
                "UPDATE users SET password_salt=%s, password_hash=%s WHERE id=%s",
                (salt, pw_hash, user_id),
            )
        return

    conn = _sqlite_conn()
    try:
        conn.execute(
            "UPDATE users SET password_salt=?, password_hash=? WHERE id=?",
            (salt, pw_hash, user_id),
        )
        conn.commit()
    finally:
        conn.close()


def delete_sessions_by_user_id(user_id: int):
    init_db()
    if db_backend() == "postgres":
        with _pg_cursor(False) as cur:
            cur.execute("DELETE FROM sessions WHERE user_id=%s", (user_id,))
        return
    conn = _sqlite_conn()
    try:
        conn.execute("DELETE FROM sessions WHERE user_id=?", (user_id,))
        conn.commit()
    finally:
        conn.close()


def get_user_by_username(username: str) -> Optional[User]:
    init_db()
    if db_backend() == "postgres":
        with _pg_cursor(True) as cur:
            cur.execute("SELECT id, username FROM users WHERE username=%s", (username,))
            row = cur.fetchone()
            if not row:
                return None
            return User(id=int(row["id"]), username=row["username"])
    conn = _sqlite_conn()
    try:
        row = conn.execute("SELECT id, username FROM users WHERE username=?", (username,)).fetchone()
        if not row:
            return None
        return User(id=int(row["id"]), username=row["username"])
    finally:
        conn.close()


def create_user(username: str, password: str) -> User:
    init_db()
    salt = secrets.token_hex(16)
    pw_hash = _pbkdf2(password, salt)
    now = int(time.time())

    if db_backend() == "postgres":
        try:
            with _pg_cursor(True) as cur:
                cur.execute(
                    "INSERT INTO users(username,password_salt,password_hash,created_at) VALUES (%s,%s,%s,%s) RETURNING id",
                    (username, salt, pw_hash, now),
                )
                row = cur.fetchone()
                return User(id=int(row["id"]), username=username)
        except Exception as e:
            if _pg_unique_conflict(e):
                raise HTTPException(status_code=409, detail="用户名已存在")
            raise

    conn = _sqlite_conn()
    try:
        cur = conn.execute(
            "INSERT INTO users(username,password_salt,password_hash,created_at) VALUES (?,?,?,?)",
            (username, salt, pw_hash, now),
        )
        conn.commit()
        return User(id=int(cur.lastrowid), username=username)
    except sqlite3.IntegrityError:
        raise HTTPException(status_code=409, detail="用户名已存在")
    finally:
        conn.close()


def verify_user(username: str, password: str) -> Optional[User]:
    init_db()
    if db_backend() == "postgres":
        with _pg_cursor(True) as cur:
            cur.execute(
                "SELECT id, username, password_salt, password_hash FROM users WHERE username=%s",
                (username,),
            )
            row = cur.fetchone()
            if not row:
                return None
            expected = row["password_hash"]
            got = _pbkdf2(password, row["password_salt"])
            if secrets.compare_digest(expected, got):
                return User(id=int(row["id"]), username=row["username"])
            return None

    conn = _sqlite_conn()
    try:
        row = conn.execute(
            "SELECT id, username, password_salt, password_hash FROM users WHERE username=?",
            (username,),
        ).fetchone()
        if not row:
            return None
        expected = row["password_hash"]
        got = _pbkdf2(password, row["password_salt"])
        if secrets.compare_digest(expected, got):
            return User(id=int(row["id"]), username=row["username"])
        return None
    finally:
        conn.close()


def create_session(user_id: int, ttl_seconds: int = 7 * 24 * 3600) -> str:
    init_db()
    token = secrets.token_urlsafe(32)
    now = int(time.time())
    exp = now + ttl_seconds

    if db_backend() == "postgres":
        with _pg_cursor(False) as cur:
            cur.execute(
                "INSERT INTO sessions(token,user_id,created_at,expires_at) VALUES (%s,%s,%s,%s)",
                (token, user_id, now, exp),
            )
        return token

    conn = _sqlite_conn()
    try:
        conn.execute(
            "INSERT INTO sessions(token,user_id,created_at,expires_at) VALUES (?,?,?,?)",
            (token, user_id, now, exp),
        )
        conn.commit()
        return token
    finally:
        conn.close()


def delete_session(token: str):
    init_db()
    if db_backend() == "postgres":
        with _pg_cursor(False) as cur:
            cur.execute("DELETE FROM sessions WHERE token=%s", (token,))
        return
    conn = _sqlite_conn()
    try:
        conn.execute("DELETE FROM sessions WHERE token=?", (token,))
        conn.commit()
    finally:
        conn.close()


def get_user_by_token(token: str) -> Optional[User]:
    init_db()
    now = int(time.time())

    if db_backend() == "postgres":
        with _pg_cursor(True) as cur:
            cur.execute(
                """
                SELECT u.id as id, u.username as username, s.expires_at as expires_at
                FROM sessions s JOIN users u ON s.user_id = u.id
                WHERE s.token=%s
                """,
                (token,),
            )
            row = cur.fetchone()
            if not row:
                return None
            if int(row["expires_at"]) < now:
                with _pg_cursor(False) as cur2:
                    cur2.execute("DELETE FROM sessions WHERE token=%s", (token,))
                return None
            return User(id=int(row["id"]), username=row["username"])

    conn = _sqlite_conn()
    try:
        row = conn.execute(
            """
            SELECT u.id as id, u.username as username, s.expires_at as expires_at
            FROM sessions s JOIN users u ON s.user_id = u.id
            WHERE s.token=?
            """,
            (token,),
        ).fetchone()
        if not row:
            return None
        if int(row["expires_at"]) < now:
            conn.execute("DELETE FROM sessions WHERE token=?", (token,))
            conn.commit()
            return None
        return User(id=int(row["id"]), username=row["username"])
    finally:
        conn.close()


def get_profile(user_id: int) -> dict:
    init_db()
    if db_backend() == "postgres":
        with _pg_cursor(True) as cur:
            cur.execute("SELECT nickname, avatar_filename FROM users WHERE id=%s", (user_id,))
            row = cur.fetchone()
            if not row:
                return {"nickname": "", "avatar_filename": ""}
            return {"nickname": row.get("nickname") or "", "avatar_filename": row.get("avatar_filename") or ""}
    conn = _sqlite_conn()
    try:
        row = conn.execute(
            "SELECT nickname, avatar_filename FROM users WHERE id=?",
            (user_id,),
        ).fetchone()
        if not row:
            return {"nickname": "", "avatar_filename": ""}
        nickname = row["nickname"] or ""
        avatar_filename = row["avatar_filename"] or ""
        return {"nickname": nickname, "avatar_filename": avatar_filename}
    finally:
        conn.close()


def set_nickname(user_id: int, nickname: str) -> str:
    init_db()
    if db_backend() == "postgres":
        with _pg_cursor(False) as cur:
            cur.execute("UPDATE users SET nickname=%s WHERE id=%s", (nickname, user_id))
        return nickname
    conn = _sqlite_conn()
    try:
        conn.execute("UPDATE users SET nickname=? WHERE id=?", (nickname, user_id))
        conn.commit()
        return nickname
    finally:
        conn.close()


def set_avatar_filename(user_id: int, avatar_filename: str) -> str:
    init_db()
    if db_backend() == "postgres":
        with _pg_cursor(False) as cur:
            cur.execute("UPDATE users SET avatar_filename=%s WHERE id=%s", (avatar_filename, user_id))
        return avatar_filename
    conn = _sqlite_conn()
    try:
        conn.execute("UPDATE users SET avatar_filename=? WHERE id=?", (avatar_filename, user_id))
        conn.commit()
        return avatar_filename
    finally:
        conn.close()


def get_users_count() -> int:
    init_db()
    if db_backend() == "postgres":
        with _pg_cursor(True) as cur:
            cur.execute("SELECT COUNT(*) as c FROM users")
            row = cur.fetchone()
            return int(row["c"]) if row else 0
    conn = _sqlite_conn()
    try:
        row = conn.execute("SELECT COUNT(*) as c FROM users").fetchone()
        return int(row["c"]) if row else 0
    finally:
        conn.close()


def parse_bearer(authorization: Optional[str]) -> Optional[str]:
    if not authorization:
        return None
    parts = authorization.split(" ", 1)
    if len(parts) != 2:
        return None
    if parts[0].lower() != "bearer":
        return None
    return parts[1].strip() or None


def get_current_user(authorization: Optional[str] = Header(None)) -> User:
    token = parse_bearer(authorization)
    if not token:
        raise HTTPException(status_code=401, detail="未登录")
    user = get_user_by_token(token)
    if not user:
        raise HTTPException(status_code=401, detail="登录已过期")
    return user
