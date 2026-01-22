# AvaLong

AvaLong is a web application that implements the social deduction game The Resistance: Avalon for asynchronous or real-time play.
It’s designed so you and your friends can play over multiple days, each player taking turns at their own pace. It can also be used for normal-paced games.

## Overview

AvaLong faithfully reproduces the logic and rules of Avalon in a web-based format. Players can create or join games directly from the browser, and the system manages all state transitions: proposals, voting, missions, and the final assassination phase.

The interface is minimal but fully functional. It runs live on an OpenBSD VPS, but can easily be deployed elsewhere.

Key Features

* Fully functional Avalon ruleset

* Asynchronous gameplay

* Persistent, multi-game concurrent, management

* uWSGI app with Flask front-end

## Setup
1. Clone and Install
git clone https://github.com/mathslug/avalom.git
cd avalom
pip install -r requirements.txt
(a virtual environment is recommended.)

2. Run (within Tmux for persistance)
`uwsgi --ini fcgi_conf_alt.ini`

## Live Instance

[https://avalong.mathslug.com/avalom/](https://avalong.mathslug.com/avalom/)

## Future Directions

Improved front-end design and UX.

Persistent game storage (database instead of memory).

Integration of LLM players to fill out games or analyze player behavior.

Enhanced logging and visualization of player actions.

## License

MIT License
