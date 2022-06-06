import tkinter
import tkinter.simpledialog
import tkinter.colorchooser
import tkinter.filedialog

import numpy as np
from PIL import Image, ImageTk, ImageGrab
import time
from tkinter import *
from tkinter import ttk
import copy
import ShortestPath as SP
import DataStructure as DS
import MatrixTranslationModel as TM
from tkinter.messagebox import showinfo, showwarning, showerror
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
from matplotlib.patches import FancyArrowPatch
from mpl_toolkits.mplot3d import proj3d
import datetime


class Arrow3D(FancyArrowPatch):
    def __init__(self, xs, ys, zs, *args, **kwargs):
        FancyArrowPatch.__init__(self, (0,0), (0,0), *args, **kwargs)
        self._verts3d = xs, ys, zs

    def draw(self, renderer):
        xs3d, ys3d, zs3d = self._verts3d
        xs, ys, zs = proj3d.proj_transform(xs3d, ys3d, zs3d, renderer.M)
        self.set_positions((xs[0], ys[0]), (xs[1], ys[1]))
        FancyArrowPatch.draw(self, renderer)

class MyApp():
    def __init__(self):
        root = Tk()
        self.w = root
        # 程序参数/数据
        # 控制是否允许画图的变量，1：允许，0：不允许
        self.yesno = tkinter.IntVar(value=0)
        # 控制画图类型的变量，1：曲线，2：直线，3：矩形，4：文本，5：橡皮 6：圆形
        self.what = tkinter.IntVar(value=1)
        # 记录鼠标位置的变量
        self.X = tkinter.IntVar(value=0)
        self.Y = tkinter.IntVar(value=0)

        # 临时存储变量
        self.sle_grid = []
        self.edgeInfo_temp = [0, 0, 0, 0, 0]
        self.basic_draw = []
        # 前景色
        self.foreColor = '#000001'
        self.backColor = '#FFFFFF'
        # 程序界面
        self.setupUI()
        self.createMenu()
        self.createFunc()
        root.mainloop()

    def setupUI(self):
        # 创建画布
        # image = tkinter.PhotoImage()
        self.w.title('Matrix Translation Model-V1.0')
        self.w.geometry('1200x650')
        self.w.canvas = tkinter.Canvas(self.w, bg='white', width=1000, height=600)
        # 画布上增加参考点
        for i in range(0, 1000, 20):
            for j in range(0, 600, 20):
                self.basic_draw.append(self.w.canvas.create_oval(i - 1, j - 1, i + 1, j + 1, outline=self.foreColor, fill=self.foreColor))
        # 参考点行和列的编号
        for i in range(0, 1000, 20):
            for j in range(0, 600, 20):
                if j == 0 and i > 0:
                    self.basic_draw.append(self.w.canvas.create_text(i, j + 10, text=str(int(i / 20))))
                if i == 0 and j > 0:
                    self.basic_draw.append(self.w.canvas.create_text(i + 10, j, text=str(int(j / 20))))

        # 记录最后绘制图形的id
        self.lastDraw = 0
        self.end = [0]  # 每次抬起鼠标时，最后一组图形的编号
        self.size = "20"  # 初始字号
        self.w.canvas.bind('<Button-1>', self.onLeftButtonDown)  # 单击左键
        self.w.canvas.bind('<B1-Motion>', self.onLeftButtonMove)  # 按住并移动左键
        self.w.canvas.bind('<ButtonRelease-1>', self.onLeftButtonUp)  # 释放左键
        self.w.canvas.bind('<ButtonRelease-3>', self.onRightButtonUp)  # 释放右键
        self.w.canvas.bind('<Motion>', self.onMove)  # 释放右键
        self.w.canvas.place(x=150, y=0)
        # canvas.pack(fill=tkinter.BOTH, expand=tkinter.NO)


    def createMenu(self):
        '''主菜单及其关联的函数'''
        menu = Menu(self.w)
        menu.add_command(label='Clear', command=self.Clear)
        menu.add_command(label='Cancle', command=self.Back)
        menu.add_command(label='Save', command=self.Save)
        menu.add_command(label='Load', command=self.Load)
        menu.add_separator()  # 添加分割线
        self.w.config(menu=menu)

    def createFunc(self):
        # 楼层选择
        lf = LabelFrame(self.w, width=100, height=100, text="Floor")
        # lf.pack(padx=15, pady=8, side=TOP)
        lf.place(x=10, y=0)
        top_frame = Frame(lf)
        top_frame.pack(expand=False, side=TOP, padx=15, pady=8)

        # 当前楼层
        self.floors = []
        self.cbx = ttk.Combobox(top_frame, values=self.floors, width=10)
        self.cbx.bind("<<ComboboxSelected>>", self.cbxSelect)  # 绑定事件,(下拉列表框被选中时，绑定go()函数)
        self.cbx.grid(row=2, column=1, columnspan=2)
        Label(top_frame, text="Current Floor：").grid(row=1, column=1, columnspan=2, sticky=W)

        # 新建楼层
        self.img01 = PhotoImage(file='./LOGO/新建楼层.png')  # 此处必须设为全局变量
        Button(top_frame, text="新建楼层", fg="blue", bd=2, width=28, command=self.newFloor, image=self.img01) \
            .grid(row=3, column=1, sticky=W)
        Label(top_frame, text="New Floor").grid(row=3, column=2, sticky=W)

        # 复制楼层
        self.img02 = PhotoImage(file='./LOGO/复制楼层.png')  # 此处必须设为全局变量
        Button(top_frame, text="复制楼层", fg="blue", bd=2, width=28, command=self.copyFloor, image=self.img02) \
            .grid(row=4, column=1, sticky=W)
        Label(top_frame, text="Copy Floor").grid(row=4, column=2, sticky=W)

        # 保存楼层
        self.img03 = PhotoImage(file='./LOGO/保存楼层.png')  # 此处必须设为全局变量
        Button(top_frame, text="保存楼层", fg="blue", bd=2, width=28, command=self.saveFloor, image=self.img03) \
            .grid(row=5, column=1, sticky=W)
        Label(top_frame, text="Save Floor").grid(row=5, column=2, sticky=W)

        # 加载楼层
        self.img04 = PhotoImage(file='./LOGO/加载楼层.png')  # 此处必须设为全局变量
        Button(top_frame, text="加载楼层", fg="blue", bd=2, width=28, command=self.loadFloor, image=self.img04) \
            .grid(row=6, column=1, sticky=W)
        Label(top_frame, text="Load Floor").grid(row=6, column=2, sticky=W)

        # 网络生成
        lf = LabelFrame(self.w, width=100, height=500, text="Network")
        # lf.pack(padx=15, pady=8, side=TOP)
        lf.place(x=10, y=180)

        top_frame = Frame(lf)
        top_frame.pack(expand=False, side=TOP, padx=15, pady=8)
        # 1参考线绘制
        self.img1 = PhotoImage(file='./LOGO/参考线.png') # 此处必须设为全局变量
        Button(top_frame, text="参考线", fg="blue", bd=2, width=28, command=self.drawCurve, image=self.img1)\
            .grid(row=1, column=1, sticky=W)
        Label(top_frame, text="Refline").grid(row=1, column=2, sticky=W)
        # 2绘制发点
        self.img2 = PhotoImage(file='./LOGO/发点.png')  # 此处必须设为全局变量
        Button(top_frame, text="发 点", fg="blue", bd=2, width=28, command=self.drawStartNode, image=self.img2) \
            .grid(row=2, column=1, sticky=W)
        Label(top_frame, text="Souc Node").grid(row=2, column=2, sticky=W)
        # 3绘制中间节点
        self.img3 = PhotoImage(file='./LOGO/中间节点.png')  # 此处必须设为全局变量
        Button(top_frame, text="中间节点", fg="blue", bd=2, width=28, command=self.drawIntNode, image=self.img3) \
            .grid(row=3, column=1, sticky=W)
        Label(top_frame, text="Iter Node").grid(row=3, column=2, sticky=W)
        # 4绘制收点
        self.img4 = PhotoImage(file='./LOGO/收点.png')  # 此处必须设为全局变量
        Button(top_frame, text="收 点", fg="blue", bd=2, width=28, command=self.drawEndNode, image=self.img4) \
            .grid(row=4, column=1, sticky=W)
        Label(top_frame, text="Sink Node").grid(row=4, column=2, sticky=W)

        # 5绘制楼层连接点
        self.img5 = PhotoImage(file='./LOGO/虚拟节点.png')  # 此处必须设为全局变量
        Button(top_frame, text="连接节点", fg="blue", bd=2, width=28, command=self.cnctNode, image=self.img5) \
            .grid(row=5, column=1, sticky=W)
        Label(top_frame, text="Virt Node").grid(row=5, column=2, sticky=W)

        # 6删除节点
        self.img6 = PhotoImage(file='./LOGO/删除节点.png')  # 此处必须设为全局变量
        Button(top_frame, text="删除节点", fg="blue", bd=2, width=28, command=self.deleNode, image=self.img6) \
            .grid(row=6, column=1, sticky=W)
        Label(top_frame, text="Dele Node").grid(row=6, column=2, sticky=W)
        # 7添加无向边
        self.img7 = PhotoImage(file='./LOGO/无向边.png')  # 此处必须设为全局变量
        Button(top_frame, text="无向边", fg="blue", bd=2, width=28, command=self.addEdge, image=self.img7) \
            .grid(row=7, column=1, sticky=W)
        Label(top_frame, text="Edge").grid(row=7, column=2, sticky=W)
        # 8删除边
        self.img8 = PhotoImage(file='./LOGO/删除边.png')  # 此处必须设为全局变量
        Button(top_frame, text="删除边", fg="blue", bd=2, width=28, command=self.deleEdge, image=self.img8) \
            .grid(row=8, column=1, sticky=W)
        Label(top_frame, text="Dele Edge").grid(row=8, column=2, sticky=W)

        self.img9 = PhotoImage(file='./LOGO/生成路径.png')  # 此处必须设为全局变量
        Button(top_frame, text="确定", fg="blue", bd=2, width=28, command=self.netGenerate, image=self.img9) \
            .grid(row=9, column=1, sticky=W)
        Label(top_frame, text="Inti Ntk").grid(row=9, column=2, sticky=W)


        # 网络生成
        lf = LabelFrame(self.w, width=100, height=500, text="Simulation")
        # lf.pack(padx=15, pady=8, side=TOP)
        lf.place(x=10, y=440)

        bot_frame = Frame(lf)
        bot_frame.pack(expand=False, side=TOP, padx=15, pady=8)

        self.disp_flag = IntVar()
        self.disp_flag.set(0)
        Checkbutton(bot_frame, variable=self.disp_flag, onvalue=1, offvalue=0) \
            .grid(row=1, column=1, sticky=W)
        Label(bot_frame, text="Display").grid(row=1, column=2, sticky=W)

        self.img10 = PhotoImage(file='./LOGO/开始.png')  # 此处必须设为全局变量
        Button(bot_frame, text="开始", fg="blue", bd=2, width=28, command=self.runTransM, image=self.img10) \
            .grid(row=2, column=1, sticky=W)
        Label(bot_frame, text="Run MTM").grid(row=2, column=2, sticky=W)

        self.img11 = PhotoImage(file='./LOGO/优化.png')  # 此处必须设为全局变量
        Button(bot_frame, text="开始", fg="blue", bd=2, width=28, command=self.optTransM, image=self.img11) \
            .grid(row=3, column=1, sticky=W)
        Label(bot_frame, text="Optimize").grid(row=3, column=2, sticky=W)


    # 添加绘图菜单
    # 添加菜单，清除
    def Clear(self):
        for item in self.w.canvas.find_all():
            self.w.canvas.delete(item)
        self.end = [0]
        self.lastDraw = 0

    # 撤销
    def Back(self):
        try:
            for i in range(self.end[-2], self.end[-1] + 1):  # 要包含最后一个点，否则无法删除图形
                self.w.canvas.delete(i)
            self.end.pop()  # 弹出末尾元素
        except:
            self.end = [0]

    # 保存地图
    def Save(self):
        global nw
        time.sleep(0.5)  # 等待一会，否则会把点击“保存”那一刻也存进去

        # 保存node，edge，path
        filename = tkinter.filedialog.asksaveasfilename(defaultextension='.tm',
                                                        initialdir='.\\')
        file = open(filename, 'w')
        file.write('\n')
        for i in range(len(nw.floor_dict)):
            file.write("FLOOR NAME:" + nw.floor_dict[i].name + '\n')
            file.write("FLOOR NUM:" + str(nw.floor_dict[i].num) + '\n')
            file.write("FLOOR NODES:" + str(len(nw.floor_dict[i].nodes)) + '\n')
            for j in range(len(nw.floor_dict[i].nodes)):
                node_j = nw.floor_dict[i].nodes[j]
                node_save = [node_j.x, node_j.y, node_j.num, node_j.tp, node_j.is_shadow]
                file.write(str(node_save) + '\n')
            file.write("FLOOR EDGES:" + str(len(nw.floor_dict[i].edges)) + '\n')
            for j in range(len(nw.floor_dict[i].edges)):
                edge_j = nw.floor_dict[i].edges[j]
                edge_save = [edge_j.ns, edge_j.ne, edge_j.l, edge_j.w, edge_j.pn, edge_j.pt, edge_j.tp]
                file.write(str(edge_save) + '\n')
            file.write('\n')

        file.write("END OF TMFILE!"+'\n')
        file.write("This is a .tm file of TransitionMatrix Model developed by Dr. Zhongyi Huang." + '\n')
        file.write("All rights reserved." + '\n')
        file.close()

    # 加载地图
    def Load(self):
        global nw
        filename = tkinter.filedialog.askopenfilename(defaultextension='.tm',
                                                        initialdir='.\\map\\')
        # 读入Node,Edge和Path
        with open(filename, "r") as f:
            flines = f.readlines()
            floor_name = ""
            for i in range(len(flines)):
                line = flines[i].strip('\n')  # 去掉列表中每一个元素的换行符
                if "NAME" in line:
                    floor_name = line.split(':')[1]
                    nw.name_fi = floor_name
                    self.floors.append(floor_name)

                if "NUM" in line:
                    floor_num = int(line.split(':')[1])
                    # 先新建楼层
                    nw.new_floor(floor_name, floor_num)
                    # 加载该楼层
                    nw.load_floor(floor_name)

                if "NODE" in line:
                    node_num = int(line.split(':')[1])
                    for j in range(i + 1, i + node_num + 1):
                        line_j = flines[j].strip('\n')
                        node_j = eval(line_j)
                        x, y, num, type_, cid, is_shadow = node_j[0], node_j[1], node_j[2], node_j[3], [], node_j[4]
                        nw.add_node(x, y, num, type_, cid, is_shadow, floor_num)
                        if num > nw.node_sn:
                            nw.node_sn = num

                if "EDGE" in line:
                    edge_num = int(line.split(':')[1])
                    for j in range(i + 1, i + edge_num + 1):
                        line_j = flines[j].strip('\n')
                        edge_j = eval(line_j)
                        ns, ne, length, width, pedestrian_num, pre_time, type_, cid = edge_j[0], edge_j[1], edge_j[2], edge_j[3], edge_j[4], edge_j[5], edge_j[6], []
                        nw.add_edge(ns, ne, length, width, pedestrian_num, pre_time, type_,  cid, floor_num)

                    # 保存该楼层
                    nw.save_floor(floor_name)
        # 加载第一个楼层
        nw.node_sn = nw.node_sn + 1
        nw.name_fi = nw.floor_dict[0].name
        nw.node_fi = nw.find_floor_name(nw.floor_dict, nw.name_fi).nodes
        nw.edge_fi = nw.find_floor_name(nw.floor_dict, nw.name_fi).edges
        self.cbx["values"] = self.floors
        self.canvasFresh()
        self.loadFloor()

    # 刷新画布
    def canvasFresh(self, v_flag=0):
        # 按照楼层绘制节点和边
        for fi in self.floors:
            canvas_i = []
            # 绘制f_i楼层的节点
            floor_i = nw.find_floor_name(nw.floor_dict, fi)
            nodes = floor_i.nodes
            edges = floor_i.edges
            for i in range(len(nodes)):
                if nodes[i].tp == 0:
                    lastDraw = []
                    lastDraw.append(
                        self.w.canvas.create_rectangle(nodes[i].x - 5, nodes[i].y - 5, nodes[i].x + 5,
                                                       nodes[i].y + 5, width=0,
                                                       outline=self.foreColor, fill='red'))
                    lastDraw.append(self.w.canvas.create_text(nodes[i].x, nodes[i].y - 11, text=str(nodes[i].num)))
                    nodes[i].cid = lastDraw
                    canvas_i.append(lastDraw[0])
                    canvas_i.append(lastDraw[1])
                if nodes[i].tp == 1:
                    lastDraw = []
                    if nodes[i].is_shadow == 0:
                        lastDraw.append(self.w.canvas.create_oval(nodes[i].x - 5, nodes[i].y - 5, nodes[i].x + 5,
                                                              nodes[i].y + 5, width=0,
                                                              outline=self.foreColor, fill='blue'))
                    else:
                        lastDraw.append(self.w.canvas.create_oval(nodes[i].x - 5, nodes[i].y - 5, nodes[i].x + 5,
                                                                  nodes[i].y + 5, width=0,
                                                                  outline=self.foreColor, fill='yellow'))
                    lastDraw.append(self.w.canvas.create_text(nodes[i].x, nodes[i].y - 11, text=str(nodes[i].num)))
                    nodes[i].cid = lastDraw
                    canvas_i.append(lastDraw[0])
                    canvas_i.append(lastDraw[1])
                if nodes[i].tp == 2:
                    lastDraw = []
                    lastDraw.append(self.w.canvas.create_oval(nodes[i].x - 5, nodes[i].y - 5, nodes[i].x + 5,
                                                              nodes[i].y + 5, width=0,
                                                              outline=self.foreColor, fill='green'))
                    lastDraw.append(self.w.canvas.create_text(nodes[i].x, nodes[i].y - 11, text=str(nodes[i].num)))
                    nw.node_fi[i].cid = lastDraw
                    canvas_i.append(lastDraw[0])
                    canvas_i.append(lastDraw[1])
            for i in range(len(edges)):
                lastDraw = []
                node_1 = []
                node_2 = []
                for n in range(len(nodes)):
                    if nodes[n].num == edges[i].ns:
                        node_1 = nodes[n]
                    if nodes[n].num == edges[i].ne:
                        node_2 = nodes[n]
                if v_flag == 0:
                    lastDraw.append(self.w.canvas.create_line(node_1.x, node_1.y, node_2.x, node_2.y, width=2,
                                                              fill=self.foreColor))
                else:
                    lastDraw.append(self.w.canvas.create_line(node_1.x, node_1.y, node_2.x, node_2.y, width=2,
                                                              arrow=LAST, fill=self.foreColor))
                edges[i].cid = lastDraw
                canvas_i.append(lastDraw[0])
            floor_i.cids = canvas_i

    # 绘制新的
    def plotTree(self):
        plt.figure()
        # 按照楼层绘制节点和边
        for fi in self.floors:
            canvas_i = []
            # 绘制f_i楼层的节点
            floor_i = nw.find_floor_name(nw.floor_dict, fi)
            nodes = floor_i.nodes
            edges = nw.shortest_path
            for i in range(len(nodes)):
                if nodes[i].tp == 0:
                    plt.Rectangle((nodes[i].x - 5, nodes[i].y - 5), 5, 5, color='red')
                    plt.text(nodes[i].x, nodes[i].y - 11, s=str(nodes[i].num))
                if nodes[i].tp == 1:
                    plt.Rectangle((nodes[i].x - 5, nodes[i].y - 5), 5, 5, color='blue')
                    plt.text(nodes[i].x, nodes[i].y - 11, s=str(nodes[i].num))
                if nodes[i].tp == 2:
                    plt.Rectangle((nodes[i].x - 5, nodes[i].y - 5), 5, 5, color='green')
                    plt.text(nodes[i].x, nodes[i].y - 11, s=str(nodes[i].num))
            for i in range(len(edges)):
                node_1 = []
                node_2 = []
                for n in range(len(nodes)):
                    if nodes[n].num == edges[i][0]:
                        node_1 = nodes[n]
                    if nodes[n].num == edges[i][1]:
                        node_2 = nodes[n]
                plt.arrow(node_1.x, node_1.y, node_2.x-node_1.x, node_2.y-node_1.y, head_width=5)
        plt.show()

    # # 刷新画布
    # def canvasFresh(self):
    #     global nw
    #     self.w.canvas.delete('all')
    #     print("清除所有")
    #     for i in range(len(nw.node_fi)):
    #         if nw.node_fi[i].tp == 0:
    #             lastDraw = []
    #             lastDraw.append(self.w.canvas.create_rectangle(nw.node_fi[i].x-5, nw.node_fi[i].y-5, nw.node_fi[i].x+5, nw.node_fi[i].y+5,
    #                                                       outline=self.foreColor, fill='red'))
    #             lastDraw.append(self.w.canvas.create_text(nw.node_fi[i].x, nw.node_fi[i].y - 11, text=str(i)))
    #             nw.node_fi[i].cid = lastDraw
    #         if nw.node_fi[i].tp == 1:
    #             lastDraw = []
    #             lastDraw.append(self.w.canvas.create_oval(nw.node_fi[i].x-5, nw.node_fi[i].y-5, nw.node_fi[i].x+5, nw.node_fi[i].y+5,
    #                                                       outline=self.foreColor, fill='blue'))
    #             lastDraw.append(self.w.canvas.create_text(nw.node_fi[i].x, nw.node_fi[i].y - 11, text=str(i)))
    #             nw.node_fi[i].cid = lastDraw
    #         if nw.node_fi[i].tp == 2:
    #             lastDraw = []
    #             lastDraw.append(self.w.canvas.create_oval(nw.node_fi[i].x-5, nw.node_fi[i].y-5, nw.node_fi[i].x+5, nw.node_fi[i].y+5,
    #                                                       outline=self.foreColor, fill='green'))
    #             lastDraw.append(self.w.canvas.create_text(nw.node_fi[i].x, nw.node_fi[i].y - 11, text=str(i)))
    #             nw.node_fi[i].cid = lastDraw
    #         if nw.node_fi[i].tp == 3:
    #             lastDraw = []
    #             lastDraw.append(self.w.canvas.create_oval(nw.node_fi[i].x-5, nw.node_fi[i].y-5, nw.node_fi[i].x+5, nw.node_fi[i].y+5,
    #                                                       outline=self.foreColor, fill='yellow'))
    #             lastDraw.append(self.w.canvas.create_text(nw.node_fi[i].x, nw.node_fi[i].y - 11, text=str(i)))
    #             nw.node_fi[i].cid = lastDraw
    #     for i in range(len(nw.edge_fi)):
    #         lastDraw = []
    #         node_1 = nw.node_fi[nw.edge_fi[i][0]]
    #         node_2 = nw.node_fi[nw.edge_fi[i][1]]
    #         lastDraw.append(self.w.canvas.create_line(node_1[0], node_1[1], node_2[0], node_2[1], width=2,
    #                                              fill=self.foreColor))
    #         nw.edge_fi[i][6] = lastDraw

    # 加载画布
    def canvasLoad(self, floor_name):
        global nw
        # 隐藏上一楼层元素，加载当前楼层元素
        for item in self.w.canvas.find_all():
            if item not in self.basic_draw:
                self.w.canvas.itemconfig(item, state="hidden")
        canv = nw.find_floor_name(nw.floor_dict, floor_name).cids
        for i in range(len(canv)):
            self.w.canvas.itemconfig(canv[i], state="normal")

    # 选择当前楼层
    def cbxSelect(self, event):
        global nw
        nw.name_fi = self.cbx.get()
        self.canvasLoad(nw.name_fi)
        nw.load_floor(nw.name_fi)
        print("当前选择楼层及编号：", nw.name_fi, nw.find_floor_name(nw.floor_dict, nw.name_fi).num)

    # 新建楼层
    def newFloor(self):
        global nw
        # 先保存当前楼层
        if nw.name_fi != "":
            nw.save_floor(nw.name_fi)
        fd = FloorDialog()
        self.w.wait_window(fd)  # 这一句很重要！！！
        self.floors.append(fd.name)
        self.cbx["values"] = self.floors
        # 数据中新建该楼层
        nw.new_floor(fd.name, fd.num)
        return 0

    # 复制楼层
    def copyFloor(self):
        inputDialog = FloorDialog()
        self.w.wait_window(inputDialog)  # 这一句很重要！！！
        self.floors.append(nw.name_fi)
        return 0

    # 载入楼层
    def loadFloor(self):
        global nw
        nw.load_floor(nw.name_fi)
        # 显示更新
        self.canvasLoad(nw.name_fi)
        return 0

    # 保存楼层
    def saveFloor(self):
        global nw
        nw.save_floor(nw.name_fi)
        return 0

    # 鼠标左键单击，允许画图
    def onLeftButtonDown(self, event):
        self.yesno.set(1)
        self.X.set(event.x)
        self.Y.set(event.y)
        # if what.get() == 4:
        #     canvas.create_text(event.x, event.y, font=("微软雅黑", int(size)), text=text, fill=foreColor)
        #
        # elif what.get() == 7:
        #     global person_img, b
        #     person_img = tkinter.PhotoImage(file="personlogo.png")
        #     b = canvas.create_image(event.x, event.y, image=person_img, anchor='nw')
        #     what.set(0)

    # 按住鼠标左键移动
    def onLeftButtonMove(self, event):
        global lastDraw, nw
        # 删除节点
        if self.what.get() == 6:
            x = event.x
            y = event.y
            for i in range(len(nw.node_fi)):
                if abs(nw.node_fi[i].x - x) < 5 and abs(nw.node_fi[i].y - y) < 5:
                    self.w.canvas.itemconfig(nw.node_fi[i].cid[0], fill='white')
                    nw.node_dele.append(nw.node_fi[i].num)
        # 删除边
        elif self.what.get() == 7:
            x = event.x
            y = event.y
            for i in range(len(nw.node_fi)):
                if abs(nw.node_fi[i].x - x) < 5 and abs(nw.node_fi[i].y - y) < 5:
                    self.w.canvas.itemconfig(nw.node_fi[i].cid[0], fill='white')
                    # 将选中的节点进行记录
                    if len(nw.node_temp) == 0:
                        nw.node_temp.append(nw.node_fi[i])
                    else:
                        if nw.node_fi[i].cid != nw.node_temp[-1].cid:
                            nw.node_temp.append(nw.node_fi[i])

    # 鼠标左键抬起，完成画图
    def onLeftButtonUp(self, event):
        global lastDraw, nw
        # person_img = tkinter.PhotoImage(file="圆logo.png")
        if self.what.get() == 1:
            # 绘制参考线
            lastDraw = self.w.canvas.create_line(self.X.get(), self.Y.get(), event.x, event.y, fill=self.foreColor)

        elif self.what.get() == 2:
            # 绘制发点
            x = int(event.x / 20) * 20
            y = int(event.y / 20) * 20
            lastDraw = []
            lastDraw.append(self.w.canvas.create_rectangle(x - 5, y - 5, x + 5, y + 5, outline=self.foreColor,
                                               fill='red'))
            # 将发点添加至网络
            lastDraw.append(self.w.canvas.create_text(x, y-11, text=str(nw.node_sn)))
            floor_num = nw.find_floor_name(nw.floor_dict, nw.name_fi).num
            nw.add_node(x, y, nw.node_sn, 0, lastDraw, 0, floor_num)
            nw.node_sn = nw.node_sn + 1

        elif self.what.get() == 3:
            x = int(event.x / 20) * 20
            y = int(event.y / 20) * 20
            lastDraw = []
            lastDraw.append(self.w.canvas.create_oval(x - 5, y - 5, x + 5, y + 5, outline=self.foreColor,
                                          fill='blue'))
            # 将中间节点添加至网络
            lastDraw.append(self.w.canvas.create_text(x, y - 11, text=str(nw.node_sn)))
            floor_num = nw.find_floor_name(nw.floor_dict, nw.name_fi).num
            nw.add_node(x, y, nw.node_sn, 1, lastDraw, 0, floor_num)
            nw.node_sn = nw.node_sn + 1

        elif self.what.get() == 4:
            x = int(event.x / 20) * 20
            y = int(event.y / 20) * 20
            lastDraw = []
            lastDraw.append(self.w.canvas.create_oval(x - 5, y - 5, x + 5, y + 5, outline=self.foreColor,
                                          fill='green'))
            # 将收点添加至网络
            lastDraw.append(self.w.canvas.create_text(x, y - 11, text=str(nw.node_sn)))
            floor_num = nw.find_floor_name(nw.floor_dict, nw.name_fi).num
            nw.add_node(x, y, nw.node_sn, 2, lastDraw, 0, floor_num)
            nw.node_sn = nw.node_sn + 1

        elif self.what.get() == 5:
            # 上下层连接节点
            x = int(event.x / 20) * 20
            y = int(event.y / 20) * 20
            lastDraw = []
            lastDraw.append(self.w.canvas.create_oval(x - 5, y - 5, x + 5, y + 5, outline=self.foreColor,
                                                      fill='yellow'))
            # 通过弹窗获取该节点的连接编号
            nd = NodeDialog()
            self.w.wait_window(nd)  # 这一句很重要！！！
            cnum = nd.cnode
            # 标注上实际节点编号
            lastDraw.append(self.w.canvas.create_text(x, y - 11, text="REAL:"+str(cnum)))
            floor_num = nw.find_floor_name(nw.floor_dict, nw.name_fi).num
            nw.add_node(x, y, cnum, 1, lastDraw, 1, floor_num)
            nw.node_sn = nw.node_sn + 1

        elif self.what.get() == 6:
            # 删除节点以及与节点相连的边
            del_obj = []
            for i in range(len(nw.node_dele)):
                for j in range(len(nw.node_fi)):
                    if nw.node_dele[i] == nw.node_fi[j].num:
                        for k in range(len(nw.node_fi[j].cid)):
                            self.w.canvas.itemconfig(nw.node_fi[j].cid[k], state="hidden")
                        del_obj.append(nw.node_fi[j])
            # 删除与该节点相连的边
            for i in range(len(nw.node_dele)):
                for j in range(len(nw.edge_fi)):
                    if nw.node_dele[i] == nw.edge_fi[j].ns or nw.node_dele[i] == nw.edge_fi[j].ne:
                        for k in range(len(nw.edge_fi[j].cid)):
                            self.w.canvas.itemconfig(nw.edge_fi[j].cid[k], state="hidden")
                        del_obj.append(nw.edge_fi[j])
            del del_obj

        elif self.what.get() == 7:
            # 选择无向边选项
            # 选择最后两个临时存储的节点，生成边
            node_1 = nw.node_temp[-1]
            node_2 = nw.node_temp[-2]
            lastDraw = []
            lastDraw.append(self.w.canvas.create_line(node_1.x, node_1.y, node_2.x, node_2.y, width=2, fill=self.foreColor))
            # 重新将节点颜色调整为红色
            for i in range(len(nw.node_temp)):
                if nw.node_temp[i].tp == 0:
                    self.w.canvas.itemconfig(nw.node_temp[i].cid[0], fill='red')
                elif nw.node_temp[i].tp == 1:
                    self.w.canvas.itemconfig(nw.node_temp[i].cid[0], fill='blue')
                elif nw.node_temp[i].tp == 2:
                    self.w.canvas.itemconfig(nw.node_temp[i].cid[0], fill='green')
                elif nw.node_temp[i].tp == 3:
                    self.w.canvas.itemconfig(nw.node_temp[i].cid[0], fill='yellow')
            [l, w, n, pre_time, tp] = self.ask_edgeinfo()
            # ni, nj, l, w, n, s
            floor_num = nw.find_floor_name(nw.floor_dict, nw.name_fi).num
            nw.add_edge(node_1.num, node_2.num, l, w, n, pre_time, tp, lastDraw, floor_num)
            nw.node_temp = []
        self.yesno.set(0)
        self.end.append(lastDraw)

        # 鼠标右键抬起，弹出菜单

    def onRightButtonUp(self, event):
        self.w.menu.post(event.x_root, event.y_root)

    def onMove(self, event):
        if self.what.get() == 2 or self.what.get() == 3 or self.what.get() == 4 or self.what.get() == 5:
            # 吸附效果
            if len(self.sle_grid) == 0:
                x = int(event.x / 20) * 20
                y = int(event.y / 20) * 20
                lastDraw = self.w.canvas.create_oval(x - 2, y - 2, x + 2, y + 2, outline=self.foreColor, fill='yellow')
                self.sle_grid.append([x, y, lastDraw])
            else:
                x = int(event.x / 20) * 20
                y = int(event.y / 20) * 20
                if not(x == self.sle_grid[0] and y == self.sle_grid[1]):
                    self.w.canvas.delete(self.sle_grid[0][2])
                    lastDraw = self.w.canvas.create_oval(x - 3, y - 3, x + 3, y + 3, outline=self.foreColor,
                                                         fill='yellow')
                    self.sle_grid = []
                    self.sle_grid.append([x, y, lastDraw])

    # 设置函数
    def drawCurve(self):
        if nw.name_fi == "":
            tkinter.messagebox.showerror('Error', 'Build a new floor first！')
        else:
            self.what.set(1)

    def drawStartNode(self):
        if nw.name_fi == "":
            tkinter.messagebox.showerror('Error', 'Build a new floor first！')
        else:
            self.what.set(2)

    def drawIntNode(self):
        if nw.name_fi == "":
            tkinter.messagebox.showerror('Error', 'Build a new floor first！')
        else:
            self.what.set(3)

    def drawEndNode(self):
        if nw.name_fi == "":
            tkinter.messagebox.showerror('Error', 'Build a new floor first！')
        else:
            self.what.set(4)

    # 添加上下层的连接节点
    def cnctNode(self):
        if nw.name_fi == "":
            tkinter.messagebox.showerror('Error', 'Build a new floor first！')
        else:
            self.what.set(5)

    def deleNode(self):
        if nw.name_fi == "":
            tkinter.messagebox.showerror('Error', 'Build a new floor first！')
        else:
            self.what.set(6)

    def addEdge(self):
        if nw.name_fi == "":
            tkinter.messagebox.showerror('Error', 'Build a new floor first！')
        else:
            self.what.set(7)

    def deleEdge(self):
        if nw.name_fi == "":
            tkinter.messagebox.showerror('Error', 'Build a new floor first！')
        else:
            self.what.set(5)

    # 生成路径
    def netGenerate(self):
        global nw
        SP.shortest_path(nw)
        self.canvasFresh(v_flag=1)
        self.loadFloor()

    # 开始模拟
    def runTransM(self):
        global nw
        if nw.shortest_path == []:
            showerror(title="Error",
                      message="Please initialize the network!")
        else:
            if self.disp_flag.get() == 1:
                t, n, rt = TM.transition_matrix_vis(nw)
            else:
                t, n, rt = TM.transition_matrix(nw)
            plt.plot(t, n, label="new")
            plt.xlabel("Time (s)")
            plt.ylabel("Pedestrian NUmber")
            plt.legend()
            plt.show()

    # 优化
    def optTransM(self):
        global nw
        if nw.shortest_path == []:
            showerror(title="Error",
                      message="Please initialize the network!")
        else:
            TM.optimizing(nw)
        # self.plotTree()

    # 选择前景色
    def chooseForeColor(self):
        self.foreColor = tkinter.colorchooser.askcolor()[1]

    def ask_edgeinfo(self):
        print(self.edgeInfo_temp)
        inputDialog = EdgeDialog(self.edgeInfo_temp)
        self.w.wait_window(inputDialog)  # 这一句很重要！！！
        self.edgeInfo_temp = inputDialog.edgeinfo
        return inputDialog.edgeinfo

