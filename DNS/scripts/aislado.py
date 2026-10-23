#!/usr/bin/env python3
"""Crea sólo dos namespaces nuevos en la VM, captura y limpia sus recursos."""
import hashlib
import os
import signal
import subprocess
import time
from registrar import ROOT, run

CLIENT, SERVER = 'dns-client-20260920', 'dns-server-20260920'
created = []
processes = []

def checked(args):
    if run(args): raise RuntimeError('Fallo: ' + str(args))

try:
    for name in (CLIENT,SERVER):
        checked(['ip','netns','add',name])
        created.append(name)
    checked(['ip','-n',CLIENT,'link','add','dns-cli','type','veth','peer','name','dns-rx','netns',SERVER])
    for name,dev,address in [(CLIENT,'dns-cli','10.203.0.1/30'),(SERVER,'dns-rx','10.203.0.2/30')]:
        checked(['ip','-n',name,'addr','add',address,'dev',dev])
        checked(['ip','-n',name,'link','set','lo','up'])
        checked(['ip','-n',name,'link','set',dev,'up'])
        checked(['ip','-n',name,'-br','addr'])
        checked(['ip','-n',name,'route'])
    time.sleep(0.5)
    for name in (CLIENT, SERVER):
        checked(['ip','-n',name,'addr'])
        checked(['ip','-n',name,'route'])
    (ROOT/'resultados/receptor_listo').unlink(missing_ok=True)
    capture_cmd = ['ip','netns','exec',CLIENT,'dumpcap','-i','dns-cli','-p','-P','-w','-']
    print('CAPTURA:', ' '.join(capture_cmd),flush=True)
    with (ROOT/'resultados/dumpcap_exfil.txt').open('w') as out, (ROOT/'capturas/dns_exfiltration.pcap').open('wb') as pcap:
        capture = subprocess.Popen(capture_cmd,stdout=pcap,stderr=out)
        processes.append(capture)
        receiver = subprocess.Popen(['ip','netns','exec',SERVER,'python3',str(ROOT/'scripts/dns_demo.py'),'receiver'])
        processes.append(receiver)
        for _ in range(50):
            if (ROOT/'resultados/receptor_listo').exists(): break
            time.sleep(0.1)
        else: raise RuntimeError('Receptor no disponible')
        time.sleep(0.5)
        if capture.poll() is not None:
            raise RuntimeError('Captura no iniciada; no se enviaran datos')
        checked(['ip','netns','exec',CLIENT,'python3',str(ROOT/'scripts/dns_demo.py'),'sender'])
        if receiver.wait(timeout=5): raise RuntimeError('Fallo receptor')
        time.sleep(0.5)
        capture.send_signal(signal.SIGINT)
        if capture.wait(timeout=5): raise RuntimeError('Fallo al finalizar dumpcap')
    assert (ROOT/'capturas/dns_exfiltration.pcap').stat().st_size > 24
    original = (ROOT/'resultados/dns_demo.txt').read_bytes()
    received = (ROOT/'resultados/dns_demo_recibido.txt').read_bytes()
    assert original == received
    print('VERIFICACION: archivos identicos,', len(original), 'bytes; SHA256',hashlib.sha256(original).hexdigest(),flush=True)
    print((ROOT/'resultados/dumpcap_exfil.txt').read_text(),flush=True)
finally:
    for process in processes:
        if process.poll() is None:
            process.terminate()
            process.wait(timeout=5)
    for name in reversed(created): run(['ip','netns','del',name])
    run(['ip','netns','list'])
    for directory in ('capturas','resultados'):
        for path in (ROOT/directory).iterdir():
            if path.is_file(): os.chown(path,1002,1002)
