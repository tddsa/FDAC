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



dbname = "data/new.db"
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

keywords_frequence_list.sort(key=lambda x:-x[0])

# 基于keyword筛选节点与边
keywords_most_list = keywords_frequence_list[0:10] #ten attribute
keywords_most_list = [i for _,i in keywords_most_list[::-1]]

sample_nodes = []
for i in keywords_most_list:
    for j in all_nodes:
        if j in sample_nodes:
            continue
        keyword = j[-1].lower()
        keyword = keyword.split(';')
        if i in keyword:
            sample_nodes.append(j)

print('sample_nodes', len(sample_nodes))
sample_nodes_all = []
label = 0
for j in sample_nodes:
    keyword = j[-1].lower()
    keyword = keyword.split(';')
    keyword_j = ''
    for i in keywords_most_list:
        if i in keyword:
            keyword_j = i
            break
    # 过滤掉期刊与keyword相同的节点
    if j[3] in keyword and j[1] in keyword:
        # print(j)
        continue
    node = {'label':label, 'id':j[0], 'name':j[1], 'attribute1':keyword_j}
    label += 1
    sample_nodes_all.append(node)

print('sample_nodes_all', len(sample_nodes_all))
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
print('初步筛选出的边的数目', len(sample_edges_all))
# 提取最大子图
import networkx as nx
import matplotlib.pyplot as plt
G = nx.Graph()
G.add_edges_from(detect_community)
pos = nx.spring_layout(G)  # 布局为中心放射状
nx.draw(G, pos, node_color='#A0CBE2', width=4, with_labels=True)
max_subgraph = max(nx.connected_components(G))
print('最大子图中节点的数目', len(max_subgraph))

# 根据最大子图获取最终的点
nodes_all = []
label = 0
for j in sample_nodes_all:
    if j['id'] in max_subgraph:
        nodes_all.append(j)
print('nodes number:', len(nodes_all))

# 根据最大子图获取最终的边
edges_all = []
for j in sample_edges_all:
    if j['source'] in max_subgraph and j['target'] in max_subgraph:
        edges_all.append(j)

print('edges number:', len(edges_all))

# 节点与属性的映射
node_map_attr = {}
for i in nodes_all:
    node_map_attr[i['id']] = i['attribute1']

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

forcerate = 0
maxforce = 0
for i in nodes_all:
    ID = i['id']
    attr = i['attribute1']
    neigbors = get_neigbors(G, ID, depth=1)
    same, unsame = 1, 0
    for j in neigbors[1]:
        if node_map_attr[j] == attr:
            same += 1
        else:
            unsame += 1
    i['same'] = same
    i['unsame'] = unsame
    maxforce = max(maxforce, unsame/same)
    forcerate += (unsame/same)
print(forcerate/513, maxforce)

# save into json
sample = {'nodes': nodes_all, 'links': edges_all}
json_sample = json.dumps(sample, indent=4, ensure_ascii=False)
with open('data/sample_keyword.json', 'w', encoding='utf-8') as f:
    f.write(json_sample)
    f.close()