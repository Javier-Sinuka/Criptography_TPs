#!/usr/bin/env python3
"""Muestra resultados verificables para su inspección en una terminal real."""
import hashlib
import json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
results=ROOT/'resultados'
origin=results/'vm' if (results/'vm').is_dir() else results
files=[origin/'dns_demo.txt',origin/'dns_demo_recibido.txt',results/'dns_demo_desde_pcap.txt']
data=[f.read_bytes() for f in files]
assert data[0]==data[1]==data[2]
print('LABORATORIO DNS - VERIFICACION SOBRE ARCHIVOS Y PCAP\n')
for f,b in zip(files,data):
    print(f.name, ':',len(b),'bytes')
    print('SHA256:',hashlib.sha256(b).hexdigest())
print('\nComparacion byte a byte: IGUALES los tres archivos\n')
print('Primeras cuatro lineas del archivo sintetico:')
print('\n'.join(data[0].decode().splitlines()[:4]))
summaries=json.loads((results/'analisis.json').read_text())
for stem,s in summaries.items():
    print('\n'+stem+'.pcap')
    print('Tramas:',s['frames'],'Consultas:',s['dns_queries'],'Respuestas:',s['dns_responses'])
    print('FQDN unicos:',s['unique_fqdns'],'Candidatas:',s['candidate_queries'],'Alertas:',len(s['alerts']))
    print('Entropia media:',round(s['longest_label_entropy_mean'],4),'bits/caracter')
    print('Intervalo medio:',round(s['interarrival_mean_s'],6),'segundos')
    for a in s['alerts']:
        print('ALERTA:',a['source'],a['suffix'],a['unique_candidates'],'consultas candidatas distintas')
