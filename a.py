# Put your solution here.
import networkx as nx
import random
import numpy as np
from numpy import inf

##find the nearest neighbour from u
def findneighbour(client,map1,u):
    neighbourlist=[]
    for i in range(1,client.v+1):
        if map1[i][u]!=0:
            neighbourlist.append(i)
    return neighbourlist

def MW(all_students,map1, client, epsilon):
    #print(all_students)
    botslocation = []  # record all bots locations
    remainbots = client.bots  # record number of bots unfounded yet
    h = client.home  # home
    all = set([i + 1 for i in range(client.v)])
    visited = set([h])  # visited vertices set
    unvisited = all - visited  # unvisited vertices set
    xx = [1 / client.students] * (client.students)  # Multi-Weight:x
    weight = xx.copy()  # Multi-Weight:weight
    #I want to do the same for home, not the nearest
    ##first iertation: find the nearest neighbor from h
    mindis1 = inf
    v1 = 0  # store nearest neighbor from h
    for vv in findneighbour(client, map1, h):
        if map1[vv][h] < mindis1:
            mindis1 = map1[vv][h]
            v1 = vv
            break
    visited.add(v1)  # add v1 into visited set

    ##first iteration: scout, remote and update
    weightsum = 0
    claim = client.scout(v1, all_students)
    #print("claim: ",claim)
    if client.remote(v1, h) == 0:
        for stu in range(client.students):
            if claim[stu + 1] == True:
                weight[stu] = xx[stu] * (1 - epsilon)
            weightsum += weight[stu]
        for stu in range(client.students):
            xx[stu] = weight[stu] / weightsum
    else:
        #botslocation.append(h)
        remainbots -= 1
        for stu in range(client.students):
            if claim[stu + 1] == False:
                weight[stu] = xx[stu] * (1 - epsilon)
            weightsum += weight[stu]
        for stu in range(client.students):
            xx[stu] = weight[stu] / weightsum
    visited.add(v1)
    unvisited.remove(v1)

    ##pick next vertex:
    while remainbots > 0:
        maxvote = 0  # mark the maximum score that a bot will be there
        un = 0  # unvisited vertex
        vn = 0  # visited vertex
        ##find the most possible vertex that a bot will be there
        wanted=[]
        for v in visited:
            for u in unvisited:
                if u in findneighbour(client, map1, v) and u not in wanted:
                    wanted.append(u)
        for u in wanted:
            claim = client.scout(u, all_students)
            currvote = 0  # mark the current score that a bot will be there
            for stu in range(client.students):
                if claim[stu + 1] == True:
                    currvote += xx[stu]
            if currvote > maxvote:
                maxvote = currvote
                vn = v
                un = u
        if un == 0: #very rare case, you may omit
            print("something goes wrong here")
            un = unvisited.pop()
            visited.add(un)
        else:
            visited.add(un)
            unvisited.remove(un)
            claim = client.scout(un, all_students)
            if client.remote(un, vn) == 0:
                for stu in range(client.students):
                    if claim[stu + 1] == True:
                        weight[stu] = xx[stu] * (1 - epsilon)
                    weightsum += weight[stu]
                for stu in range(client.students):
                    xx[stu] = weight[stu] / weightsum
            else:
                botslocation.append(vn)
                remainbots -= 1
                for stu in range(client.students):
                    if claim[stu + 1] == False:
                        weight[stu] = xx[stu] * (1 - epsilon)
                    weightsum += weight[stu]
                for stu in range(client.students):
                    xx[stu] = weight[stu] / weightsum
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
                    if map1[w][v] < min1 and logo[w] == 1 and map1[w][v]!=0:
                        now = v
                        pre = w
                        min1 = map1[w][v]  # edge prev[v],v
        prev[now] = pre
        if now == inf:  # not updated
            print("no!!!")
            break
        logo[now] = 1  # as picked in the MST
        dist[now] = dist[prev[now]] + min1
    students=list(range(1,client.students+1))

    MW(students,map1,client,0.1)
    #print(client.bot_locations)
    #client.end()#break point here
    found=[0]*(client.v+1)
    for location in client.bot_locations:
        found[location]=1
    
    for t in range(1, len(dist) - 1):
        maxx = -1
        u = -1
        for v in range(1, len(dist)):
            if maxx < dist[v]:
                u = v
                maxx = dist[v]
        dist[u] = -1
        if found[u]:#u has one
            #print("u is "+str(int(u))+" prev u is "+str(int(prev[u])))
            temp = client.remote(u, prev[u])
            #print("temp is ",temp)
            found[u]=0
            found[prev[u]]=1
##            if prev[u] == client.h:
##                summ += temp
    client.end()
