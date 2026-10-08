# Seafi bot

> This project is currently under active development.

**seafi** is a project for convenient housing search in Kyrgyzstan. It collects new rental and real estate listings and sends them to users.

**seafi-bot** is a client part of the project. It is Telegram Bot for the project's own server.
[@seafi_arenda_bot](https://t.me/seafi_arenda_bot).

## Architecture

Telegram Bot → API → WebAgent → Real Estate Websites

## Stack

* Python
* python-telegram-bot
* pydantic
* httpx

## Running

### Local

```bash
python -m venv .venv
pip install -r requirements.txt
```
Start:

```bash
python -m src.app.main
```