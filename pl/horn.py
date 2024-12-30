import numpy as np
from utils import generate_cnf, elaborate_clauses
from dpll import find_unit_clause

def generate_horn(symbols, n_conj, max_disj, min_disj):
    clauses = generate_cnf(symbols, n_conj, max_disj, min_disj, p_negative=1.0)

    for clause in clauses:
        for i in range(len(clause)): 
            if np.random.random() <= 1 / len(clause):
                clause[i] = clause[i].replace('!', '')
                break

    return clauses

def horn_satisfiable(symbols, clauses, model):
    literal = find_unit_clause(symbols, clauses, model)
    while(literal != None):
        if ('!' in literal):
            model[symbols.index(literal.replace('!', ''))] = False 
        else: 
            model[symbols.index(literal.replace('!', ''))] = True
        literal = find_unit_clause(symbols, clauses, model)
    unsat, _ = elaborate_clauses(symbols, clauses, model)
    if len(unsat) > 0:
        return None
    else:
        return [False if x is None else x for x in model]

if __name__ == '__main__':
    import argparse
    from utils import get_ordered_symbols

    parser = argparse.ArgumentParser()

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
    
    horn = generate_horn(symbols, args.conjunctions, args.disjunctions[1], min_disj=args.disjunctions[0])
    print(horn)

    input()
    model = [None] * len(symbols)
    ans = horn_satisfiable(symbols, horn, model)

    print(f"Solution of symbols {get_ordered_symbols(horn)} is {ans}")