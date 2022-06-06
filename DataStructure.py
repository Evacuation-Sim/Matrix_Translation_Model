import copy
import datetime

import numpy as np
import random
import matplotlib.pyplot as plt

GRID_L = 0.5
GRID_W = 0.5
DELTA_T = 0.30
SW = 0.40
ST = 0.20
OUT_SUM = 0

TIME_SUM = 0

# 保存建筑网络的结构体
class NetworkStructure:
    def __init__(self):
        # floor_dict: [floor_name, floor_num, [nodes], [edge], [canvs]]
        self.floor_dict = []
        # fi层的node:[x, y, num, tp, cid]
        self.node_fi = []
        # fi层的edge:[ni, nj, l, w, n, tp, cid, cedge];
        self.edge_fi = []
        # fi层的canv
        self.canv_fi = []
        # fi层的名称
        self.name_fi = ""
        # 所有楼层的整合结果
        self.node_list = []
        self.edge_list = []

        # 由dijkstra计算得到最短路径
        self.shortest_path = []

        self.node_sn = 0  # 节点的全局计数

        # 显示相关
        self.node_temp = []
        self.node_dele = []
        self.edge_dele = []

    def new_floor(self, floor_name, floor_num):
        # 新建楼层
        new_floor = Floor(floor_name, floor_num, [], [], [])
        self.floor_dict.append(new_floor)

    def load_floor(self, sle_floor):
        for i in range(len(self.floor_dict)):
            if self.floor_dict[i].name == sle_floor:
                self.node_fi = self.floor_dict[i].nodes
                self.edge_fi = self.floor_dict[i].edges
                self.canv_fi = self.floor_dict[i].cids

    def find_floor_name(self, floor_dict, floor_name):
        floor_find = []
        for i in range(len(floor_dict)):
            if floor_dict[i].name == floor_name:
                floor_find = floor_dict[i]
        return floor_find

    # 保存当前楼层
    def save_floor(self, floor_name):
        # 保存楼层
        # 保存节点
        # floor_i: floor_name, floor_num, [nodes], [edges], [canvs]
        floor_find = self.find_floor_name(self.floor_dict, floor_name)
        floor_find.nodes = self.node_fi
        floor_find.edges = self.edge_fi
        canv_id = []
        for i in range(len(self.node_fi)):
            for j in range(len(self.node_fi[i].cid)):
                canv_id.append(self.node_fi[i].cid[j])
        for i in range(len(self.edge_fi)):
            for j in range(len(self.edge_fi[i].cid)):
                canv_id.append(self.edge_fi[i].cid[j])
        floor_find.cids = canv_id

    # 新增普通节点，自动增长编号
    # x，y: 节点的中心位置；num: 节点编号；tp; cid：canvas的id
    # tp: 0: 发点；1：中间节点；2：收点
    def add_node(self, x, y, num, tp, cid, is_shadow, floor_num):
        new_node = copy.deepcopy(Node(x, y, num, tp, cid, is_shadow, floor_num))
        self.node_fi.append(new_node)

    def find_node(self, num):
        nd = []
        for i in range(len(self.node_fi)):
            if self.node_fi[i].num == num:
                nd = self.node_fi[i]
        return nd

    # node: x, y, cid
    # ni, nj: 与该边相连的两个节点编号；l：边的长度；w：边的宽度；n：边上的人数；tp：边的类型，0：房间，1：走廊，2楼梯，3门；
    # cid：canvas的id;
    def add_edge(self, ns, ne, length, width, pnum, pre_time, type_, cid, floor_num):
        new_edge = Edge(ns, ne, length, width, pnum, pre_time, type_, cid, floor_num)
        self.edge_fi.append(new_edge)

class Floor:
    def __init__(self, name, num, nodes, edges, cids):
        self.name = name
        self.num = num
        self.nodes = nodes
        self.edges = edges
        self.cids = cids

