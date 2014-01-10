# -*- coding: utf-8 -*-
"""
This module implements a simple, heuristic algorithm to group extracted
entities into clusters. It works this way:

1. Each HTML token is assigned a position: position is increased
   with each token and when HTML element changes.

2. Distances between subsequent entities are calculated.

3. If a distance between 2 subsequent entities is greater than
   a certain threshold then new "cluster" is started.

4. Clusters are scored - longer clusters get bigger scores,
   but clusters with several entities of the same type are penalized.

5. Threshold value for the final clustering is selected
   to maximize total clustering score.

"""
from __future__ import absolute_import
import collections
import operator
from webstruct.sequence_encoding import IobEncoder


# XXX: If functions in this module are not flexible enough,
# PRs with refactoring are welcome.


_select_score = operator.itemgetter(1)
def choose_best_clustering(html_tokens, tags, score_func=None, score_kwargs=None):
    """
    Select a best way to split ``html_tokens`` and ``tags`` into clusters
    of named entities. Return ``(threshold, score, clustering)`` tuple.

    ``clustering`` is a list of clusters; each cluster is a list of
    named entities: ``(html_tokens, tag, distance)`` tuples.
    """
    score_func = score_func or default_clustering_score
    score_kwargs = score_kwargs or {}

    entities, positions = _entities_with_positions(html_tokens, tags)
    distances = _get_distances(positions)

    # first distance is irrelevant; prefer longer clusters
    thresholds = sorted(set(distances[1:]), reverse=True)

    if not thresholds:
        return (0, 0, group_entities_by_threshold(html_tokens, tags, 0))

    possible_clusterings = [
        group_entities_by_threshold(html_tokens, tags, threshold)
        for threshold in thresholds
    ]
    scores = [score_func(cl, threshold, **score_kwargs)
              for cl, threshold in zip(possible_clusterings, thresholds)]
    return max(zip(thresholds, scores, possible_clusterings), key=_select_score)


def default_clustering_score(clusters, threshold, dont_penalize=None):
    """
    Heuristic scoring function for clusters:

    - larger clusters get bigger scores;
    - clusters with multiple entities with the same tag are penalized.

    ``dont_penalize`` is a set of tags for which duplicates
    are allowed (empty by default).
    """

    # XXX: Maybe penalize large thresholds?

    dont_penalize = set(dont_penalize or set())
    score = 0
    for cluster in clusters:
        cnt = collections.Counter(tag for tokens, tag, dist in cluster)
        cl_score = sum(v for k, v in cnt.items()
                       if v == 1 or k in dont_penalize)
        cl_score -= sum(v for k, v in cnt.items()
                        if v != 1 and k not in dont_penalize)
        cl_score -= 1
        score += cl_score

    return score


def group_entities_by_threshold(html_tokens, tags, threshold, iob_encoder=IobEncoder):
    entities, positions = _entities_with_positions(html_tokens, tags, iob_encoder)
    distances = _get_distances(positions)

    groups, buf = [], []
    for ent, dist in zip(entities, distances):
        if dist > threshold:
            if buf:
                groups.append(buf)
                buf = []
        buf.append((ent[0], ent[1], dist))
    if buf:
        groups.append(buf)
    return groups


def _get_positions(html_tokens):
    # XXX: IMHO it penalizes text between entities too much
    pos = -(2+2+1)
    prev_parent, prev_elem = None, None
    positions = []
    for tok in html_tokens:
        if tok.parent is not prev_parent:
            pos += 2
            prev_parent = tok.parent
        if tok.elem is not prev_elem:
            pos += 1
            prev_elem = tok.elem
        pos += 2
        positions.append(pos)
    return positions


def _get_distances(start_end_pairs):
    """
    >>> _get_distances([(0,1), (5,10), (11,12)])
    [0, 4, 1]
    """
    distances = []
    prev_pos = 0
    for start, end in start_end_pairs:
        distances.append(start-prev_pos)
        prev_pos=end
    return distances


def _entities_with_positions(html_tokens, tags, iob_encoder=IobEncoder):
    tokens_with_positions = zip(html_tokens, _get_positions(html_tokens))
    data = zip(tokens_with_positions, tags)

    entities, positions = [], []
    for items, tag in iob_encoder.group(data):
        if tag == 'O':
            continue
        tokens, token_positions = zip(*items)
        entities.append((tokens, tag))
        positions.append((token_positions[0], token_positions[-1]))

    return entities, positions
