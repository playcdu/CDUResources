"""Check committed explorer content, allowing platform-specific PNG compression."""
import base64
import hashlib
import io
import json
from pathlib import Path
import subprocess

from PIL import Image

ROOT = Path(__file__).resolve().parents[1]
MARKER = "const SCREENS="
PNG_PREFIX = "data:image/png;base64,"


def explorer_content(html):
    """Preserve the page and control data; compare images by dimensions and pixels."""
    prefix, marker, payload = html.partition(MARKER)
    if not marker:
        raise ValueError("Missing explorer screen data")
    screens, end = json.JSONDecoder().raw_decode(payload)
    if not isinstance(screens, dict) or not screens:
        raise ValueError("Explorer screen data must be a nonempty object")
    for key, screen in screens.items():
        data_url = screen["image"]
        if not data_url.startswith(PNG_PREFIX):
            raise ValueError(f"{key}: expected an embedded PNG")
        raw = base64.b64decode(data_url[len(PNG_PREFIX):], validate=True)
        with Image.open(io.BytesIO(raw)) as image:
            if image.format != "PNG" or getattr(image, "n_frames", 1) != 1:
                raise ValueError(f"{key}: expected a single-frame PNG preview")
            screen["image"] = {
                "size": list(image.size),
                "rgba_sha256": hashlib.sha256(image.convert("RGBA").tobytes()).hexdigest(),
            }
    # Keep all HTML/CSS/JS exact, and JSON values, types and display ordering.
    return prefix, payload[end:], json.dumps(screens, ensure_ascii=True)


def verify(committed, generated):
    if explorer_content(committed) != explorer_content(generated):
        raise ValueError(
            "CONTROL-EXPLORER.html is stale: rebuild and commit the refreshed browser tool"
        )


def main():
    committed = subprocess.run(
        ["git", "show", "HEAD:CONTROL-EXPLORER.html"], cwd=ROOT,
        check=True, capture_output=True,
    ).stdout.decode("utf-8")
    generated = (ROOT / "CONTROL-EXPLORER.html").read_text(encoding="utf-8")
    verify(committed, generated)
    print("Committed control explorer matches generated page, controls and artwork pixels")


if __name__ == "__main__":
    main()
