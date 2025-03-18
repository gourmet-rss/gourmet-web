# Gourmet

The rss feeder that only give you the best content you want.

## Features

- [ ]
- [ ]
- [ ]

## Local dev

Start the database with `docker compose -f docker-compose.yml -f docker-compose.dev.yml up -d`

Add a `.env` file to the root directory (see `.env.example` for required variables)

### With `uv`

cd into the `/server` directory and run `uv venv` to create a virtual environment

Run `uv sync` to install the dependencies

Run `uv run -m src/database.py` to migrate the database

Run `uv run -m src.pipeline` to insert a piece of sample content

Run `uv run -m src.handler` to run the user request cycle as a CLI tool

### Frontend client

cd into the `/client` directory and run `npm run dev` (make sure to run `npm install` first if you haven't already.)

Open [http://localhost:3000](http://localhost:3000) with your browser to see the result.

### Building for production

#### Server

Run `docker buildx build --platform linux/amd64 -t cameronnimmo/gourmet-server ./server` to build the docker image

Run `docker push cameronnimmo/gourmet-server` to push the image to the registry (or run the build command with `--push`)

#### Client

Run `docker buildx build --platform linux/amd64 -t cameronnimmo/gourmet-client ./client --build-arg NEXT_PUBLIC_CLERK_PUBLISHABLE_KEY=$(grep NEXT_PUBLIC_CLERK_PUBLISHABLE_KEY .env | cut -d '=' -f2)` to build the docker image (pulling the clerk publishable key from the .env file in the root directory)

Run `docker push cameronnimmo/gourmet-client` to push the image to the registry (or run the build command with `--push`)

### Running in production

Run `CLERK_SECRET_KEY=your-secret-key docker compose -f docker-compose.yml -f docker-compose.prod.yml up -d`

This will launch postgres, the server, and the client

### Testing production images

To test the production setup in your local environment, with the CLERK_SECRET_KEY variable injected from the .env file, and the postgres database exposed on port 5433, run:

```
export $(grep -v '^#' .env | xargs) && docker compose -f docker-compose.yml -f docker-compose.prod.yml -f docker-compose.dev.yml up -d
```

### Deploying with Ansible

First make sure you have built the latest images for the server and client, and pushed them to the registry (see above).

Create an `inventory.ini` file with the following content:

```
[production]
<your-production-server-ip>
```

Ensure your .env file includes the following variables:

- `DOCKER_HUB_USERNAME`
- `DOCKER_HUB_PASSWORD`
- `CLERK_SECRET_KEY`

Run the playbook:

```
export $(grep -v '^#' .env | xargs) && ansible-playbook -i inventory.ini playbook.yml
```
