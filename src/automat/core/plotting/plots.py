"""
plots.py

desc: Classes which provide a higher level OO interface to matplotlib 2D
      plot rendering.
auth: Craig Versek (cversek@physics.umass.edu)
      Mike Thorn   (mthorn@physics.umass.edu)
last update: 2008 9 8
"""
import pylab, numpy
from matplotlib.figure import Figure #use to create an object oriented only figure which can be gargbage collected
from matplotlib.font_manager import FontProperties

###############################################################################
class Plot(object):
    """Provide higher level common base for rendering pylab plots"""
    def __init__(self,
                 title             = '',
                 title_position    = 1.0,
                 axis_position     = None,
                 xticks            = None,
                 xticklabels       = None,
                 xlabel            = 'X',
                 yticks            = None,
                 yticklabels       = None,
                 ylabel            = 'Y',
                 set_xscale        = 'linear',
                 set_yscale        = 'linear',
                 axis_scaling      = 'auto',
                 axis_xbuffer      = 0.1, #percent of range to pad out x axis
                 axis_ybuffer      = 0.1, #percent of range to pad out x axis
                 invert_yaxis      = False,
                 xticks_powerlimits = None,
                 yticks_powerlimits = None,
                 hide_xticklabels  = False,
                
                 #settings for errorbars
                 use_errorbars     = False,
                 #settings for optional top axis
                 topaxis_display     = False,
                 topaxis_xticks      = [],
                 topaxis_xticklabels = [],
                 topaxis_xlabel      = '',
                 topaxis_xbuffer     = 0.1, #percent of range to pad out x axis             
                 ):
        attrs={}
        attrs['title'] = title
        attrs['title_position'] = title_position
        attrs['axis_position']  = axis_position
        attrs['xticks']      = xticks
        attrs['xticklabels'] = xticklabels
        attrs['xlabel']      = xlabel
        attrs['yticks']      = yticks
        attrs['yticklabels'] = yticklabels
        attrs['ylabel']      = ylabel
        attrs['set_xscale'] = set_xscale
        attrs['set_yscale'] = set_yscale
        attrs['axis_scaling'] = axis_scaling
        attrs['axis_xbuffer']        = axis_xbuffer 
        attrs['axis_ybuffer']        = axis_ybuffer 
        attrs['invert_yaxis'] = invert_yaxis
        attrs['xticks_powerlimits'] = xticks_powerlimits
        attrs['yticks_powerlimits'] = yticks_powerlimits
        attrs['hide_xticklabels']   = hide_xticklabels
        #settings for errorbars
        attrs['use_errorbars'] = use_errorbars
        #settings for optional top axis
        attrs['topaxis_display']     = topaxis_display
        attrs['topaxis_xticks']      = topaxis_xticks
        attrs['topaxis_xticklabels'] = topaxis_xticklabels
        attrs['topaxis_xlabel']      = topaxis_xlabel
        attrs['topaxis_xbuffer']     = topaxis_xbuffer 
        self.attrs = attrs
        #signal the state when "plot" method has been called once
        self._has_been_plotted = False

    def configure(self, **kwargs):
        """ Allow attributes of the plot to be changed"""
        for key, val in list(kwargs.items()):
            if key not in self.attrs:
                raise KeyError("'%s' is not a valid attribute" % key)
            self.attrs[key] = val
                       
        
    def plot(self, X, Y, figure=None, subplot=None, axis=None, **kwargs):
        """renders a plot of the data X,Y on figure (new if not supplied)
           at the subplot xor axis location
        """
        attrs = self.attrs
        figure, ax1, ax2 = self._setup_figure(figure, subplot, axis)
        X = numpy.array(X)
        Y = numpy.array(Y)
        #chose the appropriate plotting function
        plot_func = None
        if attrs['use_errorbars']:
            plot_func = ax1.errorbar
        else:
            plot_func = ax1.plot
        plot_func(X, Y, **kwargs)
        self._has_been_plotted = True
        return figure
        
    def has_been_plotted(self):
        return self._has_been_plotted

    def _setup_figure(self, figure, subplot, axis):
        """create figure if not supplied; apply the formatting
           and layout
        """
        attrs = self.attrs
        if figure is None:
            figure = Figure() #use to create an object oriented only figure which can be gargbage collected
        if subplot is None and axis is None:
            ax1 = figure.add_subplot(111)
        elif not subplot is None:
            ax1 = figure.add_subplot(subplot)
        elif not axis is None:
            ax1 = figure.add_axes(axis)
        #configure the main plot axis
        axis_position = attrs['axis_position']
        if not axis_position is None:
            ax1.set_position(axis_position)
        #configure the optional top axis
        ax2 = None
        if attrs['topaxis_display']:
            ax2 = ax1.twiny()
            ax2.set_xlabel(attrs['topaxis_xlabel'])
            ax2.set_xticks(attrs['topaxis_xticks'])
            ax2.set_xticklabels(attrs['topaxis_xticklabels'])   
        ax1.set_title(self._render_title(), y=attrs['title_position'])
        if not attrs['xticks'] is None:
            ax1.set_xticks(attrs['xticks'])
        if not attrs['xticklabels'] is None:
            ax1.set_xticklabels(attrs['xticklabels'])
        if attrs['hide_xticklabels']:#REMOVE TICK LABELS
            xtl = ax1.get_xticklabels()
            for tl in xtl:
                tl.set_visible(False)

        ax1.set_xlabel(self._render_xlabel())
        ax1.set_xscale(attrs['set_xscale'])
        if not attrs['yticks'] is None:
            ax1.set_yticks(attrs['yticks'])
        if not attrs['yticklabels'] is None:
            ax1.set_yticklabels(attrs['yticklabels'])
        ax1.set_ylabel(self._render_ylabel())
        ax1.set_yscale(attrs['set_yscale'])
        if attrs['invert_yaxis']:
            ax1.invert_yaxis()
        #setup the power limits under which NOT to use scientific notation for ticks
        xticks_powerlimits = attrs['xticks_powerlimits']
        yticks_powerlimits = attrs['yticks_powerlimits']
        if not xticks_powerlimits is None:
            ax1.xaxis.major.formatter.set_powerlimits(xticks_powerlimits)
        if not yticks_powerlimits is None:
            ax1.yaxis.major.formatter.set_powerlimits(yticks_powerlimits)
        #apply the axis scaling
        ax1.axis(attrs['axis_scaling'])
        return figure,ax1,ax2

    def _post_plot_adjustments(self,
                               figure,
                               ax1   = None,
                               ax2   = None,
                               x_min = None,
                               x_max = None,
                               y_min = None,
                               y_max = None,
                              ):
        """make formatting adjustments that depend on knowing
           the plotted data
        """
        attrs = self.attrs
        if ax1 is None:
            ax1 = figure.axes[0]
        #compute the left and right x axis limits
        if not (x_min is None or x_max is None):
            xbuff = max(attrs['axis_xbuffer'], attrs['topaxis_xbuffer']) 
            x_rng = x_max - x_min
            x_left  = x_min - xbuff*x_rng
            x_right = x_max + xbuff*x_rng
            #set both bottom and top axes if they exist
            ax1.set_xlim(x_left,x_right)
            if not ax2 is None:
                ax2.set_xlim(ax1.get_xlim())
        #compute the left and right y axis limits
        if not (y_min is None or y_max is None):
            ybuff = attrs['axis_ybuffer']
            y_rng = y_max - y_min
            y_left  = y_min - ybuff*y_rng
            y_right = y_max + ybuff*y_rng
            if attrs['invert_yaxis']:
                y_left,y_right = (y_right, y_left) #don't screw up inversion
            #set both bottom and top axes if they exist
            ax1.set_ylim(y_left,y_right)
            if not ax2 is None:
                ax2.set_ylim(ax1.get_ylim())

    def _render_title(self):
        """make title string from attributes; 
           good candidate for child class overloading
        """
        return self.attrs['title']

    def _render_xlabel(self):
        """make xlabel string from attributes; 
           good candidate for child class overloading
        """
        return self.attrs['xlabel']

    def _render_ylabel(self):
        """make ylabel string from attributes; 
           good candidate for child class overloading
        """
        return self.attrs['ylabel']
    

