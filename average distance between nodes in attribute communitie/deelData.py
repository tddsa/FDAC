import json
import math
import time

with open('data/_result_result (12).json', 'r', encoding = 'utf-8') as f:
    data = f.read()
    f.close()
data = json.loads(data)

# 获取数据，并统计最大最小值用于正则化
node = {}
for i in data['kernelNodes']:
    node[i['id']] = []

max_x = 0
min_x = float('inf')
max_y = 0
min_y = float('inf')
for i in data['nodes']:
    node[i['attribute1']].append([i['x'], i['y']])
    max_x = max(max_x, i['x'])
    min_x = min(min_x, i['x'])
    max_y = max(max_y, i['y'])
    min_y = min(min_y, i['y'])

# print(max_x, min_x, max_y, min_y)
# 进行正则化
for i in node.keys():
    n = len(node[i])
    for j in range(n):
        node[i][j][0] = (node[i][j][0]- min_x) / (max_x - min_x)
        node[i][j][1] = (node[i][j][1]- min_y) / (max_y - min_y)

# 分别计算各社区内节点间平均距离
ans = {}
for i in node:
    n = len(node[i])
    result = 0
    for j in range(n):
        for k in range(j + 1, n):
            deltaX = node[i][j][0] - node[i][k][0]
            deltaY = node[i][j][1] - node[i][k][1]
            length = math.sqrt(deltaX * deltaX + deltaY * deltaY)
            result += length
    result = 2 * result / (n * (n - 1))
    ans[i] = result
    
localtime = time.asctime( time.localtime(time.time()))

# save result
with open('result/result_all.txt', 'a', encoding = 'utf-8') as f:
    write = [localtime, data['filename'][0], data['filename'][1], data['filename'][2], ans]
    write = str(write)
    f.write(write+'\n')
    f.close()