# 边弹窗
class EdgeDialog(Toplevel):
    def __init__(self, Info_temp, coord=(0, 0)):
        self.coord = coord
        super().__init__()
        self.title('Set edge properties')
        # 弹窗界面
        self.setup_UI(Info_temp)

    def deiconify(self):
        x, y = self.coord
        self.geometry('{width}x{height}+{x}+{y}' \
                      .format(width=200, height=100, x=x, y=y))
        super().deiconify()

    def setup_UI(self, Info_temp):
        # 第一行（两列）
        row1 = Frame(self)
        row1.pack(fill="x")
        Label(row1, text='Occupant Number（ped）：', width=20).pack(side=LEFT)
        self.n = IntVar()
        self.n.set(Info_temp[2])
        Entry(row1, textvariable=self.n, width=10).pack(side=LEFT)
        # 第二行
        row2 = Frame(self)
        row2.pack(fill="x", ipadx=1, ipady=1)
        Label(row2, text='Length（m）：', width=20).pack(side=LEFT)
        self.l = DoubleVar()
        self.l.set(Info_temp[0])
        Entry(row2, textvariable=self.l, width=10).pack(side=LEFT)
        # 第三行
        row3 = Frame(self)
        row3.pack(fill="x", ipadx=1, ipady=1)
        Label(row3, text='Width（m）：', width=20).pack(side=LEFT)
        self.w = DoubleVar()
        self.w.set(Info_temp[1])
        Entry(row3, textvariable=self.w, width=10).pack(side=LEFT)
        # 第四行
        row4 = Frame(self)
        row4.pack(fill="x", ipadx=1, ipady=1)
        Label(row4, text='Pre-movement time（s）：', width=20).pack(side=LEFT)
        self.pt = DoubleVar()
        self.pt.set(Info_temp[3])
        Entry(row4, textvariable=self.pt, width=10).pack(side=LEFT)
        # 第四行
        row5 = Frame(self)
        row5.pack(fill="x", ipadx=1, ipady=1)
        Label(row5, text='Type（*）：', width=20).pack(side=LEFT)
        self.et = IntVar()
        self.et.set(Info_temp[4])
        Checkbutton(row5, text="Walkway", variable=self.et, onvalue=0, offvalue=-1) \
            .pack(side=LEFT)
        Checkbutton(row5, text="Stairway", variable=self.et, onvalue=1, offvalue=-1) \
            .pack(side=LEFT)
        Checkbutton(row5, text="Door", variable=self.et, onvalue=2, offvalue=-1) \
            .pack(side=LEFT)

        # 第五行
        row6 = Frame(self)
        row6.pack(fill="x")
        Button(row6, text="Cancle", command=self.cancel).pack(side=RIGHT)
        Button(row6, text="Ok", command=self.ok).pack(side=RIGHT)


    def ok(self):
        if self.et.get() == -1:
            showerror(title="Error",
                      message="Please select the edge type!")
        else:
            self.edgeinfo = [self.l.get(), self.w.get(), self.n.get(), self.pt.get(), self.et.get()]  # 设置数据
            self.destroy()  # 销毁窗口

    def cancel(self):
        self.edgeinfo = None  # 空！
        self.destroy()

