from math import log

def storeTree(inputTree, fileName):
    import pickle
    fw = open(fileName,'w')
    pickle.dump(inputTree, fw)
    fw.close()

def grabTree(fileName):
    import pickle
    fr = open(fileName)
    return pickle.load(fr)

def majorityCnt(classList):
    classCount = {}
    for vote in classList:
        if vote not in classCount.keys():
            classCount[vote] = 0
        classCount[vote] += 1
        sortedClassCount = sorted(classCount.iteritems(), 
                key = operator.iteritems(1), reverse = True)
        return sortedClassCount[0][0]

def createTree(dataSet, labels):
    classList = [example[-1] for example in dataSet]
    if classList.count(classList[0]) == len(classList):
        return classList[0]
    if len(dataSet[0]) == 1:
        return majorityCnt(classList)
    bestFeature = chooseBestFeatureToSplit(dataSet)
    print bestFeature
    print labels
    bestFeatLabel = labels[bestFeature]
    myTree = {bestFeatLabel:{}}
    del(labels[bestFeature])
    featValues = [example[bestFeature] for example in dataSet]
    uniqueVal = set(featValues)
    for value in uniqueVal:
        subLabels = labels[:]
        myTree[bestFeatLabel][value] = createTree(splitDataSet(dataSet, bestFeature, value), subLabels)
    return myTree


def splitDataSet(dataSet, axis, value):
    retDataSet = []
    for featVec in dataSet:
        if featVec[axis] == value:
            reducedFeatVec = featVec[:axis]
            reducedFeatVec.extend(featVec[axis+1: ])
            retDataSet.append(reducedFeatVec)
    return retDataSet

def chooseBestFeatureToSplit(dataSet):
    numberFeatures = len(dataSet[0]) - 1
    baseEntropy = calcShannonEnt(dataSet)
    bestInfoGain = 0.0; bestFeature = -1
    for i in range(numberFeatures):
        featureList = [example[i] for example in dataSet]
        uniqueVal = set(featureList)
        newEntropy = 0.0
        for value in uniqueVal:
            subDataSet = splitDataSet(dataSet, i, value)
            prob = len(subDataSet) / float(len(dataSet))
            newEntropy += prob * calcShannonEnt(subDataSet)
        infoGain = baseEntropy - newEntropy
        if(infoGain > bestInfoGain):
            bestInfoGain = infoGain
            bestFeature = i
    return bestFeature

def calcShannonEnt(dataSet):
    numberEntries = len(dataSet)
    labCount = {}
    for featVec in dataSet:
        currentLabel = featVec[-1]
        if currentLabel not in labCount.keys():
            labCount[currentLabel] = 0
        labCount[currentLabel] += 1

    shannonEnt = 0.0
    for key in labCount:
        prob = float(labCount[key])/numberEntries
        shannonEnt -= prob * log(prob, 2)
    return shannonEnt

def createDataSet():
    dataSet = [
            [1, 1, 'yes'],
            [1, 1, 'yes'],
            [1, 0, 'no'],
            [0, 1, 'no'],
            [0, 1, 'no']
            ]
    labels = ['no surfacing', 'flippers']
    return dataSet, labels

