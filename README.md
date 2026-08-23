# RestAPI-Python

A small Python script that pulls 500 comments from the public JSONPlaceholder REST API, respects a 300-requests-per-5-minutes rate limit, and writes them into a local SQLite table.

![Python](https://img.shields.io/badge/python-3.8%2B-blue) ![License](https://img.shields.io/badge/license-MIT-green)

## Why

I wrote this in November 2019 as a take-home "full stack developer test". The brief was: consume a REST API, stay inside a rate limit, persist the data in a database, and ship something a reviewer can run. It was my first time using `ratelimit` and `backoff` together, and the first repo where I tried to keep everything PEP 8.

It is still a decent minimal example of the pattern "HTTP JSON in, SQLite out, with a rate limiter and a retry decorator", which is the skeleton of most small data-collection scripts.

## Quickstart

```bash
git clone https://github.com/joelstephen97/RestAPI-Python.git
cd RestAPI-Python
python -m venv .venv && source .venv/bin/activate   # Windows: .venv\Scripts\activate
pip install -r requirements.txt
python main.py fetch
# 500 data fields have been entered into table from the ReST API.
python main.py show -n 3
```

Or with Docker:

```bash
docker build -t restapi-python .
docker run --rm -v "$PWD/data:/app/data" restapi-python fetch
docker run --rm -v "$PWD/data:/app/data" restapi-python count
```

## Usage

```
python main.py            interactive menu (the original 2019 behaviour)
python main.py fetch      download comments and insert them (fails if the table already has rows)
python main.py reset      drop and recreate the table
python main.py show -n 5  print the first 5 rows
python main.py count      number of stored rows
```

The database file defaults to `database.db` in the working directory; set `DB_PATH` to change it. This script has no HTTP server of its own: it is a client of `https://jsonplaceholder.typicode.com/comments`, not an API.

## How it works

- `call_api()` is wrapped in `@limits(calls=300, period=300)` from `ratelimit`, plus `@sleep_and_retry` and a `backoff` exponential retry on `RateLimitException`, so a loop calling it can never exceed the limit.
- The JSON (postId, id, name, email, body) goes into `data_table` with `executemany` and parameterised `?` placeholders; `id` is the primary key so a second `fetch` without `reset` raises an `IntegrityError` instead of duplicating rows.
- Everything lives in `main.py`; `argparse` subcommands were added in 2026 on top of the original interactive menu.

## Status and limitations

- Verified August 2026 on Python 3.12 with the pinned requirements: `fetch` inserts 500 rows, `count`, `show`, `reset` and the menu all work.
- The committed virtualenv and IDE files from 2019 were removed from git; clone size is now tiny.
- The Dockerfile was not rebuilt during the 2026 cleanup (no Docker on the machine I used), but it is a plain `python:3.12-alpine` image with `pip install`.
- The rate limiter is only exercised once per run; it is there to satisfy the original brief.

## License

MIT, see `LICENSE`.
