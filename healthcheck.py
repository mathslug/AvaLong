#!/usr/bin/env python3
"""Container health check: exits 0 if the app answers, 1 otherwise."""

import sys
import urllib.request

try:
    with urllib.request.urlopen("http://127.0.0.1:8001/healthz", timeout=5) as r:
        sys.exit(0 if r.status == 200 else 1)
except Exception:
    sys.exit(1)
