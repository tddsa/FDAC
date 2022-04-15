import json
import sqlite3


# DataMining  HumanComputerInteraction  MachineLearning  Visualization
with open('data/Visualization.json', 'r', encoding = 'utf-8') as f:
    data = f.read()
    f.close()

data = json.loads(data)
dbname = "data/Visualization.db"
db = sqlite3.connect(dbname)
cursor = db.cursor()
print("Opened database successfully")

print(len(data['links']))
for i in data['links']:
    sql_edge = "INSERT INTO edge(source, target) VALUES ('%s', '%s')" %(i['source'], i['target'])
    cursor.execute(sql_edge)
    db.commit()
print(len(data['nodes']))
for i in data['nodes']:
    sql_node = "INSERT INTO node(id, name, institution, num_papers, num_citation, H_index, interests, publications) VALUES (?, ?, ?, ?, ?, ?, ?, ?)"
    cursor.execute(sql_node, (i['id'], i['name'], i['institution'], i['num_papers'], i['num_citation'], i['H_index'], i['interests'], i['publications']))
    db.commit()
print("closed database successfully")
db.close()