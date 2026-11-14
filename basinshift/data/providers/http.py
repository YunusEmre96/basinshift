"""Ortak HTTP yardımcıları: zaman aşımı, yeniden deneme, anlaşılır hata."""
from __future__ import annotations

import time

import requests

USER_AGENT = "BasinShift/1.0 (NASA Space Apps 2026; decision-support research tool)"


class FetchError(RuntimeError):
    """Uzak servisten veri alınamadı."""


def get_json(url: str, params: dict | None = None, timeout: float = 60, retries: int = 3,
             session: requests.Session | None = None, headers: dict | None = None) -> dict:
    sess = session or requests.Session()
    hdrs = {"User-Agent": USER_AGENT, **(headers or {})}
    last_err: Exception | None = None
    for attempt in range(retries):
        try:
            resp = sess.get(url, params=params, timeout=timeout, headers=hdrs)
            if resp.status_code == 429 or resp.status_code >= 500:
                raise FetchError(f"HTTP {resp.status_code}: {resp.text[:200]}")
            if resp.status_code >= 400:
                # İstemci hatası: yeniden denemek işe yaramaz
                raise FetchError(f"HTTP {resp.status_code} ({url}): {resp.text[:300]}")
            return resp.json()
        except FetchError as exc:
            last_err = exc
            if "HTTP 4" in str(exc) and "429" not in str(exc):
                raise
        except (requests.RequestException, ValueError) as exc:
            last_err = exc
        time.sleep(min(2 ** attempt, 10))
    raise FetchError(f"{url} alınamadı ({retries} deneme): {last_err}")


def get_text(url: str, params: dict | None = None, timeout: float = 60, retries: int = 3,
             session: requests.Session | None = None, headers: dict | None = None) -> str:
    sess = session or requests.Session()
    hdrs = {"User-Agent": USER_AGENT, **(headers or {})}
    last_err: Exception | None = None
    for attempt in range(retries):
        try:
            resp = sess.get(url, params=params, timeout=timeout, headers=hdrs)
            if resp.status_code >= 400:
                raise FetchError(f"HTTP {resp.status_code} ({url}): {resp.text[:300]}")
            return resp.text
        except (requests.RequestException, FetchError) as exc:
            last_err = exc
            time.sleep(min(2 ** attempt, 10))
    raise FetchError(f"{url} alınamadı ({retries} deneme): {last_err}")
