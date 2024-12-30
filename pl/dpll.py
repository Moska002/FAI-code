import numpy as np
import networkx as nx
from utils import elaborate_clauses, get_ordered_symbols

def find_unit_clause(symbols, clauses, model):
    save_index = None
    for clause in clauses:
        i = 0
        c_none = 0
        sat = False
        while i < len(clause) and not sat:
            literal_index = symbols.index(clause[i].replace('!', ''))
            if model[literal_index] == None: 
                save_index = i
                c_none = c_none + 1
            else:
                if('!' not in clause[i]):
                    sat = sat or model[literal_index]
                else:
                    sat = sat or not model[literal_index]
            i = i + 1
        if c_none == 1 and not sat:
            return clause[save_index]
    return None

def find_first(symbols, clauses, model):
    i = 0
    list_of_symbols = get_ordered_symbols(clauses)
    while i < len(model):
        if model[i] == None and symbols[i] in list_of_symbols:
            return i
        i = i + 1
    return None

def dpll_satisfailable(clauses):
    symbols = get_ordered_symbols(clauses)
    model = [None] * len(symbols)

    search_tree = nx.Graph()
    search_tree.add_node(0)
    
    labels = {0:'Start'}
    return (dpll(clauses, symbols, model, search_tree, 0, labels), search_tree, labels)

def dpll(clauses, symbols, model, search_tree, parent_node, labels):
    false_clauses, unsat_clauses = elaborate_clauses(symbols, clauses, model)
    print(model)
    if len(false_clauses) > 0:
        # I have at least one clause unsatisfailable with the current model
        id = search_tree.number_of_nodes()
        search_tree.add_node(id)
        search_tree.add_edge(parent_node, id)
        labels[id] = 'FAIL'
        return False
    elif len(unsat_clauses) == 0:
        id = search_tree.number_of_nodes()
        search_tree.add_node(id)
        search_tree.add_edge(parent_node, id)
        labels[id] = 'SAT'
        return True
    else:
        lonely_literal = find_unit_clause(symbols, unsat_clauses, model)
        if lonely_literal != None:
            literal = lonely_literal
            new_model = [x for x in model]
            if ('!' in literal):
                new_model[symbols.index(literal.replace('!', ''))] = False 
            else: 
                new_model[symbols.index(literal.replace('!', ''))] = True

            id = search_tree.number_of_nodes()
            search_tree.add_node(id)
            search_tree.add_edge(parent_node, id)
            labels[id] = literal

            return dpll(clauses, symbols, new_model, search_tree, id, labels)
        else:
            # Search for the first unassigned literal in a unsatisfied clause
            literal_index = find_first(symbols, unsat_clauses, model)
            if literal_index == None:
                # I found no literal
                id = search_tree.number_of_nodes()
                search_tree.add_node(id)
                search_tree.add_edge(parent_node, id)
                labels[id] = 'FAIL'
                return False
            # Model setting the literal to true
            new_model_true = [x for x in model]
            new_model_true[literal_index] = True
            
            id = search_tree.number_of_nodes()
            search_tree.add_node(id)
            search_tree.add_edge(parent_node, id)
            labels[id] = symbols[literal_index]

            ans = dpll(clauses, symbols, new_model_true, search_tree, id, labels)

            # Model setting the literal to false
            new_model_false = [x for x in model]
            new_model_false[literal_index] = False

            id = search_tree.number_of_nodes()
            search_tree.add_node(id)
            search_tree.add_edge(parent_node, id)
            labels[id] = '!' + symbols[literal_index]

            ans = ans or dpll(clauses, symbols, new_model_false, search_tree, id, labels)

            return ans

if __name__ == '__main__':
    import argparse
    import matplotlib.pyplot as plt
    from utils import parse_formula, get_ordered_symbols, generate_cnf, hierarchy_pos

    parser = argparse.ArgumentParser()

    parser.add_argument('--solve', type=str, nargs='+', 
                        help=f"List of literals in atrix form, where length of each clause is expressed in clause_lengths",
                        default=None)
    parser.add_argument('--clause_lengths', type=int, nargs='+',
                        help=f"A list that expresses the lenght of each clauses in solve",
                        default=None)

    parser.add_argument('-c', '--conjunctions', type=int,
                    help=f"Number of conjunctions in the formula",
                    default=4)
    parser.add_argument('-d', '--disjunctions', type=int, nargs=2,
                    help=f"Limit of minimum and maximum disjunctions in the formula",
                    default=(1, 4))
    
    parser.add_argument('-l', '--literals', type=str, nargs="+",
                    help=f"Literal list from which the formula is created",
                    default=['A', 'B', 'C', 'D', 'E', 'F'])

    parser.add_argument('-s', '--seed', type=int,
                    help=f"Random seed number",
                    default=int(np.random.random() * 1000))

    args = parser.parse_args()

    np.random.seed(args.seed)
    print("SEED: ", args.seed)
    symbols = args.literals

    if len(symbols) < args.disjunctions[1]:
        raise ValueError("Number of literals " +
                             "is not sufficient to generate a formula " +
                             "with maximum disjunctions")
    
    if args.solve == None:
        cnf = generate_cnf(symbols, args.conjunctions, args.disjunctions[1], min_disj=args.disjunctions[0])
    elif args.solve != None and args.clause_lengths != None:
        cnf = parse_formula(args.solve, args.clause_lengths)
    else:
        raise ValueError('Formula or disjunctions lengths not provided')
    
    print(cnf)

    input()
    (ans, search_tree, labels) = dpll_satisfailable(cnf)

    print(f"Solution of symbols {get_ordered_symbols(cnf)} is {ans}")

    nx.draw(search_tree, pos=hierarchy_pos(search_tree, 0), labels=labels)
    plt.show()