"""   
desc:  Setup script for 'automat' package.
auth:  Craig Wm. Versek (cversek@physics.umass.edu)
date:  7/8/2011
notes: install with "sudo python setup.py install"
"""




import platform, os, shutil




PACKAGE_METADATA = {
    'name'         : 'automat',
    'version'      : 'dev',
    'author'       : "Craig Versek",
    'author_email' : "cversek@physics.umass.edu",
}
    
PACKAGE_SOURCE_DIR = 'src'
MAIN_PACKAGE_DIR   = 'automat'
MAIN_PACKAGE_PATH  = os.path.abspath(os.sep.join((PACKAGE_SOURCE_DIR,MAIN_PACKAGE_DIR)))

INSTALL_REQUIRES = []

LINUX_CONFIG_DIR = '/etc/Automat'



def ask_yesno(prompt, default='y'):
    while True:
        full_prompt = prompt + "([y]/n): "
        val = input(full_prompt)
        if val == "":
            val = default
        if val in ['y','Y']:
            return True
        elif val in ['n','N']:
            return False

###############################################################################
# verify hardware dependencies

def check_linux_gpib():
    try:
        print("Checking for python-gpib...", end=' ')
        import gpib
        print(" found")
        return True
    except ImportError:
        print("\n\tWarning: python-gpib has not been installed, no GPIB support will be available.\n\tSee docs/GPIB_support.txt for more info.")
        return False

def check_pyserial():
    try:
        print("Checking for pyserial...", end=' ')
        import serial
        print(" found")
        return True
    except ImportError:
        print("\n\tWarning: pyserial has not been installed.")
        val = ask_yesno("Should setuptools try to download an install this package?")
        if val:
            INSTALL_REQUIRES.append('pyserial')
        return False
 

###############################################################################
# MAIN
###############################################################################
if __name__ == "__main__":
    print("*"*80)
    #check the system 
    system = platform.system()
    print("Detected system: %s" % system) 
    print("Running hardware compatibility check:")
    if system == 'Linux':
        #FIXME - this is a hack to get python path working with 'sudo python setup.py...'
        import sys
        major, minor, _,_,_ = sys.version_info
        sys.path.append("/usr/local/lib/python%d.%d/site-packages" % (major,minor))
        #END FIXME
        check_linux_gpib()
        check_pyserial()
    elif system == 'Darwin':
        pass
    elif system == 'Windows':
        pass

    #gather platform specific data
    platform_data = {}   
    platform_data['system'] = system
    config_dirpath = None
    if system == 'Linux' or system == 'Darwin':
        config_dirpath = LINUX_CONFIG_DIR
        if not os.path.isdir(config_dirpath):
            print("creating config directory: %s" % config_dirpath)
            os.mkdir(config_dirpath)
        else:
            print("config directory already exists: %s" % config_dirpath)
    elif system == 'Windows':
        from win32com.shell import shellcon, shell
        appdata_path   = shell.SHGetFolderPath(0, shellcon.CSIDL_APPDATA, 0, 0)
        config_dirpath = appdata_path

    platform_data['config_dirpath'] = config_dirpath
   
   

    #autogenerate the package information file
    
    pkg_info_filename   = os.sep.join((MAIN_PACKAGE_PATH,'pkg_info.py'))
    print("Writing the package info file: %s" % pkg_info_filename)
    pkg_info_file       = open(pkg_info_filename,'w')
    pkg_info_file.write("metadata = %r\n" % PACKAGE_METADATA)
    pkg_info_file.write("platform = %r"   % platform_data)
    pkg_info_file.close()

    input("press 'Enter' to continue...")
    print("*"*80)

    #the rest is controlled by setuptools
    from ez_setup import use_setuptools
    use_setuptools()

    from setuptools import setup, find_packages

    # run the setup script
    setup(
        
          #packages to install
          package_dir  = {'':'src'},
          packages     = find_packages('src'),
          
          #non-code files
          package_data     =   {'': ['*.yaml','*.yml']},

          #dependencies
          install_requires = INSTALL_REQUIRES,
          extras_require = {
                            'Plotting': ['matplotlib >= 0.98'],
                            'YAML Command Specification':  ['pyaml']
                           },
          dependency_links = [
                              #'http://sourceforge.net/project/showfiles.php?group_id=80706', #matplotlib
                             ],
          #scripts and plugins
          entry_points = {
                          #'console_scripts': ['automat_decode_nispy = automat.scripts.decode_nispy:main']
                         },
          **PACKAGE_METADATA 
    )
