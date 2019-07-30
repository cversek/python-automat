from tkinter import *
import tkinter.simpledialog

class Field(Frame):
    def __init__(self,parent,name,value=None,label=None,var_type=StringVar,state=NORMAL):
        Frame.__init__(self,parent)
        self.name   = name
        if label is None:
            #use name by default
            label = name
        self.label = label
        self.state = state
        #instantiate a tk variable
        self.var    = var = var_type(self)
        #create and cache the sub widgets
        self._label = Label(self,text=label)    
        self._entry = Entry(self,textvariable=var,state=state)
        #set the value if given
        if not value is None:
            self.set(value)
    def get(self):
        return self.var.get()
    def set(self, val):
        self.var.set(val)
    def bind(self,*args,**kwargs):
        "bind to the entry widget"
        self._entry.bind(*args,**kwargs)
    def pack(self,label_width=None,*args,**kwargs):
        if label_width is None:
            label_width = len(self.label)
        #set the label width
        self._label.config(width=label_width)
        #pack the sub widgets
        self._label.pack(side=LEFT)
        self._entry.pack(side=RIGHT,expand=YES,fill=X)  #grow horizontally
        Frame.pack(self,*args,**kwargs)
        
class VariableForm(Frame):
    def __init__(self,parent,title=None, default_field_state=NORMAL):
        Frame.__init__(self,parent)
        self.default_field_state = default_field_state
        if not title is None:
            Label(self,text=title).pack(side=TOP, fill=X)
        self.fields     = []
        self.field_dict = {} 
    def new_field(self,*args,**kwargs):
        #use default state if not specified
        if kwargs.get('state',None) is None:
            kwargs['state'] = self.default_field_state
        field = Field(self,*args,**kwargs)   #create Field sub Frame
        self.fields.append(field)            #cache in order
        self.field_dict[field.name] = field  #lookup by name    
    def __getitem__(self,key):
        field = self.field_dict[key]
        return field.get()
    def __setitem__(self,key,val):
        field = self.field_dict[key]
        field.set(val)
    def to_dict(self):
        return dict([(name,field.get()) for name, field in list(self.field_dict.items())])
    def get_field_widget(self,name):
        return self.field_dict[name]
    def bind_field_override(self,field_name, binding,
                                 command = lambda field: None):
        field = self.get_field_widget(field_name)
        msg      = "Enter new value for field '%s':" % field.label
        wm_title = 'Override Field'
        #create override dialog wrapper
        def override_func(event):
            val = tkinter.simpledialog.askfloat(wm_title,msg, parent=self)
            if not val is None:
                field.set(val)
            #run the command function
            command(field)
        field.bind(binding,override_func)
    def pack(self,*args,**kwargs):
        fields = self.fields
        #obtain the largest field label length
        max_label_width = max([len(field.label) for field in fields])
        #pack all the field, knowing the form constraints
        for field in fields:
            field.pack(label_width = max_label_width,
                       side = TOP,
                       fill = X)
        Frame.pack(self,*args,**kwargs)
   
            
if __name__ == "__main__":
    root = Tk()
    VF = VariableForm(root, default_field_state = 'readonly')
    VF.new_field(name='name',label='Name and stuff')
    VF.new_field(name='job', label='Job')
    VF.new_field(name='pay', label='Pay')
    VF.pack(expand=YES, fill=BOTH)
    VF['name'] = 'Mike'
    VF['job']  = 'student'
    VF['pay']  = '30000.00'
    root.mainloop()
    
            
        


