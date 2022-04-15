# coding:utf-8
import sqlite3
import numpy as np
import networkx as nx
import matplotlib.pyplot as plt
from fa2 import ForceAtlas2
from collections import Counter


# fixme: 获得指定数据库中表格的字段.
def get_db_table_fields(dbname=None, table_name="node", discard_fields=None):
    """
    :param dbname:
    :param table_name:表名
    :param discard_fields: e.g, ["id", ...] 在前端不需要考虑的字段, 如id, name这些.
    :return:
    """
    db = sqlite3.connect(dbname)
    cursor = db.cursor()
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
    cursor.execute("SELECT * FROM sqlite_master WHERE type='table'")
    tables = cursor.fetchall()  # Tables 为元组列表 [('author',), ('paper',), ('coauthor',), ('author2paper',)]
    db_tables_list = []  # 对应数据库中,除了node + edge之外的表, e.g.[publictions]
    for each_one in tables:
        tb = each_one[1]
        if tb != "node" and tb != "edge":
           db_tables_list.append(tb)

    cursor.execute("SELECT * FROM {}".format(table_name))

    col_name_list = []  # 获得表中的字段.
    for tuple_ in cursor.description:
        fd = tuple_[0]
        if fd not in discard_fields:
            col_name_list.append(fd)
    col_name_type_list = {}  # col_name_list中各元素对应的类型.
    counter = -1
    for each_field in col_name_list:
        counter += 1
        type_field = "select typeof(" + each_field + ") from node limit 0,1"  # limit 0,1 表示从第1条开始的一条记录.
        cursor.execute(type_field)
        data = cursor.fetchall()
        type_each_field = data[0][0]
        col_name_type_list[col_name_list[counter]] = type_each_field
    """
    返回格式:
    col_name_list=['id', 'name', 'institution', 'num_papers', 'num_citation', 'H_index', 'P_index', 'UP_index', 'interests']
    col_name_type_list={'num_citation': 'integer', 'P_index': 'real', 'interests': 'text', 'num_papers': 'integer', 'UP_index': 'real', 'H_index': 'integer', 'name': 'text', 'id': 'integer', 'institution': 'text'}
    """
    col_name_obj = []
    for each_one in col_name_list:
        col_name_obj.append({"value": each_one, "label": each_one})
    return col_name_obj, col_name_type_list


# TODO:获得指定数据库的对应字段的值.目前需要定制,即不同数据库,情况是不一样的.
def get_db_table_field_values(dbname=None, field=None, field_type=None):
    """
    :param dbname:
    :param field: 字段, 即属性.
    field_type: 属性类型, e.g., text, integer
    :return: sort_result: [{"value":XXX, "number":XXX}, ...], 如果是字符串类型,按照出现次数降序排列,数值类型,则按照大小降序排列.
    """
    db = sqlite3.connect(dbname)  # 将要在PacificVIS.db数据库中创建PAPER表格，数据库中已经有Colection表
    cursor = db.cursor()
    results = []  # ["a;b;c", "c;d", ...]
    sql = "select " + field + " from node"
    cursor.execute(sql)
    data = cursor.fetchall()  # 使用这种方式取出所有查询结果
    for each_one in data:
        results.append(each_one[0])
    # print("results")
    # print(results[:10])
    type_field = field_type.lower()  # 用于记录字段的类型.
    # 针对含有多个值的,比如兴趣,机构,按照分号划分,统计相同的iterm的数量.
    set_items = set()  # iterm的集合
    list_items = list()  # 所有iterm的列表. ["a", "b", ...]
    """
    备注:数据库表中,处理数据缺失的情况如下.
        1. 如果是text类型,则填入NULL.
        2. 如果是int类型,则填入0.
        3. 如果是float类型,则填入0.0.
        数据库表常见的类型也就这几种: text, real, int.

    """
    if type_field == "text":
        for each_one in results:
            if each_one.lower() != "null":  # 排除掉"NULL"
                each_one = each_one.strip()
                each_one = each_one.split(";")  # ["a", "b", ...]
                for item in each_one:
                    list_items.append(item.lower())

    else:
        for each_one in results:
            set_items.add(each_one)

    sort_result = []  # 用于装排序好的结果.
    if type_field == "text":  # 如果是字符串类型.
        # 统计每个iterm的数量.
        result = Counter(list_items)  # {'mao': 4, 'aa': 4, 'yun': 3, 'bb': 1}
        for each_one in result.most_common():  # [("mao", 20), ...]
            sort_result.append({"number": each_one[1], "value": each_one[0]})

    elif type_field == "integer" or type_field == "float":
        result = sorted(set_items, reverse=True)  # [100, 90, 80, ...]
        for each_one in result:
            sort_result.append({"value": str(each_one)})
    else:  # 可能是bool型,暂时没有遇到.
        for i in set_items:
            temp_obj = {"value": i}
            sort_result.append(temp_obj)
    print("sort_result")
    print(sort_result[:10])
    return sort_result  # [{"value":XXX, "number":XXX}, ...]


