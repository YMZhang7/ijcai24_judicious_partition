import networkx as nx
from general import assign_weights, count_unexplored
from LP_cut import get_cut
import heapdict
import random


def spiral_anytime(G, S, t, budget, result):
    total_edges = count_unexplored(G)
    edge_candidates = set()
    result['res'] = 0

    while True:
        if len(edge_candidates) == total_edges:
            return result['res']
        k = len(S) - result['res']
        edges = edge_sampling(G, S, t, k)
        for u, v in edges:
            edge_candidates.add((u, v))
            G[u][v]['weight'] += 1
        res, chokepoints = get_cut(G, S, t, budget, edge_candidates)
        if res > result['res']:
            print(f'Disconnected source nodes: {res}')
            result['res'] = res
            edge_candidates.clear()
            assign_weights(G, S, t)

def edge_sampling(G, S, t, k):
    G_r = G.reverse()
    paths = nx.shortest_path(G_r, t, weight='weight')
    s_edges = heapdict.heapdict()

    for s in S:
        if s in paths:
            path = paths[s]
            count = 0
            for u, v in zip(path, path[1:]):
                if G_r[u][v]['weight'] == 0:
                    count -= 1
            s_edges[s] = count
    
    included_S = set()
    edges = set()
    total_count = 0
    while len(included_S) < k:
        s, count = s_edges.popitem()
        total_count -= count
        path = paths[s]
        for u, v in zip(path, path[1:]):
            if G[v][u]['weight'] == 0:
                edges.add((v, u))
            if v in S:
                included_S.add(v)
            if u in S:
                included_S.add(u)
    if len(edges) == 0:
        print(f'random sampling starts')
        pool = []
        for u, v in G.edges():
            if G[u][v]['weight'] == 0:
                pool.append((u, v))
        if len(pool) > 50:
            edges = random.sample(pool, 50)
        else:
            edges = set(pool)
    return edges
