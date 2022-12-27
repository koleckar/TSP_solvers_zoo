import time
import os

from plotting_matplotlib import *

rng = np.random.default_rng()


def rank(permutation):
    ...


# Debugging only.
def create_random_tsp_instance(n):
    graph = np.triu(rng.integers(10, 100, [n, n]))
    graph += graph.T
    graph[np.eye(n) == 1] = 0
    return graph


def initialize_solution_permutation(solution_size):
    return rng.permutation(np.arange(solution_size))


def initialize_population(graph, initialize_solution, population_size, solution_size, mode='random'):
    population = np.zeros([population_size, solution_size], dtype=np.int32)

    if mode == 'random':
        for i in range(population_size):
            population[i, :] = initialize_solution(solution_size)

    elif mode == 'random_search':
        tries = 10 ** 3
        for i in range(population_size):
            nodes = np.arange(solution_size)
            bsf = [np.inf, np.zeros(solution_size)]
            for _ in range(tries):
                new_sol = rng.permutation(nodes)
                fitness = tsp_fitness(graph, new_sol)
                if fitness < bsf[0]:
                    bsf = [fitness, new_sol]
            print('seed', i, ' found, fit: ', bsf[0])
            population[i, :] = bsf[1]

    elif mode == 'informed':
        raise NotImplementedError

    else:
        raise NotImplementedError

    return population


def nearest_neighbour_search(start, distances, params):
    n = params["solution_size"]
    visited = np.zeros(n, dtype=bool)

    visited[start] = True
    tour = [start]
    cost = 0
    for _ in range(1, n):
        prev = tour[-1]
        min_dist = np.inf
        min_id = np.nan
        for j in range(n):
            if prev == j or visited[j]:
                continue
            dist = distances[prev, j]
            if dist < min_dist:
                min_dist = dist
                min_id = j

        if min_id is np.nan:
            assert min_id is not np.nan, "min not assigned correctly."
        visited[min_id] = True
        tour.append(min_id)
        cost += min_dist

    cost += distances[tour[-1], tour[0]]
    return tour, cost


def tsp_fitness(graph, solution):
    cost = 0
    mode = graph.edge_weight_type
    offset = 1 if mode == 'EUC_2D' else 0  # TSPLIB_95 EUC_2D Graph for some reason indexed from 1.
    for i in range(len(solution) - 1):
        u = solution[i]
        v = solution[i + 1]
        cost += graph.get_weight(u + offset, v + offset)
    u = solution[-1]
    v = solution[0]
    cost += graph.get_weight(u + offset, v + offset)

    return cost


def evaluate_specimen(graph, specimen):
    size = specimen.shape[0]
    fitness = np.zeros(size)
    for i in range(size):
        fitness[i] = tsp_fitness(graph, specimen[i, :])
    return fitness


def get_distances(graph):
    n = graph.dimension
    dists = np.zeros([n, n])

    offset = 1 if graph.edge_weight_type == 'EUC_2D' else 0  # due to indexing bug in tsplib!

    for i in range(n):
        for j in range(i, n):
            if i == j:
                continue
            w = graph.get_weight(i + offset, j + offset)
            dists[i, j] = w
            dists[j, i] = w

    return dists


def get_coordinates_for_plotting(graph):
    coords = np.zeros([2, graph.dimension])

    if graph.edge_weight_type == 'EUC_2D':
        for i in range(graph.dimension):
            coords[0, i] = graph.node_coords[i + 1][0]
            coords[1, i] = graph.node_coords[i + 1][1]
    elif graph.edge_weight_type == 'EXPLICIT':
        r = 1
        for i in range(graph.dimension):
            t = i * (2 * np.pi / graph.dimension)
            coords[0, i] = r * np.cos(t)
            coords[1, i] = r * np.sin(t)

    return coords


def assert_params(params):
    assert params['population_size'] >= params['parents_size']


def collect_statistics(model: 'Model'):
    algorithm = model.params_general["algorithm"]
    params = {**model.params_general}
    params.update(model.params_ea) if model.algorithm_name is "ea" else params.update(model.params_ls)

    min_fit = np.inf
    for model.actual_run in range(model.params_general['runs']):
        model.generation_count = 0
        model.stats_over_runs.append({'bsf': model.bsf, 'stats': model.stats, 'time': 0})

        print('\n', params["dataset_name"], ' run:', model.actual_run, '  ', end='')

        time_start = time.time()
        algorithm(model, params)
        time_end = time.time()
        model.stats_over_runs[model.actual_run]["time"] = time_end - time_start

        if min_fit > model.bsf[1]:
            min_fit = model.bsf[1]
        model.stats = []

    print("\nplotting runs...")
    plot_stats_over_multiple_runs(model.stats_over_runs, min_fit, params)
    print("Done.")


def collect_statistics_for_all_data(model):
    for model.dataset_name in os.listdir('data'):
        model.update_chosen_dataset()
        model.stats_over_runs = []
        collect_statistics(model)
