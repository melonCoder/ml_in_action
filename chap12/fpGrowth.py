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
    # Note to remove personal keys before published
    CONSUMER_KEY = ''
    CONSUMER_SECRET = ''
    ACCESS_TOKEN_KEY = ''
    ACCESS_TOKEN_SECRET = ''
    # twitter api has changed since ml_in_action was written, now, we can
    # at most get 100 search results.
    api = twitter.Api(consumer_key = CONSUMER_KEY,
                      consumer_secret = CONSUMER_SECRET,
                      access_token_key = ACCESS_TOKEN_KEY,
                      access_token_secret = ACCESS_TOKEN_SECRET)
    resultPages = api.GetSearch(term = searchStr, count = 100)
    return resultPages

def textParse(bigString):
    urlsRemoved = re.sub('(http[s]?:[/][/]|www.)([a-z]|[A-Z]|[0-9]|[/.]|[~])*',\
            '', bigString)
    listOfTokens = re.split(r'\W*', urlsRemoved)
    # since in english, plenty of worlds are meaningless, remember to
    # remove it
    forbiddenList = ['and', 'the', 'this', 'with', 'for', 'is', 'are',\
            'was', 'were']
    return [tok.lower() for tok in listOfTokens \
            if len(tok) > 2 and tok.lower() not in forbiddenList]

def mineTweets(tweetArr, minSup = 5):
    parsedList = []
    for i in range(100):
        parsedList.append(textParse(tweetArr[i].text))
    initSet = createInitSet(parsedList)
    myFptree, myHeaderTab = createTree(initSet, minSup)
    myFreqList = []
    mineTree(myFptree, myHeaderTab, minSup, set([]), myFreqList)
    return myFreqList
