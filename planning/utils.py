def print_duration_table(dag, labels, durations):
    print('Node | Duration')
    for node in sorted(list(dag.nodes)):
        print("%4s | %8i" % (labels[node], durations[node]))

def print_solution_table(dag, labels, es, ls):
    print('Node | ES | LS')
    for node in sorted(list(dag.nodes)):
        print("%4s | %2i | %2i" % (labels[node], es[node], ls[node]))