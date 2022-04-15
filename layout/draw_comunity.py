# coding:utf-8
# Standard Library
import random
from collections import defaultdict
from copy import copy

# Third Party
import numpy as np
import networkx as nx
import matplotlib.pyplot as plt
from matplotlib.path import Path
from matplotlib.patches import PathPatch
from matplotlib import cm
from scipy.interpolate import splprep, splev
from scipy.spatial import ConvexHull, Delaunay


##################
# COMMUNITY LAYOUT
##################


def _inter_community_edges(G, partition):
    """
    遍历图中每条边, 如果边的节点的社区编号不同,则它隶属于编号所对应的超边.
    例如 边(node1, node2),其中node1属于社区0, node2属于社区1, 则改边属于超边(社区0, 社区1),
    放入字典中 {(社区0, 社区1): [(node1, node2), ...]}
    :param G:
    :param partition:
    :return:
    """
    edges = defaultdict(list)  # {x: [], ...}
    for (i, j) in G.edges():
        c_i = partition[i]
        c_j = partition[j]
        if c_i == c_j:
            continue
        edges[(c_i, c_j)].append((i, j))
    return edges


def _position_communities(G, partition, **kwargs):
    hypergraph = nx.Graph()  # 创建一个无向超图.
    # fixme: 超图的节点, 节点数量 == 社区数量
    hypergraph.add_nodes_from(set(partition))

    inter_community_edges = _inter_community_edges(G, partition)  # 社区直接的边,即超边. {(0, 1): [(3, 5), ...]}
    # fixme: 为超图构建边.
    for (c_i, c_j), edges in inter_community_edges.items():
        hypergraph.add_edge(c_i, c_j, weight=len(edges))  # 此时输入是无向图, 所以用的是边的数量作为权重, 如果是加权图则用总权重值.
    # fixme: 使用力引导算法布局超图.
    pos_communities = nx.spring_layout(hypergraph, **kwargs)  # {社区0: (x, y), ...}

    # Set node positions to positions of its community
    # fixme: 将原图中节点的位置初始化为社区的位置.
    pos = dict()
    for node, community in enumerate(partition):
        pos[node] = pos_communities[community]

    return pos  # {node1: (x,y), node2: (x,y), ...}


def _position_nodes(G, partition, **kwargs):
    """
    对每个社区内的子图进行布局
    :param G:
    :param partition:
    :param kwargs:
    :return: pos={node1: (x, y), node2: (x, y), ...}
    """
    communities = defaultdict(list)  # {x: [], ...}
    for node, community in enumerate(partition):
        communities[community].append(node)  # {社区0: [node1, node3, ...], 社区1: [node4, ...], ...}

    pos = dict()
    for c_i, nodes in communities.items():  # c_i: 社区0, nodes: [node1, node3, ...]
        # fixme: 提取社区内节点构成的子图, 即社区结构.
        subgraph = G.subgraph(nodes)
        # fixme: 对社区结构进行布局
        pos_subgraph = nx.spring_layout(subgraph, **kwargs)
        pos.update(pos_subgraph)

    return pos


# Adapted from: https://stackoverflow.com/questions/43541376/how-to-draw-communities-with-networkx
def community_layout(G, partition):
    # fixme: 原始图中节点的位置被初始化为社区位置. pos_communities = {node1: (x,y), node2: (x,y), ...}
    pos_communities = _position_communities(G, partition, scale=10.0)  # 先将社区视为一个节点, 形成一个超图, 布局社区节点的位置.
    # fixme: 对每个社区内的子图进行布局
    pos_nodes = _position_nodes(G, partition, scale=2.0)

    # Combine positions
    pos = dict()
    for node in G.nodes():
        pos[node] = pos_communities[node] + pos_nodes[node]  # fixme: 相当于将子图布局视图的中心平移到社区位置.

    return pos


#########
# PATCHES
#########


def _node_coordinates(nodes):
    collection = copy(nodes)
    collection.set_offset_position("data")
    return collection.get_offsets()


def _convex_hull_vertices(node_coordinates, community):
    points = np.array(node_coordinates[list(community)])
    hull = ConvexHull(points)

    x, y = points[hull.vertices, 0], points[hull.vertices, 1]
    vertices = np.column_stack((x, y))

    return vertices


# https://en.wikipedia.org/wiki/Shoelace_formula#Statement
def _convex_hull_area(vertices):
    A = 0.0
    for i in range(-1, vertices.shape[0] - 1):
        A += vertices[i][0] * (vertices[i + 1][1] - vertices[i - 1][1])

    return A / 2


