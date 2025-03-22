import os
import torch
import uuid
import numpy as np
from datetime import datetime
from src import database, util, constants
import sqlalchemy

from openai import OpenAI

client = OpenAI(base_url=os.getenv("LLM_BASE_URL"), api_key=os.getenv("LLM_API_KEY"))


#
#
#
async def get_recommendation_candidates(
  user_id: int, user_embedding: list, recommendation_ids: list[int] | None = None
):
  """
  Get a list of recommendation candidates for a user
  """

  db = await database.get_db()

  max_distance = util.cosine_to_l2_distance(constants.MIN_SEARCH_COSINE_SIMILARITY)

  # Find all content ids near the user embedding
  candidates = await db.fetch_all(
    f"""
        SELECT c.id, c.date, c.embedding <-> :user_embedding AS distance
        FROM content c
        LEFT JOIN user_content_ratings ucr ON c.id = ucr.content_id AND ucr.user_id = :user_id
        WHERE c.date >= CURRENT_DATE - INTERVAL '{constants.MAX_CONTENT_AGE} days'
        AND c.id NOT IN (SELECT UNNEST(cast(:ignored_ids as int[])))
        AND (ucr.rating IS NULL OR ucr.rating >= 0)
        AND c.embedding <-> :user_embedding < :max_distance
        ORDER BY c.embedding <-> :user_embedding
        LIMIT :limit
    """,
    {
      "user_id": user_id,
      "user_embedding": util.list_to_string(user_embedding),
      "ignored_ids": recommendation_ids,
      "max_distance": max_distance,
      "limit": 100,
    },
  )

  if not candidates:
    return []

  current_date = datetime.now().timestamp()

  # Adjust the distance by applying the age penalty
  for candidate in candidates:
    age_in_seconds = current_date - candidate.date.timestamp()
    age_in_hours = age_in_seconds / 3600
    candidate.distance += age_in_hours * constants.AGE_PENALTY_FACTOR

  # Sort the candidates by distance
  candidates.sort(key=lambda x: x.distance)

  return candidates


def rank_candidates(candidates: list):
  """
  Rank the candidates based on their distance and a random factor
  """

  for idx, candidate in enumerate(candidates):
    candidate.rating = len(candidates) / ((idx + 1) * np.random.random())

  candidates.sort(key=lambda x: x.rating)

  return candidates


async def get_recommendations(user_id: int, flavour_id: int | None = None, recommendation_ids: list[int] | None = None):
  """
  Get recommendations for user
  """

  db = await database.get_db()
  user = await db.fetch_one(database.users.select().where(database.users.c.id == user_id))

  if flavour_id:
    flavour = await db.fetch_one(database.user_flavours.select().where(database.user_flavours.c.id == flavour_id))
    reference_embedding = flavour.embedding
  else:
    reference_embedding = user.embedding

  candidates = await get_recommendation_candidates(user_id, reference_embedding, recommendation_ids)
  ranked_candidates = rank_candidates(candidates)
  recommendation_ids = [candidate.id for candidate in ranked_candidates][: constants.NUM_RECOMMENDATIONS]

  # Join content with user_content_ratings to get user ratings
  content = await db.fetch_all(
    """
    SELECT
      c.id, c.content_type, c.title, c.url, c.description, c.source_id, c.date, c.media,
      s.url as source_url,
      COALESCE(ucr.rating, 0) as rating
    FROM content c
    LEFT JOIN user_content_ratings ucr ON c.id = ucr.content_id AND ucr.user_id = :user_id
    LEFT JOIN sources s ON c.source_id = s.id
    WHERE c.id IN (SELECT UNNEST(cast(:content_ids as int[])))
    """,
    {"user_id": user_id, "content_ids": recommendation_ids},
  )

  return content


