from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict, Optional
import json
import os
import urllib.request


DEFAULT_ANKI_CONNECT_URL = os.environ.get("ANKI_CONNECT_URL", "http://localhost:8765")


@dataclass
class AnkiResponse:
    result: Any
    error: Optional[str]


def _post_json(url: str, payload: Dict[str, Any]) -> Dict[str, Any]:
    data = json.dumps(payload).encode("utf-8")
    request = urllib.request.Request(
        url=url,
        data=data,
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    with urllib.request.urlopen(request) as response:
        response_text = response.read().decode("utf-8")
        return json.loads(response_text)


def invoke(action: str, params: Optional[Dict[str, Any]] = None, version: int = 6, url: str = DEFAULT_ANKI_CONNECT_URL) -> AnkiResponse:
    payload: Dict[str, Any] = {"action": action, "version": version}
    if params is not None:
        payload["params"] = params
    raw = _post_json(url, payload)
    return AnkiResponse(result=raw.get("result"), error=raw.get("error"))


def ensure_deck(deck_name: str, url: str = DEFAULT_ANKI_CONNECT_URL) -> None:
    resp = invoke("deckNames", url=url)
    if resp.error:
        raise RuntimeError(f"deckNames failed: {resp.error}")
    deck_names = set(resp.result or [])
    if deck_name not in deck_names:
        created = invoke("createDeck", {"deck": deck_name}, url=url)
        if created.error:
            raise RuntimeError(f"createDeck failed: {created.error}")


def add_notes(notes: list[dict[str, Any]], url: str = DEFAULT_ANKI_CONNECT_URL) -> list[int]:
    resp = invoke("addNotes", {"notes": notes}, url=url)
    if resp.error:
        raise RuntimeError(f"addNotes failed: {resp.error}")
    return resp.result
