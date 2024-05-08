import math
import networkx as nx
import random
from time import sleep
from threading import Thread


class Node:
    def __init__(self, subgraph, edges, parent=None):
        self.subgraph = subgraph
        self.edges = edges
        self.Q = 0
        self.parent = parent
        self.children = {}
        self.N = 0
        self.terminated = False

class MCTS2:
    def __init__(self, G, S, t, budget):
        self.root = Node(subgraph=self.get_subgraph(G, S, t, []), edges=set())
        self.G = G
        self.S = S
        self.t = t
        self.budget = budget
    
    def run(self, time_limit):
        print(f'Compute within time {time_limit}s')
        t = Thread(target=self.search)
        t.daemon = True
        t.start()
        sleep(time_limit)
        print(f'Retrieving result...')
        return self.get_res()
    
    def search(self):
        while True:
            node = self.selection()
            score = self.simulation(node)
            self.backpropogate(node, score)

    def selection(self):
        node = self.root
        # non-terminal state
        while len(node.edges) < self.budget:
            if len(node.children) == node.subgraph.number_of_edges():
                picked_child = None
                highest_score = -1
                for child in node.children.values():
                    # UCB
                    score = child.Q / child.N + (2 * math.log(node.N) / child.N)**0.5
                    if score > highest_score:
                        picked_child = child
                        highest_score = score
                node = picked_child
            else:
                edges = node.edges.copy()
                new_edges = self.sample_edge(node)
                edges.update(new_edges)
                sub_G = self.get_subgraph(self.G, self.S, self.t, edges)
                new_node = Node(subgraph=sub_G, edges=edges, parent=node)
                assert len(new_edges) == 1
                node.children[new_edges[0]] = new_node
                return new_node
        return node
    
    def get_subgraph(self, G, S, t, cut_edges):
        sub_G = nx.DiGraph()
        G_r = G.reverse()
        for u, v in cut_edges:
            G_r.remove_edge(v, u)
        paths = nx.shortest_path(G_r, t)
        for s in S:
            if s in paths:
                for u, v in zip(paths[s], paths[s][1:]):
                    sub_G.add_edge(v, u)
        return sub_G

    def backpropogate(self, node, reward):
        temp = node
        while temp:
            temp.N += 1
            temp.Q += reward
            temp = temp.parent

    def simulation(self, node):
        cut_edges = node.edges.copy()
        pool = []
        for u, v in self.G.edges():
            if (u, v) not in cut_edges:
                pool.append((u, v))
        new_edges = random.sample(pool, self.budget - len(cut_edges))
        cut_edges.update(new_edges)
        G_copy = self.G.copy()
        for u, v in cut_edges:
            G_copy.remove_edge(u, v)
        count_S = 0
        for s in self.S:
            if not nx.has_path(G_copy, s, self.t):
                count_S += 1
        reward = count_S / len(self.S)
        return reward
    
    def sample_edge(self, node):
        edges = []
        for u, v in node.subgraph.edges():
            if (u, v) not in node.children:
                edges.append((u, v))
        new_edges = random.sample(edges, 1)
        return new_edges
    
    def get_res(self):
        temp = self.root
        while len(temp.children) > 0:
            next_node = None
            max_reward = -1
            for c in temp.children.values():
                if c.N == 0:
                    # Program got terminated before backpropagation completed for the new MCTS node
                    assert len(c.children) == 0
                    print('passed')
                    c.N = 1
                reward = c.Q / c.N
                if reward > max_reward:
                    max_reward = reward
                    next_node = c
            temp = next_node
        for u, v in temp.edges:
            self.G.remove_edge(u, v)
        count_S = 0
        for s in self.S:
            if not nx.has_path(self.G, s, self.t):
                count_S += 1
        print(count_S)
        return count_S

