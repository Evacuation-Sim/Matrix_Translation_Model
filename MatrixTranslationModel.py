import numpy as np
import copy
import random
import matplotlib.pyplot as plt
import json
import DataStructure as DS
import ShortestPath as SP
import RealTimeDis as RTD
# 全局字体设置为Times New Roman
plt.rc('font', family='Times New Roman')


def empty_delete(spath):
    sp = copy.deepcopy(spath)
    res = []
    for i in range(len(sp)):
        if not (sp[i][4] == 0 and sp[i][5] == 0):
            res.append(spath[i])
    return res

# 查看系统中有多少个人
def empty_check(edge_list):
    ped_sum = 0
    for i in range(len(edge_list)):
        ped_sum = ped_sum + np.sum(edge_list[i].mtx)
        # 保存每条边的运算记录
        mtx_temp = copy.deepcopy(edge_list[i].mtx)
        edge_list[i].mtx_save.append(mtx_temp)
    return ped_sum

# 将所有边上的人数记录下来
def arc_save(edge_list):
    dict = {}
    print("正在保存json文件！")
    for i in range(len(edge_list)):
        A_list_i = []
        A_name = str(edge_list[i].ns) + "_" + str(edge_list[i].ne) + "_" + str(edge_list[i].floor_num)
        for j in range(len(edge_list[i].mtx_save)):
            A_list_j = []
            for k in range(len(edge_list[i].mtx_save[j])):
                A_list_j.append(list(edge_list[i].mtx_save[j][k]))
            A_list_i.append(A_list_j)
        dict[A_name] = A_list_i
    file_name = open("save.json", 'w')
    json.dump(dict, file_name)


def network_init(nw):
    node_list = []
    edge_list = []
    for i in range(len(nw.floor_dict)):
        for j in range(len(nw.floor_dict[i].nodes)):
            node_list.append(nw.floor_dict[i].nodes[j])

        for j in range(len(nw.floor_dict[i].edges)):
            edge_list.append(nw.floor_dict[i].edges[j])

    for i in range(len(edge_list)):
        edge_list[i].mtx_init()

    edge_dict = {}
    for i in range(len(edge_list)):
        name = str(edge_list[i].ns) + "_" + str(edge_list[i].ne)
        di = {name: edge_list[i]}
        edge_dict.update(di)

    # 2. 确定每个节点的流入边和流出边
    for i in range(len(node_list)):
        for j in range(len(nw.shortest_path)):
            if node_list[i].num == nw.shortest_path[j][0]:
                name_ej = str(nw.shortest_path[j][0]) + "_" + str(nw.shortest_path[j][1])
                edge_ej = edge_dict[name_ej]
                node_list[i].edge_down.append(edge_ej)
                node_list[i].node_down.append(nw.shortest_path[j][1])
            elif node_list[i].num == nw.shortest_path[j][1]:
                name_ej = str(nw.shortest_path[j][0]) + "_" + str(nw.shortest_path[j][1])
                edge_ej = edge_dict[name_ej]
                node_list[i].edge_up.append(edge_ej)
                node_list[i].node_up.append(nw.shortest_path[j][0])

    return node_list, edge_list


def dict_init(node_list, edge_list):
    node_dict = {}
    edge_dict = {}
    for i in range(len(node_list)):
        di = {node_list[i].num: node_list[i]}
        node_dict.update(di)
    for i in range(len(edge_list)):
        name = str(edge_list[i].ns) + "_" + str(edge_list[i].ne)
        di = {name: edge_list[i]}
        edge_dict.update(di)
    return node_dict, edge_dict


# 计算从任一节点到出口的距离
def dist_solve(node, node_dict, edge_dict):
    dist = 0
    node_now = node
    while 1:
        try:
            node_next = node_dict[node_now.node_down[0]]
            edge_name = str(node_now.num) + "_" + str(node_next.num)
            edge_now = edge_dict[edge_name]
            dist = dist + edge_now.l
            node_now = node_next
        except IndexError:
            break
    return dist


