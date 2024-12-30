import numpy as np 
import re
import networkx as nx
import itertools

def select_choice(options, choices):
    '''Simulated stochastic process that deterministically pick an
    option given a pre-determined list of choices. Choices are
    cycled through. Options are weighted.

    '''
    w_sum = sum(w for _, w in options)

    print("options:", [(o, w/w_sum) for o,w in options])
    print("choices:", choices)

    choice = choices.pop(0) 
    choices.append(choice) # cycling

    p = 0
    for opt, w in options:
        p += w/w_sum
        if choice <= p:
            return opt, p
        
def hierarchy_pos(G, root=None, width=1., vert_gap = 0.2, vert_loc = 0, xcenter = 0.5):
    '''
    From Joel's answer at https://stackoverflow.com/a/29597209/2966723.  
    Licensed under Creative Commons Attribution-Share Alike 
    
    If the graph is a tree this will return the positions to plot this in a 
    hierarchical layout.
    
    G: the graph (must be a tree)
    
    root: the root node of current branch 
    - if the tree is directed and this is not given, 
      the root will be found and used
    - if the tree is directed and this is given, then 
      the positions will be just for the descendants of this node.
    - if the tree is undirected and not given, 
      then a random choice will be used.
    
    width: horizontal space allocated for this branch - avoids overlap with other branches
    
    vert_gap: gap between levels of hierarchy
    
    vert_loc: vertical location of root
    
    xcenter: horizontal location of root
    '''
    if not nx.is_tree(G):
        raise TypeError('cannot use hierarchy_pos on a graph that is not a tree')

    if root is None:
        if isinstance(G, nx.DiGraph):
            root = next(iter(nx.topological_sort(G)))  #allows back compatibility with nx version 1.11
        else:
            root = np.random.choice(list(G.nodes))

    def _hierarchy_pos(G, root, width=1., vert_gap = 0.2, vert_loc = 0, xcenter = 0.5, pos = None, parent = None):
        '''
        see hierarchy_pos docstring for most arguments

        pos: a dict saying where all nodes go if they have been assigned
        parent: parent of this branch. - only affects it if non-directed

        '''
    
        if pos is None:
            pos = {root:(xcenter,vert_loc)}
        else:
            pos[root] = (xcenter, vert_loc)
        children = list(G.neighbors(root))
        if not isinstance(G, nx.DiGraph) and parent is not None:
            children.remove(parent)  
        if len(children)!=0:
            dx = width/len(children) 
            nextx = xcenter - width/2 - dx/2
            for child in children:
                nextx += dx
                pos = _hierarchy_pos(G,child, width = dx, vert_gap = vert_gap, 
                                    vert_loc = vert_loc-vert_gap, xcenter=nextx,
                                    pos=pos, parent = root)
        return pos

            
    return _hierarchy_pos(G, root, width, vert_gap, vert_loc, xcenter)

def get_ordered_symbols(clauses):
    '''
    Return a list with all the symbols present in a set of clauses
    '''
    symbols = set([x.replace('!', '') for x in list(itertools.chain.from_iterable(clauses))])
    return sorted(list(symbols), key=lambda x: re.sub('[^A-Za-z]+', '', x).lower())
        
def generate_cnf(symbols, n_conj, max_disj, min_disj = 1):
    '''
    Creates a random formula in cnd form. 
    The formula is expressed in a matrix where:
    each cell in each row is in the same disjuction and
    each row is in conjuction with the others
    '''

    cnf = []
    for conj in range(0, n_conj):
        choices = np.random.choice(
            len(symbols), 
            size=np.random.randint(min_disj, max_disj + 1), 
            replace=False)
        literals = []
        for x in range(len(choices)):
            if np.random.random() <= 0.5:
                literals.append('!' + symbols[choices[x]])
            else:
                literals.append('' + symbols[choices[x]])
        cnf.append(sorted(literals, key=lambda x: re.sub('[^A-Za-z]+', '', x).lower()))
    return cnf

def elaborate_clauses(symbols, clauses, model):
    '''
    Search for unsatisfied clauses given a model.
    If a clause contains empty (None) values, it is not returned
    only if the known values make it satisfied
    '''

    unsolvable = []
    unsatisfied = []
    for clause in clauses:
        i = 0
        sat = False
        still_solvable = False
        while i < len(clause) and not sat:
            literal = symbols.index(clause[i].replace('!', ''))
            if model[literal] != None:
                if('!' not in clause[i]):
                    sat = sat or model[literal]
                else:
                    sat = sat or not model[literal]
            else:
                still_solvable = True
            i = i + 1
        if not sat:
            if still_solvable:
                unsatisfied.append(clause)
            else:
                unsolvable.append(clause)

    return (unsolvable, unsatisfied)