import numpy as np
from function_tools import rng


def mutate(x, operator='swap2', *args):
    if operator == 'swap2':
        idx1, idx2 = rng.integers(0, len(x), 2)
        x_i1 = x[idx1]
        x[idx1] = x[idx2]
        x[idx2] = x_i1
    elif operator == 'reverse_sub':  # len 3
        sub_len = 4
        idx = rng.integers(0, len(x) - sub_len)
        sub = x[idx: idx + sub_len]
        x[idx: idx + sub_len] = sub[::-1]
    else:
        raise NotImplementedError


def crossover(x, y, mode='erx'):
    """
    operator: ox2 - Order crossover 2, pmx - Partially mapped crossover, erx - Edge recombination crossover
    """
    child = np.zeros(len(x), dtype=np.int32)

    cut_1 = rng.integers(0, len(x) - 1)
    cut_2 = rng.integers(cut_1, len(x) + 1)

    child[cut_1: cut_2] = x[cut_1: cut_2]
    genes_in_child = set(x[cut_1: cut_2])

    if mode == 'ox2':
        idx_child = cut_2
        idx_y = cut_2
        while len(genes_in_child) != len(child):
            if idx_child >= len(child):
                idx_child = 0

            if idx_y >= len(y):
                idx_y = 0
            while y[idx_y] in genes_in_child:
                if idx_y >= len(y) - 1:
                    idx_y = 0
                else:
                    idx_y += 1

            child[idx_child] = y[idx_y]
            genes_in_child.add(y[idx_y])

            idx_child += 1

    elif mode == 'pmx':
        gene_map_x_to_y = dict(zip(x[cut_1: cut_2], y[cut_1: cut_2]))
        idx = cut_2
        while len(genes_in_child) != len(child):
            if idx >= len(child):
                idx = 0

            gene = y[idx]
            while gene in genes_in_child:
                # find gene idx in x and use it as map to y
                gene = gene_map_x_to_y[gene]

            child[idx] = gene
            genes_in_child.add(gene)

            idx += 1

    elif mode == 'erx':
        # generate neighb. list
        # x = first node from random parrent
        # while child isnt full
        #   append x to child
        #   remove x from neighb. list
        # if X neighb list is empty
        #   Z = random not in child
        # else
        #   Z = neighb. of X with fewest neighbs. (ties break at random)
        # X =Z
        genes_in_child = set()
        genes_not_in_child = set(x)
        neighbors = [set() for _ in range(len(x))]
        child = []

        for i in range(len(x)):
            left = (i - 1) % len(x)
            right = (i + 1) % len(x)
            neighbors[x[i]].add(x[left])
            neighbors[x[i]].add(x[right])
            neighbors[y[i]].add(y[left])
            neighbors[y[i]].add(y[right])

        gene = rng.integers(len(x))
        child.append(gene)
        genes_in_child.add(gene)
        genes_not_in_child.remove(gene)
        while len(genes_in_child) < len(x):

            for i in range(len(x)):
                neighbors[i].discard(gene)

            if len(neighbors[gene]) == 0:
                z = tuple(genes_not_in_child)[rng.integers(len(genes_not_in_child))]
            else:
                least_neighbors = np.inf
                z = np.nan
                for i in range(len(x)):
                    if i in genes_in_child:
                        continue
                    if len(neighbors[i]) < least_neighbors:
                        least_neighbors = len(neighbors[i])
                        z = i
            gene = z
            child.append(gene)
            genes_in_child.add(gene)
            genes_not_in_child.remove(gene)

        return np.array(child, dtype=np.int32)

    else:
        raise NotImplementedError

    return child




# the gain is (a, d) + (b, c) - (a, b) - (c, d)
# def opt_2(x):
#     idx1, idx2 = rng.integers(0, len(x), 2)
#     x_i1 = x[idx1]
#     x[idx1] = x[idx2]
#     x[idx2] = x_i1
#     return {0: idx2, 1: idx1}