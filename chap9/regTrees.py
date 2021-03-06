from numpy import *

def loadDataSet(fileName):
    dataMat = []
    fr = open(fileName)
    for line in fr.readlines():
        curLine = line.strip().split('\t')
        #fltLine = map(float, curLine)
        fltLine = [float(x) for x in curLine]
        dataMat.append(fltLine)
    return dataMat

def plotData(fileName, i = 0, j = 1):
    dataSet = loadDataSet(fileName)
    dataMat = mat(dataSet)

    import matplotlib.pyplot as plt
    fig = plt.figure()
    ax = fig.add_subplot(111)
    ax.scatter(dataMat[:, i].flatten().A[0], dataMat[:, j].flatten().A[0])
    plt.show()

def binSplitDataSet(dataSet, feature, value):
    mat0 = dataSet[nonzero(dataSet[:, feature] > value)[0], :]
    mat1 = dataSet[nonzero(dataSet[:, feature] <= value)[0], :]
    return mat0, mat1

def regLeaf(dataSet):
    return mean(dataSet[:, -1])

def regErr(dataSet):
    return var(dataSet[:, -1]) * shape(dataSet)[0]

def linearSolve(dataSet):
    m, n = shape(dataSet)
    X = mat(ones((m, n)))
    Y = mat(ones((m, 1)))
    X[:, 1 : n] = dataSet[:, 0 : n - 1]
    Y = dataSet[:, -1]
    xTx = X.T*X
    if linalg.det(xTx) == 0.0:
        raise NameError('This matrix is singular, can not do inverse,\n\
                try increase the second value of ops')
    ws = xTx.I * (X.T * Y)
    return ws, X, Y

def modelLeaf(dataSet):
    ws, X, Y = linearSolve(dataSet)
    return ws

def modelErr(dataSet):
    ws, X, Y = linearSolve(dataSet)
    yHat = X * ws
    return sum(power(Y - yHat, 2))

# createTree is not compliable until regLeaf, regErr and chooseBestSplit is
# defined.
def createTree(dataSet, leafType = regLeaf, errType = regErr, ops = [1, 4]):
    feat, val = chooseBestSplit(dataSet, leafType, errType, ops)
    if feat == None:
        return val

    retTree = {}
    retTree['spInd'] = feat
    retTree['spVal'] = val
    lSet, rSet = binSplitDataSet(dataSet, feat, val)
    retTree['left'] = createTree(lSet, leafType, errType, ops)
    retTree['right'] = createTree(rSet, leafType, errType, ops)
    return retTree

def chooseBestSplit(dataSet, leafType = regLeaf, errType = regErr, ops = [1,
    4]):
    tolS = ops[0]
    tolN = ops[1]
    if len(set(dataSet[:, -1].T.tolist()[0])) == 1:
        return None, leafType(dataSet)

    m, n = shape(dataSet)
    S = errType(dataSet)
    bestS = inf
    bestIndex = 0
    bestValue = 0
    for featIndex in range(n - 1):
        for splitVal in set(dataSet[:, featIndex].T.tolist()[0]):
            mat0, mat1 = binSplitDataSet(dataSet, featIndex, splitVal)
            if (shape(mat0)[0] < tolN) or (shape(mat1)[0] < tolN):
                continue
            newS = errType(mat0) + errType(mat1)
            if newS  < bestS:
                bestIndex = featIndex
                bestValue = splitVal
                bestS = newS

    if(S - bestS) <tolS:
        return None, leafType(dataSet)
    mat0, mat1 = binSplitDataSet(dataSet, bestIndex, bestValue)
    if (shape(mat0)[0] < tolN) or (shape(mat1)[0] < tolN):
        return None, leafType(dataSet)
    return bestIndex, bestValue

def isTree(obj):
    return (type(obj).__name__ == 'dict')

def getMean(tree):
    if isTree(tree['right']):
        tree['right'] = getMean(tree['right'])
    if isTree(tree['left']):
        tree['left'] = getMean(tree['left'])
    return (tree['left'] + tree['right']) / 2.0

def prune(tree, testData):
    if shape(testData)[0] == 0:
        return getMean(tree)

    if (isTree(tree['right'])) or (isTree(tree['left'])):
        lSet, rSet = binSplitDataSet(testData, tree['spInd'], tree['spVal'])
    if isTree(tree['left']):
        tree['left'] = prune(tree['left'], lSet)
    if isTree(tree['right']):
        tree['right'] = prune(tree['right'], rSet)
    if not isTree(tree['left']) and not isTree(tree['right']):
        lSet, rSet = binSplitDataSet(testData, tree['spInd'], tree['spVal'])
        errorNoMerge = sum(power(lSet[:, -1] - tree['left'], 2)) + \
                sum(power(rSet[:, -1] - tree['right'], 2))
        treeMean = (tree['left'] + tree['right']) / 2.0
        errorMerge = sum(power(testData[:, -1] - treeMean, 2))
        if errorNoMerge > errorMerge:
            print("Merging")
            return treeMean
        else:
            return tree
    else:
        return tree

def TestModelTree():
    myMat = mat(loadDataSet('exp2.txt'))
    print(createTree(myMat, modelLeaf, modelErr, (1, 10)))

def regTreeEval(model, inDat):
    return float(model)

def modelTreeVal(model, inDat):
    n = shape(inDat)[1]
    X = mat(ones((1, n + 1)))
    X[:, 1 : n + 1] = inDat
    return float(X * model)

def treeForeCast(tree, inDat, modelEval = regTreeEval):
    if not isTree(tree):
        return modelEval(tree, inDat)

    if inDat[tree['spInd']] > tree['spVal']:
        if isTree(tree['left']):
            return treeForeCast(tree['left'], inDat, modelEval)
        else:
            return modelEval(tree['left'], inDat)
    else:
        if isTree(tree['right']):
            return treeForeCast(tree['right'], inDat, modelEval)
        else:
            return modelEval(tree['right'], inDat)

def createForeCast(tree, testData, modelEval = regTreeEval):
    m = len(testData)
    yHat = mat(zeros((m, 1)))
    for i in range(m):
        yHat[i, 0] = treeForeCast(tree, mat(testData[i]), modelEval)
    return yHat

def TestComprasion():
    trainMat = mat(loadDataSet('bikeSpeedVsIq_train.txt'))
    testMat = mat(loadDataSet('bikeSpeedVsIq_test.txt'))

    # Regression tree
    myTree = createTree(trainMat, ops = (1, 20))
    yHat = createForeCast(myTree, testMat[:, 0])
    corRegTree = corrcoef(yHat, testMat[:, 1], rowvar = 0)[0, 1]
    print("corrcoef of regression tree is %f", corRegTree)

    # Model tree
    myTree = createTree(trainMat, modelLeaf, modelErr, ops = (1, 20))
    yHat = createForeCast(myTree, testMat[:, 0], modelTreeVal)
    corModelTree = corrcoef(yHat, testMat[:, 1], rowvar = 0)[0, 1]
    print("corrcoef of model tree is %f", corModelTree)

    # classical regression tree
    ws, X, Y = linearSolve(trainMat)
    for i in range(shape(testMat)[0]):
        yHat[i] = testMat[i, 0] * ws[1, 0] + ws[0, 0]
    corReg = corrcoef(yHat, testMat[:, 1], rowvar = 0)[0, 1]
    print("corrcoef of classical regression is %f", corReg)
