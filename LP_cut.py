from pulp import LpVariable, LpProblem, LpStatus, value, lpSum, GUROBI_CMD, LpMinimize


def get_cut(G, S, t, budget, edge_candidates):
    prob = LpProblem("IP", LpMinimize)
    node_vars = {}
    cut_vars = {}
    for u, v in edge_candidates:
        cut_vars[(u, v)] = LpVariable(f'c_{len(cut_vars)+1}', cat='Binary')
    for u, v in G.edges():
        if (u, v) not in cut_vars:
            cut_vars[(u, v)] = 0
    for n in G.nodes():
        if n == t:
            node_vars[n] = 1
        else:
            node_vars[n] = LpVariable(f'{n}', cat="Binary")

    prob += lpSum([node_vars[s] for s in S]), "Minimise S"

    # constraints
    for u, v in G.edges():
        prob += node_vars[u] >= node_vars[v] - cut_vars[(u, v)]
    # budget
    prob += lpSum(list(cut_vars.values())) <= budget
    prob.solve(GUROBI_CMD(msg=False))
    assert LpStatus[prob.status] == "Optimal"

    res = len(S) - int(value(prob.objective))
    chokepoints = []
    for u, v in cut_vars:
        try:
            if cut_vars[(u, v)].varValue > 0:
                chokepoints.append((u, v))
        except:
            continue
    return res, chokepoints