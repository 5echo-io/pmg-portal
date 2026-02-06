#!/usr/bin/env bash
set -euo pipefail
sudo journalctl -u pmg-portal.service -f --no-pager
