import pyqtgraph as pg
import numpy as np


def plot_graph_nodes(model: 'Model', widget):
    graph = model.graph
    coords = model.graph_coords
    for i in range(graph.dimension):
        widget.plot([coords[0, i]], [coords[1, i]], symbol='o', pen=pg.mkPen(width=0.1))
        t = pg.TextItem(str(i))
        t.setPos(coords[0, i], coords[1, i])
        widget.addItem(t)


def plot_solution(model: 'Model', solution, fitness, widget, lines):
    coords = model.graph_coords
    x = [coords[0, x] for x in solution]
    x.append(coords[0, 0])
    y = [coords[1, y] for y in solution]
    y.append(coords[1, 0])
    lines.setData(x, y)


# todo: x is generation count !!! not arange
def plot_fitness_graph(model, stats, lines):
    y = [stats[i][1] for i in range(len(stats))]
    x = [stats[i][2] for i in range(len(stats))]
    lines.setData(x, y)
