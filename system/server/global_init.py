# coding: utf-8
import json

# fixme: 读取已存在的数据库名称(存放在数据库配置文件里)
with open("DB/database_config.json", 'r') as load_f:
    load_dict = json.load(load_f)
database_network = load_dict["networks"]


if __name__ == "__main__":
    # with open("DB/database_config.json", 'r') as load_f:
    #     load_dict = json.load(load_f)
    pass


