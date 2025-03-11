import torch
import uuid
import numpy as np
from src import database, util

async def get_recommendations(user_id: int):
    db = await database.get_db()
    user = await db.fetch_one(database.users.select().where(database.users.c.id == user_id))

    # TODO - randomnly push the query embedding around within a radius to add a sort of "temperature" to results
    results = await db.fetch_all("""
        SELECT id, embedding <-> :user_embedding as distance
        FROM documents
        ORDER BY embedding <-> :user_embedding
        LIMIT :limit
    """, {
        "user_embedding": util.list_to_string(user.embedding),
        "limit": 5
    })

    doc_ids = tuple([doc.id for doc in results])

    if len(doc_ids) == 0:
        raise Exception("No documents found")

    documents = await db.fetch_all(database.documents.select().where(database.documents.c.id.in_(doc_ids)))

    return documents

async def sign_up():
    user_id = uuid.uuid4()

    db = await database.get_db()

    await db.execute(database.users.insert(), {
        "id": user_id
    })

    sample_count = 100

    sample_doc_ids = await db.fetch_all(f"""
        SELECT MIN(id) AS id
        FROM documents
        WHERE embedding IS NOT NULL
        GROUP BY source_id
        ORDER BY RANDOM()
        LIMIT {sample_count}
    """)

    if len(sample_doc_ids) == 0:
        raise Exception("No documents found")

    sample_doc_ids = tuple([doc.id for doc in sample_doc_ids])

    sample_docs = await db.fetch_all(database.documents.select().where(database.documents.c.id.in_(sample_doc_ids)))

    print(f"Signed up as {user_id}")

    return user_id, sample_docs

async def onboard(user_id: int, selected_docs: list):
    doc_embeddings = torch.tensor(np.array([doc.embedding for doc in selected_docs]))
    mean_embedding = torch.mean(doc_embeddings, dim=0)

    db = await database.get_db()

    await db.execute(database.users.update().where(database.users.c.id == user_id), {
        "embedding": mean_embedding.tolist()
    })

async def main():
    user_id = input("What is your user id? Leave blank to sign up.")

    if not user_id:
        user_id, doc_sample = await sign_up()

        print("Here are some posts you may be interested in")
        for i, doc in enumerate(doc_sample):
            print(f"{i + 1}) {doc['title']}")

        res = input("Choose some posts by entering their numbers (separated by commas), then press enter:\n")

        doc_indices = [int(x) for x in res.split(",")]

        selected_docs = [doc_sample[i - 1] for i in doc_indices]

        await onboard(user_id, selected_docs)

    recs = await get_recommendations(user_id)

    print(f"Here are some recommended posts for you:\n{util.list_to_string([rec['title'] for rec in recs])}")

if __name__ == "__main__":
    import asyncio
    asyncio.run(main())