async def get_closest_content(user_id: int):
  db = await database.get_db()
  user = await db.fetch_one(database.users.select().where(database.users.c.id == user_id))

  user_embedding = torch.tensor(user.embedding)

  # Join content with user_content_ratings to get user ratings
  content = await db.fetch_all(
    """
    SELECT
      c.id, c.content_type, c.title, c.url, c.description, c.source_id, c.date, c.media,
      s.url as source_url,
      COALESCE(ucr.rating, 0) as rating
    FROM content c
    LEFT JOIN user_content_ratings ucr ON c.id = ucr.content_id AND ucr.user_id = :user_id
    LEFT JOIN sources s ON c.source_id = s.id
    ORDER BY :user_embedding <-> c.embedding ASC
    LIMIT 5
    """,
    {"user_id": user_id, "user_embedding": util.list_to_string(user_embedding.tolist())},
  )

  return content


#
#
#
async def update_user_embedding(user_id: int, updated_embedding: torch.Tensor):
  db = await database.get_db()
  await db.execute(database.users.update().where(database.users.c.id == user_id), {"embedding": updated_embedding})


async def update_user_content_rating(user_id: int, content_id: int, rating: float):
  db = await database.get_db()

  # First check if a rating already exists
  existing_rating = await db.fetch_one(
    database.user_content_ratings.select().where(
      (database.user_content_ratings.c.user_id == user_id) & (database.user_content_ratings.c.content_id == content_id)
    )
  )

  if existing_rating:
    # Update existing rating
    await db.execute(
      database.user_content_ratings.update().where(
        (database.user_content_ratings.c.user_id == user_id)
        & (database.user_content_ratings.c.content_id == content_id)
      ),
      {"rating": rating, "timestamp": sqlalchemy.func.now()},
    )
  else:
    # Insert new rating
    await db.execute(
      database.user_content_ratings.insert(), {"user_id": user_id, "content_id": content_id, "rating": rating}
    )


async def handle_feedback(user_id: int, content_id: int, rating: float):
  """
  Adjust user embedding based on feedback

  Args:
      user_id (int): ID of the user providing feedback
      content_id (int): ID of the content being rated
      rating (float): Rating value indicating user's feedback between -1 and 1
  """

  if rating > 1 or rating < -1:
    raise Exception("Rating must be between -1 and 1")

  db = await database.get_db()
  user = await db.fetch_one(database.users.select().where(database.users.c.id == user_id))
  content = await db.fetch_one(database.content.select().where(database.content.c.id == content_id))

  # Adjust the embedding based on the rating using exponential moving average (EMA)
  updated_embedding = constants.USER_ADJUST_FACTOR * content.embedding * rating + (
    (1 - constants.USER_ADJUST_FACTOR) * user.embedding
  )

  # Normalize the embedding to unit length
  norm = torch.linalg.vector_norm(torch.tensor(updated_embedding))
  if norm > 0:
    updated_embedding = updated_embedding / norm

  # Print the geometric length (norm) of the embedding
  print("Embedding norm: ", norm)
  print("Updated embedding norm: ", torch.linalg.vector_norm(torch.tensor(updated_embedding)))

  await update_user_embedding(user_id, updated_embedding)
  await update_user_content_rating(user_id, content_id, rating)


#
#
#
async def sign_up():
  user_id = uuid.uuid4()

  db = await database.get_db()

  user = await db.execute(database.users.insert(), {"id": user_id})

  return user


