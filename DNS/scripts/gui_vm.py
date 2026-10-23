#!/usr/bin/env python3
"""Control de ventanas reales de la VM mediante X11; las PNG las toma VirtualBox."""
import ctypes as C
import os
from pathlib import Path
import subprocess
import sys
import time

os.environ['DISPLAY']=':0'
os.environ['XAUTHORITY']='/home/analyst/.Xauthority'
mode,*args=sys.argv[1:]
if mode=='launch':
    with open('/home/analyst/dns-lab/resultados/gui.log','ab') as f:
        process=subprocess.Popen(args,stdin=subprocess.DEVNULL,stdout=f,stderr=f,start_new_session=True)
    print('Ventana iniciada, PID',process.pid)
    raise SystemExit
x=C.CDLL('libX11.so.6'); xt=C.CDLL('libXtst.so.6')
x.XOpenDisplay.argtypes=[C.c_char_p];x.XOpenDisplay.restype=C.c_void_p
d=x.XOpenDisplay(b':0')
assert d,'No se pudo abrir el display'
x.XFlush.argtypes=[C.c_void_p]
x.XStringToKeysym.argtypes=[C.c_char_p];x.XStringToKeysym.restype=C.c_ulong
x.XKeysymToKeycode.argtypes=[C.c_void_p,C.c_ulong];x.XKeysymToKeycode.restype=C.c_uint
xt.XTestFakeKeyEvent.argtypes=[C.c_void_p,C.c_uint,C.c_int,C.c_ulong]
xt.XTestFakeButtonEvent.argtypes=[C.c_void_p,C.c_uint,C.c_int,C.c_ulong]
xt.XTestFakeMotionEvent.argtypes=[C.c_void_p,C.c_int,C.c_int,C.c_int,C.c_ulong]
def keys(names):
    codes=[x.XKeysymToKeycode(d,x.XStringToKeysym(a.encode())) for a in names]
    for code in codes:xt.XTestFakeKeyEvent(d,code,1,0)
    for code in reversed(codes):xt.XTestFakeKeyEvent(d,code,0,0)
    x.XFlush(d)
    time.sleep(0.12)
if mode=='keys':
    keys(args)
elif mode=='sequence':
    for combo in args: keys(combo.split('+'))
elif mode=='click':
    px,py=map(int,args[:2]);button=int(args[2]) if len(args)>2 else 1
    xt.XTestFakeMotionEvent(d,-1,px,py,0)
    xt.XTestFakeButtonEvent(d,button,1,0);xt.XTestFakeButtonEvent(d,button,0,0)
elif mode=='drag':
    a,b,c,e=map(int,args)
    xt.XTestFakeMotionEvent(d,-1,a,b,0)
    xt.XTestFakeButtonEvent(d,1,1,0)
    xt.XTestFakeMotionEvent(d,-1,c,e,100)
    xt.XTestFakeButtonEvent(d,1,0,100)
x.XFlush(d)
time.sleep(0.3)
