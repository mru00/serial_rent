class EpisodeScorer:
  def score(self, candidates):
    assert len(candidates) > 0
    if len(candidates) == 1:
      return candidates[0]
    return candidates[0]


def score(candidates):
  return EpisodeScorer().score(candidates)
