import tsplib95
from tsplib95 import distances

from function_tools import *
from evolutionary_algorithm import evolutionary_algorithm
from local_search import local_search, opt_2_best_improving, opt_3_best_improving
from operators import *


class Model:
    def __init__(self, dataset_name="gr17.tsp", algorithm_name="opt-2"):
        self.dataset_name = dataset_name
        self.algorithm_name = algorithm_name

        self.graph = tsplib95.load("data/" + dataset_name)
        self.graph_coords = get_coordinates_for_plotting(self.graph)

        self.params_general = {}
        self.params_ea = {}
        self.params_ls = {}


        self.available_algorithms = {"ea": evolutionary_algorithm,
                                     "ls": local_search,
                                     "opt-2": opt_2_best_improving,
                                     "opt-3": opt_3_best_improving
                                     }

        self.optimums = {"gr17.tsp": 2085, "gr21.tsp": 2707, "gr24.tsp": 1272, "gr48.tsp": 5046,
                         "hk48.tsp": 11461,
                         "si175.tsp": 21407, "si535.tsp": 48450, "si1032.tsp": 92650,
                         "swiss42.tsp": 1273,
                         "berlin52.tsp": 7542,
                         "a280.tsp": 2579}

        self.create_params()

        self.bsf = [np.nan, np.nan]
        self.stats = []
        self.stats_over_runs = []
        self.actual_run = 0
        self.generation_count = 0

    def update_chosen_dataset(self):
        print("Loading dataset " + self.dataset_name) if self.params_general["verbose"] else ...
        self.graph = tsplib95.load("data/" + self.dataset_name)
        print(self.dataset_name + " loaded.") if self.params_general["verbose"] else ...

        self.graph_coords = get_coordinates_for_plotting(self.graph)
        self.params_general['dataset_name'] = self.dataset_name
        self.params_general['optimum'] = self.optimums[self.dataset_name]
        self.params_general['solution_size'] = self.graph.dimension

        self.params_ls['distances'] = get_distances(self.graph)

    # todo change generations to fitness calls and keep call counter.

    def create_params(self):
        self.params_general = {'algorithm': self.available_algorithms[self.algorithm_name],
                               'algorithm_name': self.algorithm_name,
                               'generations': 200,
                               'solution_size': self.graph.dimension,
                               'runs': 10,
                               'dataset_name': self.dataset_name,
                               'optimum': self.optimums[self.dataset_name],
                               'plot_solutions': False,
                               'verbose': True,
                               'save_result_plot': True,
                               'save_results_file_name': self.dataset_name + "_" + self.algorithm_name}

        self.params_ea = {'population_size': 40,
                          'offspring_size': 120,
                          'parents_size': 30,
                          'initialize_solution_func': initialize_solution_permutation,
                          'replacement_strategy': "generational",
                          'parent_selection': "tournament",
                          'crossover': "pmx",
                          'mutation': "swap2",
                          'mutation_prob': 0.45,
                          }

        self.params_ls = {'initialize_solution_func': initialize_solution_permutation,
                          'perturbation_operator': mutate,
                          'distances': get_distances(self.graph),
                          'ls_stype': opt_2_best_improving,
                          }

        assert_params({**self.params_general, **self.params_ea, **self.params_ls})

    def run_model(self):
        collect_statistics(self)
        # collect_statistics_for_all_data(self)


if __name__ == '__main__':
    model = Model("si175.tsp", "opt-2")
    model.run_model()
    # get_statistics(params, graph, params["algorithm"])




    # def main(self):
    #     ...
    # dists = get_distances(graph)
    # tours = []
    # costs = []
    # for i in range(graph.dimension):
    #     tour, cost = nearest_neighbour_search(i, dists, params)
    #     tours.append(tour)
    #     costs.append(cost)
    #
    # best_nn_tour_idx = np.argmin(costs)
    # best_nn_tour = tours[best_nn_tour_idx]
    # best_nn_cost = costs[best_nn_tour_idx]
    #
    # plot_solution(graph, get_coordinates_for_plotting(graph), best_nn_tour, best_nn_cost, params)