# 获取列表的第二个元素
def take_second(elem):
    return elem[1]


def order_init(node_list, node_dict, edge_dict):
    dist_list = []
    for i in range(len(node_list)):
        dist = dist_solve(node_list[i], node_dict, edge_dict)
        dist_list.append([i, dist])
    dist_list.sort(key=take_second)
    update_list = []
    for i in range(len(dist_list)):
        update_list.append(node_list[dist_list[i][0]])

    # 将源点设置为不活跃节点
    for i in range(len(node_list)):
        # 将源点设置为不活跃节点
        if not node_list[i].node_up:
            node_list[i].active = 0
        else:
            for j in range(len(node_list[i].node_up)):
                nd = node_dict[node_list[i].node_up[j]]
                node_list[i].node_up_list.append(nd)
    return update_list

def density_update(edge_list):
    for i in range(len(edge_list)):
        den = 0
        for j in range(len(edge_list[i].mtx_save)):
            den = den + np.sum(edge_list[i].mtx_save[j]) / edge_list[i].area
        edge_list[i].density = den / len(edge_list[i].mtx_save)


def sim_init(node_list, edge_list):
    # 初始化边和节点的属性
    for i in range(len(node_list)):
        node_list[i].edge_up = []
        node_list[i].edge_down = []
        node_list[i].node_up = []
        node_list[i].node_down = []
        node_list[i].node_up_list = []
        node_list[i].active = 1
    for i in range(len(edge_list)):
        edge_list[i].mtx_save = []
        edge_list[i].mtx = []
        edge_list[i].time = 0

def real_time_dis(edge_list, node_list, fn, tn):
    mtx_fn = {}
    for i in range(len(edge_list)):
        if edge_list[i].floor_num == fn:
            mtx_name = str(edge_list[i].ns) + "_" + str(edge_list[i].ne)
            mtx_fn[mtx_name] = edge_list[i].mtx
    node_list_fn = []
    for i in range(len(node_list)):
        if node_list[i].floor_num == fn:
            node_list_fn.append(node_list[i])
    Ax_0, Ay_0, Ax_1, Ay_1, Nx, Ny = RTD.real_time_display(mtx_fn, node_list_fn)
    plt.cla()
    plt.scatter(Ax_0, Ay_0, s=2, c='gray', marker="s")
    plt.scatter(Ax_1, Ay_1, s=2, c='r', label="Occupants")
    plt.scatter(Nx, Ny, s=5, c='b', alpha=0.5, marker="*", label="Nodes")
    plt.text(500, 700, str(round(tn))+" s")
    plt.xlim([50, 950])
    plt.ylim([50, 750])
    plt.gca().invert_yaxis()
    plt.xlabel("Length (m)")
    plt.ylabel("Width (m)")
    # plt.axis('off')
    plt.legend()
    plt.pause(0.5)


# 平移矩阵模型
def transition_matrix(nw):
    # 初始化网络模型：生成节点和边列表，每条边生成矩阵，根据最短路径为每个节点更新上游节点
    node_list, edge_list = network_init(nw)


    # 新建根据名字查找边的字典
    node_dict, edge_dict = dict_init(node_list, edge_list)

    # 确定各节点更新顺序
    update_list = order_init(node_list, node_dict, edge_dict)

    # 更新
    t, n = [], []
    time = 0
    flag_end = 100

    iters = 0
    time_sum = 0
    while flag_end:
        for i in range(len(update_list)):
            if update_list[i].active:
                time_sum = time_sum + update_list[i].update(time)
        time = time + DS.DELTA_T
        if iters % 10 == 0:
            flag_end = empty_check(edge_list)
            t.append(time)
            n.append(flag_end)
        iters = iters + 1
    # arc_save(edge_list)
    sim_init(node_list, edge_list)
    return t, n, time_sum

