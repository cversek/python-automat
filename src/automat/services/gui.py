###############################################################################
#Standard Python provided
import Tkinter as tk
import ttk
#Standard or substitute
OrderedDict = None
try:
    from collections import OrderedDict
except ImportError:
    from automat.substitutes.ordered_dict import OrderedDict
#3rd party packages
import Pmw
#Automat framework provided
from automat.system_tools.daemonize import ignore_KeyboardInterrupt, notice_KeyboardInterrupt
###############################################################################
# Module Constants
DEFAULT_WINDOW_TITLE = "Automat GUI Control"

###############################################################################
#replacement dialog box, since Pmw.MessageDialog appears to mysteriously segfault
import Dialog

def launch_MessageDialog(title, message_text, buttons = ('OK',), bitmap='', default=0):
    d = tk.Dialog.Dialog(title=title, text = message_text, bitmap=bitmap, default=default, strings=buttons)
    return buttons[d.num]
      
###############################################################################
class GUIBase:
    def __init__(self, application, window_title = DEFAULT_WINDOW_TITLE):
        self._app = application
        self._window_title = window_title
        self._win = None

    def load(self):
        self._app.print_comment("Starting GUI interface:")
        self._app.print_comment("please wait while the application loads...")
        self.build_window()
        #run the method to build the GUI, overloaded in child class
        self.build_widgets()
        self.load_settings()

    def build_window(self):
       #build the GUI interface as a seperate window
        win = tk.Tk()
        Pmw.initialise(win) #initialize Python MegaWidgets
        win.withdraw()
        win.wm_title(self._window_title)
        win.focus_set() #put focus on this new window
        self._win = win
        #handle the user hitting the 'X' button
        self._win.protocol("WM_DELETE_WINDOW", self.close)

    def build_widgets(self):
        #overload this in child class, called on load
        pass

    def load_settings(self):
        #overload this in child class, called on load
        pass
                  
    def cache_settings(self):
        #overload this in child class, called on close
        pass

    def launch(self):
        #run the GUI handling loop
        ignore_KeyboardInterrupt()
        self.flush_event_queues()
        #reveal the main window
        self._win.deiconify()
        self._win.mainloop()
        notice_KeyboardInterrupt()
        
    def flush_event_queues(self):
        for handle in self._app._used_controllers:
            controller = self._app._load_controller(handle)
            #read out all pending events
            while not controller.event_queue.empty():
                event, info = controller.event_queue.get()
                self.print_event(event,info)
    
    def busy(self):
        self._win.config(cursor="watch")
        
    def not_busy(self):
        self._win.config(cursor="")
        
    def busy_dialog(self, msg):
        self._busy()
        self._wait_msg_window = tk.Toplevel(self._win)
        msg_label = tk.Label(self._wait_msg_window,
                             text = msg,
                             font = HEADING_LABEL_FONT)
        msg_label.pack(fill="both",expand="yes", padx=1,pady=1)
        # get screen width and height
        ws = self._win.winfo_screenwidth()
        hs = self._win.winfo_screenheight()
        w = ws/2
        h = hs/4
        # calculate position x, y
        x = (ws/2) - (w/2)
        y = (hs/2) - (h/2)
        self._wait_msg_window.geometry("%dx%d+%d+%d" % (w,h,x,y))
        self._wait_msg_window.update()
        self._wait_msg_window.lift()
        self._wait_msg_window.grab_set()
        self._app.print_comment(msg)
    
    def end_busy_dialog(self):
        self.not_busy()
        self._app.print_comment("busy dialog finished")
        try:
            self._wait_msg_window.destroy()
        except AttributeError: #ignore case when the window doesn't exist
            return
        
    def abort(self):
        #abort all active controllers
        self._app._abort_all_controllers()
        #cache the GUI settings
        self.cache_settings()
        self._win.destroy()
            
    def close(self):
        self._app.print_comment("\tApplication Close requested.")
        #check if any controllers are still alive
        running_controllers = []
        for handle in self._app._used_controllers:
            self._app.print_comment("\tChecking status of controller '%s'..." % handle)
            controller = self._app._load_controller(handle)
            if controller.thread_isAlive():
                self._app.print_comment("\tRUNNING")
                running_controllers.append(handle)
            else:
                self._app.print_comment("\tSTOPPED")
        if running_controllers:
            msg = "Warning: the following controllers are still running: %r\nAre you sure you want to abort?" % running_controllers
            dlg = Pmw.MessageDialog(parent = self._win,
                                    message_text = msg,
                                    buttons = ('Cancel','Abort'),
                                    defaultbutton = 'Cancel',
                                    title = "Running Controllers Warning",
                                    )
            choice = dlg.activate()
            if choice == 'Abort':
                self.abort()
        else:
            self.cache_settings()
            self._win.destroy()
