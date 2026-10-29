import os

import httpx
import streamlit as st
from supabase import ClientOptions, create_client


def _get_secret(*keys):
    try:
        secrets = st.secrets
    except (AttributeError, TypeError):
        return None

    for key in keys:
        try:
            value = secrets.get(key)
        except (AttributeError, TypeError):
            value = None
        if value:
            return value
    return None


SUPABASE_URL = (
    os.getenv("SUPABASE_URL")
    or os.getenv("supabase_URL")
    or _get_secret("supabase_URL", "SUPABASE_URL", "supabase_url")
)
SUPABASE_KEY = (
    os.getenv("SUPABASE_KEY")
    or os.getenv("Supabase_Key")
    or _get_secret("Supabase_Key", "SUPABASE_KEY")
)

http_client = httpx.Client(
    timeout=httpx.Timeout(30.0, connect=10.0),
    transport=httpx.HTTPTransport(retries=2),
)

supabase = None
if SUPABASE_URL and SUPABASE_KEY:
    try:
        supabase = create_client(
            SUPABASE_URL,
            SUPABASE_KEY,
            options=ClientOptions(httpx_client=http_client),
        )
    except (TypeError, ValueError, RuntimeError, OSError):
        supabase = None

supabase_available = supabase is not None
