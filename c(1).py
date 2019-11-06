# Put your solution here.
import networkx as nx
import random
import numpy as np
from numpy import inf
np.set_printoptions(threshold=np.inf)

def showweight(client,xx):
    xxx=xx.copy()
    print("weight:",xxx)

def showx(client,xx):
    xxx=xx.copy()
    for stu in range(client.k):
        xxx[stu]=int(xxx[stu]*1000)
    print("xx:",xxx)

##find the nearest neighbour from u
def findneighbour(client, map1, u):
    neighbourlist = []
    for i in range(1, client.v + 1):
        if map1[i][u] != 0:
            neighbourlist.append(i)
    return neighbourlist

def MW(all_students,map1, client, epsilon):
    botslocation = []  # record all bots locations
    remainbots = client.bots  # record number of bots unfounded yet
    h = client.home  # home
    all = set([i + 1 for i in range(client.v)])
    visited = set([h])  # visited vertices set
    unvisited = all - visited  # unvisited vertices set
    xx = [np.random.normal(1,0.1)/client.students] * (client.students)  # Multi-Weight:x
    weightsum=0
    weight=np.zeros(len(xx))
    for i in range(len(xx)):
        weightsum+=xx[i]
    for i in range(len(xx)):
        weight[i]=xx[i]/weightsum
    claim2=[0]
    for i in range(1,client.v+1):
        if i==client.h:
            claim2.append([False]*client.k)
        else:
            claim2.append(client.scout(i, all_students))
    assert len(claim2)==client.v+1
    ##pick next vertex:
    while remainbots > 0 and len(visited)<client.v:
        weightsum=0
        maxvote = 0  # mark the maximum possibility where a bot will be at
        minvote=inf
        un = 0  # most possible vertex
        vn = 0  # neighbour of un that is least possible
        ##find the most possible and least possible vertex where a bot may be at
        for u in unvisited:
            currvote = 0  # mark the current score that a bot will be there
            for stu in range(client.students):
                if claim2[u][stu + 1] == True:
                    currvote += xx[stu]
            if currvote > maxvote:
                maxvote = currvote
                un = u
        #print("maxvote:", maxvote)
        """
                for v in set(findneighbour(client,map1,un))-{client.h}:
            currvote=0
            for stu in range(client.students):
                if claim2[v][stu + 1] == True:
                    currvote += xx[stu]
            if currvote < minvote:
                minvote = currvote
                vn = v
        """
        if map1[un][h]==0:
            for v in set(findneighbour(client, map1, un)) - {client.h}:
                currvote = 0
                for stu in range(client.students):
                    if claim2[v][stu + 1] == True:
                        currvote += xx[stu]
                if currvote < minvote:
                    minvote = currvote
                    vn = v
        else:
            vn=h
        #print("minvote:", minvote)
        if un == 0: #very rare case, you may omit
            un = unvisited.pop()
            visited.add(un)
        else:
            visited.add(un)
            unvisited.remove(un)
            localsum = 0
            changinglist=[]
            getbot=client.remote(un, vn)
            if getbot == 0 or getbot==None:
                for stu in range(client.students):
                    if claim2[un][stu + 1] == True:
                        localsum+=1
                        changinglist.append(stu+1)
                        weight[stu] = xx[stu] * (1 - epsilon)
                    else:
                        weight[stu]=xx[stu]
                    weightsum += weight[stu]
                for stu in range(client.students):
                    xx[stu] = weight[stu] / weightsum
            else:
                botslocation.append(vn)
                remainbots -= getbot
                for stu in range(client.students):
                    if claim2[un][stu + 1] == False:
                        localsum+=1
                        changinglist.append(stu + 1)
                        weight[stu] = xx[stu] * (1 - epsilon)
                    else:
                        weight[stu]=xx[stu]
                    weightsum += weight[stu]
                for stu in range(client.students):
                    xx[stu] = weight[stu] / weightsum
        #print("changing list",changinglist)
        #print("weightsum:",weightsum)
        #print("changing rate:",localsum/client.k)
        #showweight(client,weight)
        #showx(client,xx)
    return client.bot_locations

def solve(client):
    client.end()
    client.start()

    all_students = list(range(1, client.students + 1))
    non_home = list(range(1, client.home)) + list(range(client.home + 1, client.v + 1))
    s = []  # the visited vertices
    logo = [0] * (client.v + 1)  # initialize all vertices for chosen points
    map1 = np.zeros((client.v + 1, client.v + 1))  # matrix storing all the edge values
    summ = 0  # seek for dist in descending order
    dist = [inf] * (client.v + 1)
    prev = [inf] * (client.v + 1)  # RECORD the previous vertex
    for u, v in client.G.edges:
        map1[u][v] = client.G[u][v]['weight']
        map1[v][u] = map1[u][v]
        if u == client.home:
            dist[v] = map1[u][v]
            prev[v] = u
    dist[client.home] = 0
    logo[client.home] = 1
    for t in range(1, client.v):  # run v-1 iterations to get the edges
        now = inf  # should be modified if the graph is connected
        min1 = inf
        pre = inf
        previous = 0  # initial
        for v in range(1, client.v + 1):
            if logo[v] == 0:  # min among all not picked v and finite h->v
                for w in range(1, client.v + 1):
                    if map1[w][v] < min1 and logo[w] == 1 and map1[w][v] != 0:
                        now = v
                        pre = w
                        min1 = map1[w][v]  # edge prev[v],v
        prev[now] = pre
        if now == inf:  # not updated
            print("no!!!")
            break
        logo[now] = 1  # as picked in the MST
        dist[now] = dist[prev[now]] + min1
    MW(all_students, map1, client, 0.01)
    print("over!")
    # print(client.bot_locations)
    # client.end()#break point here
    found = [0] * (client.v + 1)
    for location in client.bot_locations:
        found[location] = 1

    for t in range(1, len(dist) - 1):
        maxx = -1
        u = -1
        for v in range(1, len(dist)):
            if maxx < dist[v]:
                u = v
                maxx = dist[v]
        dist[u] = -1
        if found[u]:  # u has one
            # print("u is "+str(int(u))+" prev u is "+str(int(prev[u])))
            temp = client.remote(u, prev[u])
            print("temp is ",temp)
            found[u] = 0
            found[prev[u]] = 1
    ##            if prev[u] == client.h:
    ##                summ += temp
    print(client.l)
    print("home:",client.h)
    client.end()
