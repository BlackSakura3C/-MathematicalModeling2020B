import numpy as np
import matplotlib.pyplot as plt
import mpl_toolkits.mplot3d as axes3d
import seaborn as sns
import copy
import json
from scipy import interpolate


class Cell2(object):
    def __init__(self,paintingOn=0,fileOpen=0,testType=0,iterationTime=50,renderOn=0,length=10,height=20,**kw):
        '''
        :param paintingOn:
        :param fileOpen:
        :param testType:
        :param iterationTime:
        :param renderOn:渲染开启
        :param length:初始情况时没有考虑到多种模型 用于正方体专用
        :param height:初始情况时没有考虑到多种模型 用于圆柱体专用
        :param kw: cuboidx=10,cuboidy=10,cuboidz=10 ovala ovalb ovalh spherea sphereb spherec
                    RoundFrustumr,RoundFrustumR(底面半径),RoundFrustumh,cube45diagonal,cube45h
        '''
        self.IterationStop = 0  # 当没有变化时结束循环遍历 public
        self.IterationTargetTime = iterationTime  #确定迭代次数
        self.__finishIterationTime=0
        self.__renderOn=renderOn
        self.__size=length
        self.__surplusNode = []
        self.__changeNum = []
        self.__cylinderHeight = height
        self.__lastNodeNum = 0
        self.__reduceRate = 0
        self.__allNodeNum=0
        self.__rainMaxHeight=[]  # 测试下雨时最大高度变化
        '''
        surplusNode用于记录剩余沙点数
        sx sy sz用于绘制点
        '''
        self.__fileOpen=fileOpen
        self.__paintingOn=paintingOn
        if testType==0:
            self.initCube()
        elif testType==1:
            self.initCylinder()
        elif testType==2:
            self.__cuboidX=kw['cuboidx']
            self.__cuboidY=kw['cuboidy']
            self.__cuboidZ=kw['cuboidz']
            self.__maxYForRain = self.__cuboidY # 希望造成剩余前半部分冲刷更为严重的现象 记录剩余的部分最大最小Y（迎击海浪方向）
            self.__minYForRain = 1
            self.initCuboid()
        elif testType==3:
            self.__ovalA=kw['ovala']
            self.__ovalB=kw['ovalb']
            self.__ovalH=kw['ovalh']
            self.__maxYForRain = self.__ovalB*2
            self.__minYForRain = 1
            self.initovalCylinder()
        elif testType==4:
            self.__sphereA=kw['spherea']
            self.__sphereB = kw['sphereb']
            self.__sphereC = kw['spherec']
            self.__maxYForRain = self.__sphereA*2
            self.__minYForRain = 1
            self.initSphere()
        elif testType==5:
            self.__RoundFrustumr=kw['RoundFrustumr']
            self.__RoundFrustumR = kw['RoundFrustumR']
            self.__RoundFrustumh=kw['RoundFrustumh']
            self.__maxYForRain = max(self.__RoundFrustumR*2,self.__RoundFrustumr*2)
            self.__minYForRain = 1
            self.initRoundFrustum()
        elif testType==6:
            self.__diagonal=kw['cube45diagonal']  # 定义的是45度角斜放的立方体的对角线长度
            self.__cube45H=kw['cube45h']
            self.__maxYForRain = self.__diagonal
            self.__minYForRain = 1
            self.initCube45()

    def initCube(self):
        self.__data = np.zeros((self.__size + 2, self.__size + 2, self.__size + 2))
        self.__loopx, self.__loopy, self.__loopz = self.__size + 1, self.__size + 1, self.__size + 1
        self.__maxYForRain = self.__size
        self.__minYForRain = 1
        self.initMatrix()
        self.__data[0, :, :] = 1
        self.__data[self.__size + 1, :, :] = 1
        self.__data[:, 0, :] = 1
        self.__data[:, self.__size + 1, :] = 1
        self.__data[:, :, 0] = 0
        self.__data[:, :, self.__size + 1] = 1

    def initCube45(self):
        self.__data=np.zeros((self.__diagonal*2+5,self.__diagonal*2+5,self.__cube45H+2))
        self.__loopx, self.__loopy, self.__loopz =self.__diagonal*2+3,self.__diagonal*2+3,self.__diagonal+1
        self.__sx = []
        self.__sy = []
        self.__sz = []
        for k in range(1, self.__loopz, 1):
            for j in range(1, self.__loopy, 1):
                for i in range(1, self.__loopx, 1):
                    if j<=i+(self.__diagonal+1) and j<=-i+3*(self.__diagonal+1) and j>=-i+(self.__diagonal+1) and j>=i-(self.__diagonal+1):
                        self.__sx.append(i)
                        self.__sy.append(j)
                        self.__sz.append(k)
                    else:
                        self.__data[i, j, k] = 1

    def initCylinder(self):
        '''
        该函数中使用的private size代表的是圆柱的半径
        :return:
        '''
        self.__data=np.zeros((self.__size*2+2+1,self.__size*2+2+1,self.__cylinderHeight+2))  #将圆柱以长方体存储 周围空余部位存水即可 以圆心为中间点
        self.__loopx,self.__loopy,self.__loopz=self.__size*2+1+1,self.__size*2+1+1,self.__cylinderHeight+1
        self.__maxYForRain = self.__size*2+2+1
        self.__minYForRain = 1
        self.initCylinderMatrix()

    def initCylinderMatrix(self):
        self.__sx = []
        self.__sy = []
        self.__sz = []
        middle = self.__size+1  # 圆心位置
        for k in range(1, self.__loopz, 1):
            for j in range(1, self.__loopy, 1):
                for i in range(1, self.__loopx, 1):
                    if (i - middle) ** 2 + (j - middle) ** 2 <= self.__size ** 2:
                        self.__sx.append(i)
                        self.__sy.append(j)
                        self.__sz.append(k)
                    else:
                        self.__data[i, j, k] = 1

    def initCuboid(self):
        self.__data=np.zeros((self.__cuboidX+2,self.__cuboidY+2,self.__cuboidZ+2))
        self.__loopx,self.__loopy,self.__loopz=self.__cuboidX+1,self.__cuboidY+1,self.__cuboidZ+1
        self.__data[0,:,:]=1
        self.__data[self.__cuboidX+1,:,:]=1
        self.__data[:,0,:]=1
        self.__data[:,self.__cuboidY+1,:]=1
        self.__data[:,:,self.__cuboidZ+1]=1
        self.__data[:,:,0]=0
        self.initMatrix()

    def initovalCylinder(self):
        self.__data=np.zeros((self.__ovalA*2+3,self.__ovalB*2+3,self.__ovalH+2))
        self.__loopx, self.__loopy, self.__loopz =self.__ovalA*2+2,self.__ovalB*2+2,self.__ovalH+1
        self.__sx = []
        self.__sy = []
        self.__sz = []
        middlex = self.__ovalA + 1  # 圆心x位置
        middley = self.__ovalB + 1
        for k in range(1, self.__loopz, 1):
            for j in range(1, self.__loopy, 1):
                for i in range(1, self.__loopx, 1):
                    if ((i - middlex) ** 2)/(self.__ovalA**2) + ((j - middley) ** 2)/(self.__ovalB**2) <= 1:
                        self.__sx.append(i)
                        self.__sy.append(j)
                        self.__sz.append(k)
                    else:
                        self.__data[i, j, k] = 1

    def initRoundFrustum(self):
        '''
        圆台的初始化 可以推广到圆锥
        :return:
        '''
        r=max(self.__RoundFrustumR,self.__RoundFrustumr)
        self.__data=np.zeros((r*2+3,r*2+3,self.__RoundFrustumh+2))
        self.__loopx, self.__loopy, self.__loopz =r*2+2,r*2+2,self.__RoundFrustumh+1
        self.__sx = []
        self.__sy = []
        self.__sz = []
        middle=r+1
        for k in range(1, self.__loopz, 1):
            for j in range(1, self.__loopy, 1):
                for i in range(1, self.__loopx, 1):
                    if (i-middle)**2+(j-middle)**2<=(self.__RoundFrustumR-k/self.__RoundFrustumh*(self.__RoundFrustumR-self.__RoundFrustumr))**2:
                        self.__sx.append(i)
                        self.__sy.append(j)
                        self.__sz.append(k)
                    else:
                        self.__data[i, j, k] = 1

    def initSphere(self):
        '''
        包括了球体的特例
        :return:
        '''
        self.__data=np.zeros((self.__sphereA*2+3,self.__sphereB*2+3,self.__sphereC*2+3))
        self.__loopx, self.__loopy, self.__loopz =self.__sphereA*2+2,self.__sphereB*2+2,self.__sphereC*2+2
        self.__sx = []
        self.__sy = []
        self.__sz = []
        middlex = self.__sphereA + 1  # 球心x位置
        middley = self.__sphereB + 1
        middlez = 1
        for k in range(1, self.__loopz, 1):
            for j in range(1, self.__loopy, 1):
                for i in range(1, self.__loopx, 1):
                    if ((i - middlex) ** 2)/(self.__sphereA**2) + ((j - middley) ** 2)/(self.__sphereB**2) +((k-middlez)**2)/(self.__sphereC**2)<= 1:
                        self.__sx.append(i)
                        self.__sy.append(j)
                        self.__sz.append(k)
                    else:
                        self.__data[i, j, k] = 1

    def initMatrix(self):
        self.__sx = []
        self.__sy = []
        self.__sz = []
        for i in range(1,self.__loopx,1):
            for j in range(1,self.__loopy,1):
                for k in range(1,self.__loopz,1):
                    if self.__data[i,j,k]==0:
                        self.__sx.append(i)
                        self.__sy.append(j)
                        self.__sz.append(k)

    def drawCell(self):
        #plt.ion()
        plt.figure(num=1,figsize=(8,8))
        plt.clf()
        ax3=plt.axes(projection='3d')
        ax3.scatter(self.__sx,self.__sy,self.__sz,s=100,marker='s',color='peru')
        ax3.set_xlabel('Facing the sea')
        # ax3.set_ylabel('Y')
        # ax3.set_zlabel('Z')
        scale=max(self.__loopx,self.__loopy,self.__loopz)
        ax3.set_zlim(0, scale)
        plt.xlim(0,scale)
        plt.ylim(0,scale)
        plt.title('3D Sandcastle Simulation')
        self.surfacePaintHelper()
        plt.pause(0.7)
        #plt.ioff()

    def changeRule(self):
        dataTemp=copy.deepcopy(self.__data) #由于list内部含有list 必须使用深拷贝 不然内层list仍然指向同一个list
        nodeNum=0
        for i in range(1,self.__loopx,1):
            for j in range(1,self.__loopy,1):
                for k in range(1,self.__loopz,1):
                    side_num = dataTemp[i - 1:i + 2, j - 1:j + 2, k - 1:k + 2].sum() - dataTemp[i, j, k]
                    #print(side_num)
                    '''
                    0代表的是沙子
                    '''
                    if dataTemp[i,j,k]==0:
                        nodeNum=nodeNum+1
                        temp=np.random.randint(1, 26)
                        #print(i,j,k,side_num,temp)
                        if temp<side_num:
                            self.__data[i,j,k]=1
                    elif np.random.randint(1,48)<(26-side_num):
                        self.__data[i,j,k]=0
                    else:
                        continue
        self.__finishIterationTime=self.__finishIterationTime+1
        if nodeNum==0:
            self.IterationStop=1
        self.__surplusNode.append(nodeNum)
        self.initMatrix()
        self.drawCell()

    def newChangeRule(self):
        dataTemp = copy.deepcopy(self.__data)  # 由于list内部含有list 必须使用深拷贝 不然内层list仍然指向同一个list
        nodeNum = 0
        maxHeight=0
        for i in range(1,self.__loopx,1):
            for j in range(1,self.__loopy,1):
                for k in range(1,self.__loopz,1):
                    # 在该部分中认为水正面冲击能力为4 左右上下为2 后方为返潮带走沙子 能力为1
                    # 按照3D视图默认角度 为了更好的体现效果 我将j正方向当作是海浪冲击正方向
                    water_weight = 0
                    # 下方检查顺序为立方体前左右下上后
                    if dataTemp[i,j-1,k]==1:
                        water_weight+=20
                    if dataTemp[i-1,j,k]==1:
                        water_weight+=4
                    if dataTemp[i+1,j,k]==1:
                        water_weight+=4
                    if dataTemp[i,j,k-1]==1:
                        water_weight+=0
                    if dataTemp[i,j,k+1]==1:
                        # 基于剩余宽度确定 前半部分由于迎浪 权重更大
                        # if j>=self.__minYForRain and j<=(self.__maxYForRain-self.__minYForRain)/2:
                        #     water_weight+=10
                        # else:
                        #     water_weight+=5
                        water_weight+=20
                    if dataTemp[i,j+1,k]==1:
                        water_weight+=1
                    #增加了侧方水点对3x3同平面正方形中间沙子的影响 下面方向均是以海浪方向为正方向
                    if dataTemp[i-1,j-1,k]==1:#左下
                        water_weight+=9
                    if dataTemp[i+1,j-1,k]==1:#右上
                        water_weight+=9
                    if dataTemp[i-1,j+1,k]==1:#左上
                        water_weight+=1
                    if dataTemp[i+1,j+1,k]==1:
                        water_weight+=1

                    if dataTemp[i,j,k]==0:
                        if maxHeight<k:
                            maxHeight=k
                        nodeNum+=1
                        if np.random.randint(1, 70)<=water_weight:
                            self.__data[i,j,k]=1

        self.__rainMaxHeight.append(maxHeight)
        if self.__lastNodeNum==0:
            self.__lastNodeNum = nodeNum
            self.__allNodeNum=nodeNum
            self.__changeNum.append(0)
            self.__surplusNode.append(1)
        else:
            self.__changeNum.append(self.__lastNodeNum-nodeNum)
            self.__lastNodeNum = nodeNum
            self.__reduceRate=(nodeNum)/self.__allNodeNum
            self.__surplusNode.append(self.__reduceRate)
        self.withGravity()
        self.__finishIterationTime = self.__finishIterationTime + 1
        if nodeNum == 0:
            self.IterationStop = 1
        '''
        下面注释行用于测试沙子剩余量
        '''
        #self.__surplusNode.append(nodeNum)
        self.initMatrix()
        if self.__paintingOn==1:
            self.drawCell()

    def withGravity(self):
        '''
        该函数的作用是将当前的三维矩阵进行整形
        让上面的部分下落到下方空白部分
        模仿所有沙砾都是重力块的情况
        :return:
        '''
        for i in range(1,self.__loopx,1):
            for j in range(1,self.__loopy,1):
                lineNum=0   #当前数列上沙子个数
                for k in range(1,self.__loopz,1):
                    if self.__data[i,j,k]==0:
                        lineNum+=1
                self.__data[i,j,1:lineNum+1]=0
                self.__data[i,j,lineNum+1:]=1

    def showInfo(self):
        if self.__fileOpen==1:
            self.fileRecord()
        plt.figure(num=2,figsize=(8,8))
        plt.plot(np.arange(self.__finishIterationTime),self.__surplusNode)
        plt.plot(np.arange(self.__finishIterationTime),[0.4]*(self.__finishIterationTime))
        plt.xticks(np.arange(0,self.__finishIterationTime,2))
        #plt.yticks(np.arange(min(self.__surplusNode),max(self.__surplusNode),0.05))
        plt.yticks(np.arange(0, 1, 0.05))
        plt.xlim(0,self.__finishIterationTime)
        plt.ylim(0,1)
        plt.title('Sand Quantity Chart')
        plt.show()

    def fileRecord(self):
        f = open(r'.\rainTest2\sphere_height\15-21-50-ramain', 'w', encoding='UTF-8')
        temp_list = json.dumps(self.__surplusNode)
        #不同的temp_list传入值可以保存特定的内容
        #temp_list=json.dumps(self.__changeNum)
        f.write(temp_list)
        f.close()
        f = open(r'.\rainTest2\sphere_height\15-21-50-height', 'w', encoding='UTF-8')
        temp_list = json.dumps(self.__rainMaxHeight)
        f.write(temp_list)
        f.close()

    def showInterationTime(self):
        return self.__finishIterationTime

    def surfacePaintHelper(self):
        '''
        将散点图所得数据进行处理 取有效xy平面绘制成曲面图
        :return:
        '''
        min_x=self.__loopx-1
        max_x=1  #loop_x作用于循环 由于py左闭右开的特点 所以在这里能取到的max我们-1处理
        min_y=self.__loopy-1
        max_y=1
        # 下方循环并没有合并（本来可以一遍三重循环完成 但是不太希望有周围没有高度的平沙部分 所以用下面两重循环处理了有效xy平面）
        for i in range(1,self.__loopx,1):
            for j in range(1,self.__loopy,1):
                    if self.__data[i,j,1]==0:
                        if i>max_x:
                            max_x=i
                        if i<=min_x:
                            min_x=i
                        if j>max_y:
                            max_y=j
                        if j<=min_y:
                            min_y=j
        self.__maxYForRain=max_y
        self.__minYForRain=min_y
        x=np.arange(min_x,max_x+1,1)
        y=np.arange(min_y,max_y+1,1)
        xx,yy=np.meshgrid(x,y)
        z=[]
        for j in range(min_y, max_y+1, 1):
            for i in range(min_x,max_x+1,1):
                # if j==min_y-1 or j==max_y+1 or i==min_x-1 or i==max_x+1:
                #     z.append(1)
                #     continue
                max_z = 1
                for k in range(1,self.__loopz,1):
                    if self.__data[i,j,k]==0:
                        if k>max_z:
                            max_z=k
                    else:
                        break   #   由于我们是重力模型 沙子都在底部
                z.append(max_z)

        z = np.array(z)
        z_length=len(z)
        if z_length == 0:
            return
        # 绘制时增加了周围一圈最低边界点 所以在中的点数(max_y - min_y+1)的基础上多加了2。下方znew.reshape同理
        # 上面一行注释用于测试手动效果1.0版本 暂时没用
        z = z.reshape(max_y - min_y + 1, max_x - min_x + 1)
        z_background = np.ones((max_y - min_y + 1, max_x - min_x + 1))
        '''
        以下部分用于线性插值 细化3D曲面图 renderOn=1时开启渲染效果
        multiple 为倍数 倍数越高代表插值越细
        '''
        try:
            if self.__renderOn == 1:
                multiple = 5
                # f=interpolate.RegularGridInterpolator(x, y, z,method='nearest')
                f = interpolate.interp2d(x, y, z, kind='cubic')
                x = np.arange(min_x, max_x + 0.81, 1 / multiple)
                y = np.arange(min_y, max_y + 0.81, 1 / multiple)
                znew = f(x, y)
                x_new = [min_x - 1]
                x_new.extend(x)
                x_new.append(max_x + 1)
                y_new = [min_y - 1]
                y_new.extend(y)
                y_new.append(max_y + 1)
                z_withside = []
                k1, k2 = 0, 0
                for i in range(1, len(x_new) + 1, 1):
                    if i == 1 or i == len(x_new):
                        temp = [1] * len(y_new)
                        z_withside.extend(temp)
                        continue
                    for j in range(1, len(y_new) + 1, 1):
                        if j == 1 or j == len(y_new):
                            z_withside.append(1)
                        else:
                            z_withside.append(znew[k1, k2])
                            if k2 == len(x) - 1:
                                k1 = (k1 + 1) % len(y)
                            k2 = (k2 + 1) % len(x)
                            #print(k1, k2)
                xx, yy = np.meshgrid(x_new, y_new)
                #print(" ", len(x_new), len(y_new), len(z_withside))
                z_length=len(z_withside)
                z = np.array(z_withside)
                z = z.reshape(len(y_new), len(x_new))
                z_background=np.ones((len(y_new), len(x_new)))
            elif self.__renderOn == 2:
                multiple = 5
                # f=interpolate.RegularGridInterpolator(x, y, z,method='nearest')
                f = interpolate.interp2d(x, y, z, kind='cubic')
                x = np.arange(min_x - 0.8, max_x + 0.81, 1 / multiple)
                y = np.arange(min_y - 0.8, max_y + 0.81, 1 / multiple)
                znew = f(x, y)
                xx,yy=np.meshgrid(x,y)
                z=znew.reshape(len(y),len(x))
                z_background = np.ones((len(y),len(x)))
        except:
            pass

        plt.figure(num=3, figsize=(8, 8))
        # plt.text(0,30,'Running time:',self.__finishIterationTime)
        # plt.text(0,30,'Residual sand/Amount of sand={:.4f}'.format(self.__surplusNode[self.__finishIterationTime]))
        ax2 = plt.axes(projection='3d')
        scale = max(self.__loopx, self.__loopy, self.__loopz)
        ax2.set_zlim(0, scale)
        plt.xlim(0, scale)
        plt.ylim(0, scale)
        ax2.set_xlabel('Facing the sea')
        plt.title('3D Sandcastle Simulation')
        # ax2.set_ylabel('Y')
        # ax2.set_zlabel('Z')
        #ax2.plot_surface(xx,yy,z,rstride=1,cstride=1,cmap='rainbow',shade=True)
        ax2.plot_surface(xx, yy, z, rstride=1, cstride=1, color='sandybrown', shade=True)
        '''
        ***下面这行可以开启对3D沙堆表面图增加地板（显示效果还存在一些小问题）
        '''
        #ax2.plot_surface(xx, yy, z_background, rstride=1, cstride=1, color='sandybrown', shade=True)


