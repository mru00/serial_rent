
# This module provides the means to filter the best result
# when multiple matching torrents are found.
#
# In future, preferences like "no hdtv", "i prefer eztv", ...
# could be implemented here.

class EpisodeScorer:
  def score(self, candidates):
    assert len(candidates) > 0
    if len(candidates) == 1:
      return candidates[0]
    return candidates[0]


def score(candidates):
  return EpisodeScorer().score(candidates)
