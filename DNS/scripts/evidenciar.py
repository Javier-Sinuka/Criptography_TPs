#!/usr/bin/env python3
"""Obtiene screenshots de la VM; no dibuja ni modifica ninguna imagen."""
import time
from vm import guest, VM
from registrar import ROOT, run
GUI='python3 /home/analyst/dns-lab/scripts/gui_vm.py '

def shot(name):
    time.sleep(0.5)
    run(['VBoxManage','controlvm',VM,'screenshotpng',str(ROOT/'evidencias'/name)])

def sequence(keys):
    guest(GUI+'sequence '+keys)

for name,keys in [
    ('07_ipv4_query.png','Control_L+Left Home Down Down Right'),
    ('08_udp_query.png','Control_L+Left Home Down Down Down Right'),
    ('09_dns_query.png','Control_L+Left End Shift_L+Right'),
]:
    sequence(keys);shot(name)
sequence('Control_L+g 2 Return')
guest(GUI+'click 250 270')
sequence('Control_L+Left End Shift_L+Right');shot('10_dns_respuesta_cisco.png')
sequence('Control_L+g 5 Return')
guest(GUI+'click 250 270')
sequence('Control_L+Left Home Down Down Down Right');shot('12_google_consulta_udp.png')
sequence('Control_L+g 6 Return')
guest(GUI+'click 250 270')
sequence('Control_L+Left End Shift_L+Right');shot('13_google_respuesta.png')
guest(GUI+'launch wireshark --fullscreen -n -r /home/analyst/dns-lab/capturas/dns_exfiltration.pcap -Y dns -g 6')
time.sleep(2)
guest(GUI+'click 250 270')
sequence('Control_L+Left End Shift_L+Right');shot('14_exfiltracion_dns.png')
