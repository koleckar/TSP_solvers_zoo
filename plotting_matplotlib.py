import numpy as np

from matplotlib import pyplot as plt, transforms

plt.style.use('bmh')


def plot_graph_nodes(model: 'Model', axes):
    graph = model.graph
    coords = model.graph_coords
    for i in range(graph.dimension):
        axes.plot(coords[0, i], coords[1, i], 'o', mfc='none', markersize=3)
        axes.text(coords[0, i], coords[1, i], str(i), size=9)


def plot_solution(model: 'Model', canvas, axes):
    coords = model.graph_coords
    solution, fitness = model.bsf

    axes.cla()

    plot_graph_nodes(model, canvas, axes)

    for i in range(len(solution) - 1):
        u = solution[i]
        v = solution[i + 1]
        axes.plot([coords[0, u], coords[0, v]], [coords[1, u], coords[1, v]], 'g', linewidth=0.75)
    u = solution[-1]
    v = solution[0]
    axes.plot((coords[0, u], coords[0, v]), (coords[1, u], coords[1, v]), 'g', linewidth=0.75)
    canvas.super().super().draw_iddle()

    # figure.canvas.suptitle(model.graph.name + "    " + "fitness: " + str(fitness) +
    #                 "   opt:" + str(model.params_general["optimum"]))


def plot_stats(bsf, stats, time):
    plt.plot()
    interval_len = stats[0][2]
    plt.plot(np.arange(0, stats[0][2] + 1), [stats[0][1]] * (interval_len + 1), 'b-')
    plt.vlines(x=stats[0][2], ymin=stats[0][1], ymax=stats[1][1], color='b', linestyle='-')
    for i in range(1, len(stats) - 1):
        interval_len = stats[i + 1][2] - stats[i][2]
        plt.plot(np.arange(stats[i][2], stats[i + 1][2] + 1), [stats[i][1]] * (interval_len + 1), 'b-')
        plt.vlines(x=stats[i + 1][2], ymin=stats[i][1], ymax=stats[i + 1][1], color='b', linestyle='-')
    plt.title("minimum: " + str(bsf[1]) + "  time passed: " + str(time))
    plt.show()


# todo: optimum gap, fitness calls
def plot_stats_over_multiple_runs(stats_over_runs, f_min, params):
    fig = plt.figure()
    ax = fig.add_subplot()

    colors = ['tab:blue', 'tab:orange', 'tab:green', 'tab:red', 'tab:purple', 'tab:brown', 'tab:pink', 'tab:grey',
              'tab:olive', 'tab:cyan']
    times = []
    bsfs = []

    for k, stats_dic in enumerate(stats_over_runs):
        stats = stats_dic['stats']
        bsfs.append(stats_dic['bsf'][1])
        times.append(np.round(stats_dic['time'], 2))

        ax.plot(0, stats[0][1], '.', color=colors[k], markersize=5)

        interval_len = stats[0][2]
        ax.plot(np.arange(0, stats[0][2] + 1), [stats[0][1]] * (interval_len + 1), colors[k], linewidth=0.5)
        ax.vlines(x=stats[0][2], ymin=stats[0][1], ymax=stats[1][1], color=colors[k], linewidth=0.5)

        for i in range(1, len(stats) - 1):
            interval_len = stats[i + 1][2] - stats[i][2]
            ax.plot(np.arange(stats[i][2], stats[i + 1][2] + 1), [stats[i][1]] * (interval_len + 1),
                    color=colors[k], linewidth=0.5)
            ax.vlines(x=stats[i + 1][2], ymin=stats[i][1], ymax=stats[i + 1][1], color=colors[k], linewidth=0.5)

        interval_len = 200 - stats[-1][2]
        ax.plot(np.arange(stats[-1][2], 200), [stats[-1][1]] * interval_len, color=colors[k], linewidth=0.5)

    plt.axhline(params['optimum'], color='g', linestyle='-.', linewidth=0.7)
    ax.set_xlabel('fitness_evaluations')
    ax.set_ylabel('cost')

    trans = transforms.blended_transform_factory(
        ax.get_yticklabels()[0].get_transform(), ax.transData)
    ax.text(0, params['optimum'], "{:.0f}".format(params['optimum']), color="green", transform=trans,
            ha="right", va="center")

    info = ["f_min=" + str(f_min),
            "f_min_avg=" + str(np.average(bsfs)),
            "avg_time=" + str(np.round(np.average(times), 2)) + 's',
            "avg_opt_gap=" + str(np.round(get_avg_opt_gap(bsfs, params["optimum"]), 2)) + "%"]
    offset = -0.04
    for i, text in enumerate(info):
        ax.text(0.97, 0.97 + i * offset, text,
                verticalalignment='top', horizontalalignment='right',
                transform=ax.transAxes,
                color='black', fontsize=9)

    title = params["algorithm_name"] + "_" + params["dataset_name"]
    plt.title(title, fontsize=12)
    plt.savefig('plots/' + title + '.png')

    plt.show()


