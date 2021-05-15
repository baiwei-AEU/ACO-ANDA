import  numpy as np
import re
import uuid
import random
import copy
import datetime

def random_pick(some_list, probabilities):
    x = random.uniform(0,1)
    cumulative_probability = 0.0
    for item, item_probability in zip(some_list, probabilities):
         cumulative_probability += item_probability
         if x < cumulative_probability:
               break
    return item

class CKnapsack (object):
    def __init__(self, cap_num, item_num, profitMatrix, item_restrictMatrix, max_capacityMatrix):
        ##m
        self.cap_num=cap_num
        ##n
        self.item_num=item_num
        ##cj
        self.profitMatrix=profitMatrix
        ##aij
        self.item_restrictMatrix=item_restrictMatrix
        ##bj
        self.max_capacityMatrix=max_capacityMatrix

    ##判断是否满足条件
    def consSatisfy(self,tabulist,numSelect):
        newlist=copy.deepcopy(tabulist)
        newlist.append(numSelect)
        for i in range(self.cap_num):
            selectWeight=self.item_restrictMatrix[i,newlist]
            if(np.sum(selectWeight)>self.max_capacityMatrix[0][i]):
                return False
        return True


class CAnt(object):
    def __init__(self):
        self.number=uuid.uuid1()
        self.nowNode=0
        self.tabuList=[]
        self.tabuList_backup=[]
        self.profit=0;

