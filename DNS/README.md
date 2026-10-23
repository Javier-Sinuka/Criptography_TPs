# Laboratorio DNS

Informe: **DNS.tex / DNS.pdf**. Autor: Javier Siñuka. Ejecución: 20/09/2026.
Formato de `Firma_Digital.tex`: article, 11 pt, A4, Latin Modern, margen 2,5 cm,
título con `maketitle`, mismas convenciones de secciones y figuras.

## Qué se ejecutó

- VM existente `Cybersecurity LabVM Worksation 20230210`, perfil `analyst`
  para CyberOps Associate, Ubuntu 22.04.1, Wireshark 3.6.7, adaptador NAT.
- Vaciado de la caché de systemd-resolved y consultas normales con nslookup/dig.
- Captura real con dumpcap y análisis gráfico con Wireshark.
- Dos namespaces dentro de la VM, unidos por veth y sin ruta predeterminada:
  `10.203.0.1/30` → `10.203.0.2:53`.
- Transferencia de 1072 bytes ficticios en 34 consultas A y 34 respuestas.
- Reconstrucción desde el receptor y, por separado, desde el PCAP.
- Detección Python: 33 candidatas, una alerta; ninguna en las 10 consultas normales.
- Contraste con rawshark: 1099 valores coincidentes.

No se instaló software. No se abrió Google en el navegador: se utilizó dig como
alternativa explícita. El adaptador original era NAT, no puente. Se usaron dos
namespaces dentro de una VM, no dos VM independientes. No se ejecutó DNSteal,
Zeek ni Suricata; estos últimos se describen como alternativas. Los datos de la
transferencia se generaron en el script, sin leer documentos personales.

## Archivos principales

| Ruta | Contenido |
|---|---|
| `DNS.tex`, `DNS.pdf` | Informe y versión compilada |
| `capturas/normal_dns.pcap` | 22 tramas: 10 consultas, 10 respuestas, 2 ARP |
| `capturas/dns_exfiltration.pcap` | 83 tramas: 34 consultas, 34 respuestas, 15 auxiliares |
| `evidencias/` | Capturas PNG auténticas del framebuffer de VirtualBox |
| `resultados/comandos.txt` | Comandos del host, stdout/stderr, fechas y códigos de retorno |
| `resultados/vm/` | Salidas del laboratorio dentro de la VM y archivo ficticio |
| `resultados/vm/intento_01/` | Primer intento: transferencia correcta pero captura fallida |
| `resultados/*_paquetes.json`, `*.csv` | Campos leídos del PCAP |
| `resultados/analisis.json` | Estadísticas y tramas candidatas |
| `resultados/rawshark_*.txt` | Campos producidos por Wireshark, usados como contraste |
| `resultados/dns_demo_desde_pcap.txt` | Archivo recuperado sólo de preguntas del PCAP |
| `resultados/SHA256SUMS` | Huellas de los entregables |
| `GUIA_DEFENSA.md` | Explicación y veinte preguntas de defensa |
| `CHECKLIST.md` | Cobertura y adaptaciones de las consignas |

Los DOCX originales permanecen en la carpeta. Su texto, incluidas las tres
tablas del segundo documento, se extrajo en `resultados/`. La imagen de la
consigna general mencionada en el texto del usuario no estaba en la carpeta.

## Comprobar el resultado sin generar tráfico

Desde esta carpeta, con Python 3 y su biblioteca estándar:

```bash
sha256sum -c resultados/SHA256SUMS
python3 scripts/analizar.py
python3 scripts/contrastar_rawshark.py
python3 scripts/resumen.py
```

El primer comando verifica los entregables originales. El analizador vuelve a
escribir los JSON/CSV de forma determinista a partir de los PCAP; no abre sockets
ni transmite paquetes. El contraste comprueba direcciones, puertos, longitudes
UDP, flags, IDs, nombres y respuestas A/AAAA/CNAME contra rawshark.

La versión entregada del lector procesa PCAP clásico Ethernet/IPv4/UDP/DNS sin
fragmentación. No es un lector general de PCAPNG ni de todos los protocolos.

Abrir los PCAP en Wireshark y aplicar:

```text
dns
udp.port == 53
dns.qry.name == "www.cisco.com"
frame.number == 1 || frame.number == 2
frame.number == 5 || frame.number == 6
dns.flags.response == 0 && len(dns.qry.name) > 60
```

