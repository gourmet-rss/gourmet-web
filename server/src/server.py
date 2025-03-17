from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
from typing import Dict, Any
from fastapi.responses import HTMLResponse
from src import service, visualize, validators, auth
import sys

# Create FastAPI app instance
app = FastAPI(title="Gourmet API", description="API for Gourmet content recommendation system")

# Add CORS middleware
app.add_middleware(
  CORSMiddleware,
  allow_origins=["*"],  # TODO: In production, replace with specific origins
  allow_credentials=True,
  allow_methods=["*"],
  allow_headers=["*"],
)


@app.get("/onboarding")
async def get_onboarding(request: Request, existing_content: str = "") -> Dict[str, list]:
  await auth.authenticate(request)
  existing_content_ids = [int(x) for x in existing_content.split(",")] if existing_content else []
  sample_content = await service.get_onboarding_content(existing_content_ids)
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
async def get_feed(request: Request) -> Dict[str, list]:
  user = await auth.authenticate(request)
  if user.embedding is None:
    raise HTTPException(status_code=409, detail="User has not completed onboarding")
  content = await service.get_recommendations(user.id)
  return {"content": [validators.UserContentItem(**x) for x in content]}


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
  args = sys.argv[1:]
  if [x for x in args if x == "--prod"]:
    start_server(debug=False)
  else:
    start_server(debug=True)
