import os
import psycopg2
import psycopg2.extras
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

SCHEMA_PATH = (Path(__file__).parent / "schema.sql").resolve()

import streamlit as st

@st.cache_resource
def get_cached_connection():
    """One connection per Streamlit session, reused across reruns.
    Streamlit handles cleanup automatically when the session ends."""
    database_url = os.getenv("DATABASE_URL")
    if not database_url:
        raise RuntimeError("DATABASE_URL not found.")
    conn = psycopg2.connect(database_url, cursor_factory=psycopg2.extras.RealDictCursor)
    conn.autocommit = False
    return conn
def get_connection():
    """Returns a fresh Postgres connection. Caller is responsible for closing it."""
    database_url = os.getenv("DATABASE_URL")
    if not database_url:
        raise RuntimeError(
            "DATABASE_URL not found. Make sure it's set in your .env file "
            "or Streamlit secrets."
        )
    try:
        return psycopg2.connect(database_url, cursor_factory=psycopg2.extras.RealDictCursor)
    except psycopg2.Error as e:
        raise RuntimeError(f"Failed to connect to database: {e}") from e


def release_connection(conn):
    """No-op now — connection is cached and reused via st.cache_resource,
    not closed after each use."""
    pass


def init_db():
    conn = get_connection()
    try:
        with open(SCHEMA_PATH, "r") as f:
            with conn.cursor() as cur:
                cur.execute(f.read())
        conn.commit()
    finally:
        release_connection(conn)


def ensure_user(user_id: str):
    conn = get_connection()
    try:
        with conn.cursor() as cur:
            cur.execute(
                "INSERT INTO users (id) VALUES (%s) ON CONFLICT (id) DO NOTHING",
                (user_id,),
            )
        conn.commit()
    finally:
        release_connection(conn)