# 平移矩阵模型
def transition_matrix_vis(nw):
    # 初始化网络模型：生成节点和边列表，每条边生成矩阵，根据最短路径为每个节点更新上游节点
    node_list, edge_list = network_init(nw)

    # 新建根据名字查找边的字典
    node_dict, edge_dict = dict_init(node_list, edge_list)

    # 确定各节点更新顺序
    update_list = order_init(node_list, node_dict, edge_dict)

    # 更新
    t, n = [], []
    time = 0
    flag_end = 100

    # 实时显示某一段路径
    plt.figure(figsize=(8, 5))
    plt.ion()
    iters = 0
    time_sum = 0
    while flag_end:
        for i in range(len(update_list)):
            if update_list[i].active:
                time_sum = time_sum + update_list[i].update(time)
            # else:
            #     print(update_list[i].num)
        time = time + DS.DELTA_T
        # display every ten times steps
        if iters % 10 == 0:
            flag_end = empty_check(edge_list)
            # 实时显示
            real_time_dis(edge_list, node_list, nw.find_floor_name(nw.floor_dict, nw.name_fi).num, time)
            t.append(time)
            n.append(flag_end)
        iters = iters + 1
    plt.close()
    arc_save(edge_list)
    density_update(edge_list)
    sim_init(node_list, edge_list)
    return t, n, time_sum

# 找到节点所在的子树，返回树的根节点名称
def find_tree(trees, node):
    tree_name = -1
    keys = trees.keys()
    for key in keys:
        tree = trees[key]
        if node in tree:
            tree_name = key
    return tree_name

# 求势能
def potential_solve(nw, tree_bridge):
    tree_potential = {}
    for i in range(len(nw.floor_dict)):
        for j in range(len(nw.floor_dict[i].nodes)):
            if nw.floor_dict[i].nodes[j].tp == 2:
                s = nw.floor_dict[i].nodes[j].num
                t = nw.floor_dict[i].nodes[j].out_time
                tree_potential[s] = t
    # print(tree_potential)
    t1 = tree_bridge[0]
    t2 = tree_bridge[1]
    pot_diff = tree_potential[t1] - tree_potential[t2]
    return pot_diff, tree_potential

# 路径层面优化
def PathOptimize(nw):
    # 1. 将节点按子树分类
    node_list, edge_list = network_init(nw)
    shortest_path = nw.shortest_path
    trees = {}
    times = {}
    for i in range(len(node_list)):
        if node_list[i].tp == 2:
            s = node_list[i].num
            t = node_list[i].out_time
            node_list[i].out_time = 0
            tree_i = []
            node_up = node_list[i].node_up
            tree_i = tree_i + node_up
            while node_up:
                node_up_temp = []
                for j in node_up:
                    for k in range(len(node_list)):
                        if node_list[k].num == j:
                            node_up_temp = node_up_temp + node_list[k].node_up
                tree_i = tree_i + node_up_temp
                node_up = node_up_temp
            trees[s] = tree_i
            times[s] = t

    # 2. 找到桥边：不在树中，且两端节点属于不同的树
    bridge = []
    pot_diff = []
    tree_bridge = []
    for i in range(len(edge_list)):
        flag_in = 0
        for j in range(len(shortest_path)):
            if edge_list[i].ns == shortest_path[j][0] and edge_list[i].ne == shortest_path[j][1] or edge_list[i].ns == \
                    shortest_path[j][1] and edge_list[i].ne == shortest_path[j][0]:
                flag_in = 1
        if flag_in == 0:
            t1 = find_tree(trees, edge_list[i].ns)
            t2 = find_tree(trees, edge_list[i].ne)
            if t1 >= 0 and t2 >= 0 and t1 != t2:
                p1 = times[t1]
                p2 = times[t2]
                if p1 >= p2:
                    bridge.append([edge_list[i].ns, edge_list[i].ne])
                    pot_diff.append(p1 - p2)
                    tree_bridge.append([t1, t2])
                else:
                    bridge.append([edge_list[i].ne, edge_list[i].ns])
                    pot_diff.append(p2 - p1)
                    tree_bridge.append([t2, t1])

    # 3. 选取桥边：选取差值最大的桥边，调整起始节点
    max_index = pot_diff.index(max(pot_diff))
    node_high = bridge[max_index][0]
    node_low = bridge[max_index][1]

    # 4. 路径调整：更新节点的上下游关系
    for i in range(len(nw.floor_dict)):
        for j in range(len(nw.floor_dict[i].nodes)):
            if nw.floor_dict[i].nodes[j].num == node_high:
                nw.floor_dict[i].nodes[j].node_down = [node_low]
        for j in range(len(nw.floor_dict[i].edges)):
            if nw.floor_dict[i].edges[j].ns == bridge[max_index][1] and nw.floor_dict[i].edges[j].ne == \
                    bridge[max_index][0]:
                nw.floor_dict[i].edges[j].ns, nw.floor_dict[i].edges[j].ne = node_high, node_low


    sp = copy.deepcopy(nw.shortest_path)
    nd = [node_high, node_low]
    for i in range(len(nw.shortest_path)):
        if nw.shortest_path[i][0] == node_high:
            nw.shortest_path[i][1] = node_low

    sim_init(node_list, edge_list)
    return tree_bridge[max_index], pot_diff[max_index], sp, nd

