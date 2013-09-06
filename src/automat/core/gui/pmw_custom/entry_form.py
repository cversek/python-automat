try:
    from collections import OrderedDict
except ImportError:
    from automat.substitutes.ordered_dict import OrderedDict
    
from Tkinter import Frame, Label
import Pmw
import string

################################################################################
class EntryForm(Frame):
    """ A Pmw-based widget for multiple entries with validation.
    """
    def __init__(self,
                 parent=None,
                 title=None, 
                 default_entry_state = 'normal',
                 default_labelpos = 'w',
                ):
        Frame.__init__(self,parent)
        self.default_entry_state = default_entry_state
        self.default_labelpos    = default_labelpos
        if not title is None:
            Label(self,text=title).pack(side='top', fill='x')
        self.fields     = []
        self.field_dict = OrderedDict()

    def new_field(self,name,**kwargs):
        #use default state if not specified
        if kwargs.get('entry_state',None) is None:
            kwargs['entry_state'] = self.default_entry_state
        if kwargs.get('labelpos',None) is None:
            kwargs['labelpos'] = self.default_labelpos
        #construct entry field widget
        field = Pmw.EntryField(self,**kwargs)
        self.fields.append(field)            #cache in order
        self.field_dict[name] = field        #lookup by name

    def __getitem__(self,key):
        field = self.get_field_widget(key)
        return field.getvalue()

    def __setitem__(self,key,val):
        field = self.get_field_widget(key)
        field.setvalue(val)

    def get_field_widget(self,key):
        #try indexing by number
        try:
            return self.fields[key]
        except TypeError: #otherwise index by name
            return self.field_dict[key]

    def to_dict(self, filter_empty = False):
        if filter_empty:
            return dict([(name,field.get()) for name, field in self.field_dict.items() if field.get() != ""])
        else:
            return dict([(name,field.get()) for name, field in self.field_dict.items()])
    
    def pack(self,*args,**kwargs):
        fields = self.fields
        #pack all the field, knowing the form constraints
        for field in fields:
            field.pack(side = 'top',
                       fill = 'x')
        Pmw.alignlabels(fields) #adjusts all the labels for the entries
        Frame.pack(self,*args,**kwargs)

    def disable(self):
        #prevent entry for all the fields in the form 
        for field in self.fields:
            field.component('entry').config(state = 'readonly')

    def enable(self):
        #prevent entry for all the fields in the form 
        for field in self.fields:
            field.component('entry').config(state = 'normal')
            
################################################################################
# TEST CODE
################################################################################
if __name__ == "__main__":
    root = Pmw.initialise()
    VF = EntryForm(root, default_entry_state = 'readonly')
    VF.new_field('name',label_text='Name and stuff')
    VF.new_field('job', label_text='Job')
    VF.new_field('pay', label_text='Pay')
    VF.pack(expand='yes', fill='both')
    VF['name'] = 'Mike'
    VF['job']  = 'student'
    VF['pay']  = '30000.00'
    #root.mainloop()
    