def test_graph():
    dbname = "DB/social_network.db"
    db = sqlite3.connect(dbname)  # 将要在PacificVIS.db数据库中创建PAPER表格，数据库中已经有Colection表
    cursor = db.cursor()
    sql = "select * from edge"
    cursor.execute(sql)
    data = cursor.fetchall()
    edges_list_with_weight = []
    nodes_obj = {}  # id-atrrs
    for each_edge in data:
        edges_list_with_weight.append(each_edge[:3])  # [(source_id, target_id, weight), ...]
        source = each_edge[0]
        target = each_edge[1]
        # weight = each_edge[2]  # weight int类型.
        # weight_set.add(weight)
        source_name = each_edge[3]
        target_name = each_edge[4]
        nodes_obj[source] = source_name
        nodes_obj[target] = target_name
    print("edges_list_with_weight")
    print(edges_list_with_weight)
    print("nodes_obj")
    print(nodes_obj)
    G = nx.Graph()
    G.add_weighted_edges_from(edges_list_with_weight)
    # fixme: 节点索引列表
    nodes_list = list(G.nodes())  # e.g., ['g', 'e', 'c', 'd', 'b', 'f', 'a']
    print("nodes_list")
    print(nodes_list)
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
    nx.draw(G, pos, node_color='#A0CBE2', width=4, with_labels=True)
    plt.show()


if __name__ == "__main__":
    # dbname = "DB/social_network.db"
    # field = "interest"
    # db = sqlite3.connect(dbname)  # 将要在PacificVIS.db数据库中创建PAPER表格，数据库中已经有Colection表
    # cursor = db.cursor()
    # results = set()
    # sql = "PRAGMA table_info(node)"
    # cursor.execute(sql)
    # data = cursor.fetchall()  # 使用这种方式取出所有查询结果
    # print(data)
    # for each_one in data:
    #     results.add(each_one[0])
    # results = list(results)  # [XXX, XXX, ...,XXX]
    # print("results")
    # print(results)
    # test_graph()

    # from collections import Counter
    #
    # a = ["mao", "yun", "yun", "yun", "aa", "aa", "aa", "aa", "bb", "mao", "mao", "mao"]
    # result = Counter(a)  # {'mao': 4, 'aa': 4, 'yun': 3, 'bb': 1}
    # print(result.most_common())
    # a = [90.8, 78.9, 55.9, 23.9, 100.89]
    dbname = "DB/citation.db"
    field = "keywords"
    field_type = "text"
    # field = "n_citation"
    # r = get_db_table_field_values(dbname=dbname, field=field)
    # print(r)
    r = get_db_table_fields(dbname=dbname, table_name="node", discard_fields=['id', 'name', 'abstract', 'authors', 'public_venue','reference', 'keywords'])
    print(r)
    # discard_fields = ["id", "name", "reference", "abstract", "authors"]
    # col_name_list, col_name_type_list = get_db_table_fields(dbname=dbname, table_name="node", discard_fields=discard_fields)
    # print("col_name_list")
    # print(col_name_list)
    # print("col_name_type_list")
    # print(col_name_type_list)
    # r = get_db_table_field_values(dbname=dbname, field=field, field_type=field_type)
    # print(r[:10])

    # r = get_db_table_field_values(dbname=dbname, field=field)