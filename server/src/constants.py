EMBED_DIM = 768  # Must match the dimension of the model
MAX_CONTENT_AGE = 7  # Days
AGE_PENALTY_FACTOR = 6e-3  # Penalty for older content
USER_ADJUST_FACTOR = 1e-1  # Adjust the proportion of content to show based on rating
NUM_RECOMMENDATIONS = 5  # Number of recommendations to show
SAMPLE_COUNT = 10  # Number of content ids to sample
MAX_SEARCH_DISTANCE = 3e-1  # Maximum new embedding distance from the user embedding for search