# 连接节点弹窗
class NodeDialog(Toplevel):
    def __init__(self):
        super().__init__()
        self.title('Set edge properties')
        # 弹窗界面
        self.cnode = 0
        self.strvar = StringVar()
        self.setupUIN()

    def setupUIN(self):
        # 第一行（两列）
        row1 = Frame(self)
        row1.pack(fill="x")
        Label(row1, text='Node number：', width=20).pack(side=LEFT)
        ttk.Entry(row1, textvariable=self.strvar, width=10).pack(side=LEFT)


        # 第二行
        row2 = Frame(self)
        row2.pack(fill="x")
        Button(row2, text="Cancle", command=self.newCancel).pack(side=RIGHT)
        Button(row2, text="Ok", command=self.newOk).pack(side=RIGHT)

    def newOk(self):
        self.cnode = int(self.strvar.get())
        self.destroy()  # 销毁窗口

    def newCancel(self):
        self.node_name = None  # 空！
        self.destroy()

# 新建楼层弹窗
class FloorDialog(Toplevel):
    def __init__(self):
        super().__init__()
        self.title('New Floor')
        self.name = ""
        self.num = 0
        # 弹窗界面
        self.setupUIN()

    def setupUIN(self):
        # 第一行（两列）
        row1 = Frame(self)
        row1.pack(fill="x")
        Label(row1, text='New floor name：', width=20).pack(side=LEFT)
        self.strvar = StringVar()
        Entry(row1, textvariable=self.strvar, width=10).pack(side=LEFT)
        row2 = Frame(self)
        row2.pack(fill="x")
        Label(row2, text='New floor number：', width=20).pack(side=LEFT)
        self.intvar = IntVar()
        Entry(row2, textvariable=self.intvar, width=10).pack(side=LEFT)

        # 第二行
        row3 = Frame(self)
        row3.pack(fill="x")
        Button(row3, text="Cancle", command=self.newCancel).pack(side=RIGHT)
        Button(row3, text="Ok", command=self.newOk).pack(side=RIGHT)


    def newOk(self):
        self.name = self.strvar.get()
        self.num = self.intvar.get()
        self.destroy()  # 销毁窗口

    def newCancel(self):
        self.name = "none"
        self.num = NONE
        self.destroy()

if __name__ == '__main__':
    nw = DS.NetworkStructure()
    app = MyApp()
