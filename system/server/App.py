# coding:utf-8
from flask import Flask, jsonify, request
from flask_cors import CORS
import json

import global_init as gi
from operate_db import get_db_table_fields, get_db_table_field_values
from deelDataAllNew import getData
# configuration
DEBUG = True

# 如下实现跨域请求.
app = Flask(__name__)
app.config.from_object(__name__)
CORS(app, resources={r"/*": {"origins": "*"}})


# fixme: 打开页面后,请求数据库名称
@app.route("/selectdataset/dbnames", methods=['GET', 'POST'])
def select_dataset_db_names():
    dbnamelist = []
    for data in gi.database_network:
        dbnamelist.append(data)
    db_name_obj = {"dbnamelist": dbnamelist}  # dbnamelist=[name1, ...]
    # print("db_name_obj")
    # print(db_name_obj)
    return jsonify(db_name_obj)


# fixme: 选中数据集后, 加载数据库对应的属性
@app.route("/selectdataset/whichdb", methods=['GET', 'POST'])
def select_dataset():
    param = json.loads(request.values.get('param'))
    db_name = param["dbname"]
    discard_fields = gi.database_network[db_name]["discard_fields"]
    db_name = "DB/" + db_name + ".db"
    col_name_list, col_name_type_obj = get_db_table_fields(dbname=db_name, table_name="node", discard_fields=discard_fields)
    obj = {"attrs": col_name_list, "attrTypes": col_name_type_obj}
    return jsonify(obj)


# fixme: 选中某个属性后,请求该属性下的所有属性值.
@app.route("/search/getFieldAllVal", methods=['GET', 'POST'])
def search_get_attr_val():
    param = json.loads(request.values.get('param'))
    print('search_get_attr_val', param)
    db_name = param["dbname"]
    db_name = "DB/" + db_name + ".db"
    atrr = param["field"]
    attr_type = param["attrType"]  # text, integer
    attr_val_list = get_db_table_field_values(dbname=db_name, field=atrr, field_type=attr_type)
    return jsonify(attr_val_list)


# # fixme: 查询出关键词匹配的节点.
# @app.route("/search/getQueryResults", methods=['GET', 'POST'])
# def search_query_results():
#     param = json.loads(request.values.get('param'))
#     db_name = param["dbname"]
#     atrr = param["field"]
#     keyword = param["queryKeywords"]
#     # node_obj_list = [{"nodeId": "100", "name": "mao", "age": 22}]
#     node_obj_list = [{"nodeId": "100", "name": "mao", "age": 22}]
#     return jsonify(node_obj_list)

@app.route("/semantic/graph", methods=['GET', 'POST'])
def semantic_graph():
    param = json.loads(request.values.get('param'))
    print('semantic_graph:', param)
    db_name = param["dbname"]
    db_name = "DB/" + db_name + ".db"
    atrr = param["field"]
    SC_list = param["SCList"]  # [x, ...]
    print("SC_list:", SC_list)
    res = getData(db_name, atrr, SC_list)
    print('result', '\n', res)
    return jsonify("mmmmm")


if __name__ == "__main__":
    app.run(port=5000, debug=True)