from spiral import spiral_anytime
from general import get_graph, assign_weights
from MCTS1 import MCTS
from MCTS2 import MCTS2
from time import sleep
from threading import Thread
import argparse


def timer_alg(G, S, t, b, algorithm, time_limit):
    print(f'Time limit: {time_limit}')
    results = {}
    t = Thread(target=algorithm, args=(G, S, t, b, results))
    t.daemon = True
    t.start()
    sleep(time_limit)
    res = results['res']
    return res

def main():
    graphs = ['graph_json/n3191e28565.json', 'graph_json/n6191e57831.json', 'graph_json/n12191e123583.json', 'graph_json/n30191e347370.json']
    parser = argparse.ArgumentParser()
    parser.add_argument('g', type=int)
    parser.add_argument('b', type=int)
    parser.add_argument('alg', type=int)
    parser.add_argument('time', type=int)
    args = parser.parse_args()
    graph_idx = args.g
    budget = args.b
    algorithm = args.alg
    time_limit = args.time
    G, S, t = get_graph(graphs[graph_idx-1])
    assign_weights(G, S, t)
    res = 0
    # print(f'G{graph_idx+1}_a{algorithm}_b{budget}_t{time_limit}_{index}')
    print(f'graph: G{graph_idx}, budget: {budget}, time: {time_limit}s')
    if algorithm == 1:
        # MCTS1
        print(f'Running MCTS1')
        tree = MCTS(G, S, t, budget)
        res = tree.run(time_limit=time_limit)
    elif algorithm == 2:
        # MCTS2
        print('Running MCTS2')
        tree = MCTS2(G, S, t, budget)
        res = tree.run(time_limit=time_limit)
    elif algorithm == 3:
        # Spiral
        print(f'Running Spiral')
        res = timer_alg(G, S, t, budget, spiral_anytime, time_limit)
    print(f'res: {res}')



if __name__ == '__main__':
    main()