class CAntsForGraph(object):
    def __init__(self, pack,tao=400,alpha=0.7, beta=0.3, rho=0.2, Q=400):
        self.alpha = alpha  # 信息启发式因子
        self.beta = beta  # 期望启发式因子
        self.rho = rho  # 信息素挥发速度
        self.Q = Q  # 信息素强度
        self.tao=tao ##初始的信息素
        ###问题描述##
        self.pack=pack
    def solve(self,ant_num_init,maxIter,update_number=False):
        print("slove:1")
        ##初始化信息素浓度
        self.pheromo_edges = np.zeros((self.pack.item_num, self.pack.item_num))
        self.pheromo_edges=self.pheromo_edges+self.tao

        ##计算yita
        self.yita_edges = (np.tile(self.pack.profitMatrix,(self.pack.cap_num,1)))/self.pack.item_restrictMatrix
        self.yita_edges[np.isinf(self.yita_edges)]='Nan'
        self.yita_edges=np.nanmean(self.yita_edges,axis=0)
        self.yita_edges_2=self.pack.cap_num*self.pack.profitMatrix[0]/np.sum(self.pack.item_restrictMatrix,axis=0)

        ##bestSolutions
        bestSolutions=[]
        ##antNumbers
        antNumbers=[]

        ##开始计算
        ant_num_last=ant_num_init
        ##开始迭代
        startTime=datetime.datetime.now()
        bestSolution_previous=-1
        for i in range(maxIter):
            antNumber=self.getAntsNumber(ant_num_init,antNumbers,bestSolutions,update_number)
            print(str(i) + ":" + str(antNumber))
            antNumbers.append(antNumber)
            allAnts=self.AntsGeneration(antNumbers[-1])
            for ant in allAnts:
                self.getPossiblePath(ant)
                self.calculatedprofit(ant);

            ##更新最优解，更新信息素
            bestSolution_nowRound=-1
            bestTabuList=None
            for ant in allAnts:
                ##更新最优解
                if(ant.profit>bestSolution_nowRound):
                    bestSolution_nowRound=ant.profit
                    bestTabuList=ant.tabuList
            bestSolutions.append(bestSolution_nowRound)

            if(bestSolution_nowRound>bestSolution_previous):
                # for ant in allAnts:
                #     if(ant.profit==bestSolution_nowRound):
                #         ##更新信息素
                #         self.updatePheromo(ant)
                bestSolution_previous=bestSolution_nowRound
            #更新信息素
            self.pheromo_edges=self.pheromo_edges*(1-self.rho)
            for ant in allAnts:
                ##self.updatePheromo(ant)
                for i in range(len(bestTabuList)):
                    try:
                        pos=ant.tabuList.index(bestTabuList[i])
                    except Exception:
                        continue
                    self.pheromo_edges[ant.tabuList[pos]][pos] = self.pheromo_edges[ant.tabuList[pos]][pos] + ant.profit/self.Q
        ##antNumbers.append(antNumbers)
        processTime=datetime.datetime.now()-startTime
        return bestSolutions,antNumbers,processTime



    def getAntsNumber(self,ant_num_init,antNumbers,bestSolutions,update_number):
        if(not update_number or len(bestSolutions)<=2):
            return int(ant_num_init)
        delta_t=(bestSolutions[-1]-bestSolutions[-2])/bestSolutions[-2]
        bestSolutionNow=np.max(bestSolutions)
        if(bestSolutions[-1]==bestSolutionNow and delta_t==0):
            return int(antNumbers[-1]/2)
        else:

            return int(antNumbers[-1]+ant_num_init/len(bestSolutions))
        # if(delta_t>delta_t_1):
        #     return int(antNumbers[-1]-delta_t)
        # else:
        #     return int(antNumbers[-1])

    def AntsGeneration(self,antNumber):
        allAnts=[]
        for i in range(antNumber):
            allAnts.append(CAnt())
        return allAnts

    ##得到可能路径
    def getPossiblePath(self,ant):
        while(True):
            if(ant.nowNode==self.pack.item_num):
                break
            possibleVector=self.pheromo_edges[:,ant.nowNode]
            yitaVector=self.yita_edges.T
            possibleVector=np.power(possibleVector,self.alpha)*np.power(yitaVector,self.beta)
            possibleVector[ant.tabuList]=0
            ##possibleVector[ant.tabuList_backup]=0
            if(np.sum(possibleVector)==0):
                break
            possibleVector=possibleVector/np.sum(possibleVector)
            subPossibleVector=[possibleVector[i] for i in range(len(possibleVector)) if(possibleVector[i]!=0)]
            possiblePos=[i for i in range(len(possibleVector)) if(possibleVector[i]!=0)]
            numSelected=random_pick(possiblePos,subPossibleVector)
            ##判断是否满足约束
            if(self.pack.consSatisfy(ant.tabuList,numSelected)):
                ##增加禁忌表
                ant.tabuList.append(numSelected)
                ##移动到下一个节点
                ant.nowNode=ant.nowNode+1
            else:
                ##ant.tabuList_backup.append(numSelected)
                newNum=self.getMaxProfitItem(ant)
                ##采取查找最大值的方法来获取商品
                if(newNum==-1):
                    break
                else:
                    ant.tabuList.append(newNum)
                    ##移动到下一个节点
                    ant.nowNode = ant.nowNode + 1
        return

    ##利用算法2得到商品
    def getMaxProfitItem(self,ant):
        maxProfit=-1
        maxI=-1
        for i in range(self.pack.item_num):
            if(i in ant.tabuList or not self.pack.consSatisfy(ant.tabuList, i)):
                continue
            tempList=copy.deepcopy(ant.tabuList)
            tempList.append(i)
            if(maxProfit<np.sum(self.pack.profitMatrix[0][tempList])):
                maxProfit = np.sum(self.pack.profitMatrix[0][tempList])
                maxI=i
        return maxI

    ##得到最优解
    def calculatedprofit(self,ant):
        ant.profit=np.sum(self.pack.profitMatrix[0,ant.tabuList])
        return


    def solve_adjusted(self):
        return

def processFile(filename,fileType):
    if(fileType=='sac94-suite'):
        processFile_sac94_suite(filename)
    elif(fileType=='MK_GK'):
        processFile_MK_GK(filename)
    elif(fileType=='OR_Library'):
        processFile_OR_Library(filename)
    elif (fileType == 'OR_Library_Type2'):
        processFile_OR_Library_Type2(filename)

