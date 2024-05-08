import codecs
import networkx as nx
import json


def parse_adsim(file_path):
    file = open(file_path, "r", encoding="utf-8")
    text = codecs.decode(file.read().encode(), 'utf-8-sig')
    file.close()
    obj_strs = text.split('\n')

    node_type = {}
    edge_types = {}
    id_objectid = {}
    compromised_nodes = set()
    edges = set()
    low_priv = {} # objectid -> node type

    for obj_str in obj_strs:
        obj = json.loads(obj_str)
        if obj['type'] == 'node':
            if len(obj['labels']) == 1:
                assert obj['labels'][0] == 'Domain'
            id_objectid[obj['id']] = obj["properties"]["objectid"]
            node_type[obj["properties"]["objectid"]] = obj['labels'][-1]
            if len(obj['labels']) > 1 and obj['labels'][-2] == 'Compromised':
                compromised_nodes.add(obj["properties"]["objectid"])
            if obj['properties']['name'] == "DOMAIN ADMINS@TESTLAB.LOCAL":
                DA = obj["properties"]["objectid"]
            if 'highvalue' in obj["properties"]:
                if not obj["properties"]["highvalue"]:
                    assert obj["properties"]["objectid"] not in low_priv
                    low_priv[obj["properties"]["objectid"]] = obj['labels'][-1]
        else:
            assert obj['type'] == 'relationship'
            if obj['start']['id'] in id_objectid and obj['end']['id'] in id_objectid:
                edge = (id_objectid[obj['start']['id']], id_objectid[obj['end']['id']])
                edges.add(obj['label'])
                if edge not in edge_types:
                    edge_types[edge] = []
                edge_types[edge].append(obj['label'])

    G = nx.DiGraph()
    for u, v in edge_types.keys():
        G.add_edge(u, v, access_types=edge_types[(u, v)])
    G.graph["DA"] = DA
    G.graph['node_type'] = node_type
    assert G.has_node(G.graph["DA"])
    print(f'Nodes: {G.number_of_nodes()}')
    print(f'Edges: {G.number_of_edges()}')

    return G, low_priv


def get_graph(graph_file):
    G, S_types = parse_adsim(f'{graph_file}')
    S = []
    t = G.graph['DA']
    for node in S_types.keys():
        if S_types[node] in ['User', 'Computer'] and nx.has_path(G, node, t):
            S.append(node)
    return G, S, t

# edges that are on paths between S and t are marked as unexplored (weight=0)
def assign_weights(G, S, t):
    for u, v in G.edges():
        G[u][v]['weight'] = 0
        if u == t:
            G[u][v]['weight'] = int(1e10)
    for s in S:
        G.add_edge('ssrc', s)
    paths_from_s = nx.shortest_path(G, 'ssrc')
    paths_to_t = nx.shortest_path(G.reverse(), t)
    for u, v in G.edges():
        if u not in paths_from_s or v not in paths_to_t:
            G[u][v]['weight'] = int(1e10)
    G.remove_node('ssrc')

def count_unexplored(G):
    res = 0
    for u, v in G.edges():
        if G[u][v]['weight'] == 0:
            res += 1
    return res