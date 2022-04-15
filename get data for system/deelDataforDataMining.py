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


# 
dbname = "data/DataMining.db"
sql_sentence_edge = "select source, target from edge"
# node_id_list = get_n_hop_nodes(dbname, sql_sentence_edge)
sql_sentence_node = "select id, name, institution, num_papers, num_citation, H_index, interests, publications from node"
all_nodes = read_database(dbname, sql_sentence_node)
all_edges = read_database(dbname, sql_sentence_edge)

print('基于关键节点连通性样本的节点数：', len(all_nodes), '边数：', len(all_edges))
# 统计intrests频数，转化为列表并排序
interests_frequence = {}
for i in all_nodes:
    interest = i[-2].split(';')
    for j in interest:
        temp = j.lower()
        if temp in interests_frequence:
            interests_frequence[temp] += 1
        else:
            interests_frequence[temp] = 1

interests_frequence_list = []
for i in interests_frequence:
    keyword_every_list = [interests_frequence[i], i]
    interests_frequence_list.append(keyword_every_list)

interests_frequence_list.sort(key=lambda x:-x[0])

# 基于keyword筛选节点与边
# interests_most_list = ['data mining', 'machine learning', 'human-computer interaction', 'visualization']
interests_most_list = interests_frequence_list[0:10] #ten attribute
interests_most_list = [i for _,i in interests_most_list[::-1]]

sample_nodes = []
for i in interests_most_list:
    for j in all_nodes:
        if j in sample_nodes:
            continue
        interest = j[-2].lower()
        interest = interest.split(';')
        # 将完全匹配换成部分匹配
        # 完全匹配
        # if i in interest:
        #     sample_nodes.append(j)
        # 部分匹配
        for k in interest:
            if i in k:
                sample_nodes.append(j)
                break

print('sample_nodes', len(sample_nodes))

sample_nodes_all = []
label = 0
for j in sample_nodes:
    interest = j[-2].lower()
    interest = interest.split(';')
    interest_j = ''
    for i in interests_most_list:
        # 完全匹配
        # if i in interest:
        #     interest_j = i
        #     break
        # 部分匹配
        for k in interest:
            if i in k:
                interest_j = i
                break
        if interest_j != '':
            break
    # 过滤掉期刊与keyword相同的节点
    node = {'label':label, 'id':j[0], 'name':j[1], 'interests':interest_j, 'num_papers':j[3], 'num_citation':j[4], 'H_index':j[5]}
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
# plt.show()
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
    node_map_attr[i['id']] = i['interests']

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
    attr = i['interests']
    neigbors = get_neigbors(G, ID, depth=1)
    same, unsame = 1, 0
    for j in neigbors[1]:
        if node_map_attr[j] == attr:
            same += 1
        else:
            unsame += 1
    i['interests'] = {'attribute':attr, 'same':same, 'unsame':unsame}
    maxforce = max(maxforce, unsame/same)
    forcerate += (unsame/same)
print(forcerate/len(nodes_all), maxforce)

# num_papers, num_citation, H_index, interests
num_papers, num_citation, H_index = {}, {}, {}
for i in nodes_all:
    if i['num_papers'] in num_papers:
        num_papers[i['num_papers']] += 1
    else:
        num_papers[i['num_papers']] = 1
    if i['num_citation'] in num_citation:
        num_citation[i['num_citation']] += 1
    else:
        num_citation[i['num_citation']] = 1
    if i['H_index'] in H_index:
        H_index[i['H_index']] += 1
    else:
        H_index[i['H_index']] = 1

# num_papers >200 >150 >100 >50 >20 >5
num_papers_frequence_list = []
for i in num_papers:
    num_papers_every_list = [i, num_papers[i]]
    num_papers_frequence_list.append(num_papers_every_list)
num_papers_frequence_list.sort(key=lambda x:x[0])
# num_papers >200 >150 >100 >50 >20 >5
for i in nodes_all:
    temp = i['num_papers']
    if temp <= 5: i['num_papers'] = {'attribute':'<=5', 'actual':temp}
    elif temp <= 20: i['num_papers'] = {'attribute':'5~20', 'actual':temp}
    elif temp <= 50: i['num_papers'] = {'attribute':'20~50', 'actual':temp}
    elif temp <= 100: i['num_papers'] = {'attribute':'50~100', 'actual':temp}
    elif temp <= 150: i['num_papers'] = {'attribute':'100~150', 'actual':temp}
    elif temp <= 200: i['num_papers'] = {'attribute':'150~200', 'actual':temp}
    elif temp > 200: i['num_papers'] = {'attribute':'>200', 'actual':temp}
# 节点与属性的映射
node_map_attr = {}
for i in nodes_all:
    node_map_attr[i['id']] = i['num_papers']['attribute']

