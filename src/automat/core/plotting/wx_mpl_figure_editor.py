"""
snippet taken from Gael Varaqoux's tutorial "Writing a graphical application for scientific programming using TraitsUI"
        http://code.enthought.com/projects/traits/docs/html/tutorials/traits_ui_scientific_app.html
"""
###############################################################################
import wx
import matplotlib
# We want matplotlib to use a wxPython backend
#matplotlib.use('WXAgg')
from matplotlib.backends.backend_wxagg import FigureCanvasWxAgg as FigureCanvas
from matplotlib.figure import Figure
from matplotlib.backends.backend_wx import NavigationToolbar2Wx

from enthought.traits.api import Any, Instance
from enthought.traits.ui.wx.editor import Editor
from enthought.traits.ui.basic_editor_factory import BasicEditorFactory
###############################################################################

ONPICK_HANDLER_NAME = '_handle_onpick'

class _MPLFigureEditor(Editor):
    scrollable  = True

    def init(self, parent):
        self.control = self._create_canvas(parent)
        self.set_tooltip()

    def update_editor(self):
        pass

    def _create_canvas(self, parent):
        """ Create the MPL canvas. """
        # The panel lets us add additional controls.
        panel = wx.Panel(parent, -1, style=wx.CLIP_CHILDREN)
        sizer = wx.BoxSizer(wx.VERTICAL)
        panel.SetSizer(sizer)
        # matplotlib commands to create a canvas
        mpl_control = FigureCanvas(panel, -1, self.value)
        try:
            handle_onpick = getattr(self.object, ONPICK_HANDLER_NAME)
            mpl_control.mpl_connect('pick_event', handle_onpick)  #click on a point      
        except AttributeError:
            pass        
        
        sizer.Add(mpl_control, 1, wx.LEFT | wx.TOP | wx.GROW)
        toolbar = NavigationToolbar2Wx(mpl_control)
        sizer.Add(toolbar, 0, wx.EXPAND)
        self.value.canvas.SetMinSize((10,10))
        return panel

class MPLFigureEditor(BasicEditorFactory):
    klass = _MPLFigureEditor

class MPLFigureEditor2(BasicEditorFactory):
    klass = _MPLFigureEditor
