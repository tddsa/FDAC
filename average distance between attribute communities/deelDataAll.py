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

    # print(max_x, min_x, max_y, min_y)
    # 进行正则化 并统计社区质心
    k = {}
    for i in community.keys():
        sum_x = 0
        sum_y = 0
        n = len(community[i])
        for j in range(n):
            community[i][j][0] = (community[i][j][0]- min_x) / (max_x - min_x)
            community[i][j][1] = (community[i][j][1]- min_y) / (max_y - min_y)
            sum_x += community[i][j][0]
            sum_y += community[i][j][1]
        k[i] = {}
        k[i]['x'] = sum_x / n
        k[i]['y'] = sum_y / n

    # 计算平均距离
    result = 0
    kernel = list(k.keys())
    m = len(kernel)
    for i in range(m):
        for j in range(i+1, m):
            deltaX = k[kernel[i]]['x'] - k[kernel[j]]['x']
            deltaY = k[kernel[i]]['y'] - k[kernel[j]]['y']
            length = math.sqrt(deltaX * deltaX + deltaY * deltaY)
            # print(length)
            result += length
    result = 2 * result / (m * (m - 1))
    localtime = time.asctime( time.localtime(time.time()))

    with open('result/result_all.txt', 'a', encoding = 'utf-8') as f:
        write = [localtime, data['filename'][0], data['filename'][1], data['filename'][2], result]
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
    # 进行正则化 并统计社区质心
    k = {}
    for i in node.keys():
        sum_x = 0
        sum_y = 0
        n = len(node[i])
        for j in range(n):
            node[i][j][0] = (node[i][j][0]- min_x) / (max_x - min_x)
            node[i][j][1] = (node[i][j][1]- min_y) / (max_y - min_y)
            sum_x += node[i][j][0]
            sum_y += node[i][j][1]
        k[i] = {}
        k[i]['x'] = sum_x / n
        k[i]['y'] = sum_y / n

    # 计算平均距离
    result = 0
    kernel = list(k.keys())
    m = len(kernel)
    for i in range(m):
        for j in range(i+1, m):
            deltaX = k[kernel[i]]['x'] - k[kernel[j]]['x']
            deltaY = k[kernel[i]]['y'] - k[kernel[j]]['y']
            length = math.sqrt(deltaX * deltaX + deltaY * deltaY)
            # print(length)
            result += length
    result = 2 * result / (m * (m - 1))
    localtime = time.asctime( time.localtime(time.time()))

    with open('result/result_all.txt', 'a', encoding = 'utf-8') as f:
        write = [localtime, data['filename'][0], data['filename'][1], data['filename'][2], result]
        write = str(write)
        f.write(write+'\n')
        f.close()

def file_name(file_dir):
    for _, _, files in os.walk(file_dir):
        return(files)

if __name__ == '__main__':
    with open('result/result_all.txt', 'w', encoding = 'utf-8') as f:
        write = '时间                          数据集            属性(可能无属性)  方法          社区间平均距离'
        f.write(write+'\n')
        f.close()
    
    fileList = file_name('data')
    for i in fileList:
        if 'our method' in i or 'originalD3' in i:
            deelData(i)
        else:
            deelDatasigma(i)