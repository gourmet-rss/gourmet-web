EMBED_DIM = 768  # Must match the dimension of the model
MAX_CONTENT_AGE = 7  # Days
AGE_PENALTY_FACTOR = 6e-3  # Penalty for older content
USER_ADJUST_FACTOR = 0.1  # Adjust the proportion of content to show based on rating
NUM_RECOMMENDATIONS = 12  # Number of recommendations to show
SAMPLE_COUNT = 12  # Number of content ids to sample
MIN_SEARCH_COSINE_SIMILARITY = 0.05  # Minimum cosine similarity for search
MAX_ONBOARDING_COSINE_SIMILARITY = 0.2  # Maximum cosine similarity for onboarding
