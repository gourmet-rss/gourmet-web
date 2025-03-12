# Gourmet

The rss feeder that only give you the best content you want.

## Features

- [ ]
- [ ]
- [ ]

## Local dev

Start the database with `docker compose up -d`

### With `uv`

Run `uv sync` to install the dependencies

Run `uv run -m src/database.py` to migrate the database

Run `uv run -m src.pipeline` to insert a piece of sample content

Run `uv run -m src.handler` to run the user request cycle as a CLI tool
