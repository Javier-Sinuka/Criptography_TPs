# Evidencias del análisis

- `SQL_Lab.sha256`: SHA-256 del PCAP original, que no fue modificado.
- `paquetes.tsv`: número, tiempo relativo, IP origen, IP destino, flujo TCP y URI HTTP.
- `flujo_http_1.txt` a `flujo_http_6.txt`: flujos extraídos mediante TShark con descompresión HTTP.
- `verificar_hash.py` y `verificacion_hash.txt`: comprobación local de MD5, sin salto de línea.
- `../img/`: capturas reales de Wireshark, terminal y Firefox/CrackStation; no son imágenes generadas ni recreaciones.

El análisis se realizó con Wireshark/TShark en Linux local, no en la VM CyberOps.
Se usó una pantalla virtual Xvfb para capturar exclusivamente las aplicaciones de esta práctica.
CrackStation devolvió una coincidencia exacta: tipo md5, resultado charley.

Comandos para reproducir desde la carpeta Ataque_DB (con TShark instalado):

```sh
sha256sum -c evidencias/SQL_Lab.sha256
tshark -r SQL_Lab.pcap -q -z follow,http,ascii,6
python3 evidencias/verificar_hash.py
pdflatex -interaction=nonstopmode -halt-on-error Ataque_DB.tex
pdflatex -interaction=nonstopmode -halt-on-error Ataque_DB.tex
```

Correspondencia: flujo 1 / solicitud 13; flujo 2 / solicitud 16;
flujo 3 / solicitud 19; flujo 4 / solicitud 22;
flujo 5 / solicitud 25; flujo 6 / solicitud 28.
