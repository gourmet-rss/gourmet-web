from database import pg_cursor
import torch
from datetime import datetime
import uuid

class Document:
    title: str
    url: str
    description: str
    date: datetime
    embedding: torch.Tensor | None

class User:
    id: int
    embedding: torch.Tensor

def encode_document_content(document: Document) -> str:
    encoded = torch.zeros(1, 1024)

    # normalize
    encoded = torch.nn.functional.normalize(encoded, p=2, dim=1)

    return encoded

def process_document(document: Document):
    """
    Receives a document from the source feed.

    Args:
        document (Document): The document to process.

    Returns:
        None
    """

    # Extract title, URL, and content from the document

    embedding = encode_document_content(document)

    pg_cursor.execute("INSERT INTO documents (title, url, description, embedding) VALUES (%s, %s, %s, %s)", (document.title, document.url, document.description, embedding))

def filter_results_with_temperature(results):
    return results[:5]

DOC_LIMIT = 100

def handle_user_request(user_id: int):
    user_embedding = pg_cursor.execute("SELECT embedding FROM users WHERE id = %s", (user_id,))
    
    pg_cursor.execute("""
        SELECT title, url, description, embedding <-> %s as distance 
        FROM documents 
        ORDER BY embedding <-> %s
        LIMIT {DOC_LIMIT}
    """, (user_embedding, user_embedding))

    results = pg_cursor.fetchall()

    # TODO: we'll need to keep increasing DOC_LIMIT as embedding space becomes denser - switch to randomnly pushing around the user embedding instead and doing KNN
    results = filter_results_with_temperature(results)
    
    return results

def sign_up():
    user_id = uuid.uuid4()

    pg_cursor.execute("INSERT INTO users (id) VALUES (%s)", (user_id,))

    sample_count = 100

    # TODO: unique by source
    doc_sample = pg_cursor.execute("SELECT * FROM documents ORDER BY RANDOM() LIMIT %s", (sample_count,))

    return user_id, doc_sample

def onboard(user_id: int, selected_docs: list[Document]):
    mean_embedding = torch.mean(torch.stack([doc.embedding for doc in selected_docs]), dim=0)

    pg_cursor.execute("UPDATE users SET embedding = %s WHERE id = %s", (mean_embedding, user_id))

    return

def main():
    user_id = input("What is your user id? Leave blank to sign up.")

    if not user_id:
        user_id, doc_sample = sign_up()
        
        selected_docs = input("Select some docs:")
    
        onboard(user_id, selected_docs)
    
    handle_user_request(user_id)

if __name__ == "__main__":
    main()