class Node:
    def __init__(self, x, y, num, type_, cid, is_shadow, floor_number):
        self.x = x
        self.y = y
        self.num = num
        # type of the node: 0: source node, 1: inter node, 2: sink node
        self.tp = type_
        # number of canvas
        self.cid = cid
        # flag of if it is a real node
        self.is_shadow = is_shadow
        self.floor_num = floor_number

        self.edge_up = []
        self.edge_down = []
        self.node_up = []
        self.node_down = []
        self.node_up_list = []
        self.active = 1

        self.out_time = 0
        self.dist_rate = -0.1
        self.dist_num = 0

    def colum_move(self, i, mtx):
        # 将数组A的第i列下移一行
        global TIME_SUM
        t1 = datetime.datetime.now()
        mtx_copy = copy.deepcopy(np.array(mtx))
        mtx_copy[1:, i] = mtx_copy[0:-1, i]
        mtx_copy[0, i] = 0
        t2 = datetime.datetime.now()
        # TIME_SUM = TIME_SUM + (t2-t1).microseconds
        return mtx_copy

    def colum_sink(self, i, A):
        # 将数组A的第i列下沉一行
        global TIME_SUM
        t1 = datetime.datetime.now()
        A_copy = copy.deepcopy(A)
        for j in range(len(A)-1):
            idx = len(A) - j -1
            if A[idx][i] == 0 and A[idx-1][i] == 0:
                A[0][i] = 0
                for k in range(1, idx+1):
                    A[k][i] = A_copy[k-1][i]
                break
        t2 = datetime.datetime.now()
        # TIME_SUM = TIME_SUM + (t2 - t1).microseconds

    # 计算当前时间步内，walkway和stairway中向前移动的距离
    def dist_solve(self, type, area, mtx):
        # 根据密度确定下一次的更新时刻
        dist = 0
        if type == 0:
            # SFPE经验公式：S=k-akd，走廊k=1.40
            d = np.sum(mtx) / area
            s = 1.40 - 0.266 * 1.40 * d
            s = np.max([s, SW])
            dist = DELTA_T * s
        elif type == 1:
            # SFPE经验公式：S=k-akd，楼梯k=1.00
            d = np.sum(mtx) / area
            s = 1.00 - 0.266 * 1.00 * d
            s = np.max([s, ST])
            dist =DELTA_T * s
        return dist

    # 计算当前时间步内，doorway的通行流量累积
    def flow_solve(self, type, w):
        flow = 0
        we = w - 0.15 # 有效宽度
        if type == 2:
            flow = 1.3 * we * DELTA_T
        return flow

    def update(self, time):
        t1 = datetime.datetime.now()

        if self.edge_up != [] and self.edge_down != []:
            row_up = {}
            # 流入边最后一行的人数
            num_up = 0
            for i in range(len(self.edge_up)):
                if self.edge_up[i].tp == 0 or self.edge_up[i].tp == 1:
                    # walkway和stairway的速度控制
                    self.edge_up[i].dist = self.edge_up[i].dist + self.dist_solve(self.edge_up[i].tp, self.edge_up[i].area, self.edge_up[i].mtx)
                    if self.edge_up[i].dist >= GRID_L and np.sum(self.edge_up[i].mtx > 0):
                        row_up[i] = np.sum(self.edge_up[i].mtx[-1])
                        num_up = num_up + row_up[i]
                        self.edge_up[i].dist = self.edge_up[i].dist - GRID_L
                elif self.edge_up[i].tp == 2:
                    # doorway的流量控制
                    self.edge_up[i].flow = self.edge_up[i].flow + self.flow_solve(self.edge_up[i].tp, self.edge_up[i].w)
                    if self.edge_up[i].flow >= np.sum(self.edge_up[i].mtx[-1]) and np.sum(self.edge_up[i].mtx > 0):
                        row_up[i] = np.sum(self.edge_up[i].mtx[-1])
                        num_up = num_up + row_up[i]
                        self.edge_up[i].flow = 0

            row_down = {}
            # 流出边第一行的人数
            num_down = 0
            if len(self.edge_down) == 1:
                for i in range(len(self.edge_down)):
                    row_down[i] = len(self.edge_down[i].mtx[0]) - np.sum(self.edge_down[i].mtx[0])
                    num_down = num_down + row_down[i]
            elif len(self.edge_down) == 2:
                self.dist_num = self.dist_num + num_up * self.dist_rate
                # print(self.num, self.dist_num, self.dist_rate)
                row_down[0] = len(self.edge_down[0].mtx[0]) - np.sum(self.edge_down[0].mtx[0])
                num_down = num_down + row_down[0]

                # 向旁支分配
                if self.dist_num >= 1:
                    nu = np.floor(self.dist_num)
                    # 从node_up中随机选取dist_num个，分配如旁支
                    up_keys = row_up.keys()
                    R = range(int(num_up))
                    slc = random.sample(R, int(nu))
                    n = 0
                    for i in up_keys:
                        for j in range(len(self.edge_up[i].mtx[-1])):
                            if self.edge_up[i].mtx[-1][j] == 1:
                                if n in slc:
                                    self.edge_up[i].mtx[-1][j] = 0
                                    num_up = num_up - 1
                                n = n + 1

                    nd = len(self.edge_down[1].mtx[0])
                    R = range(int(nd))
                    slc = random.sample(R, int(nu))
                    print(slc)
                    n = 0
                    for j in range(len(self.edge_down[1].mtx[0])):
                        if self.edge_down[1].mtx[0][j] == 0:
                            if n in slc:
                                self.edge_down[1].mtx[0][j] = 1
                            n = n + 1
                    self.dist_num = self.dist_num - np.floor(self.dist_num)

            # 整体更新
            if num_up >= num_down: # 上游人数大于下游空格数
                up_keys = row_up.keys()
                R = range(int(num_up))
                slc = random.sample(R, int(num_down))
                n = 0
                for i in up_keys:
                    for j in range(len(self.edge_up[i].mtx[-1])):
                        if self.edge_up[i].mtx[-1][j] == 1:
                            if n in slc:
                                self.edge_up[i].mtx = self.colum_move(j, self.edge_up[i].mtx)
                            # else:
                            #     self.colum_sink(j, self.edge_up[i].mtx)
                            n = n + 1
                        else:
                            self.edge_up[i].mtx = self.colum_move(j, self.edge_up[i].mtx)

                down_keys = row_down.keys()
                for i in down_keys:
                    self.edge_down[i].mtx[0] = list(np.ones(len(self.edge_down[i].mtx[0])))
            else: # 上游人数小于下游空格数
                up_keys = row_up.keys()
                for i in up_keys:
                    self.edge_up[i].array_move()

                down_keys = row_down.keys()
                R = range(int(num_down))
                slc = random.sample(R, int(num_up))
                n = 0
                for i in down_keys:
                    for j in range(len(self.edge_down[i].mtx[0])):
                        if self.edge_down[i].mtx[0][j] == 0:
                            if n in slc:
                                self.edge_down[i].mtx[0][j] = 1
                            n = n + 1

        elif self.edge_down == []:
            # 对离开点
            for i in range(len(self.edge_up)):
                if self.edge_up[i].tp == 0 or self.edge_up[i].tp == 1:
                    # walkway和stairway的速度控制
                    self.edge_up[i].dist = self.edge_up[i].dist + self.dist_solve(self.edge_up[i].tp,
                                                                                  self.edge_up[i].area,
                                                                                  self.edge_up[i].mtx)
                    if self.edge_up[i].dist >= GRID_L:
                        self.edge_up[i].array_move()
                        self.edge_up[i].dist = 0
                elif self.edge_up[i].tp == 2:
                    # doorway的流量控制
                    self.edge_up[i].flow = self.edge_up[i].flow + self.flow_solve(self.edge_up[i].tp, self.edge_up[i].w)
                    if self.edge_up[i].flow >= np.sum(self.edge_up[i].mtx[-1]) and np.sum(self.edge_up[i].mtx) > 0:
                        # global OUT_SUM
                        # OUT_SUM = OUT_SUM + np.sum(self.edge_up[i].mtx[-1])
                        # print(OUT_SUM)
                        self.edge_up[i].array_move()
                        # print(self.edge_up[i].ne, row_last)
                        self.edge_up[i].flow = 0
                        self.out_time = time

        # 检查本节点是否清空
        active = 0
        for i in range(len(self.edge_up)):
            if np.sum(self.edge_up[i].mtx) > 0:
                active = 1
                break
        if not active:
            for i in range(len(self.node_up_list)):
                if self.node_up_list[i].active == 1:
                    active = 1
                    break

        self.active = active
        t2 = datetime.datetime.now()
        return (t2 - t1).microseconds


