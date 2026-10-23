#!/usr/bin/env python3
"""Lee PCAP Ethernet/IPv4/UDP/DNS reales y aplica una heurística explicable.

No genera paquetes. Admite PCAP clásico (no PCAPNG), sin IPv4 fragmentado.
Los campos se contrastan aparte con rawshark/Wireshark.
"""
import base64
from collections import Counter, defaultdict
import csv
import hashlib
import json
import math
from pathlib import Path
import re
import socket
import statistics
import struct

ROOT = Path(__file__).resolve().parents[1]

def name_at(data, offset, visited=None):
    visited = set() if visited is None else visited
    labels = []
    while True:
        if offset in visited: raise ValueError('Ciclo DNS')
        visited.add(offset)
        size = data[offset]
        if size & 0xc0 == 0xc0:
            target = ((size & 63)<<8) | data[offset+1]
            suffix, _ = name_at(data,target,visited)
            labels.append(suffix)
            return '.'.join(labels),offset+2
        offset += 1
        if not size: return '.'.join(labels),offset
        if size > 63: raise ValueError('Etiqueta invalida')
        labels.append(data[offset:offset+size].decode('ascii'))
        offset += size

def read_pcap(path):
    records = []
    with path.open('rb') as f:
        header = f.read(24)
        endian, scale = {b'\xd4\xc3\xb2\xa1':('<',1e6),b'\xa1\xb2\xc3\xd4':('>',1e6),
                         b'\x4d\x3c\xb2\xa1':('<',1e9),b'\xa1\xb2\x3c\x4d':('>',1e9)}[header[:4]]
        assert struct.unpack(endian+'I',header[20:24])[0] == 1
        number = 0
        while raw := f.read(16):
            sec,frac,caplen,wirelen = struct.unpack(endian+'IIII',raw)
            data = f.read(caplen)
            assert len(data) == caplen
            number += 1
            r = {'frame':number,'time':sec+frac/scale,'frame_len':wirelen,'cap_len':caplen,
                 'eth_dst':data[:6].hex(':'),'eth_src':data[6:12].hex(':'),
                 'eth_type':struct.unpack('!H',data[12:14])[0]}
            records.append(r)
            if r['eth_type'] != 0x800: continue
            ip = data[14:]
            ihl = (ip[0] & 15)*4
            r.update(ip_src=socket.inet_ntoa(ip[12:16]),ip_dst=socket.inet_ntoa(ip[16:20]),
                     ip_len=struct.unpack('!H',ip[2:4])[0],ip_header_len=ihl,ip_ttl=ip[8],ip_proto=ip[9])
            if ip[9] != 17: continue
            assert struct.unpack('!H',ip[6:8])[0] & 0x3fff == 0, 'Fragmentacion no admitida'
            sport,dport,length,checksum = struct.unpack('!HHHH',ip[ihl:ihl+8])
            r.update(udp_src=sport,udp_dst=dport,udp_len=length,udp_checksum=f'0x{checksum:04x}')
            if 53 not in (sport,dport): continue
            dns = ip[ihl+8:ihl+length]
            txid,flags,qd,an,ns,ar = struct.unpack('!HHHHHH',dns[:12])
            r.update(dns_id=f'0x{txid:04x}',dns_flags=f'0x{flags:04x}',qr=bool(flags&0x8000),
                     rd=bool(flags&0x100),ra=bool(flags&0x80),aa=bool(flags&0x400),tc=bool(flags&0x200),
                     rcode=flags&15,qd=qd,an=an,ns=ns,ar=ar,dns_len=len(dns))
            pos = 12
            questions=[]
            for _ in range(qd):
                name,pos = name_at(dns,pos)
                kind,cls = struct.unpack('!HH',dns[pos:pos+4]); pos += 4
                questions.append({'name':name,'type':kind,'class':cls})
            r['questions']=questions
            if questions: r.update(qname=questions[0]['name'],qtype=questions[0]['type'])
            rr=[]
            for index in range(an+ns+ar):
                name,pos = name_at(dns,pos)
                kind,cls,ttl,rdlen = struct.unpack('!HHIH',dns[pos:pos+10]); pos += 10
                value=dns[pos:pos+rdlen]
                if kind==1: value=socket.inet_ntoa(value)
                elif kind==28: value=socket.inet_ntop(socket.AF_INET6,value)
                elif kind in (2,5,12): value=name_at(dns,pos)[0]
                else: value=value.hex()
                rr.append({'section':'answer' if index<an else ('authority' if index<an+ns else 'additional'),
                           'name':name,'type':kind,'class':cls,'ttl':ttl,'value':value})
                pos += rdlen
            r['records']=rr
    return records

def entropy(label):
    counts=Counter(label.lower())
    return -sum((n/len(label))*math.log2(n/len(label)) for n in counts.values()) if label else 0

