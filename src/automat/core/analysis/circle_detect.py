from numpy import array, sqrt, cos, sin, linspace, histogram, hstack

from .arraytools import leastsq_diff, interp2d_scatter, filter_close_neighbors
from .curve_fitting import circle_fit

__DEBUG = True
if __DEBUG:
    from pylab import *


def circle_func(x0,y0,R):
    def inner(theta):
        X = x0 + R*cos(theta)
        Y = y0 + R*sin(theta) 
        return (X,Y)
    return inner


def circle_detect(X,Y, R_max = None, window_size = 5, interp_factor = 5, use_fit = True, debug = False, ):
    X = array(X)
    Y = array(Y)
    #safely configure default parameters
    if R_max is None:
        R_max = max(X.max(),Y.max())

    #try to interpolate the data using cubic splines to enhance algorithm robustness
    npts = int(len(X)*interp_factor)
    try:
        Xs0, Ys0 = interp2d_scatter(X,Y, npts, spacing='original')
    except SystemError: #caused by duplicate data points, a rare situation with real data
        #filter out duplicates
        Xs0, Ys0 = filter_close_neighbors(X,Y,tolerance=1e-6)
        Xs0, Ys0 = interp2d_scatter(Xs0,Ys0, npts)
        
    #compute the curvature
    DYs0  = leastsq_diff(Xs0 ,Ys0 , N = window_size )
    DDYs0 = leastsq_diff(Xs0 ,DYs0, N = window_size )
    Ks0 = DDYs0/(1.0 + DYs0**2)**(3.0/2.0)

    #filter out curvatures greater than the maxium radius circle
    s1_indices = argwhere(Ks0 < -1/R_max)
    Xs1    =   Xs0[s1_indices].flatten()
    Ys1    =   Ys0[s1_indices].flatten()
    DYs1   =  DYs0[s1_indices].flatten()
    DDYs1  = DDYs0[s1_indices].flatten()
    Ks1    =   Ks0[s1_indices].flatten()

    #build histogram of curvatures and find the peak to predict the radius
    N = 5*len(Ks1) 
    H, bins = histogram(Ks1,bins=N, new=True)
    pK = H.argmax()
    K_est1 = (bins[pK] + bins[pK+1])/2.0
    #print "bins[pK] =",bins[pK]
    #print "bins[pK+1] =",bins[pK+1]
    R_est1 = -1.0/K_est1
    
    s2_indices = argwhere((Ks1 >= bins[pK]) & (Ks1 < bins[pK+1]))
    Xs2    =   Xs1[s2_indices].flatten()
    Ys2    =   Ys1[s2_indices].flatten()
    DYs2   =  DYs1[s2_indices].flatten()
    DDYs2  = DDYs1[s2_indices].flatten()
    Ks2    =   Ks1[s2_indices].flatten()
    #use the radius estimate to transform data to estimates for circle center
    Ms2  = 1.0/sqrt(1.0 + DYs2*DYs2)
    X0s2 = Xs2 +        DYs2*R_est1*Ms2
    Y0s2 = Ys2 + sign(DDYs2)*R_est1*Ms2
    #look for the "most votes" at the histogram peaks
    H, bins = histogram(X0s2, bins = N, normed=True, new=True)
    x0_est2   = bins[H.argmax()]
    H, bins = histogram(Y0s2, bins = N, normed=True, new=True) 
    y0_est2 = bins[H.argmax()]
    
    #resample data based on estimates
    s3_indices = argwhere( (X > x0_est2 - R_est1) & (X < x0_est2 + R_est1) )
    Xs3 = X[s3_indices].flatten()
    Ys3 = Y[s3_indices].flatten()

    #perform circle fit algorithm to refine parameters
    if use_fit:
        fit_info = circle_fit(Xs3,Ys3)
        x0_est3, y0_est3, R_est3 = fit_info['p_fit']
    else:    
        x0_est3, y0_est3, R_est3 = x0_est2, y0_est2, R_est1

    if debug:
        #debugging plots
        figure()
        plot(Xs2,Ys2,'k.')
        plot(Xs2,X0s2,'r.')
        plot(Xs2,Y0s2,'m.')
        figure()
        plot(Xs1,Ks1,'k.-')
        xlabel("X")
        ylabel("K")
        figure()
        hist(Ks1,bins=N, normed=True)
        xlabel("K value")
        ylabel("% votes")
        figure()
        hist(X0s2,bins=N, normed=True)
        xlabel("X0 value")
        ylabel("% votes")
        figure()
        hist(Y0s2,bins=N, normed=True)
        xlabel("Y0 value")
        ylabel("% votes")

    return (x0_est3,y0_est3,R_est3)


   
if __name__ == "__main__":
    __DEBUG == True

    from pylab import *
    #generate test data
    
    R1  = 100.0 
    y0 = -10
    #circle
    theta = linspace(pi,0,20)
    Xc1,Yc1 = circle_func(R1,y0,R1)(theta)
    R2 = 2*R1
    Xc2,Yc2 = circle_func(Xc1[-1] + R2,y0,R2)(theta)
    #generate crap
    Xl3 = linspace(Xc2[-1], Xc2[-1] + 2*(Xc2[-1] - Xc2[0]), 20)
    Yl3 = Xl3 - Xl3[0]
    X = hstack(( Xc1,
                 Xc2,
                 Xl3
              ))
    Y = hstack(( Yc1,
                 Yc2,
                 Yl3
              ))
   
    #plot(Y,X,'b.')
   

    
    x0_est, y0_est, R_est = circle_detect(X,Y)
    print("x0_est =",x0_est)
    print("y0_est =",y0_est)
    print("R_est =",R_est) 
    
    figure()
    plot(X,Y,'b.')
    Xc,Yc = circle_func(x0=x0_est,y0=y0_est,R=R_est)(linspace(pi,0,100))
    plot(Xc,Yc,'k-')
    show()
