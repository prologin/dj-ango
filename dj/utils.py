from hsaudiotag import auto

def compute_time(fname):
  return auto.File(fname).duration
