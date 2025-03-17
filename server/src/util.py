def list_to_string(list, tuple=False):
  init = "({})" if tuple else "[{}]"
  return init.format(",".join([str(x) for x in list]))
