"""Root entrypoint shim for `fastapi run` / FastAPI Cloud.

The real application factory lives in :mod:`app.main`. The FastAPI CLI (and
FastAPI Cloud) auto-discovers an app by looking for a top-level ``main.py`` /
``app.py`` / ``api.py`` in the deploy root, so we re-export ``app`` here.

Run locally the same way the platform does:  ``fastapi run main.py``
"""

from app.main import app

__all__ = ["app"]
