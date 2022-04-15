# coding:utf-8
import numpy as np
import networkx as nx
import matplotlib.pyplot as plt
from collections import defaultdict
# from draw_comunity import draw_communities
from networkx.drawing.nx_agraph import graphviz_layout
import sqlite3
import json
import os

def read_database(dbname, sql_sentence):
    db = sqlite3.connect(dbname)
    cursor = db.cursor()
    cursor.execute(sql_sentence)  # 从edge表中读取边
    data = list(cursor.fetchall())  # edges = [(), ...]
    return data  # edges = [(), ...]



def getGraph_With_Other(DBname, ID, hop, field, atrrVals, fieldNum, other):
    db = DBname.split('/')[1].split('.')[0]
    if not other:
        otherLabel = '0'
    else:
        otherLabel = '1'
    
    fileName = db + '_' + ID + '_' + str(hop) + '_' + field +  '_' + str(atrrVals) + '_' + otherLabel + '.json'
    filePath = 'data/' + fileName
    if os.path.exists(filePath):
        with open(filePath ,'r' ,encoding='utf-8') as f:
            json_graph = f.read()
            f.close()
    else:
        dataName = db + '_' + ID + '_' + str(hop) + '.json'
        dataPath = 'dataSet/' + dataName
        with open(dataPath ,'r' ,encoding='utf-8') as f:
            json_graph_data = f.read()
            f.close()
        graph = json.loads(json_graph_data)

        print('数据库中所有样本的节点数：', len(graph['nodes']), '边数：', len(graph['links']))
        keywords_most_list = atrrVals
        if fieldNum:
            keywords_map_dict = {}
            for i in atrrVals:
                keywords_map_dict[i] = str(i[0]) + '~' + str(i[1])
        
        # 初步获取节点
        sample_nodes = []
        for i in keywords_most_list:
            for j in graph['nodes']:
                if j in sample_nodes:
                    continue
                if fieldNum:
                    keyword = j[field]
                    if keyword >= i[0] and keyword < i[1]:
                        sample_nodes.append(j)
                else:
                    keyword = j[field].lower()
                    keyword = keyword.split(';')
                    if i in keyword:
                        sample_nodes.append(j)
        
        not_sample_nodes = []
        for i in graph['nodes']:
            if i not in sample_nodes:
                not_sample_nodes.append(i)
        print('sample_nodes', len(sample_nodes), 'other_nodes', len(not_sample_nodes))

        # 给所有节点贴标签
        sample_nodes_all = []
        label = 0
        for j in sample_nodes:
            if fieldNum:
                keyword = j[field]
                keyword_j = ''
                for i in keywords_most_list:
                    if keyword >= i[0] and keyword < i[1]:
                        keyword_j = keywords_map_dict[i]
            else:                
                keyword = j[field].lower()
                keyword = keyword.split(';')
                keyword_j = ''
                for i in keywords_most_list:
                    if i in keyword:
                        if keyword_j == '':
                            keyword_j += i
                        else:
                            keyword_j += '+' + i

            node = {'label':label, 'id':j['id'], 'name':j['name'], field:keyword_j, 'actual':keyword}
            label += 1
            sample_nodes_all.append(node)
        
        not_sample_nodes_all = []
        for j in not_sample_nodes:
            if fieldNum:
                keyword = j[field]
            else:
                keyword = j[field].lower()
                keyword = keyword.split(';')
            keyword_j = 'other'
            node = {'label':label, 'id':j['id'], 'name':j['name'], field:keyword_j, 'actual':keyword}
            label += 1
            not_sample_nodes_all.append(node)
        
        print('sample_nodes_all', len(sample_nodes_all), 'not_sample_nodes_all', len(not_sample_nodes_all))

        # 初步筛选边
        sample_nodes_all_list = [i['id'] for i in sample_nodes_all]
        sample_edges_all = []
        detect_community = []

        for i in graph['links']:
            if i['source'] in sample_nodes_all_list and i['target'] in sample_nodes_all_list:
                community_edge = (i['source'],i['target'])
                detect_community.append(community_edge)
                edge = {'source': i['source'], 'target': i['target']}
                sample_edges_all.append(edge)
        
        not_sample_nodes_all_list = [i['id'] for i in not_sample_nodes_all]
        not_sample_edges_all = []
        not_detect_community = []
        for i in graph['links']:
            if (i['source'] in sample_nodes_all_list and i['target'] in not_sample_nodes_all_list):
                not_community_edge = (i['source'],'other')
                if not_community_edge not in not_detect_community:
                    not_detect_community.append(not_community_edge)
                edge = {'source': i['source'], 'target': 'other'}
                if edge not in not_sample_edges_all:
                    not_sample_edges_all.append(edge)
            elif (i['target'] in sample_nodes_all_list and i['source'] in not_sample_nodes_all_list):
                not_community_edge = (i['target'],'other')
                if not_community_edge not in not_detect_community:
                    not_detect_community.append(not_community_edge)
                edge = {'source': i['target'], 'target': 'other'}
                if edge not in not_sample_edges_all:
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
        other = {'label': -1, 'id': 'other', 'name': 'other', field:'other',  'actual':'other'}
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
        for i in (not_nodes_all):
            not_node_map_attr[i['id']] = i[field]
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
        
        for i in (not_nodes_all):
            ID = i['id']
            attr = i[field]
            actual  = i['actual']
            neigbors = get_neigbors(nG, ID, depth=1)
            same, unsame = 1, 0
            for j in neigbors[1]:
                if not_node_map_attr[j] == attr:
                    same += 1
                else:
                    unsame += 1
            i[field] = {'attribute':attr, 'actual':actual, 'same':same, 'unsame':unsame}
            del i['actual']
        
        sample = {'nodes': not_nodes_all, 'links': not_edges_all}

        # 保存结果
        json_graph = json.dumps(sample, indent=4, ensure_ascii=False)
        with open(filePath, 'w', encoding='utf-8') as f:
            f.write(json_graph)
            f.close()
    return json_graph
