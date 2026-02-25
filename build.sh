#!/usr/bin/env bash
# exit on error
set -o errexit

pip install --no-cache-dir -r requirements.txt
flask db upgrade