###############################################################################
class MultiPlot(Plot):
    """Extends Plot to allow plotting multiple datasets on the same axes with 
       optional styles specification.    
    """
    def __init__(self, 
                 styles     = [], #default style overrides
                 use_legend  = False,
                 legend_loc  = 'best',
                 legend_font = FontProperties(),
                 **kwargs
                ):
        Plot.__init__(self, **kwargs)
        attrs = self.attrs
        attrs['styles'] = list(styles)
        attrs['use_legend'] = use_legend
        attrs['legend_loc'] = legend_loc
        attrs['legend_font'] = legend_font

    def plot(self, Xs, Ys, labels = None, styles = None, figure=None, subplot=None, axis=None, **kwargs):
        """renders a plot of the data sequences Xs,Ys on figure 
           (new if not supplied) at the subplot xor axis location;
           matplotlib 'styles', supplied to the constructor, are applied to
           each plot series in turn and defaults are used thereafter
        """
        attrs = self.attrs
        if labels is None:
            labels = [None]*len(Xs)
        figure,ax1,ax2 = self._setup_figure(figure, subplot, axis)
        #retrieve the optional styles
        if styles is None:        
            styles = self.attrs['styles'][:]
        #prepare styles to be popped as a list
        styles = list(styles)
        styles.reverse() 
        
        #overall min and max for setting range
        X_min = [] 
        X_max = []
        Y_min = [] 
        Y_max = []

        N = len(Xs) 
        assert len(Ys) == N
        if attrs['use_errorbars']:
            yerrs = kwargs.get('yerrs',None)
            if yerrs is None:
                raise ValueError("no 'yerrs' specifed, even though 'use_errorbars' == True")
            assert len(yerrs) == N
        #plot each series------------------------------------------------------        
        for i in range(N):
            #ensure array types
            X = numpy.array(Xs[i])
            Y = numpy.array(Ys[i])
            label = labels[i] or ("series %d" % i)
            try:
                X_min.append(X.min())
                X_max.append(X.max())
                Y_min.append(Y.min())
                Y_max.append(Y.max())
            except ValueError: #on empty sequence
                pass
            try:
                #styles are exhausted in turn
                style = styles.pop()
                if style is None:
                    style = {}
                #use the appropriate plot function
                if attrs['use_errorbars']:
                    yerr = numpy.array(yerrs[i])
                    if type(style) == str:
                        style = {'fmt': style} #convert to a mapping 
                    else:
                        style = dict(style) #convert to a mapping
                    ax1.errorbar(X,Y,yerr, **style)
                else:
                    if type(style) == str:
                        ax1.plot(X,Y,style)
                    else:
                        style = dict(style) #convert to a mapping 
                        ax1.plot(X,Y,**style)
            except IndexError: 
                #revert to default supplied by matplotlib
                #use the appropriate plot function
                if attrs['use_errorbars']:
                    yerr = kwargs.get('yerr',None)
                    ax1.errorbar(X,Y,yerr)
                else:
                    ax1.plot(X,Y)
                
        #----------------------------------------------------------------------
        #apply the labels to the legend if they exist
        if attrs['use_legend']:
            legend_lines  = []
            legend_labels = []
            lines = ax1.lines
            for i, label in enumerate(labels):
                try:
                    if not label is None:
                        legend_lines.append(lines[i])
                        legend_labels.append(label)
                except IndexError:
                    pass #ignore too many labels
            #figure.legend(legend_lines,legend_labels, loc = attrs['legend_loc'])      
            ax1.legend(legend_lines,legend_labels, loc = attrs['legend_loc'], prop = attrs['legend_font'])         
            
        #apply the post plot formatting
        try:
            x_min = min(X_min)
            x_max = max(X_max)
            y_min = min(Y_min)
            y_max = max(Y_max)
            self._post_plot_adjustments(figure,ax1,ax2,x_min=x_min,x_max=x_max,y_min=y_min,y_max=y_max)
        except ValueError: #on empty data
            self._post_plot_adjustments(figure,ax1,ax2)
            
        self._has_been_plotted = True
        return figure

