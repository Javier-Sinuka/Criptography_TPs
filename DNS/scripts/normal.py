#!/usr/bin/env python3
"""Captura real en la interfaz NAT de la VM Cisco, con consultas ordinarias."""
import datetime
import signal
import subprocess
import time
from registrar import ROOT, run

for args in (['ip','addr','show','enp0s3'], ['ip','route'], ['ip','neigh'],
             ['cat','/etc/resolv.conf'], ['resolvectl','status'],
             ['resolvectl','flush-caches'], ['resolvectl','statistics']):
    run(args)
cmd = ['dumpcap','-i','enp0s3','-p','-P','-w',str(ROOT/'capturas/normal_dns.pcap')]
print('CAPTURA:', ' '.join(cmd), flush=True)
with (ROOT/'resultados/dumpcap_normal.txt').open('w') as log:
    capture = subprocess.Popen(cmd, stdout=log, stderr=log)
    try:
        time.sleep(1)
        if capture.poll() is not None:
            raise RuntimeError('dumpcap no pudo iniciar')
        script = 'server 10.0.2.3\nwww.cisco.com\nexit\n'
        result = subprocess.run(['nslookup'], input=script, text=True,
                                stdout=subprocess.PIPE, stderr=subprocess.STDOUT, timeout=25)
        print('=== NSLOOKUP INTERACTIVO ===\n' + script + result.stdout, flush=True)
        (ROOT/'resultados/nslookup_cisco.txt').write_text(result.stdout)
        for name, kind in [('www.google.com','A'), ('www.google.com','AAAA'),
                           ('example.com','A'), ('example.com','AAAA'),
                           ('www.iana.org','A'), ('www.iana.org','AAAA'),
                           ('www.cisco.com','A'), ('www.google.com','A')]:
            time.sleep(0.4)
            run(['dig','@10.0.2.3',name,kind,'+noedns','+time=3','+tries=1'])
        run(['ip','neigh'])
        time.sleep(1)
    finally:
        capture.send_signal(signal.SIGINT)
        capture.wait(timeout=10)
print((ROOT/'resultados/dumpcap_normal.txt').read_text())
