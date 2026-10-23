# Guía para defender el laboratorio DNS

## Explicación inicial, en unos dos minutos

Usamos una VM Cisco que ya estaba instalada, con el perfil analyst de CyberOps.
Primero registramos su IP, MAC, gateway y DNS. Vaciamos la caché local, iniciamos
una captura y consultamos nombres con nslookup y dig. Abrimos ese PCAP en
Wireshark para relacionar lo que mostraban los comandos con los campos del
paquete. La VM usó NAT: dirección 10.0.2.15, gateway 10.0.2.2 y DNS 10.0.2.3.

Después creamos dos namespaces de red dentro de esa misma VM. Un par de
interfaces virtuales los unía, sin salida a Internet. El cliente generó un
archivo de 1072 bytes totalmente ficticios y lo dividió en 34 bloques. Codificó
cada bloque en Base32 y lo puso en el nombre de una consulta DNS tipo A. El
receptor leyó las preguntas y reconstruyó el archivo. Pudimos recuperarlo también
desde el PCAP, sin utilizar el archivo recibido por el servidor. Los tres
archivos resultaron iguales byte a byte y tuvieron el mismo SHA-256.

Para detectar la actividad medimos longitud de etiquetas, entropía, nombres
únicos, frecuencia y tamaños. La regla encontró 33 consultas sospechosas en
la demo y ninguna en las diez consultas normales. El último bloque era corto
y no superó el umbral. No hubo NXDOMAIN: todas las preguntas fueron contestadas
correctamente. Para mitigar este abuso hay que controlar quién puede resolver,
qué consultas se reenvían y qué proceso las origina, además de proteger los datos.

## Cómo explicar un paquete

| Capa | Qué representa | Ejemplo real, consulta Cisco, trama 1 |
|---|---|---|
| Ethernet II | Entrega en el enlace local | MAC 08:00:27:55:44:07 → 52:54:00:12:35:00 |
| IPv4 | Extremos de la comunicación IP | 10.0.2.15 → 10.0.2.3 |
| UDP | Aplicaciones identificadas por puertos | 41544 → 53; longitud 39 bytes |
| DNS | Pregunta de resolución | A www.cisco.com; ID 0x669f; RD=1 |

La trama completa mide 73 bytes: 14 Ethernet + 20 IPv4 + 8 UDP + 31 DNS.
La respuesta es la trama 2 y mide 201 bytes. Invierte MAC, IP y puertos; conserva
el identificador y agrega tres CNAME y un registro A. QR pasa de 0 a 1, RA vale 1.

Una MAC identifica el destino del enlace: si la IP final está fuera de la
subred, la trama se entrega al gateway. No se envía directamente a la MAC de
un servidor remoto. En nuestro NAT, el DNS 10.0.2.3 está en el enlace virtual y
su MAC coincide con la del gateway 10.0.2.2 por la implementación de VirtualBox.
Eso no significa que sus direcciones IP sean iguales ni que esa MAC sea la del
router físico de casa.

## Datos que conviene recordar

- Captura normal: 22 tramas; 10 consultas y 10 respuestas DNS, más 2 ARP.
- Cisco: consulta/respuesta 1/2; ID 0x669f; puerto del cliente 41544.
- Cisco devuelve tres CNAME y A 2.20.140.117. Los AAAA vienen en otra transacción,
  tramas 3/4, sobre el nombre canónico de Akamai.
- Google: tramas 5/6; ID 0x6570; 48201 → 53 y 53 → 48201; tamaños 74 y 202 bytes.
- Demo: 83 tramas; 34 preguntas y 34 respuestas; cliente 10.203.0.1,
  receptor 10.203.0.2; puerto efímero 37400.
- Archivo ficticio: 1072 bytes; 33 bloques de 32 bytes y uno de 16 bytes.
- Nombre completo de bloque: 82 caracteres; último nombre: 56.
- Entropía media de etiqueta: 2.0288 normal y 4.4372 demo.
- Intervalo medio de la demo: 0.2016 s. La pausa programada era 0.2 s.
- Detección: 33 candidatas, 1 alerta agrupada; no 33 ataques independientes.
- Cero paquetes descartados en las dos capturas definitivas.