def processFile_OR_Library(filename):
    allNumbers=[]
    with open(filename, 'r') as f:
        lines = f.readlines()
        for line in lines:
            splits_t=re.split(' |\t|\n',line)
            for split in splits_t:
                if(split!=''):
                    allNumbers.append(split)
    ##
    n_pos=0
    cap_num=int(allNumbers[0])
    item_num=int(allNumbers[1])

    ##利润
    profitMatrix=np.zeros((1,item_num))
    n_pos=2
    for i in range(item_num):
        profitMatrix[0][i]=int(allNumbers[n_pos])
        n_pos=n_pos+1
    ##最大能力
    max_capacityMatrix=np.zeros((1,cap_num))
    for i in range(cap_num):
        max_capacityMatrix[0][i] = int(allNumbers[n_pos])
        n_pos = n_pos + 1
    ##限制条件矩阵
    item_restrictMatrix=np.zeros((cap_num,item_num))
    for i in range(cap_num):
        for j in range(item_num):
            item_restrictMatrix[i][j]=int(allNumbers[n_pos])
            n_pos = n_pos + 1

    ##optimalSolution=int(allNumbers[n_pos])
    ##n_pos = n_pos + 1

    ##for i in [100,200,300,400,500,600,700,800,900,1000]:
        ##for j in [5,10,20,50,100,200,300,400,500,600,700,800,900,1000]:
    outputFile = open(filename+"_output", 'w')
    allParameters=[]
    all_bestSolutions_times=[]
    all_bestSolutions=[]
    all_antNumbers=[]
    allProcessTimes=[]
    for z in range(1):
        for x in [100,200,300,400,500,600,700,800,900,1000]:
        ##for x in [800]:
            for y in [50,100,200]:
            ##for y in [200]:
                ##定义背包
                knapsack=CKnapsack(cap_num,item_num, profitMatrix, item_restrictMatrix, max_capacityMatrix)
                ##定义图
                ##print("tao初值:"+str(i)+";Q值："+str(j)+":\n")
                antsGraph=CAntsForGraph(knapsack,400,0.7, 0.3, 0.2, 400)
                # bestSolutions,antNumbers,processTime=antsGraph.solve(x,y,False)
                # print(str(x)+";"+str(y)+";"+str(bestSolutions)+";"+str(np.max(bestSolutions))+";"+str(antNumbers)+";"+str(processTime))
                # outputFile.write(str(x)+";"+str(y)+";"+str(bestSolutions)+";"+str(np.max(bestSolutions))+";"+str(antNumbers)+";"+str(processTime)+"\n")
                #
                # ##
                # allParameters.append((x,y,False))
                # temp=[i for i in range(len(bestSolutions)) if bestSolutions[i]==9492]
                # all_bestSolutions_times.append(len(temp))
                # all_bestSolutions.append(np.max(bestSolutions))
                # all_antNumbers.append(np.mean(antNumbers))
                # allProcessTimes.append(processTime)


                bestSolutions, antNumbers, processTime = antsGraph.solve(x, y, True)
                print(str(x)+";"+str(y)+";"+str(bestSolutions)+";"+str(np.max(bestSolutions))+";"+str(antNumbers)+";"+str(processTime))

                allParameters.append((x, y, True))
                temp = [i for i in range(len(bestSolutions)) if bestSolutions[i] == 9492]
                all_bestSolutions_times.append(len(temp))
                all_bestSolutions.append(np.max(bestSolutions))
                all_antNumbers.append(np.mean(antNumbers))
                allProcessTimes.append(processTime)
                outputFile.write(
                    str(x) + ";" + str(y) + ";" + str(bestSolutions) + ";" + str(np.max(bestSolutions)) + ";" + str(
                        antNumbers) + ";" + str(processTime) + "\n")
    print(allParameters)
    print(all_bestSolutions_times)
    print(all_bestSolutions)
    print(all_antNumbers)
    print(allProcessTimes)
    outputFile.write(str(allParameters) + "\n")
    outputFile.write(str(all_bestSolutions_times) + "\n")
    outputFile.write(str(all_bestSolutions) + "\n")
    outputFile.write(str(all_antNumbers) + "\n")
    outputFile.write(str(allProcessTimes) + "\n")
    outputFile.close()