#sns.set(style='darkgrid')
paintOn=int(input('当前模拟是否开启3D模拟图绘制(0->不开启 1->开启)'))
fileopen=int(input('当前测试结果是否记录在默认文件中(0->不记录 1->记录)'))
testType=(int)(input('输入测试用例:0/1(0->正方形 1->圆柱 2->长方体 3->椭圆柱 4->球类 5->圆台类(包括圆锥)) 6->45度角放置正方体(包含正方形底面的长方体)'))
iterationTime = int(input('输入测试用迭代次数(次数超过150可能会很慢):'))
render=int(input('当前模拟程序是否开启渲染效果(0->不开启 1->开启手动渲染 2->开启自动渲染)'))
if testType==0:
    length = int(input('输入正方形边长:'))
    cell_test = Cell2(paintOn,fileopen,testType, iterationTime,render,length)
elif testType==1:
    length,height=(input('输入圆柱底面半径 圆柱高度(空格分隔):').split())
    cell_test = Cell2(paintOn,fileopen,testType, iterationTime,render,int(length), int(height))
elif testType==2:
    x,y,z=input('输入长方体的长 宽 高(空格分隔)').split()
    cell_test=Cell2(paintOn,fileopen,testType,iterationTime,render,cuboidx=int(x),cuboidy=int(y),cuboidz=int(z))
