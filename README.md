This repository contains the source code and data associated with our paper submitted to IJCAI-2024 (https://ijcai24.org/), titled "Practical Anytime Algorithms for Judicious Partitioning of Active Directory Attack Graphs".

The code requires installing the following Python packages:
- networkx
- gurobi
- pulp
- heapdict

Before running the code, please unzip ```graphs.zip``` and make sure that all json files are in the folder ```graph_json```.

Please specify input:
 - graph_index
    - 1: G1 (n3191e28565.json)
    - 2: G2 (n6191e57831.json)
    - 3: G3 (n12191e123583.json)
    - 4: G4 (n30191e347370.json)
- budget: the number of edges to be removed
- algorithm:
    - 1: MCTS1
    - 2: MCTS2
    - 3: Spiral anytime algorithm
- time_limit: seconds

Please run the algorithms with the following command format:
```
python3 main.py graph_index budget algorithm time_limit
```

Example:
graph: G1; budget: 5; algorithm: spiral; time_limit: 30s
```
python3 main.py 1 5 3 30
```
