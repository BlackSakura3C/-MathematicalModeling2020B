import matplotlib.pyplot as plt
import json
import numpy as np
f1=open('.\data_2020_03_08_newoval_1','r',encoding='utf-8')
out1=f1.read()
out1=json.loads(out1)

f2=open('.\data_2020_03_08_newoval_2','r',encoding='utf-8')
#f2=open('.\data_2020_03_08_cylinder_1','r',encoding='utf-8')
out2=f2.read()
out2=json.loads(out2)

f3=open('.\data_2020_03_08_newoval_3','r',encoding='utf-8')
out3=f3.read()
out3=json.loads(out3)

f4=open('.\data_2020_03_08_newoval_4','r',encoding='utf-8')
out4=f4.read()
out4=json.loads(out4)

f5=open('.\data_2020_03_08_newoval_5','r',encoding='utf-8')
out5=f5.read()
out5=json.loads(out5)

f6=open('.\data_2020_03_08_newoval_6','r',encoding='utf-8')
out6=f6.read()
out6=json.loads(out6)

f7=open('.\data_2020_03_08_newoval_7','r',encoding='utf-8')
out7=f7.read()
out7=json.loads(out7)

f8=open('.\data_2020_03_08_newoval_8','r',encoding='utf-8')
out8=f8.read()
out8=json.loads(out8)

f9=open('.\data_2020_03_08_newoval_9','r',encoding='utf-8')
out9=f9.read()
out9=json.loads(out9)

f10=open('.\data_2020_03_08_newoval_10','r',encoding='utf-8')
out10=f10.read()
out10=json.loads(out10)

f11=open('.\data_2020_03_08_sphere_1','r',encoding='utf-8')
out11=f11.read()
out11=json.loads(out11)

f12=open('.\data_2020_03_08_sphere_2','r',encoding='utf-8')
out12=f12.read()
out12=json.loads(out12)

f13=open('.\data_2020_03_08_sphere_3','r',encoding='utf-8')
out13=f13.read()
out13=json.loads(out13)

f14=open('.\data_2020_03_08_sphere_4','r',encoding='utf-8')
out14=f14.read()
out14=json.loads(out14)

f15=open('.\data_2020_03_08_sphere_5','r',encoding='utf-8')
out15=f15.read()
out15=json.loads(out15)

plt.figure(num=1,figsize=(6.5,4))
# plt.plot(np.arange(len(out1)),out1,label='oval_bottom:a=11 b=30')
# plt.plot(np.arange(len(out2)),out2,label='oval_bottom:a=13 b=25')
plt.plot(np.arange(len(out3)),out3,label='elliptic cylinder:a=15 b=22 h=30')
# plt.plot(np.arange(len(out4)),out4,label='circle_bottom:r=18')
# plt.plot(np.arange(len(out5)),out5,label='oval_bottom:a=19 b=17')
# plt.plot(np.arange(len(out6)),out6,label='oval_bottom:a=21 b=16')
# plt.plot(np.arange(len(out7)),out7,label='oval_bottom:a=23 b=14')
# plt.plot(np.arange(len(out8)),out8,label='oval_bottom:a=25 b=13')
# plt.plot(np.arange(len(out9)),out9,label='oval_bottom:a=27 b=12')
# plt.plot(np.arange(len(out10)),out10,label='oval_bottom:a=29 b=11')
plt.plot(np.arange(0,51,1),[0.3]*51,linestyle='--',color='black',linewidth=0.5)
plt.xlim(0,len(out1))
plt.ylim(0,1)
plt.yticks([0,0.2,0.3,0.4,0.6,0.8,1],['0','20%','(*)30%','40%','60%','80%','100%'])

plt.plot(np.arange(len(out12)),out12,label='semi-ellipsoid:a=19 b=33 c=25')
plt.plot(np.arange(len(out13)),out13,label='semi-ellipsoid:a=21 b=30 c=25')
plt.plot(np.arange(len(out14)),out14,label='semi-ellipsoid:a=23 b=27 c=25')
plt.plot(np.arange(len(out11)),out11,label='semi-ellipsoid:a=25 b=25 c=25')
plt.plot(np.arange(len(out15)),out15,label='semi-ellipsoid:a=27 b=23 c=25')

plt.title('Comparison of elliptic cylinder and semi-ellipsoid')
plt.ylabel('Remaining ratio')
plt.xlabel('Running Time')
plt.legend()

plt.figure(num=2,figsize=(6.5,4))
x_a=[19,21,23,25,27]
runtime=[27.02,27.21,26.49,25.39,24.47]
# runtime=[22.23,23.47,23.85,21.60,21.14,20.38,18.26,17.23,15.97,14.83]
plt.plot(x_a,runtime)
plt.scatter(x_a,runtime)
plt.xlim(19,27)
plt.title('Running time when remaining ratio≤30%')
plt.ylabel('Running Time')
plt.xlabel('Half of the axis facing the waves')
# plt.legend()

plt.show()