def processFile_OR_Library_Type2(filename):
    allNumbers=[]
    with open(filename, 'r') as f:
        lines = f.readlines()
        for line in lines:
            splits_t=re.split(' |\t|\n',line)
            for split in splits_t:
                if(split!=''):
                    allNumbers.append(split)
    ##
    n_pos=0
    item_num=int(allNumbers[0])
    cap_num=int(allNumbers[1])

    n_pos = 3
    ##限制条件矩阵
    item_restrictMatrix=np.zeros((cap_num,item_num))
    for i in range(cap_num):
        for j in range(item_num):
            item_restrictMatrix[i][j]=int(allNumbers[n_pos])
            n_pos = n_pos + 1

    ##利润
    profitMatrix=np.zeros((1,item_num))
    for i in range(item_num):
        profitMatrix[0][i]=int(allNumbers[n_pos])
        n_pos=n_pos+1


    ##最大能力
    max_capacityMatrix = np.zeros((1, cap_num))
    for i in range(cap_num):
        max_capacityMatrix[0][i] = int(allNumbers[n_pos])
        n_pos = n_pos + 1

    ##optimalSolution=int(allNumbers[n_pos])
    ##n_pos = n_pos + 1

    ##for i in [100,200,300,400,500,600,700,800,900,1000]:
        ##for j in [5,10,20,50,100,200,300,400,500,600,700,800,900,1000]:
    outputFile = open(filename+"_output", 'w')
    allParameters=[]
    all_bestSolutions_times=[]
    all_bestSolutions=[]
    all_antNumbers=[]
    allProcessTimes=[]
    for z in range(1):
        for x in [100,200,300,400,500,600,700,800,900,1000]:
        ##for x in [800]:
            for y in [50,100,200]:
            ##for y in [200]:
                ##定义背包
                knapsack=CKnapsack(cap_num,item_num, profitMatrix, item_restrictMatrix, max_capacityMatrix)
                ##定义图
                ##print("tao初值:"+str(i)+";Q值："+str(j)+":\n")
                antsGraph=CAntsForGraph(knapsack,400,0.7, 0.3, 0.2, 400)
                # bestSolutions,antNumbers,processTime=antsGraph.solve(x,y,False)
                # print(str(x)+";"+str(y)+";"+str(bestSolutions)+";"+str(np.max(bestSolutions))+";"+str(antNumbers)+";"+str(processTime))
                # outputFile.write(str(x)+";"+str(y)+";"+str(bestSolutions)+";"+str(np.max(bestSolutions))+";"+str(antNumbers)+";"+str(processTime)+"\n")
                #
                # ##
                # allParameters.append((x,y,False))
                # temp=[i for i in range(len(bestSolutions)) if bestSolutions[i]==9492]
                # all_bestSolutions_times.append(len(temp))
                # all_bestSolutions.append(np.max(bestSolutions))
                # all_antNumbers.append(np.mean(antNumbers))
                # allProcessTimes.append(processTime)


                bestSolutions, antNumbers, processTime = antsGraph.solve(x, y, True)
                print(str(x)+";"+str(y)+";"+str(bestSolutions)+";"+str(np.max(bestSolutions))+";"+str(antNumbers)+";"+str(processTime))

                allParameters.append((x, y, True))
                temp = [i for i in range(len(bestSolutions)) if bestSolutions[i] == 9492]
                all_bestSolutions_times.append(len(temp))
                all_bestSolutions.append(np.max(bestSolutions))
                all_antNumbers.append(np.mean(antNumbers))
                allProcessTimes.append(processTime)
                outputFile.write(
                    str(x) + ";" + str(y) + ";" + str(bestSolutions) + ";" + str(np.max(bestSolutions)) + ";" + str(
                        antNumbers) + ";" + str(processTime) + "\n")
    print(allParameters)
    print(all_bestSolutions_times)
    print(all_bestSolutions)
    print(all_antNumbers)
    print(allProcessTimes)
    outputFile.write(str(allParameters) + "\n")
    outputFile.write(str(all_bestSolutions_times) + "\n")
    outputFile.write(str(all_bestSolutions) + "\n")
    outputFile.write(str(all_antNumbers) + "\n")
    outputFile.write(str(allProcessTimes) + "\n")
    outputFile.close()