No hace falta memorizar todos los IP públicos ni el hash: basta con saber dónde
comprobarlos. Son resultados de esa ejecución y pueden cambiar al repetirla.

## Veinte preguntas posibles

1. **¿Por qué DNS usa normalmente UDP?**
   Porque una pregunta y una respuesta pequeñas pueden intercambiarse sin abrir
   previamente una conexión, con una cabecera de sólo 8 bytes. La aplicación
   se encarga de temporizadores y reintentos. DNS también utiliza TCP.

2. **¿Cuándo necesita TCP?**
   Por ejemplo, ante una respuesta UDP truncada y para operaciones que lo
   requieren. Las implementaciones generales deben soportar DNS por TCP.
   No capturamos un fallback a TCP en esta prueba.

3. **¿Qué significan el puerto 53 y el puerto efímero?**
   El servidor escucha DNS convencional en el 53. El cliente usa un puerto
   temporal para recibir la respuesta. Nuestra VM tenía el rango local
   32768–60999, y observamos 41544 para la consulta inicial de Cisco.

4. **¿Cómo sabemos qué respuesta corresponde a qué consulta?**
   Por el ID de transacción, nombre y tipo, junto con IP y puertos invertidos.
   Un ID de 16 bits por sí solo puede repetirse y no basta para emparejar todo.

5. **¿Qué cambia entre consulta y respuesta?**
   Se invierten IP, MAC y puertos; QR pasa a 1. La respuesta conserva la
   pregunta y el ID y agrega registros y resultado. Puede anunciar RA y AA.

6. **¿RD y RA son lo mismo?**
   No. RD es la solicitud de recursión del cliente; RA es la disponibilidad
   anunciada por el servidor. RA=1 no prueba que haya consultado todos los
   servidores de la jerarquía para esa transacción: podría usar caché.

7. **¿Qué es un CNAME y por qué aparecen varias direcciones?**
   CNAME es un alias hacia otro nombre. Nuestra respuesta de Cisco encadenó
   tres alias hasta un A. Google devolvió ocho registros A. El PCAP muestra
   esos resultados, pero no determina por sí solo cómo seleccionaría una web
   su servidor ni garantiza respuestas futuras idénticas.

8. **¿Un registro AAAA implica que el paquete se transportó por IPv6?**
   No. AAAA describe el tipo de dato solicitado. La consulta AAAA que vimos
   se transportó por IPv4 y UDP; la dirección IPv6 estaba dentro de DNS.

9. **¿Por qué resolv.conf muestra 127.0.0.53 y el PCAP muestra 10.0.2.3?**
   El primero es el stub local de systemd-resolved. resolvectl muestra el
   resolver efectivo del enlace. Consultamos directamente a 10.0.2.3 para
   capturar Ethernet y evitar mezclarlo con el intercambio de loopback.

10. **¿La IP del DNS debe coincidir con el gateway?**
    No. En nuestra VM son 10.0.2.3 y 10.0.2.2. En una red doméstica pueden
    coincidir, pero no es una condición de DNS. Tampoco debe confundirse IP
    destino con MAC del siguiente salto.

11. **¿Por qué vaciaron la caché? ¿Vacían también la de Internet?**
    Para observar el comportamiento local sin entradas guardadas. Verificamos
    Current Cache Size: 0. No se vació la caché del NAT ni la de otros resolvers.
    Como usamos consultas directas al resolver del enlace, no dependíamos de
    que el stub local resolviera esos nombres.

12. **¿Cómo se exfiltran datos si la consulta es tipo A?**
    El archivo viaja codificado en el nombre preguntado, no en la dirección A
    de respuesta. El servidor ve ese nombre al recibir la consulta y extrae
    el bloque. Cambiar únicamente el tipo de registro no elimina ese canal.

