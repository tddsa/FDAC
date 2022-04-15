# coding:utf-8
import numpy as np
import networkx as nx
import matplotlib.pyplot as plt
from collections import defaultdict
# from draw_comunity import draw_communities
from networkx.drawing.nx_agraph import graphviz_layout
import sqlite3
import json

def read_database(dbname, sql_sentence):
    db = sqlite3.connect(dbname)
    cursor = db.cursor()
    # print("Opened database successfully")
    # cursor.execute("select source, target, weight, source_name, target_name from edge")  # 从edge表中读取边.
    cursor.execute(sql_sentence)  # 从edge表中读取边
    data = list(cursor.fetchall())  # edges = [(), ...]
    # print("fetched data from database")
    # print(edges[:5])
    return data  # edges = [(), ...]

def getdatakeywords(DBname, atrrVals):

    # deelDataForCitation.py

    dbname = DBname
    sql_sentence_edge = "select source, target from edge"
    # node_id_list = get_n_hop_nodes(dbname, sql_sentence_edge)
    sql_sentence_node = "select id, name, authors, public_venue, year, n_citation, reference, abstract, keywords from node"
    all_nodes = read_database(dbname, sql_sentence_node)
    all_edges = read_database(dbname, sql_sentence_edge)

    print('数据库中所有样本的节点数：', len(all_nodes), '边数：', len(all_edges))
    keywords_most_list = atrrVals

    sample_nodes = []
    for i in keywords_most_list:
        for j in all_nodes:
            if j in sample_nodes:
                continue
            keyword = j[-1].lower()
            keyword = keyword.split(';')
            if i in keyword:
                sample_nodes.append(j)
    
    not_sample_nodes = []
    for i in all_nodes:
        if i not in sample_nodes:
            not_sample_nodes.append(i)

    print('sample_nodes', len(sample_nodes))
    print('all_sample_nodes', len(not_sample_nodes)+len(sample_nodes))

    sample_nodes_all = []
    label = 0
    for j in sample_nodes:
        keyword = j[-1].lower()
        keyword = keyword.split(';')
        keyword_j = ''
        for i in keywords_most_list:
            if i in keyword:
                if keyword_j == '':
                    keyword_j += i
                else:
                    keyword_j += '+' + i
        # 过滤掉期刊与keyword相同的节点
        if j[3] in keyword or j[1] in keyword:
            # print(j)
            continue
        node = {'label':label, 'id':j[0], 'name':j[1], 'keywords':keyword_j}
        label += 1
        sample_nodes_all.append(node)
    
    not_sample_nodes_all = []
    for j in not_sample_nodes:
        keyword_j = 'other'
        # 过滤掉期刊与keyword相同的节点
        # print(j)
        if j[3] in keyword and j[1] in keyword:
            # print(j)
            continue
        node = {'label':label, 'id':j[0], 'name':j[1], 'keywords':keyword_j}
        label += 1
        not_sample_nodes_all.append(node)
    
    print('not_sample_nodes_all', len(not_sample_nodes_all))

    # 初步筛选边
    sample_nodes_all_list = [i['id'] for i in sample_nodes_all]
    sample_edges_all = []
    detect_community = []

    for i in all_edges:
        if i[0] in sample_nodes_all_list and i[1] in sample_nodes_all_list:
            community_edge = (i[0],i[1])
            detect_community.append(community_edge)
            edge = {'source': i[0], 'target': i[1]}
            sample_edges_all.append(edge)
    
    not_sample_nodes_all_list = [i['id'] for i in not_sample_nodes_all]
    not_sample_edges_all = []
    not_detect_community = []
    for i in all_edges:
        if (i[0] in sample_nodes_all_list and i[1] in not_sample_nodes_all_list):
            not_community_edge = (i[0],'other')
            not_detect_community.append(not_community_edge)
            edge = {'source': i[0], 'target': i[1]}
            not_sample_edges_all.append(edge)
        elif (i[1] in sample_nodes_all_list and i[0] in not_sample_nodes_all_list):
            not_community_edge = (i[1],'other')
            not_detect_community.append(not_community_edge)
            edge = {'source': i[0], 'target': i[1]}
            not_sample_edges_all.append(edge)
    print('与"其他"属性有边的数目', len(not_sample_edges_all), '属性内部边的数目', len(sample_edges_all))
    # 提取最大子图
    import networkx as nx
    import matplotlib.pyplot as plt

    nG = nx.Graph()
    nG.add_edges_from(detect_community+not_detect_community)
    npos = nx.spring_layout(nG)
    nx.draw(nG, npos, node_color='#A0CBE2', width=4, with_labels=True)
    not_max_subgraph = max(nx.connected_components(nG))
    print('带"其他"的最大子图中节点数目', len(not_max_subgraph))
    
    # 根据最大子图获取最终的点
    not_nodes_all = []
    for j in (not_sample_nodes_all + sample_nodes_all):
        if j['id'] in not_max_subgraph:
            not_nodes_all.append(j)
    other = {'label': -1, 'id': 'other', 'name': 'other', 'keywords':'other'}
    not_nodes_all.append(other)
    print('with other nodes number:', len(not_nodes_all))
    # 根据最大子图获取最终的边
    not_edges_all = []
    for j in (sample_edges_all + not_sample_edges_all):
        if j['source'] in not_max_subgraph and j['target'] in not_max_subgraph:
            not_edges_all.append(j)
    print('with other edges number:', len(not_edges_all))

    # 节点与属性的映射
    not_node_map_attr = {}
    for i in not_nodes_all:
        not_node_map_attr[i['id']] = i['keywords']
    # 统计基于关键词的节点邻居的信息 图为G
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
    
    for i in not_nodes_all:
        ID = i['id']
        attr = i['keywords']
        neigbors = get_neigbors(nG, ID, depth=1)
        same, unsame = 1, 0
        for j in neigbors[1]:
            if not_node_map_attr[j] == attr:
                same += 1
            else:
                unsame += 1
        i['keywords'] = {'attribute':attr, 'same':same, 'unsame':unsame}
        
    not_sample = {'nodes': not_nodes_all, 'links': not_edges_all}

    # 除了包含选定的属性，还包含“other”属性
    not_json_sample = json.dumps(not_sample, indent=4, ensure_ascii=False) 
    with open('data/not_sample_keyword.json', 'w', encoding='utf-8') as f:
        f.write(not_json_sample)
        f.close()
    return not_json_sample

def getData(DBname, field, atrrVals):
    if 'citation' in DBname:
        if 'keywords' in field:
            return getdatakeywords(DBname, atrrVals)