Las parejas 1/2 (Cisco) y 5/6 (Google) se refieren al PCAP normal. La primera
pareja DNS de la demo es 6/7. El filtro de longitud selecciona 33 consultas de
la demo; su último bloque (trama 82) tiene un nombre más corto.

`rawshark -R` imprime también las tramas no coincidentes y una marca final de
filtro (`1` coincide, `0` no coincide). No contar todas las líneas como alertas.
Además, esta versión de rawshark se alimentó por stdin: abrir directamente el
archivo con `-r ruta` falló; se corrigió a `cat ruta | rawshark -r - -s ...`.

## Compilar el informe

```bash
python3 scripts/tablas.py
latexmk -pdf -interaction=nonstopmode -halt-on-error -outdir=resultados/latex DNS.tex
cp resultados/latex/DNS.pdf DNS.pdf
```

Se necesitan los paquetes LaTeX que figuran en el preámbulo; ya estaban
disponibles en el equipo. Las figuras se leen desde `evidencias/` y las tablas
desde `resultados/`. La entrega solicitada es LaTeX/PDF, no DOCX.

## Repetir la ejecución de red

Para preservar las evidencias originales, usar una carpeta nueva **dentro de
la VM Cisco**. Copiar allí `scripts/registrar.py`, `normal.py`, `aislado.py` y
`dns_demo.py`, conservando la subcarpeta `scripts/`. Crear al mismo nivel
`capturas/` y `resultados/`.

Antes de ejecutar, comprobar con `ip addr`, `ip route` y `resolvectl status`
que `enp0s3` y el DNS `10.0.2.3` siguen correspondiendo a esa VM. `normal.py`
usa estos valores observados. El host físico tiene una configuración distinta.

```bash
# En la nueva carpeta de laboratorio, dentro de la VM:
python3 scripts/normal.py > resultados/ejecucion_normal.txt 2>&1
sudo python3 scripts/aislado.py > resultados/ejecucion_aislada.txt 2>&1
```

La captura normal necesita las capacidades que ya posee dumpcap en esa VM.
La segunda orden requiere privilegios para crear namespaces. El programa
crea sólo los dos namespaces con nombres fijos del laboratorio y los elimina
al terminar. Si ya existen, se detiene sin reemplazarlos. La cuenta `analyst`
de esta imagen tiene UID/GID 1002; el coordinador devuelve la propiedad de
sus archivos a esa cuenta. No trasladar esa suposición a otro sistema.

Las IP `10.203.0.1` y `10.203.0.2` se asignan efectivamente al par virtual.
El emisor usa únicamente el archivo sintético de su código y contacta sólo
al receptor fijo; no depende del DNS público. No hay rutas predeterminadas.
Los puertos efímeros, MAC de veth, IDs, timestamps y respuestas públicas
cambiarán en otra ejecución. No reemplazar los datos del informe con valores
de una nueva corrida sin regenerar también tablas, métricas y evidencia.

`vm.py` automatiza VirtualBox usando la cuenta pública de la imagen educativa,
no una credencial personal. `gui_vm.py` envía eventos reales de teclado y ratón
a X11. `evidenciar.py` documenta una secuencia de vistas; depende de la geometría
y del estado inicial de Wireshark y no es una reconstrucción artificial de la UI.
La sesión gráfica de la VM sigue disponible para revisar los resultados.

## Incidencia de captura

En el primer intento aislado, dumpcap no pudo abrir el archivo de salida
(`Permission denied`), aunque el archivo ficticio llegó. Se conservó ese
intento, se cambió a salida binaria estándar (`-w -`) abierta por el coordinador
y se añadió comprobación del proceso de captura antes de enviar. El segundo
intento produjo el PCAP definitivo sin descartes. No se afirma una causa
específica del fallo de permisos que no se haya demostrado.

## Alcance de la detección

La regla exige etiqueta larga, entropía y alfabeto Base32, más cinco nombres
candidatos distintos por origen/sufijo en toda la captura. Agrupa por las dos
últimas etiquetas; una herramienta general necesita Public Suffix List y
ventanas temporales. No inspecciona DoH/DoT cifrado ni detecta todas las
codificaciones posibles. La ausencia de alertas en diez consultas normales
no constituye una medida de falsos positivos en producción.
