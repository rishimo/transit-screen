#!/bin/bash
pkill -f "python.*transit_screen" || true
uv run transit-screen
