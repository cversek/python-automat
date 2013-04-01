import Tkinter
from Tkinter import Frame, Button, Label
from Pmw import Dialog

#package local
from validation import Validator
from list_entry import ScrolledListEntry
from entry_form import EntryForm
###############################################################################
DEFAULT_LABELS_TEXT = {
    'title': "Values from Range",
    'first': "first value",
    'last':  "last value",
    'step':  "step size",
}

def integer_range(lb, rb, step):
    if lb > rb:
        step = -step
    #understood to be inclusive range
    return range(lb,rb+step,step)
###############################################################################
class RangeDialog(Dialog):
    def __init__(self,
                 parent              = None,
                 range_func          = integer_range,
                 first_value_default = "",
                 last_value_default  = "",
                 step_size_default   = "",
                 validator           = None, #use only validation.Validator based objects
                 step_validator      = None,
                 labels_text         = DEFAULT_LABELS_TEXT,
                 ):
        self.range_func = range_func        
        if validator is None:
            validator      = Validator() 
        self.validator = validator        
        if step_validator is None:
            step_validator = self.validator     
        self.step_validator = step_validator        
        #set up dialog windows
        Dialog.__init__(self,
                        parent = parent,
                        title = labels_text['title'], 
                        buttons = ('Append','Overwrite','Cancel'),
                        defaultbutton = 'Append',
                       )
        frame = self.interior()
        form = EntryForm(frame)
        form.new_field('first',
                       labelpos='w',
                       label_text=labels_text['first'],
                       value = first_value_default,
                       validate = self.validator 
                      )
        form.new_field('last',
                        labelpos='w',
                        label_text=labels_text['last'],
                        value = last_value_default,
                        validate = self.validator 
                     )
        form.new_field('step',
                        labelpos='w',
                        label_text=labels_text['step'],
                        value = step_size_default,
                        validate = self.step_validator 
                      )
        form.pack(expand='yes', fill='both')
      
        self.form = form
    def activate(self):
        "override activate to construct and send back the action and the new values"
        action = Dialog.activate(self)
        if action in ('Append', 'Overwrite'):
            lb   =  self.validator.convert(self.form['first'])
            rb   =  self.validator.convert(self.form['last'])
            step =  self.step_validator.convert(self.form['step'])
            newvalues = self.range_func(lb,rb,step)
            return (action, newvalues)
        else:
            return (action, None)
###############################################################################
 

###############################################################################
# TEST CODE
###############################################################################
if __name__ == "__main__":
    

    # Initialise Tkinter and Pmw.
    import Tkinter    
    import Pmw
    #create a test window    
    root = Pmw.initialise()    
    RD = RangeDialog(root, 
                     validator = Validator(_min = 0, _max = 200, converter = int),
                     first_value_default = 0,
                     last_value_default  = 100,
                     step_size_default   = 10,
                    )
    RD.withdraw()
    def test_dialog():
        action, values = RD.activate()
        print "action:", action
        print "values:", values
    launch_button = Tkinter.Button(root,text="Test Dialog",command=test_dialog)
    launch_button.pack()
    root.mainloop()
