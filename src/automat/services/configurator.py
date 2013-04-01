import os, sys, glob
from configobj import ConfigObjError
from   automat.core.hwcontrol.config.configuration import Configuration
import automat.pkg_info


CONFIG_FILE_PATTERN = "*.cfg"

class ConfiguratorService(object):
    def __init__(self, searchpaths = None):
        if searchpaths is None:
            searchpaths = [automat.pkg_info.platform['config_dirpath']]
        self.searchpaths = searchpaths
        self.configs = []
        self._find_config_files()        

    def _find_config_files(self):
        configs = []        
        for sp in self.searchpaths:
            pattern = os.sep.join((sp,CONFIG_FILE_PATTERN))
            cfg_filenames = glob.glob(pattern)
            for fn in cfg_filenames:
                try:
                    cfg = Configuration(fn)
                    configs.append(cfg)
                except ValueError:  #FIXME transfer these to automat.config errors
                    print "automat.config error: %s" % fn
                except ConfigObjError:
                    print "configobj error: %s" % fn
        self.configs = configs

    def request_config_dialog(self):
        self._find_config_files()
        import Tkinter, Pmw
        #build the GUI interface as a seperate window
        win = Tkinter.Tk()
        Pmw.initialise(win)
        win.withdraw()
        win.wm_title(WINDOW_TITLE)
        win.focus_set() #put focus on this new window
        #handle the user hitting the 'X' button
        win.protocol("WM_DELETE_WINDOW", lambda: sys.exit(0))
        #initialize the Configurator frame
        cfg_gui = ConfiguratorGUI(parent = win,configurator_service = self)
        cfg_gui.pack(expand=True)
        win.deiconify()
        win.mainloop()
        return cfg_gui.selection


import Tkinter, Pmw
from automat.core.gui.text_widgets import TextDisplayBox
WINDOW_TITLE = "Automat Configurator"
TEXT_BUFFER_SIZE         = 10*2**10 #ten kilobytes
TEXT_DISPLAY_TEXT_HEIGHT = 40
TEXT_DISPLAY_TEXT_WIDTH  = 80

class ConfiguratorGUI(Tkinter.Frame):
        def __init__(self, parent, configurator_service):
            Tkinter.Frame.__init__(self, parent)
            self.configurator_service = configurator_service
            choices = [cfg['config_filepath'] for cfg in self.configurator_service.configs]
            # Add some contents to the dialog
            self.menu = Pmw.OptionMenu(self,
                                       items = choices,
                                       labelpos='nw',
                                       label_text='Configuration Files',
                                       command = self._option_menu_command, #called when choice is switched
                                       #selectioncommand=self.selectionCommand,
                                       #dblclickcommand = self.setup_control_mode,
                                       #usehullsize = 1,
                                       #hull_width = 200,
                                       #hull_height = 200,
                                       )
                    
            self.text_display  = TextDisplayBox(self,text_height=TEXT_DISPLAY_TEXT_HEIGHT, text_width=TEXT_DISPLAY_TEXT_WIDTH, buffer_size = TEXT_BUFFER_SIZE)
            self.select_button = Tkinter.Button(text='Select',command = self._select_button_command)

            self.menu.pack(side='top', anchor='nw')        
            self.text_display.pack(expand = True, fill = 'both', padx = 4, pady = 4)
            self.select_button.pack(side='bottom')
                        
            self.selection = None
            self.menu.invoke(index=0)
            
        def _select_button_command(self):
            print "Selection made: %s" % self.menu.getvalue()
            root = self._root()
            root.destroy()
            
        def _option_menu_command(self, option):
            choice_index = self.menu.index(Pmw.SELECT)
            self.selection = self.configurator_service.configs[choice_index]
            print "Current choice index %d, option: %s" % (choice_index,option)
            self.text_display.clear_text()
            try:
                #read in the raw file and display it in the text box
                config_filename = self.selection.filename
                text = open(config_filename, 'r').read()
                self.text_display.print_text(text)
                self.text_display.set_text_yview(0) #forces scroll back to top
            except:
                self.text_display.print_text("*** Could not read file: %s" % config_filename)
