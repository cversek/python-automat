import numpy
from collections import deque

def leastsq_diff(X,Y,N=5):
    X = numpy.array(X)
    Y = numpy.array(Y)
    return numpy.fromiter(gen_diff(X,Y,N),dtype=X.dtype)

def gen_diff(X_stream,Y_stream,N):
    X_stream = iter(X_stream)
    Y_stream = iter(Y_stream)
    #fill the sample queue
    S = deque()
    for x in range(N):
        S.append((next(X_stream),next(Y_stream)))
    #center the output on the window
    for x in range(N//2):
        yield 0.0
    #compute the accumulators
    X,Y = numpy.array(S).transpose()
    Tx  = X.sum()
    Ty  = Y.sum()
    Txx = (X*X).sum()
    Txy = (X*Y).sum()
    try:
        while True:
            #compute some squares from accumulators
            SSxx = Txx - float(Tx*Tx)/N
            SSxy = Txy - float(Tx*Ty)/N
            #compute fit parameters
            a = SSxy/SSxx
            #return results
            yield a
            #get next sample and adjust accumulators which might change
            S.popleft()
            S.append((next(X_stream),next(Y_stream)))
            X,Y = numpy.array(S).transpose()
            Tx  = X.sum()
            Ty  = Y.sum()
            Txx = (X*X).sum()
            Txy = (X*Y).sum()
    except StopIteration:
        pass
    #center the output on the window
    for x in range(N//2):
        yield 0.0    

from numpy import linspace
from scipy.interpolate import splprep, splev, interp1d        
def interp2d_scatter(X,Y,npts = None, k=3, s=0, spacing='original'):
    """ Interpolates the X,Y point data treated as a 2D curve, using a kth order spline (1 <= k <= 5).
        Note: if duplicate data points abbut each other, then SystemError is raised.
    """
    if npts is None:
        npts = 2*len(X)
    tck,U = splprep([X,Y],k=k,s=s)  #tck is the spline rep., U is the parameter from 0..1
    Ui = None
    if spacing == 'original':
        #we can interpolate the orginal U parameter to get 
        U_x  = linspace(0.0,1.0,len(U))
        U_xi = linspace(0.0,1.0,npts)
        Ui = interp1d(U_x, U, kind='linear')(U_xi)
    elif spacing == 'uniform':
        Ui = linspace(0.0,1.0,npts) 
    Xi, Yi = splev(Ui,tck)
    return (Xi, Yi)
 
from numpy import diff, argwhere, sqrt  
def filter_close_neighbors(X, Y = None, tolerance = 1e-6):
    """ Filters out neighboring points that lie within a Euclidean distance of the 'tolerance'.
    """
    if Y is None:
        dX = diff(X)
        mask = argwhere(abs(dX) > tolerance)
        return X[mask].flatten()
    else:
        dX, dY = diff(X), diff(Y) 
        mask = argwhere(sqrt(dX*dX + dY*dY) > tolerance)
        return (X[mask].flatten(), Y[mask].flatten())        
        
if __name__ == "__main__":
    A = 3.245*numpy.arange(11)
    D = leastsq_diff(A,N=5)
    print(len(A),A)
    print(len(D),D)
       
            
        
            
        
        
        
        
