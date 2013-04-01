###############################################################################
# curve_fitting.py
# desc: convenience interfaces for non-linear curve fitting usings
#       scipy's Levenberg-Marquardt algorithm scipy.optimize.leastsq
# authors: Craig Versek (cversek@physics.umass.edu)
#          Mike Thorn
###############################################################################
import inspect
import numpy, scipy
import scipy.optimize
import copy

###############################################################################
def circle_fit(X,Y):
    """Fit a circle to set of X, Y points using nonlinear minimization
       of a sum of squared distances from center.  The fit parameters
       are the center coords x0,y0 and the radius r.
    """   
    X = numpy.array(X)
    Y = numpy.array(Y)
    #create the error function for minimization
    def err_func(p,_X,_Y):
      x0 = p[0]
      y0 = p[1]
      r  = p[2]
      #distances of points from center, normalized by radius
      Dx = (_X - x0)/r
      Dy = (_Y - y0)/r
      #total distance from radius
      err = r*(numpy.sqrt(Dx*Dx + Dy*Dy) - 1.0)
      return err
    #guess intitial parameters from averages
    x_init = X.mean()
    y_init = Y.mean()
    r_init = numpy.sqrt((X-x_init)**2 + (Y-y_init)**2).mean()
    p = (x_init,y_init,r_init)
    results = scipy.optimize.leastsq( err_func, 
                                      p, 
                                      args = (X,Y),
                                      full_output=1,
                                      #factor=1.0
                                    )
    #get the number of degrees of freedom
    ndf = len(Y) - len(p)
    if results is None: 
        #the fit failed for some reason
        success = False
        p_fit = None
        reduced_chisqr = None
    else:  
        #the fit succeeded, at least in part
        success = True
        #unpack the results
        p_fit     = results[0] #the fitted parameters
        covar     = results[1] #the covariance matrix
        #compute the reduced chi-squared statistic
        err = err_func(p_fit,X,Y)
        reduced_chisqr = (err*err).sum()/ndf
        #make sure error was obtained
        if not covar is None:
            #rescale the covariance matrix to get errors
            covar *= reduced_chisqr
            #compute the errors on all the parameters
            p_var = covar.diagonal()  #get the variances
            p_err = numpy.sqrt(p_var)
        else:
            p_err = tuple( None for p in xrange(len(p_fit)) )
    #bundle information in a dictionary
    fit_info = {}
    fit_info['success'] = success
    fit_info['p_fit'] = p_fit
    fit_info['p_err'] = p_err
    fit_info['covar'] = covar
    fit_info['reduced_chisqr'] = reduced_chisqr
    fit_info['ndf'] = ndf
    return fit_info

###############################################################################    
class FittableFunction(object):
  """ An introspective wrapper class for a function, 
      which exposes a numerical fitting interface
  """
  def __init__(self, func):
    #peer into the functions internals
    args, varargs, varkwargs, defaults = inspect.getargspec(func)
    #restrict the allowed function definitions
    if not varargs is None:
      raise ValueError, "cannot use varargs"
    elif not varkwargs is None:
      raise ValueError, "cannot use varkwargs"
    self.func   = func
    self.desc   = inspect.getdoc(func) or "<FittableFunction object>"
    self.pnames = args[1:] #exclude the 'x' variable
  def fit(self,X,Y,free_params,fixed_params={}):
    """fit the modelto the data: independent array X and dependent Y
          may optionally specify initial parameters
          -> (params as dict, errors as dict)
    """
    #check to see if parameter names are valid
    opt_pnames = free_params.keys() + fixed_params.keys()
    for pname in opt_pnames:
        if not pname in self.pnames:
            raise ValueError, "Invalid parameter name '%s'" % pname
    #convert possible sequences to numpy arrays
    X = numpy.array(X)
    Y = numpy.array(Y)
    #initialize the free parameters
    all_params = {}
    all_params.update(free_params)
    all_params.update(fixed_params)
    #get the free parameters as a sorted sequence
    fpnames = free_params.keys()
    fpnames.sort()

    #create the error function closure
    def err_func(p,_X,_Y):
      #update the values in the free parameter hash
      free_params = dict( [(fpname,val) for fpname, val in zip(fpnames,p)] )
      all_params.update(free_params)
      return _Y - self.func(_X,**all_params)

    p0 = [ free_params[name] for name in fpnames ]
    #call the parameter sequence based fit function
    p, covar = self._fit_pseq(err_func,p0,X,Y)
    #if no fit could be made...bale out
    if covar is None:
        return None 
    #get the number of degrees of freedom
    ndf = len(Y) - len(p)
    #compute the chi-squared statistic
    err = Y - self.func(X,**all_params)
    reduced_chisqr = (err*err).sum()/ndf
    #compute the errors on all the parameters
    errors = {}
    pvars = [covar[i][i] for i in xrange(len(covar))]  #get the variances
    for pname, pvar in zip(fpnames,pvars):
        errors[pname] = numpy.sqrt(reduced_chisqr*pvar)
    return (all_params, errors, reduced_chisqr)
  #implementation helper functions
  def _fit_pseq(self,err_func,p0,X,Y):
    """fits usuing a parameter value sequence in implied 
       alphabetical order by name returns -> (p, success)
    """
    #minimize the error function with the nonlinear least squares 
    # algorithm (Levenberg-Marquardt)
    results = scipy.optimize.leastsq( err_func, 
                                  p0[:], 
                                  args = (X,Y),
                                  full_output=1,
                                  factor=1.0)
    p     = results[0] #the fitted parameters
    covar = results[1] #the covariance matrix
    #make sure p is iterable
    try:
      iter(p)
      return p, covar
    except TypeError:
      return [p], covar
  #special python interface methods
  def __str__(self):
    return self.desc    