13. **¿Base32 cifra la información?**
    No. Es una codificación reversible con un alfabeto adecuado para etiquetas.
    No necesita una clave. Lo comprobamos recuperando el archivo desde el PCAP.

14. **¿Qué diferencia hay entre tunneling y exfiltración?**
    Un túnel utiliza DNS para transportar otra comunicación, potencialmente
    bidireccional. Exfiltración significa trasladar datos fuera de su ámbito
    previsto. Nuestra demo representa la transferencia de un archivo a un
    receptor separado; no implementa un túnel general ni salió de la VM.

15. **¿Cómo garantizaron el aislamiento?**
    Creamos dos namespaces con sólo loopback y un extremo del par veth. Cada
    uno tenía únicamente la ruta 10.203.0.0/30; no había default ni interfaz
    hacia NAT. El servidor y el cliente tenían destinos fijos. El sufijo .test
    evita usar un dominio de terceros, pero no sustituye al aislamiento de red.

16. **¿Cómo probaron que el archivo llegó bien?**
    Comparamos byte a byte original y recibido. Después reconstruimos los
    bloques directamente desde las consultas del PCAP. Los tres archivos
    tienen 1072 bytes y el mismo SHA-256. El hash prueba igualdad en esta
    comprobación, no identidad de un remitente ni confidencialidad.

17. **¿Qué regla ejecutaron y qué limitación tiene?**
    Etiqueta de al menos 40 caracteres, entropía de al menos 3.5 y alfabeto
    Base32, con cinco nombres candidatos distintos por host/sufijo. Encontró
    33 de 34 consultas; el bloque corto no cumplía la longitud. No detecta
    necesariamente hexadecimal, datos de baja entropía o extracciones lentas.
    Tampoco demostramos su tasa de falsos positivos en una empresa.

18. **¿Por qué no bastan NXDOMAIN, TXT o una tasa alta?**
    Nuestra transferencia devolvió NOERROR y usó sólo A. Hay nombres largos
    legítimos de CDN y telemetría. Además, un emisor puede transferir lentamente.
    Hay que combinar señales y contexto, y confirmar con evidencia adicional.

19. **¿Basta con bloquear DNS directo o usar DNSSEC/DoH?**
    Bloquear DNS externo de los clientes reduce la variante directa, pero
    queda el canal que reenvía el resolver autorizado. DNSSEC autentica datos
    DNS, no impide que una consulta transporte contenido. DoH/DoT cifran el
    trayecto y cambian dónde podemos inspeccionar; se necesitan política de
    resolvers, controles de endpoint, logs y egress filtering.

20. **¿Qué falló y cómo se resolvió? ¿Qué no hicieron?**
    El primer intento recibió el archivo, pero dumpcap no pudo guardar el PCAP.
    Lo conservamos como fallo y repetimos con salida binaria abierta por el
    coordinador y comprobación del capturador. La segunda ejecución quedó
    respaldada por PCAP. Usamos NAT y dos namespaces dentro de una VM; no dos
    VM, no DNSteal, no Zeek/Suricata ejecutados y no exfiltración hacia Internet.

## Recorrido breve para mostrar evidencia

1. Abrir `DNS.pdf` y mostrar la configuración.
2. Abrir `capturas/normal_dns.pcap` en Wireshark y filtrar `dns`.
3. Seleccionar las tramas 1 y 2: MAC/IP, puertos, ID, RD/RA y CNAME/A.
4. Mostrar 5 y 6 para Google: 40 bytes UDP = 8 de cabecera + 32 DNS.
5. Abrir `capturas/dns_exfiltration.pcap`, seleccionar la trama 6 y desplegar DNS.
6. Mostrar secuencia `s0000`, total `n0034` y la etiqueta con Base32.
7. Aplicar `dns.flags.response == 0 && len(dns.qry.name) > 60`.
8. Ejecutar `python3 scripts/resumen.py` para comprobar los tres archivos y
   explicar la alerta y sus límites. No es necesario repetir tráfico en la defensa.
