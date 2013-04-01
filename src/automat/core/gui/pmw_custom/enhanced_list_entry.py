import Tkinter
from Tkinter import Frame, Button, Label
import Pmw

import string
#package local
from validation import Validator
from list_entry import ScrolledListEntry
###############################################################################
class EnhancedListEntry(Frame):
    def __init__(self, 
                 parent = None,
                 label_text  = None, 
                 init_values = [], 
                 validator = None,
                 list_entry_width = None,
                ):
        Frame.__init__(self,parent)
        self.label_text = label_text
        #use the enhanced validator if none is supplied
        if validator is None:
            validator  = Validator() 
        self.validator = validator 
        #build the scrolled list entry    
        self.list_entry = ScrolledListEntry(parent = self, 
                                            init_values = init_values,
                                            validator    = self.validator,
                                            entry_width = list_entry_width, 
                                           )
        #build the panel for buttons
        button_bar = Frame(self)
        def focus_wrapper(func,**kwargs):
            def inner():
                #find index of widget in focus
                widget = self.focus_get()
                index  = self.list_entry.resolve_widget_index(widget)
                kwargs['index'] = index
                if not index is None:
                    #run the callback, passing arguments
                    func(**kwargs)
            return inner
        
        insert_above_button = Button(button_bar,
                                          text="<",
                                          command = focus_wrapper(self.list_entry.insert,place='above'),
                                         )
        insert_below_button = Button(button_bar,
                                          text=">",
                                          command = focus_wrapper(self.list_entry.insert,place='below'),
                                         )
        delete_button       = Button(button_bar,
                                          text="X",
                                          command = focus_wrapper(self.list_entry.delete),
                                         )
        #arrange the button ordering       
        self.buttons = [insert_above_button,insert_below_button,delete_button]
        self.button_bar = button_bar   

    def pack(self, *args, **kwargs):
        if not self.label_text is None:
            Label(self,text=self.label_text).pack(side='top', anchor = 'nw')
        #pack all the buttons
        for button in self.buttons:
            button.pack(side='top', fill='x')  
        self.button_bar.pack(side='left', fill='y', anchor='nw')
        self.list_entry.pack(side='left', anchor='ne')
        Frame.pack(self, *args, **kwargs)        
        
    def get_values(self, *args, **kwargs):
        return self.list_entry.getvalues(*args, **kwargs)
    
    
               
    def disable(self):
        self.list_entry.disable()
        for button in self.buttons:
            button.config(state='disabled') 
    
    def enable(self):
        self.list_entry.enable()
        for button in self.buttons:
            button.config(state='normal')
    
    def force_validate(self):
        invalid_indices = self.list_entry.getinvalid_indices()
        #if there are invalid entries report dialog
        if invalid_indices:
            #get next invalid
            i = invalid_indices[0]
            e = self.list_entry[i]
            message_text = "Invalid value '%s' at index %d" % (e.getvalue(),i) 
            message_text += "\nmin: %s" % self.validator._min
            message_text += "\nmax: %s" % self.validator._max
            dialog = Pmw.MessageDialog(title = 'Value Error',
                                       message_text = message_text
                                      )
            dialog.activate(geometry = 'centerscreenalways')
            #focus on the invalid entry
            e.component("entry").focus_set()
            return False
        else:
            return True  
       
###############################################################################
# TEST CODE
###############################################################################
if __name__ == "__main__":
    INIT_SETPOINTS = range(200,20,-20)

    SETPOINT_MIN = 40
    SETPOINT_MAX = 230

    RANGE_FIRST_SETPOINT = 200
    RANGE_LAST_SETPOINT  = 40
    RANGE_STEPSIZE = 20

    
    #INIT_SETPOINTS = range(200,20,-20)
    # Initialise Tkinter and Pmw
    import Pmw
    root = Pmw.initialise()
    from range_dialog import RangeDialog
    RD = RangeDialog(root,
                     validator = Validator(_min = 0, _max = 200, converter = int),
                     #first_value_default = 0,
                     #last_value_default  = 100,
                     #step_size_default   = 10,
                    )
    ts_entry = EnhancedListEntry(root, 
                                 init_values  = INIT_SETPOINTS,
                                 validator    = Validator(),
                                 range_dialog = RD, 
                                )
    ts_entry.pack(expand='yes',fill="both")
    root.mainloop()
