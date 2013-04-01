import Tkinter
import Pmw
LISTBOX_MAX_HEIGHT = 40

class SelectorListBox(Tkinter.Frame):
    def __init__(self,
                 tk_parent,
                 items = [],
                 label_text = "",
                ):
        #initialize as the toplevel window
        Tkinter.Frame.__init__(self, tk_parent)
        self.items = items
        self.label = Tkinter.Label(self, text=label_text)
        #setup and configure the listbox component
        item_lens = [len(item) for item in items]
        item_lens += [len(label_text)]
        w = max(item_lens)
        h = min(len(items),LISTBOX_MAX_HEIGHT)        
        self.listbox = Pmw.ScrolledListBox(self, 
                                           items = self.items,
                                           listbox_selectmode = 'extended',
                                           listbox_width  = w,
                                           listbox_height = h,
                                          )
        self.label.pack(side='top',expand='no', fill = 'x')
        self.listbox.pack(side='top',expand='yes', fill='both')

    def get_selections(self):
        selections = self.listbox.curselection()
        return selections

class TwoPanedSelectorListBox(Tkinter.Frame):
    def __init__(self,
                 tk_parent,
                 items1 = [],
                 items2 = [],
                 label1_text = "",
                 label2_text = "",
                ):
        #initialize as the toplevel window
        Tkinter.Frame.__init__(self, tk_parent)
        self.items1 = items1
        self.items2 = items2
        #setup and configure the listbox component
        item_lens =  [len(item) for item in items1]
        item_lens += [len(item) for item in items2]
        item_lens += [len(label1_text),len(label2_text)]
        w = max(item_lens)
        h = min(max(len(items1),len(items2)),LISTBOX_MAX_HEIGHT)
        #build left panel
        self.left_panel  =  Tkinter.Frame(self)
        if label1_text:
            label1 = Tkinter.Label(self.left_panel,  text=label1_text)
            label1.pack(side='top',  expand='no', fill='x')
        self.listbox1 = Pmw.ScrolledListBox(self.left_panel, 
                                           items = self.items1,
                                           listbox_selectmode = 'extended',
                                           listbox_width  = w,
                                           listbox_height = h,
                                          )
        
        self.listbox1.pack(side='top',expand='yes', fill='y')
        #build right panel
        self.right_panel = Tkinter.Frame(self)
        if label2_text:
            label2 = Tkinter.Label(self.right_panel, text=label2_text)
            label2.pack(side='top',  expand='no', fill='x')
        self.listbox2 = Pmw.ScrolledListBox(self.right_panel, 
                                           items = self.items2,
                                           listbox_selectmode = 'extended',
                                           listbox_width  = w,
                                           listbox_height = h,
                                          )       
        self.listbox2.pack(side='top',expand='yes', fill='y')
        #construct a middle panel for extension use
        self.middle_panel = Tkinter.Frame(self)
        

    def pack(self, *args, **kwargs):
        #pack the panels        
        self.left_panel.pack(side='left',fill='y')
        self.middle_panel.pack(side='left',fill='y')
        self.right_panel.pack(side='left',fill='y')
        Tkinter.Frame.pack(self, *args, **kwargs)
        
    def get_selections1(self):
        indices = map(int,self.listbox1.curselection())
        items = map(self.items1.__getitem__,indices)
        return indices, items

    def get_selections2(self):
        indices = map(int,self.listbox2.curselection())
        items = map(self.items2.__getitem__,indices)
        return indices, items

    def copy_left_right(self):
        indices, items = self.get_selections1()
        self.items2.extend(items)
        self.listbox2.setlist(self.items2)

    def copy_right_left(self):
        indices, items = self.get_selections2()
        self.items1.extend(items)
        self.listbox1.setlist(self.items1)

    def delete_left(self):
        indices, items = self.get_selections1()
        keep_indices = set(indices) ^ set(range(len(self.items1)))
        keep_items =  map(self.items1.__getitem__,keep_indices)
        self.items1 = keep_items
        self.listbox1.setlist(self.items1)
                      
    def delete_right(self):
        indices, items = self.get_selections2()
        keep_indices = set(indices) ^ set(range(len(self.items2)))
        keep_items =  map(self.items2.__getitem__,keep_indices)
        self.items2 = keep_items
        self.listbox2.setlist(self.items2) 
