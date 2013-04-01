

import Tkinter
import Pmw
import string

from validation import Validator

###############################################################################

INSERT_ABOVE_KEY    = "<less>"
INSERT_BELOW_KEY    = "<greater>"
DELETE_KEY          = "X"
DEFAULT_ENTRY_WIDTH = 4
DEFAULT_NUM_VISIBLE_ENTRIES = 10


class ScrolledListEntry(Tkinter.Frame):
    """ Megawidget for convenient validated entry of a list numbers
    """
    def __init__(self, 
                 parent = None, 
                 init_values = [],
                 entry_width = None,
                 num_visible_entries = None,
                 validator = Validator(),
                 insert_above_key = INSERT_ABOVE_KEY,
                 insert_below_key = INSERT_BELOW_KEY,
                 delete_key       = DELETE_KEY,
                ):
        if entry_width is None:
            entry_width = DEFAULT_ENTRY_WIDTH
        if num_visible_entries is None:
            num_visible_entries = DEFAULT_NUM_VISIBLE_ENTRIES
        self.entry_width = entry_width
        self.num_visible_entries = num_visible_entries
        self.validator = validator
        self.insert_above_key = insert_above_key
        self.insert_below_key = insert_below_key
        self.delete_key       = delete_key
        
        #configure the gui compenents
        Tkinter.Frame.__init__(self, parent)
        self.sf = Pmw.ScrolledFrame(self, usehullsize=True)
        self.entry_frame = self.sf.interior()
        

        #initialize the list
        self.entryfields = []
        self.widgetIndexMap = {}
        for val in init_values:
            self.add_entry(val)

        #configure the hull size from the height and width of an individual entryfield
        entry = self.entryfields[0].component("entry")
        entry_width  = entry.winfo_reqwidth()
        entry_height = entry.winfo_reqheight()
        sf_hull = self.sf.component('hull')
        vbar_width  = self.sf.component('vertscrollbar').winfo_reqwidth()
        hbar_height = self.sf.component('horizscrollbar').winfo_reqheight()
        sf_hull['width']  = entry_width + vbar_width
        sf_hull['height'] = entry_height*self.num_visible_entries + hbar_height

        self.entry_frame.pack()
        self.sf.pack()

    def __getitem__(self,index):
        return self.entryfields[index]

    def add_entry(self,val=None):
        entryfield = Pmw.EntryField(self.entry_frame,validate = self.validator)
        entry = entryfield.component("entry")
        entry.configure(width=self.entry_width)  
        
        #configure the quick-key event handlers
        def event_wrapper(func,**kwargs):
            def inner(event):
                #find index of calling widget
                index = self.resolve_widget_index(event.widget)   
                kwargs['index'] = index
                #run the callback, passing arguments
                func(**kwargs)
                #prevent event from propagating, very important!
                return "break" 
            return inner
       
        entry.bind(self.insert_above_key,  event_wrapper(self.insert,place='above'))
        entry.bind(self.insert_below_key,  event_wrapper(self.insert,place='below'))
        entry.bind(self.delete_key,        event_wrapper(self.delete))
        entry.bind("<KeyPress-Up>",        event_wrapper(self.move_up))
        entry.bind("<KeyPress-Down>",      event_wrapper(self.move_down))
        
        
        
        #finish configuration      
        if val is not None:
            entryfield.setvalue(val)
        entryfield.pack()
        
        #add to the index map
        self.widgetIndexMap[entry.winfo_name()] = len(self.entryfields)
        #append the entryfield widget to the list
        self.entryfields.append(entryfield)
    
    def clear_list(self):
        while True:
            try:
                last_entryfield = self.entryfields.pop()
                last_entryfield.pack_forget()
            except IndexError:
                break
    
    def setvalues(self,values):
        self.clear_list()
        for val in values:
            self.add_entry(val)            
    
    def delete(self,index):
        #remove the last entryfield, unless only one left
        if len(self.entryfields) > 1:
            #get the indices of fields to shift up
            moved_indices = range(index,len(self.entryfields)-1)        
            
            #shift all the vaules up
            for i in moved_indices:
                val = self.entryfields[i+1].getvalue()
                self.entryfields[i].setvalue(val)
            
            last_entryfield = self.entryfields.pop()
            last_entryfield.pack_forget()
      
            #refocus on the new last entry if necessary    
            if index >= len(self.entryfields):
                last_entryfield = self.entryfields[-1]
                last_entryfield.component('entry').focus_set()
            
        #prevent event from propagating, very important!
        return 'break'
                
    def insert(self, index, place='below'):
        
        #get the indices of fields to shift down
        moved_indices = range(index,len(self.entryfields))        
        moved_indices.reverse()
        
        #add a new field to the end
        self.add_entry("")
        
        #shift all the vaules down
        for i in moved_indices:
            val = self.entryfields[i].getvalue()
            self.entryfields[i+1].setvalue(val)
            
        #configure the "new" entryfield
        if place == 'above':    
            entryfield = self.entryfields[index]
            entryfield.clear() #erase the contents
        elif place == 'below':
            entryfield = self.entryfields[index + 1]
            entryfield.clear() #erase the contents
            entryfield.component("entry").focus_set() #move focus down to this

    def move_up(self,index):
        index -= 1
        if index >= 0:
            entryfield = self.entryfields[index]
            entryfield.component('entry').focus_set()
    
    def move_down(self,index):
        index += 1
        if index < len(self.entryfields):
            entryfield = self.entryfields[index]
            entryfield.component('entry').focus_set()
           
    def getvalues(self, convert = True):
        if convert:
            converter = self.validator.convert
            return [converter(e.getvalue()) for e in self.entryfields]
        else:
            return [e.getvalue() for e in self.entryfields]

    def getinvalid_indices(self):
        return [i for i,e in enumerate(self.entryfields) if not e.valid()]

    def valid(self):
        for e in self.entryfields:
            if not e.valid():
                return False
        return True
        
    def resolve_widget_index(self, widget):
        #None signifies not a member of the list 
        widget_name = widget.winfo_name()
        index = self.widgetIndexMap.get(widget_name, None) 
        return index
        
    def disable(self):
        for e in self.entryfields:
            e.component('entry').config(state='readonly')
    
    def enable(self):
        for e in self.entryfields:
            e.component('entry').config(state='normal')                              

if __name__ == "__main__":
    INIT_VALUES = range(200,20,-20)
    VALIDATE    = {"validator":"integer", 'max':200,'min':40, 'maxstrict':False,'minstrict':False}
    # Initialise Tkinter and Pmw.
    root = Pmw.initialise()
    list_entry = ScrolledListEntry(root,init_values=INIT_VALUES, validator=VALIDATE)
    list_entry.pack(expand='yes',fill="both")
    #root.mainloop()
