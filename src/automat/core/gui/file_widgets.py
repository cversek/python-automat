from tkinter import *
import tkinter.filedialog
import tkinter.messagebox

class FileBundler:
    def __init__(self, start_path="~", file_types=[("all files","*")]):
        self.start_path = start_path
        self.file_types = file_types
        #build the GUI
        win = Tk()
        self.win = win
        LBF = Frame(win)
        SB = Scrollbar(LBF)
        SB.pack(side=RIGHT, fill=Y)
        self.list_box = LB = Listbox(LBF, width=100)
        LB.pack(side=LEFT, fill = BOTH, expand=True)
        SB.config(command=LB.yview)
        LB.config(yscrollcommand=SB.set)
        LBF.pack(side=TOP, fill = BOTH, expand=True)
        BF = Frame(win)
        add_button = Button(BF,text="Add",command=self.add_file)
        add_button.pack(side=LEFT)
        rm_button = Button(BF,text="Remove",command=self.remove_file)
        rm_button.pack(side=LEFT)
        done_button = Button(BF,text="Done",command=win.quit)
        done_button.pack(side=LEFT)
        BF.pack(side=TOP)
        win.mainloop()
    def add_file(self):
        filename = tkinter.filedialog.askopenfilename(initialdir=self.start_path,
                                                filetypes=self.file_types
                                               )
        self.list_box.insert(END,filename)
    def remove_file(self):
        index = self.list_box.curselection()
        self.list_box.delete(index)
    def get_all(self):
        return self.list_box.get(0,END)
