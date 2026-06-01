#!/bin/bash
pkill -f "python.*transit_screen" || true
uv run python -m transit_screen.main
