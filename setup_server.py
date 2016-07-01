from distutils.core import setup
import py2exe, sys

if __name__ == '__main__':
    if len(sys.argv) < 2:
        sys.argv.append('py2exe')
    setup(
        options = {'py2exe': {'bundle_files': 1, 'compressed': True, 'excludes': ['Tkconstants', 'Tkinter'], 'dll_excludes': ['w9xpopen.exe']}},
        console = [{'script': "server.py"}],
        zipfile = None,
    )
    raw_input("Press any key to continue")