#
#
#
async def get_onboarding_content(existing_selected_content_ids: list, existing_unselected_content_ids: list):
  db = await database.get_db()

  existing_selected_content = await db.fetch_all(
    database.content.select().where(database.content.c.id.in_(existing_selected_content_ids))
  )

  existing_unselected_content = await db.fetch_all(
    database.content.select().where(database.content.c.id.in_(existing_unselected_content_ids))
  )

  def is_far_enough(content):
    for selected_content_item in existing_selected_content:
      similarity = torch.cosine_similarity(
        torch.tensor(content.embedding), torch.tensor(selected_content_item.embedding), dim=0
      )
      if similarity.item() > constants.MAX_ONBOARDING_COSINE_SIMILARITY:
        return False
    return True

  # Converts cosine similarity to L2 distance
  min_l2_distance = util.cosine_to_l2_distance(constants.MAX_ONBOARDING_COSINE_SIMILARITY)

  print("Min L2 distance: ", min_l2_distance)

  existing_unselected_content = [x for x in existing_unselected_content if is_far_enough(x)]

  sample_count = constants.SAMPLE_COUNT - len(existing_selected_content_ids) - len(existing_unselected_content)

  if sample_count <= 0:
    return existing_selected_content + existing_unselected_content

  # Get a random sample of content ids that are at least min_l2_distance away from existing content
  sample_content_ids = await db.fetch_all(
    """
        WITH existing_embeddings AS (
            SELECT embedding
            FROM content
            WHERE id IN (SELECT UNNEST(cast(:existing_ids as int[])))
        )
        SELECT c.id AS id
        FROM content c
        WHERE c.embedding IS NOT NULL
        AND c.id NOT IN (SELECT UNNEST(cast(:existing_ids as int[])))
        AND NOT EXISTS (
            SELECT 1
            FROM existing_embeddings e
            WHERE c.embedding <-> e.embedding < :min_l2_distance
        )
        ORDER BY RANDOM()
        LIMIT :sample_count
    """,
    {
      "existing_ids": existing_selected_content_ids + existing_unselected_content_ids,
      "sample_count": sample_count,
      "min_l2_distance": min_l2_distance,
    },
  )

  if len(sample_content_ids) == 0:
    raise Exception("No content found")

  sample_content = await db.fetch_all(
    database.content.select().where(database.content.c.id.in_([x.id for x in sample_content_ids]))
  )

  return existing_selected_content + existing_unselected_content + sample_content


#
#
#
async def onboard(user_id: int, liked_content_ids: list):
  """
  Onboard a user by creating, then adjusting their embedding based on their feedback

  Args:
      user_id (int): ID of the user providing feedback
      liked_content_ids (list): List of content ids that the user liked
  """

  db = await database.get_db()

  liked_content = await db.fetch_all(database.content.select().where(database.content.c.id.in_(liked_content_ids)))

  # Create a user embedding based on the liked content
  liked_embeddings = torch.tensor(np.array([x.embedding for x in liked_content]))
  user_embedding = torch.mean(liked_embeddings, dim=0)

  # Save the user embedding to the database
  db = await database.get_db()
  await db.execute(
    database.users.update().where(database.users.c.id == user_id), {"embedding": user_embedding.tolist()}
  )


async def get_flavour(flavour_id: int):
  db = await database.get_db()
  flavour = await db.fetch_one(database.user_flavours.select().where(database.user_flavours.c.id == flavour_id))
  return flavour


async def get_flavours():
  db = await database.get_db()
  flavours = await db.fetch_all(database.user_flavours.select())
  return flavours


async def delete_flavour(flavour_id: int):
  db = await database.get_db()
  await db.execute(database.user_flavours.delete().where(database.user_flavours.c.id == flavour_id))


async def create_flavour(user_id: int, content_id: int):
  """
  Get content similar to a specific article

  Args:
      user_id (int): ID of the user
      content_id (int): ID of the content to find similar items for
      limit (int): Maximum number of similar items to return
  """
  db = await database.get_db()

  # Get the content item's embedding
  content_item = await db.fetch_one(database.content.select().where(database.content.c.id == content_id))
  if not content_item:
    return []

  prompt = f"Describe a short topic title for a feed of articles based on the following headline: {content_item.title}. Return only the topic title, no additional text."  # noqa: E501

  response = client.chat.completions.create(
    model=os.getenv("LLM_MODEL"),
    temperature=0,
    messages=[{"role": "user", "content": [{"type": "text", "text": prompt}]}],
  )

  nickname = response.choices[0].message.content

  # Create a flavour embedding based on the content item
  flavour_embedding = torch.tensor(np.array(content_item.embedding))

  # Save the flavour embedding to the database
  flavour_id = await db.execute(
    database.user_flavours.insert(), {"user_id": user_id, "nickname": nickname, "embedding": flavour_embedding.tolist()}
  )

  return flavour_id
