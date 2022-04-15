# coding:utf-8
from flask import Flask, jsonify, request
from flask_cors import CORS
import os
import json

import global_init as gi
# configuration
DEBUG = True

# 如下实现跨域请求.
app = Flask(__name__)
app.config.from_object(__name__)
CORS(app, resources={r"/*": {"origins": "*"}})


# fixme: responding to the request "get all dataset name" from the frontend.
@app.route('/selectdataset/dbnames', methods=['GET', 'POST'])
def select_dataset_db_names():
    db_client = gi.db_client
    all_db_names = db_client.list_database_names()  # [x, ...]
    all_db_names.remove("admin")
    all_db_names.remove("local")
    all_db_names.remove("dblp")  # fixme: 不探索dblp数据库
    db_name_obj = {"dbnamelist": all_db_names}
    return jsonify(db_name_obj)


if __name__ == "__main__":
    app.run(port=5000, debug=True)