###############################################################################
class Parameters(dict):
    """ An extended dictionary class to maintain 
        sets of free and fixed parameters 
        and to supply a standard ordering.
    """
    def __init__(self,pnames, fixed_params={}):
        #keep track of three sets of parameter names the whole, fixed, and free
        self.whole_pset = set(pnames)
        self.fixed_pset = set(fixed_params.keys())
        self.free_pset  = self.whole_pset - self.fixed_pset
        #set up the params hash
        self.update( [ [pname,None] for pname in pnames] )
        self.update(fixed_params)
    def get_free_params(self):
        return dict( [(pname, self[pname]) for pname in self.free_pset] )
    def get_fixed_params(self):
        return dict( [(pname, self[pname]) for pname in self.fixed_pset] )
    def fix_param(self,pname,val=None):
        if not pname in self.whole_pset:
            raise TypeError, "not a valid parameter name: %s" % pname
        #remove from the free set if it's there
        single_pset = set([pname])
        self.free_pset  -= single_pset
        self.fixed_pset |= single_pset
        if not val is None:
            self[pname] = val
    def init_param(self,pname,val):
        if not pname in self.whole_pset:
            raise TypeError, "not a valid parameter name: %s" % pname
        self[pname] = val
    def set_fixed_params(self,fixed_params):
        newfixed_pset = set(fixed_params.keys())
        for pname in newfixed_pset:
            if not pname in self.whole_pset:
                raise TypeError, "not a valid parameter name: %s" % pname
        #declare the previously fixed parameters free
        freed_pset = self.fixed_pset - newfixed_pset
        #the new free parameter set is has the newfixed elements subtracted 
        #and the freed up parameters added (union)
        self.free_pset = (self.free_pset - newfixed_pset) | freed_pset
        self.fixed_pset = newfixed_pset
        #update the values in the params hash
        self.update(fixed_params)
    def set_init_params(self, init_params, init_default=0.0): 
        #if no initial values for the free parameters are specified, 
        #use the last values
        #check that all parameter names are valid
        for pname in init_params.keys():
            if pname not in self.whole_pset:
                raise TypeError, "not a valid free parameter name: %s" % pname 
        #merge the parameter initialization into the params dict
        self.update(init_params)
        #replace any remaining None values with the init_default
        for pname, val in self.items():
            if val is None:
                self[pname] = init_default
        
##################################################################################
     
