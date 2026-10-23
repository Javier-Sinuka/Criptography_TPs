#!/bin/sh
cd /work
export TZ=America/Argentina/Cordoba
printf '$ tcpdump -nn -r evidencias/captura_http.pcap\n\n'
tcpdump -nn -r evidencias/captura_http.pcap
printf '\n$ cat evidencias/captura.log\n\n'
cat evidencias/captura.log
printf '\n'
exec sleep 600
