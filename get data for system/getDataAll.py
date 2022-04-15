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
    # print("Opened database successfully")
    # cursor.execute("select source, target, weight, source_name, target_name from edge")  # 从edge表中读取边.
    cursor.execute(sql_sentence)  # 从edge表中读取边
    data = list(cursor.fetchall())  # edges = [(), ...]
    # print("fetched data from database")
    # print(edges[:5])
    return data  # edges = [(), ...]
    
def get_n_hop_nodes(dbname, sql_sentence, node_id, hop):
    edges_list = read_database(dbname=dbname, sql_sentence=sql_sentence)
    # edges_list = [("a", "b"), ("b", "c"), ("b", "d"), ("d", "e"), ("c", "e"), ("a", "f"), ("a", "g"), ("g", "f")]
    G = nx.Graph()
    G.add_edges_from(edges_list)
    # pos = nx.spring_layout(G)  # 布局为中心放射状
    output = get_neigbors(G, node_id, depth=hop)
    return output

def getDatasetFromCitation_NonnumericalAttributes(dbname, ID, hop, field):
    fileName = 'citation' + '_' + ID + '_' + str(hop) + '.json'
    filePath = 'dataSet/' + fileName
    if os.path.exists(filePath):
        with open(filePath ,'r' ,encoding='utf-8') as f:
            json_graph_data = f.read()
            f.close()
    else:
        sql_sentence_edge = "select source, target from edge"
        sql_sentence_node = "select id, name, authors, public_venue, year, n_citation, reference, abstract, keywords from node"
        all_nodes = read_database(dbname, sql_sentence_node)
        all_edges = read_database(dbname, sql_sentence_edge)

        node_id = ID
        node_id_list = []
        node_id_list = get_n_hop_nodes(dbname, sql_sentence_edge, node_id, hop)
        
        node_center = [node_id]
        for i in range(1, hop+1):
            node_center += node_id_list[i]
        node_center = set(node_center)
        print('all nodes number:', len(node_center))

        graph_data = {'nodes':[], 'links':[]}
        for i in node_center:
            for j in all_nodes:
                if j[0] == i:
                    node_now = {'id':j[0], 'name':j[1], 'authors':j[2], 'public_venue':j[3], 'year':j[4], 'n_citation':j[5], 'reference':j[6], 'abstract':j[7], 'keywords':j[8]}
                    graph_data['nodes'].append(node_now)
                    break
        print('all nodes number:', len(graph_data['nodes']))
        # node_id_list = node_id_list[1] + node_id_list[2] + [kernel_node_id]
        for i in all_edges:
            if i[0] in node_center and i[1] in node_center:
                edge_now = {'source':i[0], 'target':i[1]}
                graph_data['links'].append(edge_now)
        print('all links number:', len(graph_data['links']))

        json_graph_data = json.dumps(graph_data, indent=4, ensure_ascii=False)
        with open(filePath ,'w' ,encoding='utf-8') as f:
            f.write(json_graph_data)
            f.close()
    
    graph = json.loads(json_graph_data)
    frequence = {}
    for i in graph['nodes']:
        keyword = i[field].split(';')
        for j in keyword:
            temp = j.lower()
            if temp in frequence:
                frequence[temp] += 1
            else:
                frequence[temp] = 1

    frequence_list = []
    for i in frequence:
        keyword_every_list = [frequence[i], i]
        frequence_list.append(keyword_every_list)

    frequence_list.sort(key=lambda x:-x[0])
    return frequence_list

