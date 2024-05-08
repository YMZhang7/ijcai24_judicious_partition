import random
import networkx as nx
import math
from time import sleep
from threading import Thread


class Node:
    def __init__(self, edges, parent=None):
        self.edges = edges
        self.Q = 0
        self.parent = parent
        self.children = {}
        self.N = 0

class MCTS:
    def __init__(self, G, S, t, budget):
        self.root = Node(set())
        self.G = G
        self.S = S
        self.t = t
        self.b = budget
        self.all_edges = self.initialise_edge_indices(G)
    
    def initialise_edge_indices(self, G):
        res = {}
        idx = 0
        for u, v in G.edges():
            idx += 1
            res[(u, v)] = idx
        return res

    def run(self, time_limit=0):
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
            score = self.simulation(node.edges)
            self.backpropogate(node, score)

    def backpropogate(self, node, reward):
        temp = node
        while temp:
            temp.N += 1
            temp.Q += reward
            temp = temp.parent
    
    def simulation(self, edges):
        pool = []
        for u, v in self.all_edges.keys():
            if (u, v) not in edges:
                pool.append((u, v))
        new_edges = random.sample(pool, self.b - len(edges))
        edges.update(new_edges)
        # assert len(edges) == self.b
        G_copy = self.G.copy()
        for u, v in edges:
            G_copy.remove_edge(u, v)
        count_S = 0
        for s in self.S:
            if not nx.has_path(G_copy, s, self.t):
                count_S += 1
        reward = count_S / len(self.S)
        return reward
    
    def selection(self):
        node = self.root
        # non-terminal state
        while len(node.edges) < self.b and self.get_max_idx(node.edges) < len(self.all_edges):
            if len(node.children) == len(self.all_edges) - self.get_max_idx(node.edges):
                # fully expanded, go to best child
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
                # expand node, return new node
                edges = node.edges.copy()
                new_edges = self.sample_edges(node, 1)
                edges.update(new_edges)
                new_node = Node(edges=edges, parent=node)
                node.children[new_edges[0]] = new_node
                return new_node
        return node
    
    def get_max_idx(self, edges):
        max_idx = 0
        for u, v in edges:
            max_idx = max(max_idx, self.all_edges[(u, v)])
        return max_idx
    
    def sample_edges(self, node, count):
        max_idx = self.get_max_idx(node.edges)
        pool = []
        for u, v in self.all_edges.keys():
            if self.all_edges[(u, v)] > max_idx and (u, v) not in node.children:
                pool.append((u, v))
        if len(pool) < count:
            return pool
        new_edges = random.sample(pool, count)
        return new_edges
    
    def get_res(self):
        temp = self.root
        while len(temp.children) > 0:
            next_node = None
            max_reward = -1
            for c in temp.children.values():
                if c.N == 0:
                    assert len(c.children) == 0
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
        print(f'res: {count_S}')
        return count_S
        
    