class Edge:
    def __init__(self, ns, ne, length, width, pedestrian_num, pre_time, type_, cid, floor_num):
        self.ns = ns
        self.ne = ne
        self.l = length
        self.w = width
        self.pn = pedestrian_num
        # tp: 0, walkway; 1: stairway; 2: doorway.
        self.tp = type_
        self.pt = pre_time
        self.cid = cid
        self.floor_num = floor_num

        # --平移矩阵所需数据
        # 边的面积
        self.area = self.l * self.w
        # 边的密度
        self.density = 0
        # 边的矩阵
        self.mtx = []
        # 矩阵保存列表
        self.mtx_save = []
        # 累积流动距离
        self.dist = 0
        # 累积通行流量
        self.flow = 0

    def mtx_init(self):
        # 有效宽度we的计算：walkway：0.2m；stairway：0.15m；doorway：0.15m
        if self.tp == 0:
            self.mtx = np.zeros([int(self.l / GRID_L), int((self.w - 0.2) / GRID_W)])
        elif self.tp == 1 or self.tp == 2:
            self.mtx = np.zeros([int(self.l / GRID_L), int((self.w - 0.15) / GRID_W)])
        # 将人随机分布在数组中
        L = range(np.size(self.mtx))
        try:
            SL = random.sample(L, self.pn)
        except "ValueError":
            print("Sample larger than population or is negative")
        for i in range(len(self.mtx)):
            for j in range(len(self.mtx[i])):
                if (i * len(self.mtx[i]) + j) in SL:
                    self.mtx[i][j] = 1

        # 为utime赋初值，即预动作时间
        self.utime = self.pt

    def swap_node(self):
        n_temp = copy.deepcopy(self.ns)
        self.ns = copy.deepcopy(self.ne)
        self.ne = n_temp

    # 将数组下移一行
    def array_move(self):
        global TIME_SUM
        t1 = datetime.datetime.now()
        mtx_copy = copy.deepcopy(np.array(self.mtx))
        mtx_copy[1:] = mtx_copy[0:-1]
        mtx_copy[0] = np.zeros(len(self.mtx[0]))
        self.mtx = mtx_copy
        t2 = datetime.datetime.now()
        TIME_SUM = TIME_SUM + (t2 - t1).microseconds


# class OptimizeTree:
#

    # def density_update(self):
    #     den = 0
    #     for i in range(len(self.mtx_save)):
    #         den = den + np.sum(self.mtx_save[i]) / self.area
    #     self.density = den / len(self.mtx_save)