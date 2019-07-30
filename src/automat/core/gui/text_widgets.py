from tkinter import *

                       
###############################################################################
class TextDisplayBox(Frame):
    """ A simple text display box with vertical and horizontal scrollbars.
    """
    def __init__(self, 
                 parent      = None, 
                 text_width  = 40, 
                 text_height = 40,
                 use_vbar    = True,
                 use_hbar    = True,
                 buffer_size = None,
                ):
        Frame.__init__(self,parent)
        #text area
        self.text = text = Text(self, 
                                width  = text_width,
                                height = text_height,
                                relief = 'sunken',
                                state  = 'disabled',
                                wrap   = "none",
                               )
        #vertical scrollbar
        if use_vbar:
            self.vbar = vbar = Scrollbar(self, 
                                         command = text.yview,
                                        )
            text.config(yscrollcommand = vbar.set) #link back to text box
        else:
            self.vbar = None
        #horizontal scrollbar
        if use_hbar:
            self.hbar = hbar = Scrollbar(self, 
                                         command = text.xview,
                                         orient='horizontal',
                                        )
            text.config(xscrollcommand = hbar.set) #link back to text box
        else:
            self.hbar = None
        self.text_length = 0
        self.buffer_size = buffer_size

    def pack(self,*args,**kwargs):
        if not self.vbar is None:
            self.vbar.pack(side='right',  fill='y') #pack first => clip last
        if not self.hbar is None:
            self.hbar.pack(side='bottom', fill='x')
        self.text.pack(side='top', fill='both', expand='yes')
        Frame.pack(self,*args,**kwargs)

    def clear_text(self):
        "delete the current text"
        # make the display editable
        self.text.config(state='normal')
        # erase all
        self.text.delete('1.0','end')  
        # make the display uneditable
        self.text.config(state='disabled')
        self.text_length = 0
  
    def print_text(self,string, eol='\n'):
        self.append_text(string)
        if eol:
           self.append_text(eol)
 
    def append_text(self,string):
        "add a string to the end of text box and force scrollbar down"
        str_len = len(string)        
        
        #remove text to stay within buffer length
        if not self.buffer_size is None:
            bs = self.buffer_size
            #remove lines from the beginning until buffer can fit the new text 
            self.text.config(state='normal')   #make the display editable         
            while self.text_length + str_len > bs:                
                #size the first line and delete it
                line = self.text.get(1.0, '1.end+1c')
                self.text.delete(1.0, '1.end+1c')                
                self.text_length -= len(line)               
            self.text.config(state='disabled') #make the display uneditable
                  
        # make the display editable
        self.text.config(state='normal')
        # add our string
        self.text.insert('end', string)
        # scroll down to the bottom again
        self.text.yview('end')
        # make the display uneditable
        self.text.config(state='disabled')
        #update the text length
        self.text_length += str_len
    def set_text_yview(self,pos):
        self.text.yview(pos)


###############################################################################


###############################################################################
# TEST CODE
###############################################################################            
if __name__ == "__main__":
    sample_line = "".join([chr(i) for i in range(ord('A'),ord('z')) ])
    sample_text = "\n".join([ ("(%d)" % i) + sample_line for i in range(80)])
    root = Tk()
    TB = TextDisplayBox(root)
    TB.pack()
    TB.append_text(sample_text)
    #TB.clear_text()
    root.mainloop()
    

