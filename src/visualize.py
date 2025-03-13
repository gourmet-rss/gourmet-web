from sklearn.manifold import TSNE
from sklearn.decomposition import PCA
import plotly.graph_objects as go
import asyncio
from src import database
import numpy as np
import torch
from datetime import datetime, timedelta

MAX_DAYS = 7.0  # Content older than 7 days is not included
MIN_SIZE = 5.0  # Minimum point size for oldest content (nearly 7 days old)
MAX_SIZE = 20.0  # Maximum point size for newest content


async def visualize_user_embedding_history(user_embeddings: list):
  db = await database.get_db()
  all_content = await db.fetch_all(
    database.content.select().where(database.content.c.date >= datetime.now() - timedelta(days=MAX_DAYS))
  )

  embeddings = torch.tensor(np.array([x.embedding for x in all_content]))

  # Combine content and user embeddings for t-SNE
  combined_embeddings = embeddings
  if user_embeddings:
    user_embeddings_tensor = torch.tensor(np.array(user_embeddings))
    combined_embeddings = torch.cat([embeddings, user_embeddings_tensor], dim=0)

  # Convert to numpy for scikit-learn
  combined_embeddings_np = combined_embeddings.numpy()

  # Apply PCA first to reduce dimensionality (recommended for t-SNE)
  # Using 50 components or fewer if the data has fewer dimensions
  n_components_pca = min(50, combined_embeddings_np.shape[1])
  pca = PCA(n_components=n_components_pca, random_state=42)
  embeddings_pca = pca.fit_transform(combined_embeddings_np)

  # Print explained variance to understand how much information is retained
  explained_variance = sum(pca.explained_variance_ratio_)
  print(f"PCA with {n_components_pca} components explains {explained_variance:.2%} of variance")

  distinct_colors = [
    "#87CEEB",  # Sky Blue
    "#FF0000",  # Bright Red
    "#228B22",  # Forest Green
    "#FFA500",  # Orange
    "#800080",  # Purple
    "#8B0000",  # Dark Red
    "#4169E1",  # Royal Blue
    "#90EE90",  # Light Green
    "#1E90FF",  # Dodger Blue
    "#32CD32",  # Lime Green
    "#000080",  # Navy Blue
  ]

  # Mapping for colors
  color_index_to_color = {i: color for i, color in enumerate(distinct_colors)}

  source_ids = [x.source_id for x in all_content]

  sources = await db.fetch_all(database.sources.select())

  # Create a mapping from source_id to source_url for legend
  source_id_to_url = {x.id: x.url for x in sources}

  def get_color_for_source(source_id):
    i = source_ids.index(source_id)
    return color_index_to_color[i % len(color_index_to_color)]

  # Function to calculate point size based on content age
  now = datetime.now()

  def get_point_size(content_date):
    # Calculate age in days
    age_days = (now - content_date).total_seconds() / (24 * 60 * 60)
    # Normalize age to [0, 1] where 0 is newest and 1 is oldest (7 days)
    normalized_age = min(age_days / MAX_DAYS, 1.0)
    # Invert so newer content has larger points
    normalized_size = 1.0 - normalized_age
    # Scale to point size range
    point_size = MIN_SIZE + normalized_size * (MAX_SIZE - MIN_SIZE)
    return point_size

  # t-SNE - 3D (now applied to PCA results)
  tsne3d = TSNE(
    n_components=3,
    random_state=42,
    perplexity=min(30, len(embeddings_pca) - 1),
    n_iter=1000,
    learning_rate="auto",
    init="pca",
  )
  tsne3d_result = tsne3d.fit_transform(embeddings_pca)

  # Get the content and user parts of the t-SNE results
  content_tsne_result = tsne3d_result[: len(embeddings)]
  user_tsne_result = tsne3d_result[len(embeddings) :] if user_embeddings else None

  # Create a figure for 3D visualization
  fig = go.Figure()

  # Add scatter points for each content item, grouped by source
  for source_id in set(source_ids):
    # Get all points for this source
    source_mask = [x.source_id == source_id for x in all_content]
    source_indices = [i for i, m in enumerate(source_mask) if m]

    if not source_indices:
      continue

    # Get source url for the legend
    source_url = source_id_to_url.get(source_id, f"Source {source_id}")

    # Calculate point sizes based on content age
    point_sizes = [get_point_size(all_content[i].date.replace(tzinfo=None)) for i in source_indices]

    # Calculate content ages in hours for hover info
    content_ages = [(now - all_content[i].date.replace(tzinfo=None)).total_seconds() // 3600 for i in source_indices]

    # Add 3D scatter plot for this source
    fig.add_trace(
      go.Scatter3d(
        x=content_tsne_result[source_indices, 0],
        y=content_tsne_result[source_indices, 1],
        z=content_tsne_result[source_indices, 2],
        mode="markers",
        marker=dict(color=get_color_for_source(source_id), size=point_sizes, opacity=0.6, sizemode="diameter"),
        name=source_url,
        hovertemplate="<b>%{text}</b><br>Age: %{customdata} hours<extra></extra>",
        text=[all_content[i].title for i in source_indices],
        customdata=content_ages,
      )
    )

  user_color = "#FF0000"

  # Add user embeddings as points
  if user_tsne_result is not None and len(user_tsne_result) > 0:
    user_texts = []
    for i, user in enumerate(user_embeddings):
      if i == 0:
        user_texts.append("Current embedding")
      else:
        user_texts.append(f"{i} steps ago")

    # Add user embedding points
    fig.add_trace(
      go.Scatter3d(
        x=user_tsne_result[:, 0],
        y=user_tsne_result[:, 1],
        z=user_tsne_result[:, 2],
        mode="markers",
        marker=dict(
          color=user_color,
          size=8,  # Slightly larger to distinguish from content
          opacity=0.8,
          symbol="diamond",  # Different symbol for users
        ),
        name="Users",
        hovertemplate="<b>%{text}</b><extra></extra>",
        text=user_texts if user_texts else ["User"] * len(user_tsne_result),
      )
    )

    # Add a path connecting user embeddings in sequence
    if len(user_tsne_result) > 1:
      fig.add_trace(
        go.Scatter3d(
          x=user_tsne_result[:, 0],
          y=user_tsne_result[:, 1],
          z=user_tsne_result[:, 2],
          mode="lines",
          line=dict(
            color=user_color,
            width=2,
          ),
          name="User Embedding Path",
          showlegend=True,
          hoverinfo="none",  # Don't show hover info for the path
        )
      )

  # Update layout
  fig.update_layout(
    title="t-SNE visualization of document/user embeddings (3D)",
    scene=dict(
      xaxis_title="X",
      yaxis_title="Y",
      zaxis_title="Z",
      aspectmode="cube",
    ),
    legend=dict(
      x=1.05,
      y=1,
      xanchor="left",
      yanchor="top",
    ),
    margin=dict(l=0, r=0, b=0, t=40),
    width=1600,
    height=800,
    hoverlabel=dict(bgcolor="white", font_size=16),
  )

  # Show the plot
  fig.show()


async def main():
  db = await database.get_db()

  sample_user = await db.fetch_one(database.users.select())

  await visualize_user_embedding_history([sample_user.embedding, sample_user.embedding + [0.1] * 768])


if __name__ == "__main__":
  asyncio.run(main())
