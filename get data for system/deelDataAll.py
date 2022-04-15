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

def getData(DBname, field, atrrVals):

    # deelDataForCitation.py

    dbname = "data/" + DBname + '.db'
    sql_sentence_edge = "select source, target from edge"
    # node_id_list = get_n_hop_nodes(dbname, sql_sentence_edge)
    sql_sentence_node = "select id, name, authors, public_venue, year, n_citation, reference, abstract, keywords from node"
    all_nodes = read_database(dbname, sql_sentence_node)
    all_edges = read_database(dbname, sql_sentence_edge)

    print('基于关键节点连通性样本的节点数：', len(all_nodes), '边数：', len(all_edges))
    # 统计keyword频数，转化为列表并排序
    keywords_frequence = {}
    for i in all_nodes:
        
        keyword = i[-1].split(';')
        for j in keyword:
            temp = j.lower()
            if temp in keywords_frequence:
                keywords_frequence[temp] += 1
            else:
                keywords_frequence[temp] = 1

    keywords_frequence_list = []
    for i in keywords_frequence:
        keyword_every_list = [keywords_frequence[i], i]
        keywords_frequence_list.append(keyword_every_list)

    # 选项列表
    keywords_frequence_list.sort(key=lambda x:-x[0])

    # 基于keyword筛选节点与边


    # keywords_most_list = keywords_frequence_list[0:10] #ten attribute
    # keywords_most_list = [i for _,i in keywords_most_list[::-1]]
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
    print('not_sample_nodes', len(not_sample_nodes))

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
        node = {'label':label, 'id':j[0], 'name':j[1], 'keywords':keyword_j, 'public_venue':j[3], 'year':j[4], 'n_citation':j[5]}
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
        node = {'label':label, 'id':j[0], 'name':j[1], 'keywords':keyword_j, 'public_venue':j[3], 'year':j[4], 'n_citation':j[5]}
        label += 1
        not_sample_nodes_all.append(node)
    
    print('sample_nodes_all', len(sample_nodes_all))
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
        if (i[0] in sample_nodes_all_list and i[1] in not_sample_nodes_all_list) or (i[1] in sample_nodes_all_list and i[0] in not_sample_nodes_all_list):
            not_community_edge = (i[0],i[1])
            not_detect_community.append(not_community_edge)
            edge = {'source': i[0], 'target': i[1]}
            not_sample_edges_all.append(edge)
    print('初步筛选出的边的数目', len(sample_edges_all))
    print('与其他属性有边的数目', len(not_sample_edges_all))
    # 提取最大子图
    import networkx as nx
    import matplotlib.pyplot as plt
    G = nx.Graph()
    G.add_edges_from(detect_community)
    pos = nx.spring_layout(G)  # 布局为中心放射状
    nx.draw(G, pos, node_color='#A0CBE2', width=4, with_labels=True)
    max_subgraph = max(nx.connected_components(G))

    nG = nx.Graph()
    nG.add_edges_from(detect_community+not_detect_community)
    npos = nx.spring_layout(nG)
    nx.draw(nG, npos, node_color='#A0CBE2', width=4, with_labels=True)
    not_max_subgraph = max(nx.connected_components(nG))
    print('最大子图中节点的数目', len(max_subgraph))
    print('带其他的最大子图中节点数目', len(not_max_subgraph))
    
    # 根据最大子图获取最终的点
    nodes_all = []
    not_nodes_all = []
    label = 0
    for j in sample_nodes_all:
        if j['id'] in max_subgraph:
            nodes_all.append(j)
    for j in (not_sample_nodes_all + sample_nodes_all):
        print(j)
        if j['id'] in not_max_subgraph:
            not_nodes_all.append(j)
    print('nodes number:', len(nodes_all))
    print('with other nodes number:', len(not_nodes_all))
    # 根据最大子图获取最终的边
    edges_all = []
    not_edges_all = []
    for j in sample_edges_all:
        if j['source'] in max_subgraph and j['target'] in max_subgraph:
            edges_all.append(j)
    for j in (sample_edges_all + not_sample_edges_all):
        if j['source'] in not_max_subgraph and j['target'] in not_max_subgraph:
            not_edges_all.append(j)
    print('edges number:', len(edges_all))
    print('with other edges number:', len(not_edges_all))

    # 节点与属性的映射
    node_map_attr = {}
    not_node_map_attr = {}
    for i in nodes_all:
        node_map_attr[i['id']] = i['keywords']
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

    # forcerate = 0
    # maxforce = 0
    for i in nodes_all:
        ID = i['id']
        attr = i['keywords']
        neigbors = get_neigbors(G, ID, depth=1)
        same, unsame = 1, 0
        for j in neigbors[1]:
            if node_map_attr[j] == attr:
                same += 1
            else:
                unsame += 1
        i['keywords'] = {'attribute':attr, 'same':same, 'unsame':unsame}
    #     maxforce = max(maxforce, unsame/same)
    #     forcerate += (unsame/same)
    # print('keyword邻接信息', forcerate/513, maxforce)
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
        # maxforce = max(maxforce, unsame/same)
        # forcerate += (unsame/same)
    # 处理期刊,年份和被引用次数 
    # public_venue, year, n_citation = {}, {}, {}
    # for i in nodes_all:
    #     if i['public_venue'] in public_venue:
    #         public_venue[i['public_venue']] += 1
    #     else:
    #         public_venue[i['public_venue']] = 1
    #     if i['year'] in year:
    #         year[i['year']] += 1
    #     else:
    #         year[i['year']] = 1
    #     if i['n_citation'] in n_citation:
    #         n_citation[i['n_citation']] += 1
    #     else:
    #         n_citation[i['n_citation']] = 1

    # # 期刊不用处理
    # # 处理年份 划分方式: <=1997 1998~2001 2002~2005 2006~2009 2010~2013 2014~2017
    # for i in nodes_all:
    #     temp = i['year']
    #     if temp <= '1997': i['year'] = {'attribute':'<=1997', 'actual':temp}
    #     elif temp <= '2001': i['year'] = {'attribute':'1998~2001', 'actual':temp}
    #     elif temp <= '2005': i['year'] = {'attribute':'2002~2005', 'actual':temp}
    #     elif temp <= '2009': i['year'] = {'attribute':'2006~2009', 'actual':temp}
    #     elif temp <= '2013': i['year'] = {'attribute':'2010~2013', 'actual':temp}
    #     elif temp <= '2017': i['year'] = {'attribute':'2014~2017', 'actual':temp}
    #     elif temp <= '2021': i['year'] = {'attribute':'2018~2021', 'actual':temp}

    # # 节点与属性的映射
    # node_map_attr = {}
    # for i in nodes_all:
    #     node_map_attr[i['id']] = i['year']['attribute']

    # forcerate = 0
    # maxforce = 0
    # for i in nodes_all:
    #     ID = i['id']
    #     attr = i['year']['attribute']
    #     neigbors = get_neigbors(G, ID, depth=1)
    #     same, unsame = 1, 0
    #     for j in neigbors[1]:
    #         if node_map_attr[j] == attr:
    #             same += 1
    #         else:
    #             unsame += 1
    #     i['year']['same'] = same
    #     i['year']['unsame'] = unsame
    #     maxforce = max(maxforce, unsame/same)
    #     forcerate += (unsame/same)
    # print('year邻接信息', forcerate/513, maxforce)

    # # 处理public_venue
    # node_map_attr = {}
    # for i in nodes_all:
    #     node_map_attr[i['id']] = i['public_venue']

    # forcerate = 0
    # maxforce = 0
    # for i in nodes_all:
    #     ID = i['id']
    #     attr = i['public_venue']
    #     neigbors = get_neigbors(G, ID, depth=1)
    #     same, unsame = 1, 0
    #     for j in neigbors[1]:
    #         if node_map_attr[j] == attr:
    #             same += 1
    #         else:
    #             unsame += 1
    #     i['public_venue'] = {'attribute':attr, 'same':same, 'unsame':unsame}
    #     maxforce = max(maxforce, unsame/same)
    #     forcerate += (unsame/same)
    # print('public_venue邻接信息', forcerate/513, maxforce)

    # # 处理n_citation 分级 >400 >200 >100 >50 >20 <=20
    # for i in nodes_all:
    #     temp = i['n_citation']
    #     if temp <= 20: i['n_citation'] = {'attribute':'<=20', 'actual':temp}
    #     elif temp <= 50: i['n_citation'] = {'attribute':'<=50', 'actual':temp}
    #     elif temp <= 100: i['n_citation'] = {'attribute': '<=100', 'actual':temp}
    #     elif temp <= 200: i['n_citation'] = {'attribute':'<=200', 'actual':temp}
    #     elif temp <= 400: i['n_citation'] = {'attribute':'<=400', 'actual':temp}
    #     elif temp > 400: i['n_citation'] = {'attribute':'>400', 'actual':temp}

    # # 节点与属性的映射
    # node_map_attr = {}
    # for i in nodes_all:
    #     node_map_attr[i['id']] = i['n_citation']['attribute']

    # forcerate = 0
    # maxforce = 0
    # for i in nodes_all:
    #     ID = i['id']
    #     attr = i['n_citation']['attribute']
    #     neigbors = get_neigbors(G, ID, depth=1)
    #     same, unsame = 1, 0
    #     for j in neigbors[1]:
    #         if node_map_attr[j] == attr:
    #             same += 1
    #         else:
    #             unsame += 1
    #     i['n_citation']['same'] = same
    #     i['n_citation']['unsame'] = unsame
    #     maxforce = max(maxforce, unsame/same)
    #     forcerate += (unsame/same)
    # print('n_citation邻接信息', forcerate/513, maxforce)

    # print(nodes_all[0])



    # save into json
    sample = {'nodes': nodes_all, 'links': edges_all}
    not_sample = {'nodes': not_nodes_all, 'links': not_edges_all}

    # 只包含选定的属性
    json_sample = json.dumps(sample, indent=4, ensure_ascii=False)
    # 除了包含选定的属性，还包含“other”属性
    not_json_sample = json.dumps(not_sample, indent=4, ensure_ascii=False) 
    with open('data/not_sample_keyword.json', 'w', encoding='utf-8') as f:
        f.write(not_json_sample)
        f.close()
    return not_json_sample

if __name__ == '__main__':
    getData('citation', 'keywords', ['graph drawing', 'information visualization', 'network visualization'])