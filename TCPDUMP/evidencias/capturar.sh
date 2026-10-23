#!/bin/sh
set -eu
cd /work
export TZ=America/Argentina/Cordoba
python3 evidencias/servidor.py > evidencias/servidor.log 2>&1 &
server_pid=$!
tcpdump -i lo -nn -s 0 -U -w evidencias/captura_http.pcap 'tcp port 8080' > evidencias/captura.log 2>&1 &
capture_pid=$!
sleep 1
curl --noproxy '*' -v http://127.0.0.1:8080/ -o evidencias/respuesta.txt 2> evidencias/curl.log
sleep 1
kill -INT "$capture_pid"
wait "$capture_pid"
kill "$server_pid"
tcpdump -nn -tttt -r evidencias/captura_http.pcap > evidencias/tcpdump.txt 2>&1
tshark -r evidencias/captura_http.pcap > evidencias/wireshark.txt 2> /tmp/tshark.log
