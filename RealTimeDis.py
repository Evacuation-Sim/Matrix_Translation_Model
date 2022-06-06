import json
import matplotlib.pyplot as plt
import math
import numpy as np

# 计算两三维向量的叉乘结果
def cross_vector(a, b):
    vector3 = [a[1] * b[2] - b[1] * a[2], a[2] * b[0] - b[2] * a[1], a[0] * b[1] - a[1] * b[0]]
    return vector3

# 求两二维向量顺时针方向夹角，从a到b
def angle_360(a, b):
    a = list(a) + [0]
    b = list(b) + [0]
    aa = np.array(a)
    bb = np.array(b)

    x1 = cross_vector(aa, bb)

    if x1[2] < 0:
        angle = math.acos(aa.dot(bb) / (np.linalg.norm(aa) * np.linalg.norm(bb)))*180 / np.pi
    elif x1[2] > 0:
        angle = 360 - math.acos(aa.dot(bb) / (np.linalg.norm(aa) * np.linalg.norm(bb))) * 180 / np.pi
    else:
        if a[0] * b[0] > 0 or a[1] * b[1] > 0:
            angle = 0
        else:
            angle = 180

    return angle

# vector a, length of vector b: b_l, the angle between a and b: a_b
def vector_rotate(a, a_b, b_l = 1):
    # rotate the vector a by angle a_b, at last adjust the length to b_l
    dir_a = angle_360([0, 1], a)
    dir_b = dir_a + a_b
    b = [math.sin(dir_b / 180 * math.pi) * b_l, math.cos(dir_b / 180 * math.pi) * b_l]
    return b




def real_time_display(frame_dict, node_list):
    # 读取node
    node_dict = {}
    for i in range(len(node_list)):
        node_name = str(node_list[i].num)
        node_pos = [node_list[i].x, node_list[i].y]
        node_dict[node_name] = node_pos

    Ax_0 = []
    Ay_0 = []
    Ax_1 = []
    Ay_1 = []

    Nx = []
    Ny = []

    # 矩阵操作
    data = frame_dict
    ks = list(data.keys())

    for i in range(len(data)):
        A = data[ks[i]]
        L, W = len(A), len(A[0])

        name = ks[i]
        node_1 = name.split('_')[0]
        node_2 = name.split('_')[1]
        # 获取两个端点的坐标
        pos_1 = node_dict[node_1]
        pos_2 = node_dict[node_2]
        Nx.append(pos_1[0])
        Nx.append(pos_2[0])
        Ny.append(pos_1[1])
        Ny.append(pos_1[1])

        x_s = pos_1[0]
        y_s = pos_1[1]
        x_delta = pos_2[0] - pos_1[0]
        y_delta = pos_2[1] - pos_1[1]
        st = math.sqrt(x_delta * x_delta + y_delta * y_delta)
        Lb = st / L
        v1 = [0, 1]
        v2 = [x_delta, y_delta]
        alpha = angle_360(v1, v2)

        for j in range(len(A)):
            for k in range(len(A[j])):
                # 生成x,y
                x = k - W / 2
                y = j
                # 伸缩
                x1 = x
                y1 = y * Lb
                l = math.sqrt(x1 * x1 + y1 * y1)

                # 旋转
                [x2, y2] = vector_rotate([x1, y1], alpha, l)
                # 平移
                x3 = x2 + x_s
                y3 = y2 + y_s

                if A[j][k] == 0:
                    Ax_0.append(x3)
                    Ay_0.append(y3)
                else:
                    Ax_1.append(x3)
                    Ay_1.append(y3)
    return Ax_0, Ay_0, Ax_1, Ay_1, Nx, Ny


