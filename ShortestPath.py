import math

import networkx as nx
import copy

D_MAX = 14

def dijkstra(G, start, end):
    RG = G.reverse()
    dist = {}
    previous = {}
    for v in RG.nodes():
        #都设置为无穷大
        dist[v] = float('inf')
        previous[v] = 'none'
    dist[end] = 0
    u = end
    # print(min(dist, key=dist.get))
    alt = 0
    while u != start:
        #获得最小值对应的键
        u = min(dist, key=dist.get)
        distu = dist[u]
        del dist[u]
        for u, v in RG.edges(u):
            if v in dist:
                alt = distu + RG[u][v]['weight']
                if alt < dist[v]:
                    dist[v] = alt
                    previous[v] = u
    path = (start,)
    last = start
    while last != end:
        nxt = previous[last]
        path += (nxt,)
        last = nxt
    p = []
    for i in range(len(path)-1):
        p.append([path[i], path[i+1]])
    return p, alt

def path_genarate(nw):
    for i in range(len(nw.floor_dict)):
        for j in range(len(nw.floor_dict[i].nodes)):
            if nw.floor_dict[i].nodes[j].is_shadow == 0:
                nw.node_list.append(nw.floor_dict[i].nodes[j])
        for j in range(len(nw.floor_dict[i].edges)):
            nw.floor_dict[i].edges[j].density = nw.floor_dict[i].edges[j].pnum / nw.floor_dict[i].edges[j].area
            nw.edge_list.append(nw.floor_dict[i].edges[j])

def max_length(nw):
    # 将路径长度超过阈值的进行等距分割
    global D_MAX
    d_max = D_MAX
    for i in range(len(nw.floor_dict)):
        floor_num = nw.floor_dict[i].num
        nw.name_fi = nw.floor_dict[i].name
        nw.node_fi = nw.find_floor_name(nw.floor_dict, nw.name_fi).nodes
        nw.edge_fi = nw.find_floor_name(nw.floor_dict, nw.name_fi).edges
        for j in range(len(nw.floor_dict[i].edges)):
            edge_ij = nw.floor_dict[i].edges[j]
            if edge_ij.l >= d_max and edge_ij.w < 4:
                n = math.ceil(edge_ij.l/d_max)
                ns = nw.find_node(edge_ij.ns)
                ne = nw.find_node(edge_ij.ne)
                eij = copy.deepcopy(edge_ij)
                # 需要添加的节点
                node_add = []
                node_1 = [ns.num]
                edge_add = []
                for k in range(n-1):
                    node_add.append(nw.node_sn)
                    node_1.append(nw.node_sn)
                    nw.node_sn = nw.node_sn + 1
                node_1.append(ne.num)

                for k in range(len(node_add)):
                    x, y, num, type_, cid, is_shadow, floor_num = ns.x+(ne.x-ns.x)/n*(k+1), ns.y+(ne.y-ns.y)/n*(k+1), node_add[k], 1, [], 0, ns.floor_num
                    nw.add_node(x, y, num, type_, cid, is_shadow, floor_num)

                for k in range(len(node_1)-1):
                    edge_add.append([node_1[k], node_1[k+1]])

                for k in range(len(edge_add)):
                    if k == 0:
                        edge_ij.ne = edge_add[k][1]
                        edge_ij.l = eij.l / n
                        edge_ij.pn = int(eij.pn / n)
                    else:
                        ns, ne, length, width, pedestrian_num, pre_time, type_, cid = edge_add[k][0], edge_add[k][1], eij.l / n, eij.w, int(eij.pn / n), eij.pt, eij.tp, []
                        nw.add_edge(ns, ne, length, width, pedestrian_num, pre_time, type_, cid, floor_num)

# 求最短路径 solve the shortest path
def shortest_path(nw):
    max_length(nw)
    G = nx.DiGraph()
    for i in range(len(nw.floor_dict)):
        for j in range(len(nw.floor_dict[i].edges)):
            edge_ij = nw.floor_dict[i].edges[j]
            G.add_edge(edge_ij.ns, edge_ij.ne, weight=edge_ij.l)
            G.add_edge(edge_ij.ne, edge_ij.ns, weight=edge_ij.l)
    start = []
    end = []
    for i in range(len(nw.floor_dict)):
        for j in range(len(nw.floor_dict[i].nodes)):
            node_ij = nw.floor_dict[i].nodes[j]
            if node_ij.is_shadow == 0:
                if node_ij.tp == 0:
                    start.append(node_ij.num)
                if node_ij.tp == 2:
                    end.append(node_ij.num)
    # 获取最短路列表
    path_l = []
    for i in range(len(start)):
        path_i = []
        length_i = []
        for j in range(len(end)):
            path, length = dijkstra(G, start[i], end[j])
            path_i.append(path)
            length_i.append(length)
            # print(start[i], end[j], length, path)
        minp = length_i.index(min(length_i))
        path_l.append(path_i[minp])
    # 将最短路列表中的重复元素删除
    path_list = []
    for i in range(len(path_l)):
        for j in range(len(path_l[i])):
            path_list.append(path_l[i][j])
    path_tm = []
    for i in range(len(path_list)):
        if path_list[i] not in path_tm:
            path_tm.append(path_list[i])
    nw.shortest_path = path_tm
    # 调整edge的方向
    edge_direction(nw)

def edge_direction(nw):
    # 根据生成的最优路径更新edge的方向
    for i in range(len(nw.shortest_path)):
        ns = copy.deepcopy(nw.shortest_path[i][0])
        ne = copy.deepcopy(nw.shortest_path[i][1])
        for j in range(len(nw.floor_dict)):
            for k in range(len(nw.floor_dict[j].edges)):
                edge_jk = nw.floor_dict[j].edges[k]
                if ns == edge_jk.ne and ne == edge_jk.ns:
                    edge_jk.swap_node()
    #
    # print("输出换向后节点：")
    # for i in range(len(nw.shortest_path)):
    #     print(nw.shortest_path[i][0], nw.shortest_path[i][1])