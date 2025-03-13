from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
from typing import Dict, Any
from src import service, database

# Create FastAPI app instance
app = FastAPI(title="Gourmet API", description="API for Gourmet content recommendation system")

# Add CORS middleware
app.add_middleware(
  CORSMiddleware,
  allow_origins=["*"],  # In production, replace with specific origins
  allow_credentials=True,
  allow_methods=["*"],
  allow_headers=["*"],
)


@app.get("/signup")
async def root() -> Dict[str, str]:
  res = service.sign_up()
  return {"message": "Hello World from Gourmet API!"}


@app.get("/onboarding")
async def get_onboarding(existing_content: list[int] = []) -> Dict[str, list]:
  sample_content = await service.get_onboarding_content(existing_content)
  sample_content = [
    {"id": x.id, "title": x.title, "description": x.description, "source_id": x.source_id} for x in sample_content
  ]
  return {"content": sample_content}


@app.post("/onboarding")
async def onboard(data: Dict[str, Any]) -> Dict[str, str]:
  selected_content = data.get("selected_content", [])
  db = await database.get_db()
  user = await db.fetch_one(database.users.select())
  await service.onboard(user.id, selected_content)
  return {"status": "success"}


@app.get("/health")
async def health_check() -> Dict[str, str]:
  """
  Health check endpoint to verify server is running.
  """
  return {"status": "healthy"}


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
  start_server(debug=True)
