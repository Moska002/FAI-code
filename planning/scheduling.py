import networkx as nx
import numpy as np

def create_dependencies(nodes, p_edge, max_duration, seed):
    g = nx.gnp_random_graph(nodes, p_edge, seed=seed, directed=True)
    dag = nx.DiGraph([(u,v) for (u,v) in g.edges() if u<v])

    labels = {}
    durations = {}
    for i in list(dag.nodes):
        labels[i] = chr(ord('A') + i)
        durations[i] = np.random.randint(1, max_duration)

    st_node = -1 
    dag.add_node(-1)
    end_node = max(list(dag.nodes))
    dag.add_node(end_node)

    for node in list(dag.nodes):
        if(node != st_node and node != end_node):
            if len(list(dag.predecessors(node))) == 0:
                dag.add_edge(st_node, node)
            if len(list(dag.successors(node))) == 0:
                dag.add_edge(node, end_node)

    labels[st_node] = 'ST'
    labels[end_node] = 'EN'
    durations[st_node] = 0
    durations[end_node] = 0

    assert nx.is_directed_acyclic_graph(dag)
    return dag, {'labels': labels, 'durations': durations}

def calculate(dag, durations):
    ls = {}
    es = {}

    order = list(nx.topological_sort(dag))
    for node in order:
        predecessors = list(dag.predecessors(node))
        if len(predecessors) == 0:
            es[node] = 0
            ls[node] = 0
        else:
            es[node] = -np.inf
            for pred in predecessors:
                if(es[pred] + durations[pred] > es[node]):
                    es[node] = es[pred] + durations[pred]
    for node in reversed(order):
        successors = list(dag.successors(node))
        if len(successors) == 0:
            ls[node] = es[node]
        else:
            ls[node] = np.inf
            for succ in successors:
                if(ls[succ] - durations[node] < ls[node]):
                    ls[node] = ls[succ] - durations[node]

    return es, ls

def print_duration_table(dag, labels, durations):
    print('Node | Duration')
    for node in sorted(list(dag.nodes)):
        print("%4s | %8i" % (labels[node], durations[node]))

def print_solution_table(dag, labels, es, ls):
    print('Node | ES | LS')
    for node in sorted(list(dag.nodes)):
        print("%4s | %2i | %2i" % (labels[node], es[node], ls[node]))

if __name__ == '__main__':
    import argparse
    import matplotlib.pyplot as plt

    parser = argparse.ArgumentParser()

    parser.add_argument('-e', '--events', type=int,
    help="Number of nodes created",
    default=6)

    parser.add_argument('-p', '--p_edge',type=float,
    help="Number of dependencies between events",
    default=0.5)

    parser.add_argument('-m', '--max_duration', type=int,
    help="Maximum duration of an event",
    default=12)

    parser.add_argument('--seed', type=int,
    help="Random seed number",
    default=int(np.random.random() * 1000))

    args = parser.parse_args()
    print("SEED:", args.seed)

    dag, info = create_dependencies(args.events, args.p_edge, args.max_duration, seed=args.seed)

    print_duration_table(dag, info['labels'], info['durations'])
    es, ls = calculate(dag, info['durations'])
    print_solution_table(dag, info['labels'], es, ls)
    nx.draw(dag, pos=nx.circular_layout(dag), labels=info['labels'])
    plt.show()