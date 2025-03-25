# Gourmet

The rss feeder that only give you the best content you want.

## Features

- [ ]
- [ ]
- [ ]

## Local development

### Initial setup

1. Start the database with `docker compose -f docker-compose.yml -f docker-compose.dev.yml up -d`

2. Add a `.env` file to the root directory (see `.env.example` for required variables)

3. cd into the `/server` directory

4. Run `uv sync` to install the dependencies (make sure you have [uv](https://github.com/astral-sh/uv) installed)

5. Run `uv run -m alembic upgrade head` to apply database migrations

6. Run `uv run -m src.database` to seed the database with sample feeds

7. Run `uv run -m src.ingest` to run the ingestion pipeline to ingest some content from the sample feeds

### Running the server

cd into the `/server` directory and run `uv run --env-file=../.env -m src.server` to launch the server

### Frontend client

cd into the `/client` directory and run `npm run dev` (make sure to run `npm install` first if you haven't already.)

Open [http://localhost:3000](http://localhost:3000) with your browser to see the result.

### Making changes to the schema

Follow these steps when making changes to the database schema:

1. Make changes to the database schema in `server/src/database.py`
2. Run `uv run -m alembic revision --autogenerate -m "description"` to generate a new migration based on your changes, replacing `description` with a description of the changes.
3. Run `uv run -m alembic upgrade head` to apply the migration.
4. If you need to revert the migration, run `uv run -m alembic downgrade -1`. Then delete the migration file manually.

## Deployment

### Building for production

The following commands should not be run locally directly, they are handled by the ci/cd actions workflow (see below).

#### Server

Run `docker buildx build --platform linux/amd64 -t ghcr.io/gourmet-rss/gourmet-server ./server` to build the docker image

Run `docker push ghcr.io/gourmet-rss/gourmet-server` to push the image to the registry (or run the build command with `--push`)

#### Client

Run `docker buildx build --platform linux/amd64 -t ghcr.io/gourmet-rss/gourmet-client ./client --build-arg NEXT_PUBLIC_CLERK_PUBLISHABLE_KEY=$(grep NEXT_PUBLIC_CLERK_PUBLISHABLE_KEY .env | cut -d '=' -f2)` to build the docker image (pulling the clerk publishable key from the .env file in the root directory)

Run `docker push ghcr.io/gourmet-rss/gourmet-client` to push the image to the registry (or run the build command with `--push`)

### Running in production

Run `CLERK_SECRET_KEY=your-secret-key POSTGRES_PASSWORD=your-password docker compose -f docker-compose.yml -f docker-compose.prod.yml up -d`

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

- `GITHUB_TOKEN`
- `CLERK_SECRET_KEY`
- `POSTGRES_PASSWORD`

Run the playbook:

```
export $(grep -v '^#' .env | xargs) && ansible-playbook -i inventory.ini playbook.yml
```

### CI/CD with GitHub Actions

This project uses GitHub Actions for continuous integration and deployment in a single workflow:

#### Development Workflow (develop branch)

When code is pushed to the `develop` branch, GitHub Actions will:

1. Build the Docker images for both the server and client
2. Push these images to Docker Hub with both the `latest` tag and a tag matching the commit SHA

#### Production Deployment (main branch)

When code is pushed to the `main` branch, GitHub Actions will:

1. Build and push Docker images (same as develop branch)
2. Deploy the application using the Ansible playbook

This workflow is defined in `.github/workflows/ci-cd.yml`.

#### Required Secrets

The following secrets must be configured in your GitHub repository:

- `GITHUB_TOKEN`: Automatically provided by GitHub Actions
- `NEXT_PUBLIC_CLERK_PUBLISHABLE_KEY`: Your Clerk publishable key
- `CLERK_SECRET_KEY`: Your Clerk secret key
- `SSH_PRIVATE_KEY`: SSH private key for accessing your server
- `SERVER_HOST`: Hostname or IP address of your production server
- `POSTGRES_PASSWORD`: Your PostgreSQL password

## Connecting to the database

### Locally

Host: 127.0.0.1
Port: 5433
User: postgres
Password: password

### Production

For production, the database is not exposed directly over the network, but can be accessed via ssh tunnel:

SSH Host: <your-production-server-ip>
SSH User: <your-ssh-user>
Host: localhost
Port: 9876
User: postgres
Password: $POSTGRES_PASSWORD (as set in the .env)