###############################################################################
class CompositePlot(object):
    """Creates a composite of Plot objects with either the pylab 'subplots' 
       row-column style layout or manually specified 'axes' locations."""
    def __init__(self, 
                 plots, 
                 subplots=None, 
                 axes=None, 
                 suptitle=None,
                ):
        self.plots    = plots
        self.subplots = subplots
        self.axes     = axes
        attrs = {}
        attrs['suptitle'] = suptitle
        self.attrs = attrs
    def configure(self, **kwargs):
        """ Allow attributes of the plot to be changed"""
        for key, val in list(kwargs.items()):
            if key not in self.attrs:
                raise KeyError("'%' is not a valid attribute" % key)
            self.attrs[key] = val
    def plot(self, Xs, Ys, labels = None, figure=None):
        """renders a composite plot of the data sequences Xs,Ys on figure 
           (new if not supplied) using the format of Plot objects, plots,
           and layout of subplots xor axes, which were supplied to the 
           constructor. The lengths of Xs,Ys, plots (and subplots xor axes) 
           must all be the same. 
        """
        plots    = self.plots
        subplots = self.subplots
        axes     = self.axes
        if labels is None:
            labels = [None]*len(plots)
        figure = self._setup_figure(figure=figure)
        if (not subplots is None) and (not axes is None):
            raise ValueError('Cannot specify both subplots and axes.')
        elif not subplots is None:
            for plot,subplot,X,Y,_labels in zip(plots,subplots,Xs,Ys,labels):
                plot.plot(X,Y, labels=_labels, figure=figure, subplot=subplot)
        elif not axes is None:
            for plot,axis,X,Y,_labels in zip(plots,axes,Xs,Ys,labels):
                plot.plot(X,Y, labels=_labels, figure=figure, axis=axis)
        return figure
    def _setup_figure(self, figure=None):
        """create figure if not supplied; apply the top-level formatting
        """
        attrs    = self.attrs
        if figure is None:
            figure = Figure() #use to create an object oriented only figure which can be gargbage collected
        suptitle = attrs['suptitle']
        if not suptitle is None:
            figure.suptitle(suptitle)
        return figure
        
###############################################################################
# TEST CODE
###############################################################################
if __name__ == "__main__":
    import numpy
    X = numpy.arange(10)
    Y = X*X
    X2 = numpy.arange(-5,15)
    plot_template = MultiPlot(topaxis_display = True,
                         topaxis_xlabel  = 'Top Axis',
                         topaxis_xticks  = X2,
                         topaxis_xticklabels = list(map(str,2*X2)),
                         )
    fig = plot_template.plot([X],[Y])
    pylab.show()
    #pylab.draw()
        
