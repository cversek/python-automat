""" interface for lockfile implementation of system wide mutex (inter-process 
    and inter-thread)
"""
###############################################################################
import os, fcntl, threading, tempfile, time, pwd, grp, getpass

DEFAULT_PATH = tempfile.gettempdir()
SLEEP_TIME = 0.01
LOCKFILE_SUBDIR = "Automat"
LOCKFILE_PREFIX = "AUTOMAT_MUTEX"

###############################################################################
class Mutex(object):
    _threadlocks = {} #cache thread locks by name
    def __init__(self, name, path = DEFAULT_PATH, default_timeout = None):
        self.name = name
        self.path = path
        self.default_timeout = default_timeout
        username = getpass.getuser()
        subdirname = "%s_%s" % (LOCKFILE_SUBDIR, username)
        self._lockfile_subdir = os.sep.join((path,subdirname))
        if not os.path.exists(self._lockfile_subdir):
            os.mkdir(self._lockfile_subdir)
            #FIXME change the permissions and change the group
#            uid = os.getuid()
#            gid = grp.getgrnam("automat").gr_gid
#            os.chown(self._lockfile_subdir, uid, gid)
#            os.chmod(self._lockfile_subdir, 0o777) #FIXME this may be insecure
            
        fname = "%s_%s" % (LOCKFILE_PREFIX, name)
        self._lockfile_name = os.sep.join((self._lockfile_subdir,fname)) 
        self._lockfile = None
        threadlock = Mutex._threadlocks.get(name)
        if threadlock is None: #unique name
            Mutex._threadlocks[name] = threadlock = threading.Lock()
        self._threadlock = threadlock

    def acquire(self, timeout = None):
        if timeout is None:
            timeout = self.default_timeout
        if self._lockfile is None:
            self._lockfile = open(self._lockfile_name,'w')
#            #FIXME change the permissions and change the group
#            uid = os.getuid()
#            gid = grp.getgrnam("automat").gr_gid
#            os.chown(self._lockfile_name, uid, gid)
#            os.chmod(self._lockfile_name, 0o777) #FIXME this may be insecure
        has_threadlock = False
        t0 = time.time()
        while True:
            try:
                #first try acquiring the thread lock (within one process)
                has_threadlock = self._threadlock.acquire(False) #False means don't block
                if not has_threadlock:
                    curr_thread = threading.current_thread()
                    raise RuntimeError("could not obtain the thread lock in thread: %s" % curr_thread.name)
                #next try to obtain the process lock (lockfile implementation)
                fcntl.lockf(self._lockfile, fcntl.LOCK_EX | fcntl.LOCK_NB) #might throw IOError
                #we have both locks now
                info = "acquired by PID %s at %s" % (os.getpid(), time.time())
                self._lockfile.truncate(0) #clean up after last thread
                self._lockfile.write(info) #tell them who you are
                self._lockfile.flush()
                return
            except IOError: #some else has lock
                dt = time.time() - t0
                if not timeout is None and dt >= timeout:
                    raise RuntimeError("acquiring the mutex lock '%s' has timed-out in %f seconds" % (self.name, timeout))
                time.sleep(SLEEP_TIME)

    def release(self):
        info = ", released at %s\n" % (time.time(),)
        #release process lock first
        self._lockfile.write(info)
        self._lockfile.flush()
        fcntl.lockf(self._lockfile, fcntl.LOCK_UN)
        #now release the thread lock
        self._threadlock.release()
        
    #implement Python 'with' statement interface
    def __enter__(self):
        #set things up
        self.acquire() #grab the lock on 'with' entrance
        
    def __exit__(self, type, value, traceback):
        #tear things down
        self.release() #release on 'with' exit

################################################################################
# TEST CODE
################################################################################
if __name__ == "__main__":
    m1 = Mutex("test1")
    n1 = Mutex("test1")
    #m1.acquire()
    #n1.acquire(timeout = 5) #should fail with RuntimeError



