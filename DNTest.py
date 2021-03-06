import FitImport as imp
import numpy as np
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
                                      "gamma": np.logspace(-10,0,npts)},
                            cv=numfolds)


#--------Descriptor Methods---------#

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
def ReadFile():
    data = []
    f = open(FILENAME,"r")
    for line in f:
        entries = line
        data.append(entries)    
    f.close()
    return data

#--------Main Method---------#

def DescrNeeds(Limit, i = 50, F=False,n=1):
    X,Y,L = imp.FullImport();
    X = normalizeData(X)
    start = n
    if(F==True):
        D = ReadFile()
    Total = len(X[0])       #The total number of Descriptors   
    aveRMS = []

    #Completes when reacing the Limit specified or the has added in all
    #Descriptors, whichever comes first
    while((n =< Limit)&(n <= Total)):
        TestSet = []
        setRMS = []

        #adds in "n" descriptors in one of two methods:
            #If have a different ordering of Descriptors added in that order
        if(F == True):  
            for t in range(n):
                Desct,_ = GODesc(X,D[t])
                TestSet.append(Desct)

             #Otherwise Descriptors added in order from file               
        else:           
            for t in range(n):
                Desct,_ = GODesc(X,t)
                TestSet.append(Desct)
        TestSet = np.swapaxes(np.array(TestSet),0,1)


        #Tests the limitted number of Descriptors i times and computes the
        # average RMS
        for t in range(i):  
            rms = MethodSelect(TestSet,Y,0.2)
            setRMS.append(rms)
        aveRMS.append(np.mean(setRMS))
        n += 1

    #Resulst are ouput
    print(" Format: (# of Descr, RMS error) ")
    for t in range(len(aveRMS)):
        print("t is "+str(t))
        print("   ("+str(t+start)+" , "+str(aveRMS[t])+")  ")


#Main method takes between 1 and 4 arguments(the inal 3 are optional.
#   arg 1:Limit (int)
#           The max number of Descriptor you want to test
#   arg 2:i (int), default = 50
#           The number of iterations you want to run at each # of Descriptors
#   arg 3:F (boolean), default = False
#           If set to true, then program will try to read from FILENAME to
#           determine the order to add in Descriptors
#   arg 4:n (int), default = 1
#           The number of Descriptors to start testing with


DescrNeeds(10,100)