def getDatasetFromCitationWithNumericalAttributes(dbname, ID, hop, field, fieldNum):
    fileName = 'citation' + '_' + ID + '_' + str(hop) + '.json'
    filePath = 'dataSet/' + fileName
    if os.path.exists(filePath):
        with open(filePath ,'r' ,encoding='utf-8') as f:
            json_graph_data = f.read()
            f.close()
    else:
        sql_sentence_edge = "select source, target from edge"
        sql_sentence_node = "select id, name, authors, public_venue, year, n_citation, reference, abstract, keywords from node"
        all_nodes = read_database(dbname, sql_sentence_node)
        all_edges = read_database(dbname, sql_sentence_edge)

        node_id = ID
        node_id_list = []
        node_id_list = get_n_hop_nodes(dbname, sql_sentence_edge, node_id, hop)
        
        node_center = [node_id]
        for i in range(1, hop+1):
            node_center += node_id_list[i]
        node_center = set(node_center)
        print('all nodes number:', len(node_center))

        graph_data = {'nodes':[], 'links':[]}
        for i in node_center:
            for j in all_nodes:
                if j[0] == i:
                    node_now = {'id':j[0], 'name':j[1], 'authors':j[2], 'public_venue':j[3], 'year':j[4], 'n_citation':j[5], 'reference':j[6], 'abstract':j[7], 'keywords':j[8]}
                    graph_data['nodes'].append(node_now)
                    break
        print('all nodes number:', len(graph_data['nodes']))
        # node_id_list = node_id_list[1] + node_id_list[2] + [kernel_node_id]
        for i in all_edges:
            if i[0] in node_center and i[1] in node_center:
                edge_now = {'source':i[0], 'target':i[1]}
                graph_data['links'].append(edge_now)
        print('all links number:', len(graph_data['links']))

        json_graph_data = json.dumps(graph_data, indent=4, ensure_ascii=False)
        with open(filePath ,'w' ,encoding='utf-8') as f:
            f.write(json_graph_data)
            f.close()
    
    # 获取所有数值属性和对应的频数
    graph = json.loads(json_graph_data)
    frequence = {}
    for i in graph['nodes']:
        temp = i[field]
        if temp in frequence:
            frequence[temp] += 1
        else:
            frequence[temp] = 1

    frequence_list = []
    for i in frequence:
        keyword_every_list = [i, frequence[i]] # 被引用次数, 对应的频数
        frequence_list.append(keyword_every_list)
    frequence_list.sort(key=lambda x:x[0])
    # 获取数值属性的分段区间
    numPerInterval = len(graph['nodes']) // fieldNum
    fieldSet = []
    fieldMin, fieldMax = frequence_list[0][0], frequence_list[-1][0]
    start = end = fieldMin
    count = 0
    for i in frequence_list:
        count += i[1]
        if i[1] >= numPerInterval:
            if count >= 2 * numPerInterval:
                end = i[0]
                fieldSet.append((start, end, count-i[1]))
                fieldSet.append((end, end, i[1]))
                start = end
                count = 0
            else:
                end = i[0]
                fieldSet.append((start, end, count))
                start = end
                count = 0
        if count >= numPerInterval:
            end = i[0]
            fieldSet.append((start, end, count))
            start = end
            count = 0
    fieldSet.append((start, fieldMax+1, count))
    return fieldSet

def getDataset_Non_numerical_Attributes(dbname, ID, hop, field):
    db = dbname.split('/')[1].split('.')[0]
    fileName = db + '_' + ID + '_' + str(hop) + '.json'
    filePath = 'dataSet/' + fileName
    if os.path.exists(filePath):
        with open(filePath ,'r' ,encoding='utf-8') as f:
            json_graph_data = f.read()
            f.close()
    else:
        sql_sentence_edge = "select source, target from edge"
        if 'citation' in db:
            sql_sentence_node = "select id, name, authors, public_venue, year, n_citation, reference, abstract, keywords from node"
        elif 'co-authorship' in db:
            sql_sentence_node = "select id, name, institution, num_papers, num_citation, H_index, interests, publications from node"
        all_nodes = read_database(dbname, sql_sentence_node)
        all_edges = read_database(dbname, sql_sentence_edge)

        node_id = ID
        node_id_list = []
        node_id_list = get_n_hop_nodes(dbname, sql_sentence_edge, node_id, hop)
        
        node_center = [node_id]
        for i in range(1, hop+1):
            node_center += node_id_list[i]
        node_center = set(node_center)
        print('all nodes number:', len(node_center))

        graph_data = {'nodes':[], 'links':[]}
        for i in node_center:
            for j in all_nodes:
                if j[0] == i:
                    if 'citation' in db:
                        node_now = {'id':j[0], 'name':j[1], 'authors':j[2], 'public_venue':j[3], 'year':j[4], 'n_citation':j[5], 'reference':j[6], 'abstract':j[7], 'keywords':j[8]}
                    elif 'co-authorship' in db:
                        node_now = {'id':j[0], 'name':j[1], 'institution':j[2], 'num_papers':j[3], 'num_citation':j[4], 'H_index':j[5], 'interests':j[6], 'publications':j[7]}
                    graph_data['nodes'].append(node_now)
                    break
        print('all nodes number:', len(graph_data['nodes']))
        # node_id_list = node_id_list[1] + node_id_list[2] + [kernel_node_id]
        for i in all_edges:
            if i[0] in node_center and i[1] in node_center:
                edge_now = {'source':i[0], 'target':i[1]}
                graph_data['links'].append(edge_now)
        print('all links number:', len(graph_data['links']))

        json_graph_data = json.dumps(graph_data, indent=4, ensure_ascii=False)
        with open(filePath ,'w' ,encoding='utf-8') as f:
            f.write(json_graph_data)
            f.close()
    
    graph = json.loads(json_graph_data)
    frequence = {}
    for i in graph['nodes']:
        keyword = i[field].split(';')
        for j in keyword:
            temp = j.lower()
            if temp in frequence:
                frequence[temp] += 1
            else:
                frequence[temp] = 1

    frequence_list = []
    for i in frequence:
        keyword_every_list = [frequence[i], i]
        frequence_list.append(keyword_every_list)

    frequence_list.sort(key=lambda x:-x[0])
    return frequence_list
    
