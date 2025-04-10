EMBED_DIM = 1024  # Must match the dimension of the model
MAX_CONTENT_AGE = 7  # Days
AGE_PENALTY_FACTOR = 6e-3  # Penalty for older content
USER_ADJUST_FACTOR = 0.1  # Adjust the proportion of content to show based on rating
NUM_RECOMMENDATIONS = 12  # Number of recommendations to show
SAMPLE_COUNT = 12  # Number of content ids to sample
MIN_SEARCH_COSINE_SIMILARITY = 0.3  # Minimum cosine similarity for search
MAX_ONBOARDING_COSINE_SIMILARITY = 0.15  # Maximum cosine similarity for onboarding
MIN_FLAVOUR_COSINE_SIMILARITY = 0.45  # Minimum cosine similarity for flavours

DB_CONSTANTS = {
  "EMBED_DIM": {
    "value": EMBED_DIM,
    "description": "Dimension of the model",
  },
  "MAX_CONTENT_AGE": {
    "value": MAX_CONTENT_AGE,
    "description": "Maximum age of content in days",
  },
  "AGE_PENALTY_FACTOR": {
    "value": AGE_PENALTY_FACTOR,
    "description": "Penalty factor for older content",
  },
  "USER_ADJUST_FACTOR": {
    "value": USER_ADJUST_FACTOR,
    "description": "Factor to adjust content proportion based on rating",
  },
  "NUM_RECOMMENDATIONS": {
    "value": NUM_RECOMMENDATIONS,
    "description": "Number of recommendations to show",
  },
  "SAMPLE_COUNT": {
    "value": SAMPLE_COUNT,
    "description": "Number of content ids to sample",
  },
  "MIN_SEARCH_COSINE_SIMILARITY": {
    "value": MIN_SEARCH_COSINE_SIMILARITY,
    "description": "Minimum cosine similarity for search",
  },
  "MAX_ONBOARDING_COSINE_SIMILARITY": {
    "value": MAX_ONBOARDING_COSINE_SIMILARITY,
    "description": "Maximum cosine similarity for onboarding",
  },
  "MIN_FLAVOUR_COSINE_SIMILARITY": {
    "value": MIN_FLAVOUR_COSINE_SIMILARITY,
    "description": "Minimum cosine similarity for flavours",
  },
}