# https://en.wikipedia.org/wiki/Centroid#Of_a_polygon
def _convex_hull_centroid(vertices):
    A = _convex_hull_area(vertices)

    c_x, c_y = 0.0, 0.0
    for i in range(vertices.shape[0]):
        x_i, y_i = vertices[i]
        if i == vertices.shape[0] - 1:
            x_i1, y_i1 = vertices[0]
        else:
            x_i1, y_i1 = vertices[i + 1]

        cross = ((x_i * y_i1) - (x_i1 * y_i))

        c_x += (x_i + x_i1) * cross
        c_y += (y_i + y_i1) * cross

    return c_x / (6 * A), c_y / (6 * A)


def _scale_convex_hull(vertices, offset):
    c_x, c_y = _convex_hull_centroid(vertices)
    for i, vertex in enumerate(vertices):
        v_x, v_y = vertex

        if v_x > c_x:
            vertices[i][0] += offset
        else:
            vertices[i][0] -= offset
        if v_y > c_y:
            vertices[i][1] += offset
        else:
            vertices[i][1] -= offset

    return vertices


def _community_patch(vertices):
    V = _scale_convex_hull(vertices, 1)  # TODO: Make offset dynamic
    tck, u = splprep(V.T, u=None, s=0.0, per=1)
    u_new = np.linspace(u.min(), u.max(), 1000)
    x_new, y_new = splev(u_new, tck, der=0)

    path = Path(np.column_stack((x_new, y_new)))
    patch = PathPatch(path, alpha=0.50, linewidth=0.0)
    return patch


def draw_community_patches(nodes, communities, axes):
    node_coordinates = _node_coordinates(nodes)
    vertex_sets = []
    for c_i, community in enumerate(communities):
        vertices = _convex_hull_vertices(node_coordinates, community)
        patch = _community_patch(vertices)
        patch.set_facecolor(nodes.to_rgba(c_i))

        axes.add_patch(patch)
        vertex_sets.append(patch.get_path().vertices)

    _vertices = np.concatenate(vertex_sets)
    xlim = [_vertices[:, 0].min(), _vertices[:, 0].max()]
    ylim = [_vertices[:, 1].min(), _vertices[: ,1].max()]

    axes.set_xlim(xlim)
    axes.set_ylim(ylim)


##################
# DRAW COMMUNITIES
##################


def draw_communities(adj_matrix, communities, dark=False, filename=None, dpi=None, seed=1):
    """
    :param adj_matrix: [[], ...]
    :param communities: [{0, 1, 4}, ...]
    :param dark:
    :param filename:
    :param dpi:
    :param seed:
    :return:
    """
    np.random.seed(seed)
    random.seed(seed)

    G = nx.from_numpy_matrix(adj_matrix)  # 邻接矩阵转化成图
    partition = [0 for _ in range(G.number_of_nodes())]  # [0, 0, 0, ..., 0]
    # 给图中每个节点打上所属的社区编号.
    for c_i, nodes in enumerate(communities):  # communities=[{0, 1, 4}, ..., {6, 9}], c_i: 社区的id
        for i in nodes:  # {0, 1, 4}
            partition[i] = c_i
    plt.rcParams["figure.facecolor"] = "black" if dark else "white"
    plt.rcParams["axes.facecolor"] = "black" if dark else "white"

    fig, ax = plt.subplots(figsize=(8, 6))
    ax.axis("off")

    node_size = 10200 / G.number_of_nodes()
    linewidths = 34 / G.number_of_nodes()

    pos = community_layout(G, partition)
    nodes = nx.draw_networkx_nodes(
        G,
        pos=pos,  # 这个是布局出来的结果, 例如 nodes = nx.draw_networkx_nodes(G, pos=nx.spring_layout(G))
        node_color=partition,
        linewidths=linewidths,
        cmap=cm.jet,
        ax=ax
    )
    nodes.set_edgecolor("w")
    # edges = nx.draw_networkx_edges(
    #     G,
    #     pos=pos,
    #     edge_color=(1.0, 1.0, 1.0, 0.75) if dark else (0.6, 0.6, 0.6, 1.0),
    #     width=linewidths,
    #     ax=ax
    # )
    draw_community_patches(nodes, communities, ax)

    if not filename:
        plt.show()
    else:
        plt.savefig(filename, dpi=dpi)

    return ax
