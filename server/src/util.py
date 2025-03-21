import numpy as np


def list_to_string(list, tuple=False):
  init = "({})" if tuple else "[{}]"
  return init.format(",".join([str(x) for x in list]))


def cosine_to_l2_distance(cosine_similarity):
  return np.sqrt(2 - 2 * cosine_similarity)
