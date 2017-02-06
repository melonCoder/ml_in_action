def loadSimpledat():
    simpDat = [['r', 'z', 'h', 'j', 'p'],
               ['z', 'y', 'x', 'w', 'v', 'u', 't', 's'],
               ['z'],
               ['r', 'x', 'n', 'o', 's'],
               ['y', 'r', 'x', 'z', 'q', 't', 'p'],
               ['y', 'z', 'x', 'e', 'q', 's', 't', 'm']]
    return simpDat

class treeNode:
    def __init__(self, nameValue, numOccur, parentNode):
        self.name = nameValue
        self.count = numOccur
        self.nodeLink = None
        self.parent = parentNode
        self.children = {}

    def inc(self, numOccur):
        self.count += numOccur

    def disp(self, ind = 1):
        print('  ' * ind, self.name, ' ', self.count)
        for child in self.children.values():
            child.disp(ind + 1)

def createInitSet(dataSet):
    retDict = {}
    for trans in dataSet:
        retDict[frozenset(trans)] = 1
    return retDict

# note the order of dataSet may influence the shape of the tree.
def createTree(dataSet, minSup  = 1):
    headerTable = {}
    for trans in dataSet:
        for item in trans:
            headerTable[item] = headerTable.get(item, 0) + dataSet[trans]
    keys = [key for key in headerTable.keys()]
    for k in keys:
        if headerTable[k] < minSup:
            del(headerTable[k])
    freqItemSet = set(headerTable.keys())
    if len(freqItemSet) == 0:
        return None, None
    for k in headerTable:
        headerTable[k] = [headerTable[k], None]
    retTree = treeNode('Null Set', 1, None)
    for tranSet, count in dataSet.items():
        localD = {}
        for item in tranSet:
            if item in freqItemSet:
                localD[item] = headerTable[item][0]
        if len(localD) > 0:
            orderedItems = [v[0] for v in sorted(localD.items(), \
                    key=lambda p:p[1], reverse=True)]
            updateTree(orderedItems, retTree, headerTable, count)
    return retTree, headerTable

def updateTree(items, inTree, headerTable, count):
    if items[0] in inTree.children:
        inTree.children[items[0]].inc(count)
    else:
        inTree.children[items[0]] = treeNode(items[0], count, inTree)
        if headerTable[items[0]][1] == None:
            headerTable[items[0]][1] = inTree.children[items[0]]
        else:
            updateHeader(headerTable[items[0]][1], inTree.children[items[0]])

    if len(items) > 1:
        updateTree(items[1::], inTree.children[items[0]], headerTable, count)

def updateHeader(nodeToTest, targetNode):
    while nodeToTest.nodeLink != None:
        nodeToTest = nodeToTest.nodeLink
    nodeToTest.nodeLink = targetNode

def ascendTree(leafNode, prefixPath):
    if leafNode.parent != None:
        prefixPath.append(leafNode.name)
        ascendTree(leafNode.parent, prefixPath)

def findPrefixPath(basePath, treeNode):
    condPaths = {}
    while treeNode != None:
        prefixPath = []
        ascendTree(treeNode, prefixPath)
        if len(prefixPath) > 1:
            condPaths[frozenset(prefixPath[1:])] = treeNode.count
        treeNode = treeNode.nodeLink
    return condPaths

def mineTree(inTree, headerTable, minSup, preFix, freqItemSet):
    bigL = [v[0] for v in sorted(headerTable.items(), key = lambda p: p[0])]
    for basePath in bigL:
        newFreqSet = preFix.copy()
        newFreqSet.add(basePath)
        freqItemSet.append(newFreqSet)
        condPattBases = findPrefixPath(basePath, headerTable[basePath][1])
        myCondTree, myHead = createTree(condPattBases, minSup)
        if myHead != None:
            print('conditional tree for: ', newFreqSet)
            myCondTree.disp(1)
            mineTree(myCondTree, myHead, minSup, newFreqSet, freqItemSet)

import twitter
from time import sleep
import re

def getLotsOfTweets(searchStr):
    CONSUMER_KEY = '5m6HL6NcT4IwLBiGLsNuAtq8F'
    CONSUMER_SECRET = 'kQpjN3qjHj0SVzAL2ulKO1dkJYoiBdbIvVm3GZBFuYdTXHMy8e'
    ACCESS_TOKEN_KEY = '371290429qOrzbUfJT0Wal3Xx1orQjO1hGdT4fEkIUv8iTYIy'
    ACCESS_TOKEN_SECRET = 'au3nO28thkLoHqCH6Lz8vRtwaZagiLncftPJw5vX6cVCI'
    api = twitter.Api(consumer_key = CONSUMER_KEY,
                      consumer_secret = CONSUMER_SECRET,
                      access_token_key = ACCESS_TOKEN_KEY,
                      access_token_secret = ACCESS_TOKEN_SECRET)
    # get 1500 results: 15 pages * 100 per pages
    # resultPages = []
    resultPages = api.GetSearch(term = searchStr, count = 100)
    #for i in range(1, 15):
    #    print('fetching page %d' % i)
    #    searchResult = api.GetSearch(searchStr, count = 100, page = i)
    #    resultPages.append(searchResult)
    #    sleep(5)
    return resultPages