def get_avg_opt_gap(opts_over_runs, gold_opt):
    avg = 0

    for opt in opts_over_runs:
        avg += np.abs((opt - gold_opt) / gold_opt)

    avg *= 100
    return avg / len(opts_over_runs)

    # def plot_stats_over_multiple_runs(stats_over_runs, min, title, params):
    #     fig = plt.figure()
    #     ax = fig.add_subplot()
    #     # fig.subplots_adjust(top=0.85)
    #
    #     colors = ['tab:blue', 'tab:orange', 'tab:green', 'tab:red', 'tab:purple', 'tab:brown', 'tab:pink', 'tab:grey',
    #               'tab:olive', 'tab:cyan']
    #     times = []
    #     bsfs = []
    #
    #     for k, stats_dic in enumerate(stats_over_runs):
    #         stats = stats_dic['stats']
    #         bsfs.append(stats_dic['bsf'][1])
    #         times.append(np.round(stats_dic['time'], 2))
    #
    #         ax.plot(0, stats[0][1], '.', color=colors[k], markersize=5)
    #
    #         interval_len = stats[0][2]
    #         ax.plot(np.arange(0, stats[0][2] + 1), [stats[0][1]] * (interval_len + 1), colors[k], linewidth=0.5)
    #         ax.vlines(x=stats[0][2], ymin=stats[0][1], ymax=stats[1][1], color=colors[k], linewidth=0.5)
    #
    #         for i in range(1, len(stats) - 1):
    #             interval_len = stats[i + 1][2] - stats[i][2]
    #             ax.plot(np.arange(stats[i][2], stats[i + 1][2] + 1), [stats[i][1]] * (interval_len + 1),
    #                     color=colors[k], linewidth=0.5)
    #             ax.vlines(x=stats[i + 1][2], ymin=stats[i][1], ymax=stats[i + 1][1], color=colors[k], linewidth=0.5)
    #
    #         interval_len = 200 - stats[-1][2]
    #         ax.plot(np.arange(stats[-1][2], 200), [stats[-1][1]] * interval_len, color=colors[k], linewidth=0.5)
    #
    #     plt.axhline(params['optimum'], color='g', linestyle='-.', linewidth=0.7)
    #     ax.set_xlabel('generations')
    #     ax.set_ylabel('cost')
    #
    #     #todo:
    #     # hyperparams = ['offspring_size: ' + str(params['offspring_size']),
    #     #                'population_size: ' + str(params['population_size']),
    #     #                'parent_size: ' + str(params['parents_size']),
    #     #                'replacement_strategy: ' + str(params['replacement_strategy']),
    #     #                'parent_selection: ' + str(params['parent_selection']),
    #     #                'crossover: ' + str(params['crossover']),
    #     #                'mutation: ' + str(params['mutation']),
    #     #                'mutation_prob: ' + str(params['mutation_prob']),
    #     #                'optimum: ' + str(params["optimum"])]
    #     # offset = -0.04
    #     # for i, text in enumerate(hyperparams):
    #     #     ax.text(0.97, 0.97 + i * offset, text,
    #     #             verticalalignment='top', horizontalalignment='right',
    #     #             transform=ax.transAxes,
    #     #             color='black', fontsize=9)
    #
    #     plt.title(title + "    min=" + str(min) + '    avg_min= ' + str(np.average(bsfs)) + '    avg_time: ' +
    #               str(np.round(np.average(times), 2)) + ' s')
    #     # plt.savefig(title + '.png')
    #     plt.show()

    if __name__ == "__main__":
        ...
