# coding:utf-8
from collections import defaultdict

import matplotlib.pyplot as plt
import networkx as nx
import numpy as np
from communities.algorithms import girvan_newman
from fa2 import ForceAtlas2


# fixme: 测试ForceAtlas2
def test_force_layout():
    adj_matrix = np.array([[0, 1, 1, 0, 0, 0],
                           [1, 0, 1, 0, 0, 0],
                           [1, 1, 0, 1, 0, 1],
                           [0, 0, 1, 0, 1, 1],
                           [0, 0, 0, 1, 0, 1],
                           [0, 0, 1, 1, 1, 0]])
    # edge_list = [(0, 1), (0, 2), (1, 2), (2, 5), (2, 3), (3, 5), (3, 4), (4, 5)]
    G = nx.from_numpy_matrix(adj_matrix)
    # fixme: 使用spring算法
    # pos = nx.spring_layout(G)  #布局为中心放射状
    # fixme: 使用Gephi的内置算法ForceAtlas2
    forceatlas2 = ForceAtlas2(
        # Behavior alternatives
        outboundAttractionDistribution=True,  # Dissuade hubs
        linLogMode=False,  # NOT IMPLEMENTED
        adjustSizes=False,  # Prevent overlap (NOT IMPLEMENTED)
        edgeWeightInfluence=1.0,

        # Performance
        jitterTolerance=1.0,  # Tolerance
        barnesHutOptimize=True,
        barnesHutTheta=1.2,
        multiThreaded=False,  # NOT IMPLEMENTED

        # Tuning
        scalingRatio=2.0,
        strongGravityMode=False,
        gravity=1.0,

        # Log
        verbose=True)

    pos = forceatlas2.forceatlas2_networkx_layout(G, pos=None, iterations=2000)
    colors = range(20)
    nx.draw(G, pos, node_color='#A0CBE2',
            width=4, with_labels=True)
    plt.show()


# fixme: 测试超图怎么形成.
def test_hypergraph_build():
    adj_matrix = np.array([[0, 1, 1, 0, 0, 0],
                           [1, 0, 1, 0, 0, 0],
                           [1, 1, 0, 1, 0, 1],
                           [0, 0, 1, 0, 1, 1],
                           [0, 0, 0, 1, 0, 1],
                           [0, 0, 1, 1, 1, 0]])
    # edge_list = [(0, 1), (0, 2), (1, 2), (2, 5), (2, 3), (3, 5), (3, 4), (4, 5)]
    G = nx.from_numpy_matrix(adj_matrix)
    # fixme: 使用spring算法
    # pos = nx.spring_layout(G)  #布局为中心放射状
    # fixme: 使用Gephi的内置算法ForceAtlas2
    forceatlas2 = ForceAtlas2(
        # Behavior alternatives
        outboundAttractionDistribution=True,  # Dissuade hubs
        linLogMode=False,  # NOT IMPLEMENTED
        adjustSizes=False,  # Prevent overlap (NOT IMPLEMENTED)
        edgeWeightInfluence=1.0,

        # Performance
        jitterTolerance=1.0,  # Tolerance
        barnesHutOptimize=True,
        barnesHutTheta=1.2,
        multiThreaded=False,  # NOT IMPLEMENTED

        # Tuning
        scalingRatio=2.0,
        strongGravityMode=False,
        gravity=1.0,

        # Log
        verbose=True)

    pos = forceatlas2.forceatlas2_networkx_layout(G, pos=None, iterations=2000)  # pos={node1:(x, y), node2: (x, y), }
    print("pos")
    print(pos)
    nx.draw(G, pos, node_color='#A0CBE2', width=4, with_labels=True)
    plt.show()

    def _inter_community_edges(G, partition):
        """
        :param G:
        :param partition: [社区编号, ...]
        :return:
        """
        edges = defaultdict(list)  # {}

        for (i, j) in G.edges():  # (source, target)
            # print("i, j")
            # print(i, j)
            c_i = partition[i]  # source的社区编号
            c_j = partition[j]  # target的社区编号

            if c_i == c_j:
                continue

            edges[(c_i, c_j)].append((i, j))
        print("hyperedge")
        print(edges)
        return edges  # {(0, 1): [(2, 3), (2, 5)]}

    communities, _ = girvan_newman(adj_matrix=adj_matrix, n=2)  # [{0, 1, 2}, {3, 4, 5}]
    print("communities")
    print(communities)

    partition = [0 for _ in range(G.number_of_nodes())]  # [0, 0, 0, ..., 0]

    # 给图中每个节点打上所属的社区编号.
    for c_i, nodes in enumerate(communities):  # communities=[{0, 1, 4}, ..., {6, 9}], c_i: 社区的id
        for i in nodes:  # {0, 1, 4}
            partition[i] = c_i

    print("partition")
    print(partition)  # [0, 0, 0, 1, 1, 1]

    _inter_community_edges(G, partition)


