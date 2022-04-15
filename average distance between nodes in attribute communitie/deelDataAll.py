import json
import math
import time
import os

def deelDatasigma(fileName):
    pathName = 'data/' + fileName
    with open(pathName, 'r', encoding = 'utf-8') as f:
        data = f.read()
        f.close()
    data = json.loads(data)

    # 获取数据，并统计最大最小值用于正则化
    node = data['nodeData']['nodes']
    community = {}
    for i in node:
        attr = i['attribute']
        if attr not in community:
            community[attr] = []

    max_x = 0
    min_x = float('inf')
    max_y = 0
    min_y = float('inf')
    for i in node:
        attr = i['attribute']
        community[attr].append([i['x'], i['y']])
        max_x = max(max_x, i['x'])
        min_x = min(min_x, i['x'])
        max_y = max(max_y, i['y'])
        min_y = min(min_y, i['y'])

    # 进行正则化
    k = {}
    for i in community.keys():
        n = len(community[i])
        for j in range(n):
            community[i][j][0] = (community[i][j][0]- min_x) / (max_x - min_x)
            community[i][j][1] = (community[i][j][1]- min_y) / (max_y - min_y)

    # 分别计算各社区内节点间平均距离
    ans = {}
    for i in community:
        result = 0
        n = len(community[i])
        if n == 1:
            result = 'only one node in community'
            continue
        for j in range(n):
            for k in range(j+1, n):
                deltaX = community[i][j][0] - community[i][k][0]
                deltaY = community[i][j][1] - community[i][k][1]
                length = math.sqrt(deltaX * deltaX + deltaY * deltaY)
                result += length
        result = 2 * result / (n * (n - 1))
        ans[i] = result

    res = 0
    for i in ans:
        res += ans[i]
    res = res / (len(ans))
    localtime = time.asctime( time.localtime(time.time()))

    # save result
    with open('result/result_all.txt', 'a', encoding = 'utf-8') as f:
        write = [localtime, data['filename'][0], data['filename'][1], data['filename'][2], res]
        write = str(write)
        f.write(write+'\n')
        f.close()

def deelData(fileName):
    pathName = 'data/' + fileName
    with open(pathName, 'r', encoding = 'utf-8') as f:
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
        if n == 1:
            result = 'only one node in community'
            continue
        result = 0
        for j in range(n):
            for k in range(j + 1, n):
                deltaX = node[i][j][0] - node[i][k][0]
                deltaY = node[i][j][1] - node[i][k][1]
                length = math.sqrt(deltaX * deltaX + deltaY * deltaY)
                result += length
        result = 2 * result / (n * (n - 1))
        ans[i] = result
    res = 0
    for i in ans:
        res += ans[i]
    res = res / (len(ans))
    localtime = time.asctime( time.localtime(time.time()))

    # save result
    with open('result/result_all.txt', 'a', encoding = 'utf-8') as f:
        write = [localtime, data['filename'][0], data['filename'][1], data['filename'][2], res]
        write = str(write)
        f.write(write+'\n')
        f.close()

def file_name(file_dir):
    for _, _, files in os.walk(file_dir):
        return(files)

if __name__ == '__main__':
    with open('result/result_all.txt', 'w', encoding = 'utf-8') as f:
        write = '时间                          数据集            属性(可能无属性)  方法          同社区节点间的平均距离'
        f.write(write+'\n')
        f.close()

    fileList = file_name('data')
    for i in fileList:
        if 'our method' in i or 'originalD3' in i:
            deelData(i)
        else:
            deelDatasigma(i)