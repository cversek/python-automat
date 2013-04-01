import gc
from Tkinter import *


import matplotlib
matplotlib.use('TkAgg')
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2TkAgg

class FigureWindow(Toplevel):
    def __init__(self, parent=None, figure=None, figsize=(7,5), dpi=100, **kwargs):
        Toplevel.__init__(self, parent, **kwargs)
        self.embedded_figure = EmbeddedFigure(parent = self, figure = figure, figsize  = figsize, dpi = dpi)
        self.embedded_figure.pack(fill='both',expand='yes')
    def get_figure(self):
        return self.embedded_figure.figure
    def update(self):
        self.embedded_figure.update()
    def destroy(self):
        "force cleanup of plot"
        #print "figure window destroyed"
        Toplevel.destroy(self) 

class EmbeddedFigure(Frame):
    def __init__(self, parent=None, figure=None, figsize=(7,5), dpi=100):
        #initialize the frame
        Frame.__init__(self,parent)
        if figure is None:
            #create the figure
            figure = matplotlib.figure.Figure(figsize=figsize,dpi=dpi)
        self.figure = figure
        self.canvas = FigureCanvasTkAgg(figure, master=self)        
        self.canvas.show()
        self.canvas.get_tk_widget().pack(side=TOP, fill=BOTH, expand=True)
        #create the navigation toolbar
        toolbar = NavigationToolbar2TkAgg(self.canvas, self )
        toolbar.update()
        #initialize the pick to None
        self.picker = None
    
    def get_tk_widget(self):
        return self.canvas.get_tk_widget()

    def config(self, *args, **kwargs):
        widget = self.canvas.get_tk_widget()
        widget.config(*args, **kwargs)

    def get_figure(self):
        return self.figure
    
    def update(self):
        self.figure.canvas.draw()
        Frame.update(self)

    def destroy(self):
        "destroy widgets and release memory"
        #print "embedded figure destroyed"
        #clean up after matplotlib
        self.figure.clear()
        #pylab.cla() #force all figure to be cleared
        #erase all the image objects
        for ax in self.figure.axes:
            ax.images = []
        self.get_tk_widget().destroy()
        Frame.destroy(self)


#    def set_picker(self, handler,
#                         dataset_indices = [(0,0)], # (axis #, line #) pairs
#                         picking_size_pt = 5.0,
#                  ):      
#        ##register picking event
#        if not self.picker is None:
#            #disconnect if a handle which has previously been set
#            self.figure.canvas.mpl_disconnect(self.picker)
#        self.picker = self.figure.canvas.mpl_connect('pick_event', handler) #click on a point
#        #set up object picking on the specified data lines
#        for axis_index, line_index in dataset_indices:
#            line = self.figure.axes[axis_index].lines[line_index]
#            line.set_picker(picking_size_pt)
       
###############################################################################
# Test Code
###############################################################################
if __name__ == "__main__":
    from numpy import *
    import pylab 

    class Application(Frame):
        def __init__(self, master=None):
            Frame.__init__(self, master)
            self.pack()
            self.createWidgets()
        def createWidgets(self):
            fig = pylab.figure()
            self.axes = fig.add_subplot(111)
            self.EF = EmbeddedFigure(parent=self, figure=fig)
            self.quit_button = Button(self, text = "QUIT", command = self.quit)
            self.plot_button = Button(self, text = "PLOT", command = self.plot)
            self.EF.pack()
            self.quit_button.pack()
            self.plot_button.pack()
        def plot(self):
            X = arange(10)
            self.axes.plot(X,X**2)
            self.EF.update()
            
    root = Tk()
    root.wm_title("Embedding")
    app = Application(master=root)
    root.protocol("WM_DELETE_WINDOW", app.quit)
    app.mainloop()
    root.destroy()
#    root = Tk()
#    app = Application(master=root)
#    app.mainloop()
#    root.destroy()