class FittingInterface(object):
    """An extension of the FitableFunction interface to provide more 
       advanced fitting modes as well as state caching.
    """
    def __init__(self, model_func, 
                       free_params={},
                       fixed_params={}, 
                       init_default = 0.0
                ):
        #expose a fitting interface to the model function
        self.fittable = FittableFunction(model_func)
        self.params   = Parameters(self.fittable.pnames,fixed_params)
        self.params.set_init_params(free_params, init_default=init_default)
        #used to constrain fit between certain range
        self.lbound = None
        self.rbound = None
    def fit(self,X,Y):
        """desc: apply a nonlinear fit based on model_func, the current parameters, 
                 and the data set X,Y
           arguments:
                 X - the whole data set, independent variable
                 Y - the whole data set, dependent variable
           returns:
                 fit_info (dict) - contains all relevant fitting information
                   keys:
                    'X' (ndarray - 1D)    - the whole data set, independent variable
                    'Y' (ndarray - 1D)    - the whole data set, dependent variable
                    'free_params' (dict)  - the initial set of variable model 
                                            parameters
                    'fixed_params' (dict) - the set of non variable model parameters
                    'lbound' (int)        - the lower index into X,Y for the fitted 
                                            range
                    'rbound' (int)        - the upper index into X,Y for the fitted 
                                            range
                    'X_obs' (ndarray - 1D) - the data to fit, independent variable
                    'Y_obs' (ndarray - 1D) - the data to fit, dependent variable
                    'success' (bool)       - whether the fit succeeded with the
                                             current parameter set
                    'new_params' (dict)    - the post-fit model parameters
                    'errors' (dict)        - the fitting errors on 'new_params'
                    'reduced_chisqr' (float) - goodness of fit 
                                
        """
        #create a fit information record to pass back
        fit_info = {}
        #ensure that sequences are ndarrays
        X = numpy.array(X)
        Y = numpy.array(Y)
        #obtain the current parameter sets
        params = self.params
        free_params  = params.get_free_params()  #these will vary during fit
        fixed_params = params.get_fixed_params() #these will not
        #constrain the data range
        lb = self.lbound
        rb = self.rbound
        if lb is None: #default to full range
            lb = 0
        if rb is None:
            rb = len(X)
        X_obs = X[lb:rb+1]
        Y_obs = Y[lb:rb+1]
        #cache all information about the fit
        fit_info['model_desc'] = self.fittable.desc
        fit_info['X'] = X
        fit_info['Y'] = Y
        fit_info['free_params']  = free_params
        fit_info['fixed_params'] = fixed_params
        fit_info['lbound'] = lb
        fit_info['rbound'] = rb
        fit_info['X_obs']  = X_obs
        fit_info['Y_obs']  = Y_obs
        #fit using the FittableFunction object
        results = self.fittable.fit(X_obs,Y_obs,free_params,fixed_params)
        if results is None: #the fit failed with these parameters
            fit_info['success'] = False
            fit_info['new_params'] = None
            fit_info['errors']     = None
            fit_info['reduced_chisqr'] = None
            fit_info['X_fit'] = None
            fit_info['Y_fit'] = None
        else:  #the fit succeeded
            new_params, errors, reduced_chisqr = results
            #update the old params with the new fits
            self.params.update(new_params)
            fit_info['success'] = True
            fit_info['new_params'] = new_params
            fit_info['errors']     = errors
            fit_info['reduced_chisqr'] = reduced_chisqr
            #generate fitted data
            fit_info['X_fit'] = X_fit = X_obs
            func = self.fitted_func()
            fit_info['Y_fit'] = Y_fit = func(X_fit)
        #send back the fitting information    
        return fit_info
    def set_range(self, lbound, rbound):
        """constrain fitting to [lbound,rbound]
              throws AssertionError if rbound >= lbound
        """
        assert lbound < rbound
        self.lbound = lbound
        self.rbound = rbound
    def fix_param(self,pname,val):
        self.params.fix_param(pname,val)
    def init_param(self,pname,val):
        self.params.init_param(pname,val)
    def set_fixed_params(self,fixed_params,**kwargs):
        self.params.fix_params(fixed_params,**kwargs)
    def set_init_params(self,init_params,**kwargs):
        self.params.set_init_params(init_params,**kwargs)
    def chi_squared(self,X,Y):
        "Compute the sum of squared error for the data with model having params"
        err = Y - self.func(X,**self.params)
        return (err*err).sum()
    def fitted_func(self):
        """returns an the model function with the fitted parameters enclosed, 
            such that post fit interpolation may be easily performed.
        """
        #None values may be present if the fit has not yet been performed
        if None in self.params.values():
            raise Exception, "the must call 'fit' before getting the fitted function"
        else:
            func = self.fittable.func
            def _fitted(X):
                return func(X,**self.params)
            return _fitted
    
    def __str__(self):
        params = self.params
        buff = []
        buff.append("Fitting Interface:")
        buff.append("  Fit Function: \"%s\"" % self.fittable.desc)
        buff.append("  Free Parameters:")
        for pname, val in params.get_free_params().items():
            buff.append("    %s: %f" % (pname,val))
        fixed_params = params.get_fixed_params()
        if fixed_params:
            buff.append("  Fixed Parameters:")
            for pname, val in fixed_params.items():
                buff.append("    - %s = %f" % (pname,val))
        else:
            buff.append("  Fixed Parameters: ~")
        return "\n".join(buff)
        
        


###############################################################################
# THIS IS JUST TEST CODE!!!!!!!!!!!!!!
###############################################################################
if __name__ == "__main__":
  import random
  #generate some test data
  A = 1.23
  B = 2.76
  print "Generating data from model A*exp(k*x) + B:"
  print "A =",A
  print "B =",B
  X = numpy.linspace(1,10,20)
  Noise = numpy.random.normal(0,0.25*A,len(X))
  Y = A*X + B
  print "X = ", X
  print "Y = ", Y
  print "Fitting data to same model:"
  #define the fitting model just as a normal python function
  #where the docstring is taking to be the representation
  def model(x,A,B):
    "f(x) = A*x + B"
    return A*x + B
#  #wrap function in curve fitting interface
#  fitmodel = FittableFunction(model)
#  p, errs, reduced_chisqr = fitmodel.fit(X,Y, free_params={'A':1.0,'B':2.0})
#  print "fitted parameters:"
#  for pname in p.keys():
#    pstr = "%s = %f" % (pname,p[pname])
#    err = errs[pname]
#    if err is not None:
#      pstr += " +/- %f" % (err)
#    print pstr
#  print "Chi-sqr/ndf = %f" % reduced_chisqr
  
  FI = FittingInterface(model,free_params={'A':1.0},fixed_params = {'B':2.7,'Q':0})
  p, errs, reduced_chisqr = FI.fit(X,Y)
  print "fitted parameters:"
  for pname in p.keys():
    pstr = "%s = %f" % (pname,p[pname])
    err = errs.get(pname,None)
    if err is not None:
      pstr += " +/- %f" % (err)
    print pstr
  print "Chi-sqr/ndf = %f" % reduced_chisqr
  