elif testType==3:
    a,b,h=input('输入椭圆台的a b 高(空格分隔)').split()
    cell_test=Cell2(paintOn,fileopen,testType,iterationTime,render,ovala=int(a),ovalb=int(b),ovalh=int(h))
elif testType==4:
    a,b,c=input('输入椭球的a b c(空格分隔)').split()
    cell_test = Cell2(paintOn,fileopen,testType, iterationTime,render, spherea=int(a), sphereb=int(b),spherec=int(c))
elif testType==5:
    R,r,h=input('输入圆台底面半径R 顶面半径r 高度(空格分隔)').split()
    cell_test=Cell2(paintOn,fileopen,testType,iterationTime,render,RoundFrustumR=int(R),RoundFrustumr=int(r),RoundFrustumh=int(h))
elif testType==6:
    l,h=input('输入底面正方形对角线长一半l 高度h(空格分隔)').split()
    cell_test=Cell2(paintOn,fileopen,testType,iterationTime,render,cube45diagonal=int(l),cube45h=int(h))
else:
    print('输入错误，启动默认测试用例')
    cell_test = Cell2()

cell_test.drawCell()
flag=0  #确保输出Run more than 的次数
for i in range(cell_test.IterationTargetTime):
    if cell_test.IterationStop==1:
        print('沙堆完全被水冲毁，模拟结束')
        break
    if i>cell_test.IterationTargetTime*0.25 and flag==0:
        print('Run more than 25%')
        flag=1
    elif i>cell_test.IterationTargetTime*0.5 and flag==1:
        print('Run more than 50%')
        flag=2
    elif i>cell_test.IterationTargetTime*0.75 and flag==2:
        print('Run more than 75%')
        flag=3
    cell_test.newChangeRule()

print('Run 100% and iteration time is:',cell_test.showInterationTime())
cell_test.showInfo()

if __name__=='__main':
    pass