def processFile_MK_GK(filename):
    allNumbers=[]
    with open(filename, 'r') as f:
        lines = f.readlines()
        for line in lines:
            splits_t=re.split(' |\t|\n',line)
            for split in splits_t:
                if(split!=''):
                    allNumbers.append(split)
    ##
    n_pos=0
    item_num=int(allNumbers[0])
    cap_num=int(allNumbers[1])
    ##利润
    profitMatrix=np.zeros((1,item_num))
    n_pos=2
    for i in range(item_num):
        profitMatrix[0][i]=int(allNumbers[n_pos])
        n_pos=n_pos+1
    ##最大能力
    max_capacityMatrix=np.zeros((1,cap_num))
    for i in range(cap_num):
        max_capacityMatrix[0][i] = int(allNumbers[n_pos])
        n_pos = n_pos + 1
    ##限制条件矩阵
    item_restrictMatrix=np.zeros((cap_num,item_num))
    for i in range(cap_num):
        for j in range(item_num):
            item_restrictMatrix[i][j]=int(allNumbers[n_pos])
            n_pos = n_pos + 1

    ##optimalSolution=int(allNumbers[n_pos])
    ##n_pos = n_pos + 1

    ##for i in [100,200,300,400,500,600,700,800,900,1000]:
        ##for j in [5,10,20,50,100,200,300,400,500,600,700,800,900,1000]:
    outputFile = open(filename+"_output", 'w')
    allParameters=[]
    all_bestSolutions_times=[]
    all_bestSolutions=[]
    all_antNumbers=[]
    allProcessTimes=[]
    for z in range(1):
        for x in [100,200,300,400,500,600,700,800,900,1000]:
        ##for x in [800]:
            for y in [50,100,200]:
            ##for y in [200]:
                ##定义背包
                knapsack=CKnapsack(cap_num,item_num, profitMatrix, item_restrictMatrix, max_capacityMatrix)
                ##定义图
                ##print("tao初值:"+str(i)+";Q值："+str(j)+":\n")
                antsGraph=CAntsForGraph(knapsack,400,0.7, 0.3, 0.2, 400)
                # bestSolutions,antNumbers,processTime=antsGraph.solve(x,y,False)
                # print(str(x)+";"+str(y)+";"+str(bestSolutions)+";"+str(np.max(bestSolutions))+";"+str(antNumbers)+";"+str(processTime))
                # outputFile.write(str(x)+";"+str(y)+";"+str(bestSolutions)+";"+str(np.max(bestSolutions))+";"+str(antNumbers)+";"+str(processTime)+"\n")
                #
                # ##
                # allParameters.append((x,y,False))
                # temp=[i for i in range(len(bestSolutions)) if bestSolutions[i]==9492]
                # all_bestSolutions_times.append(len(temp))
                # all_bestSolutions.append(np.max(bestSolutions))
                # all_antNumbers.append(np.mean(antNumbers))
                # allProcessTimes.append(processTime)


                bestSolutions, antNumbers, processTime = antsGraph.solve(x, y, True)
                print(str(x)+";"+str(y)+";"+str(bestSolutions)+";"+str(np.max(bestSolutions))+";"+str(antNumbers)+";"+str(processTime))

                allParameters.append((x, y, True))
                temp = [i for i in range(len(bestSolutions)) if bestSolutions[i] == 9492]
                all_bestSolutions_times.append(len(temp))
                all_bestSolutions.append(np.max(bestSolutions))
                all_antNumbers.append(np.mean(antNumbers))
                allProcessTimes.append(processTime)
                outputFile.write(
                    str(x) + ";" + str(y) + ";" + str(bestSolutions) + ";" + str(np.max(bestSolutions)) + ";" + str(
                        antNumbers) + ";" + str(processTime) + "\n")
    print(allParameters)
    print(all_bestSolutions_times)
    print(all_bestSolutions)
    print(all_antNumbers)
    print(allProcessTimes)
    outputFile.write(str(allParameters) + "\n")
    outputFile.write(str(all_bestSolutions_times) + "\n")
    outputFile.write(str(all_bestSolutions) + "\n")
    outputFile.write(str(all_antNumbers) + "\n")
    outputFile.write(str(allProcessTimes) + "\n")
    outputFile.close()