def NodeOptimize(nw, shortest_path, node_hl, tree_bridge):
    nw.shortest_path = shortest_path
    nw.shortest_path.append(node_hl)
    for i in range(len(nw.shortest_path)):
        for j in range(len(nw.floor_dict)):
            for k in range(len(nw.floor_dict[j].edges)):
                if nw.floor_dict[j].edges[k].ns == nw.shortest_path[i][1] and nw.floor_dict[j].edges[k].ne == \
                        nw.shortest_path[i][0]:
                    nw.floor_dict[j].edges[k].ns, nw.floor_dict[j].edges[k].ne = nw.shortest_path[i][0], nw.shortest_path[i][1]

    print(node_hl)
    # 5. 调整节点
    t_list, n_list, rt_list = [], [], []
    while 1:
        for i in range(len(nw.floor_dict)):
            for j in range(len(nw.floor_dict[i].nodes)):
                if nw.floor_dict[i].nodes[j].num == node_hl[0]:
                    nw.floor_dict[i].nodes[j].dist_rate = nw.floor_dict[i].nodes[j].dist_rate + 0.1

        t, n, rt = transition_matrix(nw)
        t_list.append(t)
        n_list.append(n)
        rt_list.append(rt)
        if potential_solve(nw, tree_bridge) < 0:
            break

    return t_list, n_list, rt_list

def path_plot(nw, sp1, sp2):
    plt.figure(figsize=(10, 6))
    nodes = nw.floor_dict[0].nodes

    plt.subplot(2, 1, 1)
    for i in range(len(nodes)):
        if nodes[i].tp == 0:
            plt.scatter(nodes[i].x, nodes[i].y, s=20, marker='s', c='r', alpha=0.8)
        elif nodes[i].tp == 1:
            plt.scatter(nodes[i].x, nodes[i].y, s=20, c='b', alpha=0.8)
        elif nodes[i].tp == 2:
            plt.scatter(nodes[i].x, nodes[i].y, s=20, c='g', alpha=0.8)

    for i in range(len(sp1)):
        node_1 = []
        node_2 = []
        pi = sp1[i]
        for n in range(len(nodes)):
            if nodes[n].num == pi[0]:
                node_1 = nodes[n]
            if nodes[n].num == pi[1]:
                node_2 = nodes[n]
        plt.arrow(node_1.x, node_1.y, node_2.x-node_1.x, node_2.y-node_1.y, color='k', length_includes_head=True,
                  width=0.5, head_width=5, head_length=8, alpha=1)
    plt.gca().invert_yaxis()
    plt.axis('off')
    plt.title('(a)')

    plt.subplot(2, 1, 2)
    for i in range(len(nodes)):
        if nodes[i].tp == 0:
            plt.scatter(nodes[i].x, nodes[i].y, s=20, marker='s', c='r', alpha=0.8)
        elif nodes[i].tp == 1:
            plt.scatter(nodes[i].x, nodes[i].y, s=20, c='b', alpha=0.8)
        elif nodes[i].tp == 2:
            plt.scatter(nodes[i].x, nodes[i].y, s=20, c='g', alpha=0.8)

    for i in range(len(sp2)):
        node_1 = []
        node_2 = []
        pi = sp2[i]
        for n in range(len(nodes)):
            if nodes[n].num == pi[0]:
                node_1 = nodes[n]
            if nodes[n].num == pi[1]:
                node_2 = nodes[n]
        plt.arrow(node_1.x, node_1.y, node_2.x - node_1.x, node_2.y - node_1.y, color='k', length_includes_head=True,
                  width=0.5, head_width=5, head_length=8, alpha=1)
    plt.gca().invert_yaxis()
    plt.axis('off')
    plt.title('(b)')

    plt.show()

    # 平移矩阵模型的优化
