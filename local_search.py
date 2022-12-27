from function_tools import *


def local_search(model: 'Model', params):
    '''
    Local search with first improving strategy for binary representation.
    '''

    perturbation_operator = params["perturbation_operator"]
    initial_solution = params['initialize_solution_func'](params["solution_size"])

    model.bsf[0] = initial_solution
    model.bsf[1] = tsp_fitness(model.graph, initial_solution)
    model.stats.append([model.bsf[0], model.bsf[1], model.generation_count])

    # todo - remember perturbation, no need to copy, just reverse the perturbation.
    iterate = True
    while iterate:

        if params['verbose']:
            print('=', end='') if model.generation_count % (params['generations'] / 100) == 0 else ...

        for i in range(10):
            y = model.bsf[0].copy()
            perturbation_operator(y)

            fitness = tsp_fitness(model.graph, y)
            if fitness < model.bsf[1]:
                model.bsf[0] = y
                model.bsf[1] = tsp_fitness(model.graph, y)

                # todo: plot_solution(graph, coords, solution_best , fitness_best) if params['plot_solutions'] else ...
                model.stats.append([model.bsf[0], model.bsf[1], model.generation_count])
                break

        if model.generation_count > params['generations']:
            iterate = False
        else:
            model.generation_count += 1

    model.stats.append([model.bsf[0], model.bsf[1], model.generation_count])


def opt_2_best_improving(model: 'Model', params):
    """Iterative improvement based on 2 exchange.
    The opt makes no calls to the fitness, because int the improvement only two distances are compared"""
    tour = params['initialize_solution_func'](params["solution_size"])
    model.bsf[0] = tour.copy()
    model.bsf[1] = tsp_fitness(model.graph, tour)
    model.stats.append([model.bsf[0], model.bsf[1], model.generation_count])

    iterate = True
    while iterate:
        delta = 0

        if params['verbose']:
            print('=', end='') if model.generation_count % (params['generations'] / 100) == 0 else ...

        for (a, b) in all_segments_2(len(tour)):
            improved, d = reverse_segment_if_better_2_opt(tour, a, b, params['distances'])
            delta += d
            if improved:
                model.bsf[0] = tour.copy()
                model.bsf[1] = tsp_fitness(model.graph, tour)
                model.generation_count += 1
                model.stats.append([model.bsf[0], model.bsf[1], model.generation_count])

        if delta >= 0:
            iterate = False

    model.bsf[0] = tour.copy()
    model.bsf[1] = tsp_fitness(model.graph, tour)
    model.stats.append([model.bsf[0], model.bsf[1], model.generation_count])


def opt_3_best_improving(model: 'Model', params):
    """Iterative improvement based on 3 exchange."""
    tour = params['initialize_solution_func'](params["solution_size"])
    model.bsf[0] = tour.copy()
    model.bsf[1] = tsp_fitness(model.graph, tour)
    model.stats.append([model.bsf[0], model.bsf[1], model.generation_count])

    iterate = True
    while iterate:
        delta = 0

        if params['verbose']:
            print('=', end='') if model.generation_count % (params['generations'] / 100) == 0 else ...

        for (a, b, c) in all_segments_3(len(tour)):
            improved, d = reverse_segment_if_better_3_opt(tour, a, b, c, params['distances'])
            delta += d
            if improved:
                model.bsf[0] = tour.copy()
                model.bsf[1] = tsp_fitness(model.graph, tour)
                model.generation_count += 1
                model.stats.append([model.bsf[0], model.bsf[1], model.generation_count])

        if delta >= 0:
            iterate = False

    model.bsf[0] = tour.copy()
    model.bsf[1] = tsp_fitness(model.graph, tour)
    model.stats.append([model.bsf[0], model.bsf[1], model.generation_count])


def reverse_segment_if_better_2_opt(tour, i, j, distances):
    """If reversing tour[i:j] would make the tour shorter, then do it."""
    # Given tour [...A-B...C-D...]
    A, B, C, D, = tour[i - 1], tour[i], tour[j - 1], tour[j]
    d0 = distances[A, B] + distances[C, D]
    d1 = distances[A, C] + distances[B, D]

    if d0 > d1:
        tour[i:j] = list(reversed(tour[i:j]))
        return True, -d0 + d1
    return False, 0


def reverse_segment_if_better_3_opt(tour, i, j, k, distances):
    """If reversing tour[i:j] would make the tour shorter, then do it."""
    # Given tour [...A-B...C-D...E-F...]
    A, B, C, D, E, F = tour[i - 1], tour[i], tour[j - 1], tour[j], tour[k - 1], tour[k % len(tour)]
    d0 = distances[A, B] + distances[C, D] + distances[E, F]
    d1 = distances[A, C] + distances[B, D] + distances[E, F]
    d2 = distances[A, B] + distances[C, E] + distances[D, F]
    d3 = distances[A, D] + distances[E, B] + distances[C, F]
    d4 = distances[F, B] + distances[C, D] + distances[E, A]

    if d0 > d1:
        tour[i:j] = list(reversed(tour[i:j]))
        return True, -d0 + d1
    elif d0 > d2:
        tour[j:k] = list(reversed(tour[j:k]))
        return True, -d0 + d2
    elif d0 > d4:
        tour[i:k] = list(reversed(tour[i:k]))
        return True, -d0 + d4
    # elif d0 > d3:
    #     tmp = tour[j:k] + tour[i:j]
    #     tour[i:k] = tmp
    #     return True, -d0 + d3

    return False, 0


def all_segments_2(n: int):
    """Generate all segments combinations"""
    return ((i, j)
            for i in range(n)
            for j in range(i + 2, n))


def all_segments_3(n: int):
    """Generate all segments combinations"""
    return ((i, j, k)
            for i in range(n)
            for j in range(i + 2, n)
            for k in range(j + 2, n + (i > 0)))
