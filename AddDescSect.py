import FitImport as imp
import numpy as np
import os
from math import *
from sklearn.kernel_ridge import KernelRidge
from sklearn.grid_search import GridSearchCV
from sklearn import cross_validation
from sklearn.cross_validation import train_test_split
from sklearn.metrics import mean_squared_error



FILENAME = "test.txt"   #If importing a File with a Descriptor order the
                        # name of the file goes here

#Method select calls The GKRR methods. To use a different machine learning tool
# in place of GKRR, returning the RMS from MethodSelect
def MethodSelect(TestSet,Y,f):
    return SplitFitGKRR(TestSet,Y,f)

##--------GKRR METHODS---------#

def GetPrediction(X,regr):
    return regr.predict(X)

def GetRMSE(Y,YP):
    return sqrt(mean_squared_error(Y,YP))

def SplitFitGKRR(X,Y,n):
    Xt,XT,Yt,YT = cross_validation.train_test_split(X, Y, test_size = n)
    regr = setBestParameters(len(Xt))
    regr.fit(Xt,Yt)
    return GetRMSE(YT,GetPrediction(XT,regr))

def setBestParameters(length,npts=25,numfolds=3):
    if numfolds > length:
        numfolds = length-2
    return GridSearchCV(KernelRidge(kernel='rbf'),
                          param_grid={"alpha": np.logspace(-6,3,npts),
                                      "gamma": np.logspace(-10,0,npts)}, cv=numfolds)

##--------GKRR METHODS---------#


#Finds the nth descriptor, if a array of descriptor names is passed, returns
# the name as well
def GODesc(X,n,label=None):
    if label != None:
        L = label[0][n]
    else:
        L = "None"
    X = X[:,n]
    return list(X),L

#normalizes the passed arrays values to be between 0 and 1
def normalizeData(X):
    for m in range(len(X[0])):
        ma = max(X[:,m])
        mi = min(X[:,m])
        for n in range(len(X)):
            if ma != mi: X[n][m] = ((X[n][m] - mi)/(ma-mi))
            else: X[n][m] = 0.5
    return X

#reads a file, creating an array where each line is a entry.
def ReadNum():
    data = []
    f = open(FILENAME,"r")
    for line in f:
        entries = line
        data.append(entries)    
    f.close()
    return data

#--------Main Method---------#

def AddDescrSection(m=10,r=50,F=False):
    X,Y,L = imp.FullImport()
    X = normalizeData(X)
    if(F==True):
        D = ReadNum()
    T = len(X[0])       #The total number of Descriptors 
    pts = len(X)        #The number of data points
    Ls = floor(T/m)     #The total number of Sections
    AllRms = []         #Holds all the average RMS

    #Completes when has done all complete sections of data specified, remaining
    # descriptors will be added to a shorter section after the loop
    for n in range(1,Ls+1):
        RMSSet = []
        TestSet = []

        #adds in "m*n" descriptors in one of two methods:
        #If have a different ordering of Descriptors added in that order
        if(F == True):
            for i in range(m*n):
                Next,_ = GODesc(X,D[i])
                TestSet.append(Next)

        #Otherwise Descriptors added in order from initial file 
        else:
            for i in range(m*n):
                Desct,_ = GODesc(X,i)
                TestSet.append(Desct)
                
        TestSet = np.swapaxes(np.array(TestSet),0,1)

        #Tests the limited number of Descriptors r times and computes the
        # average RMS
        for i in range(r):
            rms = MethodSelect(TestSet,Y,0.2)
            RMSSet.append(rms)
        AllRms.append(np.mean(RMSSet))


    #One additional loop for Descriptors that remain at end and were not added
    # to any group
    TestSet = []
    for i in range(T):
        Next,_ = GODesc(X,D[i])
        TestSet.append(Next)

    TestSet = np.swapaxes(np.array(TestSet),0,1)
    RMSSet = []

    #Tests the limited number of Descriptors r times and computes the
    # average RMS
    for i in range(r):                      
        rms = MethodSelect(TestSet,Y,0.2)
        RMSSet.append(rms)
    AllRms.append(np.mean(RMSSet))

    #Prints The results
    print("Format:  Descriptor#     RMS")
    for n in range(1,Ls):
        print("          "+str(n*m)+"          "+str(AllRms[n-1]))
    print("          "+str(T)+"          "+str(AllRms[-1]))

#Main Method takes between 0 and 3 arguments (all are optional)
#   arg 1:m (int), default = 10
#           The length of a Descriptor section to add
#   arg 2:r (int), default = 50
#           The number of iterations you want to run on each Descriptor Section
#   arg 3:F (boolean), default
#           If set to true, program will try to read from FILENAME to get the
#            indices of Descriptors to add as an order to add them in

if __name__ == '__main__':
    AddDescrSection(10,50);
