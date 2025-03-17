import os
from fastapi import HTTPException
import httpx
from clerk_backend_api import Clerk
from clerk_backend_api.jwks_helpers import AuthenticateRequestOptions
from src import database


async def authenticate(request: httpx.Request):
  sdk = Clerk(bearer_auth=os.getenv("CLERK_SECRET_KEY"))
  request_state = sdk.authenticate_request(request, AuthenticateRequestOptions())
  sub = request_state.payload["sub"]
  user_id = sub.split("_")[1]
  if not user_id:
    raise HTTPException(status_code=401, detail="Unauthorized")
  db = await database.get_db()
  user = await db.fetch_one(database.users.select().where(database.users.c.id == user_id))
  if not user:
    await db.execute(database.users.insert(), {"id": user_id})
    user = await db.fetch_one(database.users.select().where(database.users.c.id == user_id))
  return user
