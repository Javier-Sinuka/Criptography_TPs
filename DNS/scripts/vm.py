#!/usr/bin/env python3
"""Control reproducible de la VM Cisco existente; usa su cuenta pública de laboratorio."""
import sys
from registrar import run, ROOT
VM = 'Cybersecurity LabVM Worksation 20230210'
AUTH = ['--username', 'analyst', '--password', 'cyberops']
def guest(command, timeout=60):
    return run(['VBoxManage','guestcontrol',VM,'run','--exe','/bin/bash',*AUTH,
                '--wait-stdout','--wait-stderr','--','-lc',command], timeout)
if __name__ == '__main__':
    mode, *args = sys.argv[1:]
    if mode == 'run': code = guest(args[0], 300)
    elif mode in ('copyto','copyfrom'):
        code = run(['VBoxManage','guestcontrol',VM,mode,*AUTH,*args])
    elif mode == 'screenshot':
        code = run(['VBoxManage','controlvm',VM,'screenshotpng',str(ROOT/'evidencias'/args[0])])
    elif mode == 'keys':
        code = run(['VBoxManage','controlvm',VM,'keyboardputscancode',*args])
    elif mode == 'text':
        code = run(['VBoxManage','controlvm',VM,'keyboardputstring',args[0]])
    else: raise SystemExit('Modo desconocido')
    sys.exit(code)
