from function_tools import *
from plotting_matplotlib import *
from operators import *


# TODO: some other terminating criterion than generations?
def evolutionary_algorithm(model: 'Model', params):
    # initialize population
    # evaluate population
    # update BSF
    # while not terminated
    # breed : select parents, crossover, mutate

    graph = model.graph
    coords = model.graph_coords
    model.generation_count = 1

    population = initialize_population(graph, params['initialize_solution_func'],
                                       params['population_size'], params['solution_size'], mode='random')

    population_fitness = evaluate_specimen(graph, population)

    model.bsf[0] = population[np.argmin(population_fitness), :]
    model.bsf[1] = np.min(population_fitness)

    plot_solution(graph, coords, model.bsf[0], model.bsf[1], params['plot_ax']) if params['plot_solutions'] else ...

    model.stats.append([model.bsf[0], model.bsf[1], model.generation_count])

    iterate = True
    while iterate:

        if params['verbose']:

            if (model.generation_count - 1) % (params['generations'] / 10) == 0:
                print('=', end='')

        offspring = breed(population, population_fitness, params)

        offspring_fitness = evaluate_specimen(graph, offspring)

        population = replacement_strategy(population, offspring, population_fitness, offspring_fitness,
                                          params['population_size'], params['replacement_strategy'])

        if tsp_fitness(graph, population[0, :]) < model.bsf[1]:
            model.bsf[0] = population[0, :]
            model.bsf[1] = tsp_fitness(graph, population[0, :])
            # print("updating bsf: " + str(model.bsf[1]))

            # plot_solution(graph, coords, model.bsf[0], model.bsf[1], params['plot_ax']) if params['plot_solutions'] \
            #     else ...
            model.stats.append([model.bsf[0],
                                model.bsf[1],
                                model.generation_count * (
                                        model.params_ea["population_size"] + model.params_ea["offspring_size"])
                                ])

        # Todo: not generations but fitness evals.
        if model.generation_count > params['generations']:
            iterate = False
        else:
            model.generation_count += 1

    model.stats.append([model.bsf[0],
                        model.bsf[1],
                        model.generation_count * (model.params_ea["population_size"] + model.params_ea["offspring_size"])
                        ])


# TODO: tournament_size as kwargs
def parent_selection(population_fitness, parents_size, mode='tournament', **kwargs):
    if mode == 'tournament':
        parent_idcs = np.zeros(parents_size, dtype=np.int32)

        tournament_size = 10
        prob = 0.5
        tmp = np.arange(0, tournament_size)
        probs = prob * (1 - prob) ** np.arange(0, tournament_size)
        probs /= np.sum(probs)  # normalize to sum up to 1.

        for i in range(parents_size):
            in_tournament_idcs = rng.integers(0, len(population_fitness), tournament_size)
            sorted_by_fitness = np.argsort(population_fitness[in_tournament_idcs])
            parent_idcs[i] = rng.choice(sorted_by_fitness, p=probs)

        return parent_idcs

    elif mode == 'truncation':
        assert parents_size <= len(population_fitness)
        return np.argsort(population_fitness)[0: parents_size]

    elif mode == 'rank':
        raise NotImplementedError

    else:
        raise NotImplementedError


# TODO: always one children?
# TODO: one mating strategy?
def breed(population, population_fitness, params):
    offspring = np.zeros([params['offspring_size'], params['solution_size']], dtype=np.int32)

    parent_idcs = parent_selection(population_fitness, params['parents_size'],
                                   params['parent_selection'])  # TODO: kwargs operator
    mate_idcs = rng.permutation(parent_idcs)
    i = 0
    j = 0
    offsprings_created = 0
    mate = True
    while mate:
        if offsprings_created >= params['offspring_size']:
            mate = False
            continue

        if i >= len(mate_idcs) - 1:
            mate_idcs = rng.permutation(parent_idcs)
            i = 0

        if mate_idcs[i] != mate_idcs[i + 1]:
            x = population[mate_idcs[i], :]
            y = population[mate_idcs[i + 1], :]
            offspring[j, :] = crossover(x, y, params['crossover'])
        else:
            offspring[j, :] = population[mate_idcs[i], :]

        offsprings_created += 1
        i += 1
        j += 1

    for i in range(params['offspring_size']):
        if rng.random() > params['mutation_prob']:
            mutate(offspring[i, :], params['mutation'])

    return offspring


# TODO: have some elder decay, or momentum, increasing number of offspring to parents ratio ?
def replacement_strategy(population, offspring, population_fitness, offspring_fitness, population_size,
                         mode='generational'):
    if mode == 'generational':
        assert len(offspring_fitness) >= population_size
        return offspring[np.argsort(offspring_fitness)[0: population_size]]

    elif mode == 'steady_state_truncation':
        population_survivors = 0.5 * population_size
        offspring_survivors = 0.5 * population_size
        if population_survivors + offspring_survivors != population_size:
            population_survivors += population_size - (population_survivors + offspring_survivors)

        survivor_idcs_population = np.argsort(population_fitness)[0: population_survivors]
        survivor_idcs_offspring = np.argsort(offspring_fitness)[0: offspring_survivors]

        return np.vstack([population[survivor_idcs_population], offspring[survivor_idcs_offspring]])

    else:
        raise NotImplementedError