def getDataset_numerical_Attributes(dbname, ID, hop, field, fieldNum):
    fileName = 'citation' + '_' + ID + '_' + str(hop) + '.json'
    filePath = 'dataSet/' + fileName
    if os.path.exists(filePath):
        with open(filePath ,'r' ,encoding='utf-8') as f:
            json_graph_data = f.read()
            f.close()
    else:
        sql_sentence_edge = "select source, target from edge"
        sql_sentence_node = "select id, name, authors, public_venue, year, n_citation, reference, abstract, keywords from node"
        all_nodes = read_database(dbname, sql_sentence_node)
        all_edges = read_database(dbname, sql_sentence_edge)

        node_id = ID
        node_id_list = []
        node_id_list = get_n_hop_nodes(dbname, sql_sentence_edge, node_id, hop)
        
        node_center = [node_id]
        for i in range(1, hop+1):
            node_center += node_id_list[i]
        node_center = set(node_center)
        print('all nodes number:', len(node_center))

        graph_data = {'nodes':[], 'links':[]}
        for i in node_center:
            for j in all_nodes:
                if j[0] == i:
                    node_now = {'id':j[0], 'name':j[1], 'authors':j[2], 'public_venue':j[3], 'year':j[4], 'n_citation':j[5], 'reference':j[6], 'abstract':j[7], 'keywords':j[8]}
                    graph_data['nodes'].append(node_now)
                    break
        print('all nodes number:', len(graph_data['nodes']))
        # node_id_list = node_id_list[1] + node_id_list[2] + [kernel_node_id]
        for i in all_edges:
            if i[0] in node_center and i[1] in node_center:
                edge_now = {'source':i[0], 'target':i[1]}
                graph_data['links'].append(edge_now)
        print('all links number:', len(graph_data['links']))

        json_graph_data = json.dumps(graph_data, indent=4, ensure_ascii=False)
        with open(filePath ,'w' ,encoding='utf-8') as f:
            f.write(json_graph_data)
            f.close()
    
    # 获取所有数值属性和对应的频数
    graph = json.loads(json_graph_data)
    frequence = {}
    for i in graph['nodes']:
        temp = i[field]
        if temp in frequence:
            frequence[temp] += 1
        else:
            frequence[temp] = 1

    frequence_list = []
    for i in frequence:
        keyword_every_list = [i, frequence[i]] # 被引用次数, 对应的频数
        frequence_list.append(keyword_every_list)
    frequence_list.sort(key=lambda x:x[0])
    # 获取数值属性的分段区间
    numPerInterval = len(graph['nodes']) // fieldNum
    fieldSet = []
    fieldMin, fieldMax = frequence_list[0][0], frequence_list[-1][0]
    start = end = fieldMin
    count = 0
    for i in frequence_list:
        count += i[1]
        if i[1] >= numPerInterval:
            if count >= 2 * numPerInterval:
                end = i[0]
                fieldSet.append((start, end, count-i[1]))
                fieldSet.append((end, end, i[1]))
                start = end
                count = 0
            else:
                end = i[0]
                fieldSet.append((start, end, count))
                start = end
                count = 0
        if count >= numPerInterval:
            end = i[0]
            fieldSet.append((start, end, count))
            start = end
            count = 0
    fieldSet.append((start, fieldMax+1, count))
    return fieldSet

def getAttrList(dbname, ID, hop, field, fieldNum=None):
    if fieldNum:
        return 1
    else:
        return getDataset_Non_numerical_Attributes(dbname, ID, hop, field)
    # if 'citation' in dbname:
    #     if 'keywords' in field or 'authors' in field:
    #         return getDatasetFromCitation_NonnumericalAttributes(dbname, ID, hop, field)
    #     else:
    #         return getDatasetFromCitationWithNumericalAttributes(dbname, ID, hop, field, fieldNum)
    # elif 'co-authorship' in dbname:
    #     if 'interests' in field:
    #         return getDatasetFromCoauthor_NonnumericalAttributes(dbname, ID, hop, field)


if __name__ == "__main__":
    # authors keywords n_citation
    # param = {'dbname': 'co-authorship', 'field': 'interests', 'SCList': ['data mining', 'data set']}
    param = {'dbname': 'citation', 'field': 'keywords', 'SCList': ['graph drawing', 'computer graphics']}
    db_name = param["dbname"]
    db_name = "data/" + db_name + ".db"
    ID = 'ad2284d6-dd1d-46cf-b8d9-3d50a672bf0e'
    # ID = '586652'
    hop = 2
    field = param["field"]
    fieldNum = None
    # fieldNum = 4
    res = getAttrList(db_name, ID, hop, field, fieldNum)
    # print(res)
    print('end')