def processFile_sac94_suite(filename):
    allNumbers=[]
    with open(filename, 'r') as f:
        lines = f.readlines()
        for line in lines:
            splits_t=re.split(' |\t|\n',line)
            for split in splits_t:
                if(split!=''):
                    allNumbers.append(split)
    ##
    n_pos=0
    cap_num=int(allNumbers[0])
    item_num=int(allNumbers[1])
    ##利润
    profitMatrix=np.zeros((1,item_num))
    n_pos=2
    for i in range(item_num):
        profitMatrix[0][i]=int(allNumbers[n_pos])
        n_pos=n_pos+1
    ##最大能力
    max_capacityMatrix=np.zeros((1,cap_num))
    for i in range(cap_num):
        max_capacityMatrix[0][i] = int(allNumbers[n_pos])
        n_pos = n_pos + 1
    ##限制条件矩阵
    item_restrictMatrix=np.zeros((cap_num,item_num))
    for i in range(cap_num):
        for j in range(item_num):
            item_restrictMatrix[i][j]=int(allNumbers[n_pos])
            n_pos = n_pos + 1

    optimalSolution=int(allNumbers[n_pos])
    n_pos = n_pos + 1

    ##for i in [100,200,300,400,500,600,700,800,900,1000]:
        ##for j in [5,10,20,50,100,200,300,400,500,600,700,800,900,1000]:
    outputFile = open(filename+"_output", 'w')
    allParameters=[]
    all_bestSolutions_times=[]
    all_bestSolutions=[]
    all_antNumbers=[]
    allProcessTimes=[]
    for z in range(1):
        for x in [100,200,300,400,500,600]:
        ##for x in [600]:
            for y in [50,100,200]:
            ##for y in [200]:
                ##定义背包
                knapsack=CKnapsack(cap_num,item_num, profitMatrix, item_restrictMatrix, max_capacityMatrix)
                ##定义图
                ##print("tao初值:"+str(i)+";Q值："+str(j)+":\n")
                antsGraph=CAntsForGraph(knapsack,400,0.7, 0.3, 0.2, 400)
                # bestSolutions,antNumbers,processTime=antsGraph.solve(x,y,False)
                # print(str(x)+";"+str(y)+";"+str(bestSolutions)+";"+str(np.max(bestSolutions))+";"+str(antNumbers)+";"+str(processTime))
                # outputFile.write(str(x)+";"+str(y)+";"+str(bestSolutions)+";"+str(np.max(bestSolutions))+";"+str(antNumbers)+";"+str(processTime)+"\n")
                #
                # ##
                # allParameters.append((x,y,False))
                # temp=[i for i in range(len(bestSolutions)) if bestSolutions[i]==9492]
                # all_bestSolutions_times.append(len(temp))
                # all_bestSolutions.append(np.max(bestSolutions))
                # all_antNumbers.append(np.mean(antNumbers))
                # allProcessTimes.append(processTime)


                bestSolutions, antNumbers, processTime = antsGraph.solve(x, y, True)
                print(str(x)+";"+str(y)+";"+str(bestSolutions)+";"+str(np.max(bestSolutions))+";"+str(antNumbers)+";"+str(processTime))

                allParameters.append((x, y, True))
                temp = [i for i in range(len(bestSolutions)) if bestSolutions[i] == 9492]
                all_bestSolutions_times.append(len(temp))
                all_bestSolutions.append(np.max(bestSolutions))
                all_antNumbers.append(np.mean(antNumbers))
                allProcessTimes.append(processTime)
                outputFile.write(
                    str(x) + ";" + str(y) + ";" + str(bestSolutions) + ";" + str(np.max(bestSolutions)) + ";" + str(
                        antNumbers) + ";" + str(processTime) + "\n")
    print(allParameters)
    print(all_bestSolutions_times)
    print(all_bestSolutions)
    print(all_antNumbers)
    print(allProcessTimes)
    outputFile.write(str(allParameters) + "\n")
    outputFile.write(str(all_bestSolutions_times) + "\n")
    outputFile.write(str(all_bestSolutions) + "\n")
    outputFile.write(str(all_antNumbers) + "\n")
    outputFile.write(str(allProcessTimes) + "\n")
    outputFile.close()


