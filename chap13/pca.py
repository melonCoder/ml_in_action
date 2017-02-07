from numpy import *

def loadDataSet(fileName, delim = '\t'):
    fr = open(fileName)
    stringArr = [line.strip().split(delim) for line in fr.readlines()]
    dataArr = []
    for line in stringArr:
        dataArr.append([float(x) for x in line])
    return mat(dataArr)

def pca(dataMat, topNfeat = 9999999):
    meanVals = mean(dataMat, axis = 0)
    meanRemoved = dataMat - meanVals
    covMat = cov(meanRemoved, rowvar = 0)
    eigVals, eigVects = linalg.eig(mat(covMat))
    eigValInd = argsort(eigVals)
    eigValInd = eigValInd[: -(topNfeat + 1) : -1]
    redEigVects = eigVects[:, eigValInd]
    lowDDataMat = meanRemoved * redEigVects
    reconMat = (lowDDataMat * redEigVects.T) + meanVals
    return lowDDataMat, reconMat

def plotPcaResult():
    import matplotlib.pyplot as plt

    dataMat = loadDataSet('./testSet.txt')
    lowDMat1, reconMat1 = pca(dataMat, 1)
    lowDMat2, reconMat2 = pca(dataMat, 2)

    fig = plt.figure()
    ax1 = fig.add_subplot(121)
    ax2 = fig.add_subplot(122)
    ax1.scatter(dataMat[:, 0].flatten().A[0], dataMat[:, 1].flatten().A[0], \
            marker = '^', s = 90)
    ax1.scatter(lowDMat1[:, 0].flatten().A[0], [0] * len(lowDMat1), marker = '+', s = 70, \
            c = 'green')
    ax1.scatter(reconMat1[:, 0].flatten().A[0], reconMat1[:, 1].flatten().A[0],\
            marker = 'o', s= 50, c = 'red')
    ax2.scatter(dataMat[:, 0].flatten().A[0], dataMat[:, 1].flatten().A[0], \
            marker = '^', s = 90)
    ax2.scatter(lowDMat2[:, 0].flatten().A[0], lowDMat2[:, 1].flatten().A[0], \
            marker = '+', s = 70, c = 'green')
    ax2.scatter(reconMat2[:, 0].flatten().A[0], reconMat2[:, 1].flatten().A[0],\
            marker = 'o', s= 50, c = 'red')
    plt.show()

def replaceNanWithMean():
    datMat = loadDataSet('secom.data', ' ')
    numFeat = shape(datMat)[1]
    for i in range(numFeat):
        meanVal = mean(datMat[nonzero(~isnan(datMat[:, i]))[0], i])
        datMat[nonzero(isnan(datMat[:, i]))[0], i] = meanVal
    return datMat

def plotVarDistribution(n = 20):
    import matplotlib.pyplot as plt

    datMat = replaceNanWithMean()
    meanVals = mean(datMat, axis = 0)
    meanRemoved = datMat - meanVals
    covMat = cov(meanRemoved, rowvar = 0)
    eigVals, eigVects = linalg.eig(mat(covMat))

    totalVar = sum(eigVals)
    varPercent = [x / totalVar for x in eigVals]
    fig = plt.figure()
    left_axis = fig.add_subplot(111)
    right_axis = left_axis.twinx()
    left_axis.plot(range(n), varPercent[: n], marker = '^')
    right_axis.plot(range(n), [sum(varPercent[: i]) for i in range(n)], \
            marker = 'v')
    plt.show()
