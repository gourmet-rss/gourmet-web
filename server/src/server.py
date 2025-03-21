from time import sleep
from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
from typing import Dict, Any
from fastapi.responses import HTMLResponse
from src import service, visualize, validators, auth, database
import sys
import json
from contextlib import asynccontextmanager
import sentry_sdk

args = sys.argv[1:]
is_prod = [x for x in args if x == "--prod"]
is_prod = bool(len(is_prod))

if is_prod:
  sentry_sdk.init(
    dsn="https://7c941a3688a4f8ebfecdf03d2df57a65@o4509004885196800.ingest.de.sentry.io/4509006216560720",
    # Add data like request headers and IP for users,
    # see https://docs.sentry.io/platforms/python/data-management/data-collected/ for more info
    send_default_pii=True,
  )


@asynccontextmanager
async def lifespan(app: FastAPI):
  # Startup: setup resources
  await startup_db_client()
  yield
  # Shutdown: clean up resources
  await shutdown_db_client()


# Create FastAPI app instance with lifespan
app = FastAPI(title="Gourmet API", description="API for Gourmet content recommendation system", lifespan=lifespan)


# Add CORS middleware
app.add_middleware(
  CORSMiddleware,
  allow_origins=["*"],  # TODO: In production, replace with specific origins
  allow_credentials=True,
  allow_methods=["*"],
  allow_headers=["*"],
)


@app.get("/onboarding")
async def get_onboarding(request: Request, selected_content: str = "", unselected_content: str = "") -> Dict[str, list]:
  await auth.authenticate(request)
  existing_selected_ids = [int(x) for x in selected_content.split(",")] if selected_content else []
  existing_unselected_ids = [int(x) for x in unselected_content.split(",")] if unselected_content else []
  sample_content = await service.get_onboarding_content(existing_selected_ids, existing_unselected_ids)
  return {"content": [validators.ContentItem(**x) for x in sample_content]}


@app.post("/onboarding")
async def onboard(request: Request, data: Dict[str, Any]) -> Dict[str, str]:
  selected_content = data.get("selected_content", [])
  if len(selected_content) == 0:
    raise HTTPException(status_code=400, detail="At least 3 content items must be selected")
  user = await auth.authenticate(request)
  await service.onboard(user.id, selected_content)
  return {"status": "success"}


@app.get("/feed")
async def get_feed(request: Request, recommendation_ids: str = "") -> Dict[str, list]:
  user = await auth.authenticate(request)
  if user.embedding is None:
    raise HTTPException(status_code=409, detail="User has not completed onboarding")
  content = await service.get_recommendations(
    user.id, [int(x) for x in recommendation_ids.split(",")] if recommendation_ids else None
  )

  # Parse content items and ensure media is properly formatted
  validated_content = []
  for content_item in content:
    content_item_dict = dict(content_item)

    if "media" in content_item_dict:
      try:
        content_item_dict["media"] = json.loads(content_item_dict["media"])
      except json.JSONDecodeError:
        content_item_dict["media"] = []

    validated_content.append(validators.UserContentItem(**content_item_dict))

  return {"content": validated_content}


@app.get("/health")
async def health_check() -> Dict[str, str]:
  """
  Health check endpoint to verify server is running.
  """
  return {"status": "healthy"}


@app.get("/visualization", response_class=HTMLResponse)
async def get_visualization(request: Request) -> str:
  user = await auth.authenticate(request)
  # Get user embedding history if available
  user_embeddings = [user.embedding]
  # Get HTML for visualization
  html_content = await visualize.get_visualization_html(user_embeddings)
  return html_content


@app.post("/feedback")
async def feedback(request: Request, data: validators.Feedback) -> Dict[str, str]:
  user = await auth.authenticate(request)
  await service.handle_feedback(user.id, data.content_id, data.rating)
  return {"status": "success"}


async def startup_db_client():
  db = await database.get_db()
  try:
    await db.execute("SELECT 1")
    print("Database connection established")
  except Exception as e:
    print(f"Database connection failed: {e}")
    raise e


async def shutdown_db_client():
  await database.close_db()


def start_server(host: str = "0.0.0.0", port: int = 8000, debug: bool = False):
  """
  Start the FastAPI server with uvicorn.

  Args:
      host: Host address to bind the server to
      port: Port to run the server on
      debug: Whether to run in debug mode
  """
  uvicorn.run("src.server:app", host=host, port=port, reload=debug)


if __name__ == "__main__":
  # Start the server when this file is run directly
  if is_prod:
    start_server(debug=False)
  else:
    start_server(debug=True)
