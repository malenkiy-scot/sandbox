"""
'Abstract' Process Controller Class for running external programs
"""

__author__ = 'Aron Matskin'


import subprocess
import time
import logging
import os
import os.path

SLEEP_TIME = 0.5


def get_full_path(*dirlist):
    """
        Join dirlist elements into a normalized path

        @param *dirlist [in] - ordered list of paths
        @return - normalized path built from dirlist

        E.g.:
            dirlist = ['C:/foo/bar/,'..','.','foobar.txt']
            Return: 'C:/foo/foobar.txt'


    """
    path = ""
    for filename in dirlist:
        path = os.path.join(path, filename)
    return os.path.normpath(path)


class Controller(object):
    def __init__(self, exe_name, exe='', search_path=['.'], cwd=None):
        """
            @param exe_name [in] - executable name, can be a relative path against search_path
            @param exe [in] - full path to the executable
            @param search_path [in] - list of directories (as strings) where to search for the executable,
                directories in PATH environment variable are automatically appended

        """

        search_path.extend([path for path in os.environ['PATH'].split(';')])
        self.exe_name = exe_name
        self.exe = exe if exe else self.find_executable(search_path)
        self.arg_list = []
        self.process = None
        self._process_return = None
        self.cwd = cwd

        if self.exe:
            self.arg_list.append(self.exe)
            logging.debug('Found %s executable in: %s', exe_name, self.exe)
        else:
            logging.warning('Search path: %s', str(search_path))
            raise UserWarning('Executable %s not found' % exe_name)

    def find_executable(self, search_path):
        """
            Find the executable

            @param search_path [in] - directory list (as strings) where to look for the executable
            @return - full path of the executable
        """

        exe = None
        cwd = os.getcwd()

        for where in search_path:
            try:
                files = os.listdir(where)
            except OSError:
                continue
            if self.exe_name in files:
                exe = get_full_path(cwd, where, self.exe_name)
                break

        os.chdir(cwd)
        return exe

    def cleanup(self):
        """
            To be implemented by subclasses if needed
        """
        pass

    def start(self, *args):
        """
        Start the process

        @param *args [in] - list of additional parameters
        """
        if args:
            self.arg_list.extend(args)
        self.process = subprocess.Popen(self.arg_list, stdout=subprocess.PIPE, stderr=subprocess.PIPE, cwd=self.cwd)
        logging.debug("Opened process %s with args %s" % (self.exe, self.arg_list))

    def wait(self):
        """
        Wait for the process to finish

        @return - (returncode, stdoutdata, stderrdata) tuple
        """
        try:
            out, err = self.process.communicate()
        except OSError:
            logging.exception('')
        finally:
            self.cleanup()

        self._process_return = (self.process.returncode, out, err)
        logging.debug("Process %s std_out:\n %s " % (self.exe, out))
        logging.debug("Process %s std_err:\n %s" % (self.exe, err))

        return self._process_return

    def stop(self):
        """Force process to stop"""
        try:
            self.process.terminate()
            self.process.wait()
            time.sleep(SLEEP_TIME)
        except OSError as e:
            logging.debug('Ignoring exception %s', e)
        finally:
            self.cleanup()

        if self.is_alive():
            raise Exception('% did not terminate', self.exe)

    def is_alive(self):
        return self.process.poll() is None

    def is_dead(self):
        return self.process.poll() is not None
