# AvaLong

AvaLong is a web application that implements the social deduction game The Resistance: Avalon for asynchronous or real-time play.
It’s designed so you and your friends can play over multiple days, each player taking turns at their own pace. It can also be used for normal-paced games.

## Overview

AvaLong faithfully reproduces the logic and rules of Avalon in a web-based format. Players can create or join games directly from the browser, and the system manages all state transitions: proposals, voting, missions, and the final assassination phase.

The interface is minimal but fully functional. It runs as a rootless Podman container on a home Raspberry Pi server, reached through a Cloudflare Tunnel — no ports are open on the host, and TLS terminates at Cloudflare's edge, not on the Pi.

Key Features

* Fully functional Avalon ruleset

* Asynchronous gameplay

* Persistent, multi-game concurrent, management

* gunicorn app with Flask front-end

## Setup

This project uses [uv](https://github.com/astral-sh/uv) for Python package management and is pinned to Python 3.12.

1. Clone and Install
```bash
git clone https://github.com/mathslug/AvaLong.git
cd AvaLong
uv venv
source .venv/bin/activate
uv pip install -r requirements.txt
```

2. Run
For development:
```bash
python app.py
```

For production, this repo is built as a container image (`Containerfile`) and run under Podman + systemd Quadlet (`deploy/avalong.container`), driven by `deploy-app.sh` in [mathslug/server_setup](https://github.com/mathslug/server_setup). There is no manual production start step: pushing to `main` is picked up and redeployed automatically within about 15 minutes. `healthcheck.py` backs the container's health check.

## Live Instance

[https://avalong.mathslug.com/avalom/](https://avalong.mathslug.com/avalom/)

## Future Directions

Improved front-end design and UX.

Persistent game storage (database instead of memory).

Integration of LLM players to fill out games or analyze player behavior.

Enhanced logging and visualization of player actions.

## License

MIT License
