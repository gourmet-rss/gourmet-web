# Gourmet

The rss feeder that only give you the best content you want.

## Features

- [ ]
- [ ]
- [ ]

## Local dev

Start the database with `docker compose up -d`

Add a `.env` file to the root directory (see `.env.example` for required variables)

### With `uv`

Run `uv sync` to install the dependencies

Run `uv run -m src/database.py` to migrate the database

Run `uv run -m src.pipeline` to insert a piece of sample content

Run `uv run -m src.handler` to run the user request cycle as a CLI tool

### Frontend client

cd into the /client directory and run `npm run dev` (make sure to run `npm install` first if you haven't already.)

Open [http://localhost:3000](http://localhost:3000) with your browser to see the result.
