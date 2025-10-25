# HackOHIO_2025

#Authors: Trevor Clute, Shaun Xie

python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8000