# nw: 建筑网络结构
def optimizing(nw):
    flag = 1
    t_list, n_list, sp_list, nd_list, tb_list, tp_list = [], [], [], [], [], []
    run_time = 0
    # 迭代次数
    it = 1
    while flag:
        print("Number of iterations: " + str(it))
        tb, pd1, sp, nd = PathOptimize(nw)
        t, n, rt = transition_matrix(nw)
        t_list.append(t)
        n_list.append(n)
        sp_list.append(sp)
        nd_list.append(nd)
        tb_list.append(tb)
        pd2, tp = potential_solve(nw, tb)
        tp_list.append(tp)
        run_time = run_time + rt
        it = it + 1
        if pd2 < 0 and pd1 > 0:
            break

    print(run_time)
    # path_plot(nw, sp_list[0], sp_list[-1])
    # # # 第二轮节点层面循环
    # t_list, n_list, rt_list = NodeOptimize(nw, sp_list[-1], nd_list[-1], tb_list[-1])
    # 图示优化过程


    plt.figure(figsize=(10, 4))
    # 优化过程图示
    plt.subplot(1, 2, 1)
    for i in range(len(t_list)):
        if i == 0:
            plt.plot(t_list[i], n_list[i], linestyle=':', c='k', label="Initial")
        elif i == 1:
            plt.plot(t_list[i], n_list[i], linestyle='-.', c='k', label="Optimize", alpha=0.5)
        elif i == len(t_list) - 1:
            plt.plot(t_list[i], n_list[i], linestyle='--', c='r', label="$p^{s'}<0$")
        elif i == len(t_list) - 2:
            plt.plot(t_list[i], n_list[i], linestyle='-', c='k', label='Result')
        else:
            plt.plot(t_list[i], n_list[i], linestyle='-.', c='k', alpha=0.5)
    plt.legend()
    plt.xlabel("Time(s)")
    plt.ylabel("Occupant Number")
    plt.title('(a)')

    # 出口使用图示
    plt.subplot(1, 2, 2)
    exit1 = []
    exit2 = []
    exit3 = []
    for i in range(len(tp_list)):
        exit1.append(tp_list[i][97])
        exit2.append(tp_list[i][98])
        exit3.append(tp_list[i][99])
    n = range(1, len(exit1)+1)
    plt.plot(n, exit1, linestyle='-', label="Exit 1")
    plt.plot(n, exit2, linestyle='--', label="Exit 2")
    plt.plot(n, exit3, linestyle='-.', label="Exit 3")
    plt.legend()
    plt.ylabel("Clear Time(s)")
    plt.xlabel("Number of Iterations")
    plt.title('(b)')
    plt.subplots_adjust(left=0.1, right=0.95, wspace=0.3, hspace=0.5)
    plt.show()
    return 0