# fixme: 边集输入构建图, 获得图中节点的索引,以及图的邻接矩阵.
def test_edges():
    edges_list = [("a", "b"), ("b", "c"), ("b", "d"), ("d", "e"), ("c", "e"), ("a", "f"), ("a", "g"), ("g", "f")]
    G = nx.Graph()
    G.add_edges_from(edges_list)
    # fixme: 节点索引列表
    nodes_list = list(G.nodes())  # e.g., ['g', 'e', 'c', 'd', 'b', 'f', 'a']
    print("nodes_list")
    print(nodes_list)
    subg = G.subgraph(["a", "b", "c"])
    print("list(subg.edges)")
    print(list(subg.edges))
    # fixme: 获得邻接矩阵
    adj_matrix = np.array(nx.adjacency_matrix(G).todense())
    print("adj_matrix")
    print(adj_matrix)
    # fixme: 社区检测
    communities, _ = girvan_newman(adj_matrix=adj_matrix, n=2)

    # fixme: 给图中每个节点打上所属的社区编号.
    partition = [0 for _ in range(G.number_of_nodes())]  # [0, 0, 0, ..., 0]
    for c_i, nodes in enumerate(communities):  # communities=[{0, 1, 4}, ..., {6, 9}], c_i: 社区的id
        for i in nodes:  # {0, 1, 4}
            partition[i] = c_i
    print("partition")
    print(partition)  # [0, 0, 0, 1, 1, 1]
    # fixme: 图布局
    pos = nx.spring_layout(G)  # 布局为中心放射状
    nx.draw(G, pos, node_color='#A0CBE2', width=4, with_labels=True)
    plt.show()
    # fixme: 构建字典{社区: 节点集, ...}
    community_nodes = defaultdict(list)  # {x: [], ...}
    for node_id, community_id in enumerate(partition):
        community_nodes[community_id].append(nodes_list[node_id])  # {社区0: [node1, node3, ...], 社区1: [node4, ...], ...}
    print("community_nodes")
    print(community_nodes)
    pos = dict()
    for c_i, nodes in community_nodes.items():  # c_i: 社区0, nodes: [node1, node3, ...]
        # fixme: 提取社区内节点构成的子图, 即社区结构.
        subgraph = G.subgraph(nodes)
        print("list(subgraph.edges)")
        print(list(subgraph.edges))
        # fixme: 对社区结构进行布局
        pos_subgraph = nx.spring_layout(subgraph, scale=2.0)
        pos.update(pos_subgraph)
    print("here pos")
    print(pos)


if __name__ == "__main__":
    # test_edges()
    # obj = {"a": [3, 4, 5], "b": [33, 44, 55]}
    # for c, nodes in obj.items():
    #     print(c, nodes)
    # communities, _ = girvan_newman(adj_matrix=adj_matrix, n=2)  # [{0, 1, 2}, {3, 4, 5}]
    # print("communities")
    # print(communities)
    # draw_communities(adj_matrix, communities)
    ss = "maotingyun.db"
    t = ss.split(".db")[0]
    print(t)


