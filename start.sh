#!/bin/sh
echo "Starting server on port 8000"
uvicorn main:app --host 0.0.0.0 --port 8000