def analyze(records):
    queries=[r for r in records if 'qname' in r and not r['qr']]
    responses=[r for r in records if 'qname' in r and r['qr']]
    groups=defaultdict(list)
    alerts=[]
    for r in queries:
        labels=r['qname'].split('.')
        longest=max(labels,key=len)
        r['fqdn_length']=len(r['qname'])
        r['max_label_length']=len(longest)
        r['longest_label_entropy']=entropy(longest)
        # Sufijo de dos etiquetas suficiente para estos dominios concretos.
        # Una implantacion general necesita Public Suffix List.
        group=(r['ip_src'],'.'.join(labels[-2:]))
        groups[group].append(r)
        r['candidate']=(len(longest)>=40 and entropy(longest)>=3.5
                        and re.fullmatch('[a-z2-7]+',longest.lower()) is not None)
    for (source,suffix),qs in groups.items():
        suspicious=[r for r in qs if r['candidate']]
        unique=len({r['qname'] for r in suspicious})
        if unique>=5:
            alerts.append({'source':source,'suffix':suffix,'candidate_queries':len(suspicious),
                           'unique_candidates':unique,'frames':[r['frame'] for r in suspicious]})
    intervals=[b['time']-a['time'] for a,b in zip(queries,queries[1:])]
    span=queries[-1]['time']-queries[0]['time'] if len(queries)>1 else 0
    summary={'frames':len(records),'dns_queries':len(queries),'dns_responses':len(responses),
             'other_frames':[r['frame'] for r in records if 'qname' not in r],
             'unique_fqdns':len({r['qname'] for r in queries}),
             'fqdn_length_min':min(r['fqdn_length'] for r in queries),
             'fqdn_length_max':max(r['fqdn_length'] for r in queries),
             'max_label_length':max(r['max_label_length'] for r in queries),
             'longest_label_entropy_mean':statistics.mean(r['longest_label_entropy'] for r in queries),
             'query_frame_len_min':min(r['frame_len'] for r in queries),
             'query_frame_len_max':max(r['frame_len'] for r in queries),
             'query_bytes_total':sum(r['frame_len'] for r in queries),
             'dns_frame_bytes_total':sum(r['frame_len'] for r in queries+responses),
             'query_types':dict(Counter(str(r['qtype']) for r in queries)),
             'nxdomain_responses':sum(r['rcode']==3 for r in responses),
             'query_span_s':span,'query_rate_per_s':(len(queries)-1)/span if span else None,
             'interarrival_mean_s':statistics.mean(intervals) if intervals else None,
             'interarrival_std_s':statistics.pstdev(intervals) if intervals else None,
             'candidate_queries':sum(r['candidate'] for r in queries),'alerts':alerts}
    return summary

def verify_pairs(records):
    for q in [r for r in records if 'qname' in r and not r['qr']]:
        matching=[r for r in records if r.get('qr') and r['dns_id']==q['dns_id']
                  and r['qname']==q['qname'] and r['qtype']==q['qtype']
                  and (r['ip_src'],r['ip_dst'],r['udp_src'],r['udp_dst']) ==
                      (q['ip_dst'],q['ip_src'],q['udp_dst'],q['udp_src'])]
        assert len(matching)==1,(q['frame'],'pareja ambigua o ausente')
        q['response_frame']=matching[0]['frame']
        q['rtt_ms']=(matching[0]['time']-q['time'])*1000

def main():
    summaries={}
    for stem in ('normal_dns','dns_exfiltration'):
        records=read_pcap(ROOT/'capturas'/f'{stem}.pcap')
        verify_pairs(records)
        summaries[stem]=analyze(records)
        (ROOT/'resultados'/f'{stem}_paquetes.json').write_text(json.dumps(records,indent=2))
        fields=['frame','time','frame_len','eth_src','eth_dst','ip_src','ip_dst','udp_src','udp_dst',
                'udp_len','dns_id','dns_flags','qname','qtype','qr','fqdn_length','max_label_length',
                'longest_label_entropy','candidate','response_frame','rtt_ms']
        with (ROOT/'resultados'/f'{stem}.csv').open('w') as f:
            writer=csv.DictWriter(f,fields,extrasaction='ignore');writer.writeheader();writer.writerows(records)
        if stem=='dns_exfiltration':
            chunks={}
            for r in records:
                if 'qname' not in r or r['qr']: continue
                labels=r['qname'].split('.')
                index=int(labels[0][1:]); encoded=labels[2].upper()
                chunks[index]=base64.b32decode(encoded+'='*((-len(encoded))%8))
            restored=b''.join(chunks[i] for i in range(len(chunks)))
            (ROOT/'resultados/dns_demo_desde_pcap.txt').write_bytes(restored)
            assert restored==(ROOT/'resultados/vm/dns_demo.txt').read_bytes()
            assert restored==(ROOT/'resultados/vm/dns_demo_recibido.txt').read_bytes()
            summaries[stem]['reconstructed_bytes']=len(restored)
            summaries[stem]['sha256']=hashlib.sha256(restored).hexdigest()
    output=json.dumps(summaries,indent=2)
    (ROOT/'resultados/analisis.json').write_text(output+'\n')
    print(output)

if __name__=='__main__': main()