forcerate = 0
maxforce = 0
for i in nodes_all:
    ID = i['id']
    attr = i['num_papers']['attribute']
    neigbors = get_neigbors(G, ID, depth=1)
    same, unsame = 1, 0
    for j in neigbors[1]:
        if node_map_attr[j] == attr:
            same += 1
        else:
            unsame += 1
    i['num_papers']['same'] = same
    i['num_papers']['unsame'] = unsame
    maxforce = max(maxforce, unsame/same)
    forcerate += (unsame/same)
print('num_papers邻接信息', forcerate/len(nodes_all), maxforce)

# num_citation >3000 >1500 >1000 >500 >200 >100 >50 >10 <=10
num_citation_frequence_list = []
for i in num_citation:
    num_citation_every_list = [i, num_citation[i]]
    num_citation_frequence_list.append(num_citation_every_list)
num_citation_frequence_list.sort(key=lambda x:x[0])
# num_citation >3000 >1500 >1000 >500 >200 >100 >50 >10 <=10
for i in nodes_all:
    temp = i['num_citation']
    if temp <= 10: i['num_citation'] = {'attribute':'<=10', 'actual':temp}
    elif temp <= 50: i['num_citation'] = {'attribute':'10~50', 'actual':temp}
    elif temp <= 100: i['num_citation'] = {'attribute':'50~100', 'actual':temp}
    elif temp <= 200: i['num_citation'] = {'attribute':'100~200', 'actual':temp}
    elif temp <= 500: i['num_citation'] = {'attribute':'200~500', 'actual':temp}
    elif temp <= 1000: i['num_citation'] = {'attribute':'500~1000', 'actual':temp}
    elif temp <= 1500: i['num_citation'] = {'attribute':'1000~1500', 'actual':temp}
    elif temp <= 3000: i['num_citation'] = {'attribute':'1500~3000', 'actual':temp}
    elif temp > 3000: i['num_citation'] = {'attribute':'>3000', 'actual':temp}
# 节点与属性的映射
node_map_attr = {}
for i in nodes_all:
    node_map_attr[i['id']] = i['num_citation']['attribute']

forcerate = 0
maxforce = 0
for i in nodes_all:
    ID = i['id']
    attr = i['num_citation']['attribute']
    neigbors = get_neigbors(G, ID, depth=1)
    same, unsame = 1, 0
    for j in neigbors[1]:
        if node_map_attr[j] == attr:
            same += 1
        else:
            unsame += 1
    i['num_citation']['same'] = same
    i['num_citation']['unsame'] = unsame
    maxforce = max(maxforce, unsame/same)
    forcerate += (unsame/same)
print('num_citation邻接信息', forcerate/len(nodes_all), maxforce)

# H_index >30 >20 >15 >10 >5 >1 <=1
H_index_frequence_list = []
for i in H_index:
    H_index_every_list = [i, H_index[i]]
    H_index_frequence_list.append(H_index_every_list)
H_index_frequence_list.sort(key=lambda x:x[0])
# H_index >30 >20 >15 >10 >5 >1 <=1
for i in nodes_all:
    temp = i['H_index']
    if temp <= 1: i['H_index'] = {'attribute':'<=1', 'actual':temp}
    elif temp <= 5: i['H_index'] = {'attribute':'1~5', 'actual':temp}
    elif temp <= 10: i['H_index'] = {'attribute':'5~10', 'actual':temp}
    elif temp <= 15: i['H_index'] = {'attribute':'10~15', 'actual':temp}
    elif temp <= 20: i['H_index'] = {'attribute':'15~20', 'actual':temp}
    elif temp <= 30: i['H_index'] = {'attribute':'20~30', 'actual':temp}
    elif temp > 30: i['H_index'] = {'attribute':'>30', 'actual':temp}
# 节点与属性的映射
node_map_attr = {}
for i in nodes_all:
    node_map_attr[i['id']] = i['H_index']['attribute']

forcerate = 0
maxforce = 0
for i in nodes_all:
    ID = i['id']
    attr = i['H_index']['attribute']
    neigbors = get_neigbors(G, ID, depth=1)
    same, unsame = 1, 0
    for j in neigbors[1]:
        if node_map_attr[j] == attr:
            same += 1
        else:
            unsame += 1
    i['H_index']['same'] = same
    i['H_index']['unsame'] = unsame
    maxforce = max(maxforce, unsame/same)
    forcerate += (unsame/same)
print('H_index邻接信息', forcerate/len(nodes_all), maxforce)

print(nodes_all[0])




# save into json
sample = {'nodes': nodes_all, 'links': edges_all}
json_sample = json.dumps(sample, indent=4, ensure_ascii=False)
# sample_DataMining
with open('data/sample_DataMining.json', 'w', encoding='utf-8') as f:
    f.write(json_sample)
    f.close()