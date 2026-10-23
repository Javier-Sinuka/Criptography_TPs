#!/usr/bin/env python3
"""Genera tablas LaTeX exclusivamente a partir de los PCAP analizados."""
import json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
normal=json.loads((ROOT/'resultados/normal_dns_paquetes.json').read_text())
exfil=json.loads((ROOT/'resultados/dns_exfiltration_paquetes.json').read_text())
summary=json.loads((ROOT/'resultados/analisis.json').read_text())
def literal(value):
    return r'\texttt{'+str(value).replace('_',r'\_')+'}'
def table(headers,rows,cols):
    return '\n'.join([r'\begin{tabularx}{\textwidth}{'+cols+'}',r'\toprule',
                      ' & '.join(headers)+r' \\',r'\midrule',
                      *(' & '.join(row)+r' \\' for row in rows),r'\bottomrule',r'\end{tabularx}'])+'\n'
fields=[('Trama','frame'),('Longitud de trama (bytes)','frame_len'),('MAC origen','eth_src'),
        ('MAC destino','eth_dst'),('IPv4 origen','ip_src'),('IPv4 destino','ip_dst'),
        ('Puerto UDP origen','udp_src'),('Puerto UDP destino','udp_dst'),
        ('Longitud IPv4 (bytes)','ip_len'),('Longitud UDP (bytes)','udp_len'),
        ('Datos DNS (bytes)','dns_len'),('Checksum UDP observado','udp_checksum'),
        ('Transaction ID','dns_id'),('Flags DNS','dns_flags')]
for filename,records,a,b in [('tabla_cisco.tex',normal,1,2),('tabla_google.tex',normal,5,6),
                             ('tabla_exfil.tex',exfil,6,7)]:
    q,r=records[a-1],records[b-1]
    rows=[[label,literal(q[key]),literal(r[key])] for label,key in fields]
    (ROOT/'resultados'/filename).write_text(table(['Campo','Consulta','Respuesta'],rows,'Xll'))
rows=[]
for label,key in [('Tramas totales','frames'),('Consultas DNS','dns_queries'),
                  ('Respuestas DNS','dns_responses'),('FQDN distintos','unique_fqdns'),
                  ('Etiqueta más larga (caracteres)','max_label_length'),
                  ('Bytes de consultas (Ethernet incluido)','query_bytes_total'),
                  ('Bytes DNS, ambos sentidos (Ethernet incluido)','dns_frame_bytes_total'),
                  ('Respuestas NXDOMAIN','nxdomain_responses'),
                  ('Consultas candidatas de la heurística','candidate_queries')]:
    rows.append([label,str(summary['normal_dns'][key]),str(summary['dns_exfiltration'][key])])
for label,low,high in [('Longitud FQDN (caracteres)','fqdn_length_min','fqdn_length_max'),
                       ('Longitud de consulta (bytes de trama)','query_frame_len_min','query_frame_len_max')]:
    rows.append([label,*[str(s[low])+'--'+str(s[high]) for s in summary.values()]])
for label,key in [('Entropía media de etiqueta (bits/carácter)','longest_label_entropy_mean'),
                  ('Intervalo medio entre consultas (s)','interarrival_mean_s'),
                  ('Desvío poblacional del intervalo (s)','interarrival_std_s'),
                  ('Tasa entre primera y última consulta (s$^{-1}$)','query_rate_per_s')]:
    rows.append([label,*[f'{s[key]:.4f}' for s in summary.values()]])
(ROOT/'resultados/tabla_comparacion.tex').write_text(table(['Medida','Normal','Demostración'],rows,'Xrr'))
rows=[]
for p in normal:
    if 'qname' in p and not p['qr']:
        rows.append([str(p['frame'])+'/'+str(p['response_frame']),r'\nolinkurl{'+p['qname']+'}',
                     {1:'A',28:'AAAA'}[p['qtype']],p['dns_id'],f"{p['rtt_ms']:.3f}"])
(ROOT/'resultados/tabla_transacciones.tex').write_text(table(['Tramas','Nombre consultado','Tipo','ID','RTT (ms)'],rows,'lXlll'))
