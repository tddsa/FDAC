# coding:utf-8
import numpy as np
import networkx as nx
import matplotlib.pyplot as plt
from collections import defaultdict
from draw_comunity import draw_communities
from networkx.drawing.nx_agraph import graphviz_layout
import sqlite3
import json

def get_neigbors(g, node, depth=1):
    output = {}
    layers = dict(nx.bfs_successors(g, source=node, depth_limit=depth))
    nodes = [node]
    for i in range(1,depth+1):
        output[i] = []
        for x in nodes:
            output[i].extend(layers.get(x,[]))
        nodes = output[i]
    return output

def read_database(dbname, sql_sentence):
    db = sqlite3.connect(dbname)
    cursor = db.cursor()
    print("Opened database successfully")
    # cursor.execute("select source, target, weight, source_name, target_name from edge")  # 从edge表中读取边.
    cursor.execute(sql_sentence)  # 从edge表中读取边
    data = list(cursor.fetchall())  # edges = [(), ...]
    print("fetched data from database")
    # print(edges[:5])
    return data  # edges = [(), ...]
    
def get_n_hop_nodes(dbname, sql_sentence):
    edges_list = read_database(dbname=dbname, sql_sentence=sql_sentence)
    # edges_list = [("a", "b"), ("b", "c"), ("b", "d"), ("d", "e"), ("c", "e"), ("a", "f"), ("a", "g"), ("g", "f")]
    G = nx.Graph()
    G.add_edges_from(edges_list)
    # pos = nx.spring_layout(G)  # 布局为中心放射状
    node_id = "ad2284d6-dd1d-46cf-b8d9-3d50a672bf0e"
    output = get_neigbors(G, node_id, depth=2)
    return output

if __name__ == "__main__":
    dbname = "data/Citation_Visualization.db"
    sql_sentence_edge = "select source, target from edge"
    node_id_list = get_n_hop_nodes(dbname, sql_sentence_edge)
    sql_sentence_node = "select id, name, authors, public_venue, year, n_citation, reference, abstract, keywords from node"
    all_nodes = read_database(dbname, sql_sentence_node)
    all_edges = read_database(dbname, sql_sentence_edge)
    kernel_node_id = "ad2284d6-dd1d-46cf-b8d9-3d50a672bf0e"
    graph_data = {'nodes':[], 'links':[]}
    node_id_list = node_id_list[1] + node_id_list[2] + [kernel_node_id]
    for i in node_id_list:
        for j in all_nodes:
            if j[0] == i:
                node_now = {'id':j[0], 'name':j[1], 'authors':j[2], 'public_venue':j[3], 'year':j[4], 'n_citation':j[5], 'reference':j[6], 'abstract':j[7], 'keywords':j[8]}
                graph_data['nodes'].append(node_now)
                break

    for i in all_edges:
        if i[0] in node_id_list and i[1] in node_id_list:
            edge_now = {'source':i[0], 'target':i[1]}
            graph_data['links'].append(edge_now)

    json_graph_data = json.dumps(graph_data, indent=4, ensure_ascii=False)
    with open('data/Citation_Visualization.json' ,'w' ,encoding='utf-8') as f:
        f.write(json_graph_data)
        f.colse()