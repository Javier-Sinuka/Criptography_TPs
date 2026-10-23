#!/usr/bin/env python3
"""Contraste independiente del lector PCAP con campos producidos por Wireshark."""
import json
from pathlib import Path
import re
from collections import defaultdict
ROOT=Path(__file__).resolve().parents[1]
fields=['frame','eth_src','eth_dst','ip_src','ip_dst','udp_src','udp_dst','udp_len',
        'dns_id','dns_flags','qname']
for stem in ('normal_dns','dns_exfiltration'):
    packets=json.loads((ROOT/'resultados'/f'{stem}_paquetes.json').read_text())
    raw=(ROOT/'resultados'/f'rawshark_{stem}.txt').read_text()
    compared=0
    for line in raw.splitlines()[1:]:
        if not line.strip():continue
        index=int(line.split()[0])
        p=packets[index-1]
        values=defaultdict(list)
        for field,value in re.findall(r'(\d+)="([^"]*)"',line):values[int(field)].append(value)
        for i,key in enumerate(fields):
            if i not in values:continue
            assert values[i]==[str(p[key])],(stem,index,key,values[i],p.get(key))
            compared+=1
        for i,kind in [(11,1),(12,28),(13,5)]:
            if i in values:
                assert values[i]==[r['value'] for r in p['records'] if r['type']==kind]
                compared+=len(values[i])
    print(stem,':',len(packets),'tramas;',compared,'valores coincidentes con rawshark')
