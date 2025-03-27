#!/bin/bash
gunicorn --timeout 6000 --workers 3 --bind "0.0.0.0:$PORT" app:app
