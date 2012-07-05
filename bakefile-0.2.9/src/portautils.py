#
#  This file is part of Bakefile (http://www.bakefile.org)
#
#  Copyright (C) 2003,2004,2008 Vaclav Slavik
#
#  Permission is hereby granted, free of charge, to any person obtaining a copy
#  of this software and associated documentation files (the "Software"), to
#  deal in the Software without restriction, including without limitation the
#  rights to use, copy, modify, merge, publish, distribute, sublicense, and/or
#  sell copies of the Software, and to permit persons to whom the Software is
#  furnished to do so, subject to the following conditions:
#
#  The above copyright notice and this permission notice shall be included in
#  all copies or substantial portions of the Software.
#
#  THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
#  IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
#  FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
#  AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
#  LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING
#  FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS
#  IN THE SOFTWARE.
#
#  $Id: portautils.py 1181 2008-01-20 18:23:05Z vaclavslavik $
#
#  Portable utilities for misc tasks
#

import os, tempfile

#
# Secure temporary file creation:
#

def mktemp(prefix):
    """Uses tempfile.mkstemp() to atomically create named file, but works
       only with Python 2.3+."""
    handle, filename = tempfile.mkstemp(prefix=prefix)
    os.close(handle)
    return filename
    
def mktempdir(prefix):
    """Uses tempfile.mkdtemp() to atomically create named directory, but works
       only with Python 2.3+."""
    return tempfile.mkdtemp(prefix=prefix)


#
# Cross-platform file locking:
# (based on portalocker Python Cookbook recipe
# by John Nielsen <nielsenjf@my-deja.com>:
# http://aspn.activestate.com/ASPN/Cookbook/Python/Recipe/65203
#

if os.name == 'nt':
    import win32con
    import win32file
    import pywintypes
    # is there any reason not to reuse the following structure?
    __overlapped = pywintypes.OVERLAPPED()

    def lock(file):
        try:
            hfile = win32file._get_osfhandle(file.fileno())
            win32file.LockFileEx(hfile, win32con.LOCKFILE_EXCLUSIVE_LOCK,
                                 0, 0x7fffffff, __overlapped)
        except pywintypes.error, e:
            # err 120 is unimplemented call, happens on win9x:
            if e.args[0] != 120:
                raise e

    def unlock(file):
        try:
            hfile = win32file._get_osfhandle(file.fileno())
            win32file.UnlockFileEx(hfile, 0, 0x7fffffff, __overlapped)
        except pywintypes.error, e:
            # err 120 is unimplemented call, happens on win9x:
            if e.args[0] != 120:
                raise e

elif os.name == 'posix':
    import fcntl
    
    def lock(file):
        fcntl.flock(file.fileno(), fcntl.LOCK_EX)

    def unlock(file):
        fcntl.flock(file.fileno(), fcntl.LOCK_UN)

else:
    def lock(file): pass
    def unlock(file): pass