if __name__ == '__main__':
    ##for filename in ["weish06.dat", "weish14.dat", "weish28.dat"]:


    # for filename in ["weish06.dat"]:
    #     processFile(filename, 'sac94-suite')
    # for filename in ["mk_gk01.dat","mk_gk02.dat","mk_gk03.dat","mk_gk04.dat","mk_gk05.dat","mk_gk06.dat","mk_gk07.dat","mk_gk08.dat","mk_gk09.dat","mk_gk10.dat","mk_gk11.dat"]:
    #     processFile("MK_GK\MK_GK_Instances\\"+filename, 'MK_GK')

    # for filename in ["HP1.DAT","HP2.DAT","PB1.DAT","PB2.DAT","PB4.DAT","PB5.DAT","PB6.DAT","PB7.DAT","SENTO1.DAT","SENTO2.DAT","WEING1.DAT","WEING2.DAT",
    #                  "WEING3.DAT","WEING4.DAT","WEING5.DAT","WEING6.DAT","WEING7.DAT","WEING8.DAT","WEISH01.DAT","WEISH02.DAT","WEISH03.DAT","WEISH04.DAT",
    #                 "WEISH05.DAT","WEISH06.DAT","WEISH07.DAT","WEISH08.DAT","WEISH09.DAT","WEISH10.DAT","WEISH11.DAT","WEISH12.DAT","WEISH13.DAT","WEISH14.DAT",
    #                  "WEISH15.DAT","WEISH16.DAT","WEISH17.DAT","WEISH18.DAT","WEISH19.DAT","WEISH20.DAT","WEISH21.DAT","WEISH22.DAT","WEISH23.DAT","WEISH24.DAT",
    #                  "WEISH25.DAT","WEISH26.DAT","WEISH27.DAT","WEISH28.DAT","WEISH29.DAT","WEISH30.DAT"]:
    #     processFile("OR-Library\\整理后\\"+filename, 'OR_Library')

    for filename in ["250-30-1.dat"]:
        processFile("OR-Library\\整理后\\"+filename, 'OR_Library_Type2')

    # startTime = datetime.datetime.now()
    # aa=np.random.randint(2,size=(10000, 10000))
    # bb = np.random.randint(2, size=(10000, 10000))

    # print(datetime.datetime.now()-startTime)
    # for i in range(5000):
    #     aa=np.dot(aa,bb)
    #     print(datetime.datetime.now()-startTime)



