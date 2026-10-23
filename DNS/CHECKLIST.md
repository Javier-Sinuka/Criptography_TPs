# Cobertura de las consignas

Se leyeron completos los dos DOCX antes del laboratorio. El texto y las tablas
se extrajeron en resultados/. Cada documento contiene nueve preguntas contando
la consigna tabular de identificación de dispositivos del segundo.

## Actividades comprobadas

- [x] Inspeccionar host, interfaces, virtualización, resolvers y herramientas.
- [x] Usar la estación Cisco existente, con perfil analyst de CyberOps.
- [x] Documentar NAT frente al adaptador puente del DOCX.
- [x] Registrar IP, MAC, gateway, stub local y DNS efectivo.
- [x] Vaciar caché local y verificar tamaño cero.
- [x] Ejecutar nslookup interactivo y dig con consultas A/AAAA.
- [x] Capturar tráfico normal real: PCAP original de 22 tramas.
- [x] Analizar Ethernet, IPv4, UDP, DNS, flags y registros A/AAAA/CNAME.
- [x] Completar las tres tablas editables del segundo DOCX.
- [x] Guardar capturas auténticas del Wireshark de la VM y del terminal.
- [x] Estudiar el artículo de Helge Klein y fuentes primarias.
- [x] Ejecutar una transferencia ficticia en dos namespaces aislados.
- [x] Conservar el PCAP definitivo de la demostración: 83 tramas.
- [x] Documentar el intento inicial sin PCAP y la corrección de dumpcap.
- [x] Comparar original, recepción y reconstrucción desde PCAP: 1072 bytes iguales.
- [x] Ejecutar detección Python y filtro de Wireshark sobre nuestra captura.
- [x] Contrastar 1099 valores con rawshark: todos coinciden.
- [x] Explicar detección, falsos positivos, limitaciones y mitigaciones.
- [x] Responder las dos preguntas generales sobre detección y prevención.
- [x] Conservar comandos, salidas, scripts, JSON/CSV y errores relevantes.
- [x] Redactar DNS.tex y compilar DNS.pdf con el formato solicitado.
- [x] Crear README y guía con veinte preguntas para la defensa.
- [x] Usar sólo contenido sintético en la transferencia; sin infraestructura externa.

## Preguntas del laboratorio 17.1.7

Respuesta explícita en la subsección «Respuestas a todas las preguntas» del
laboratorio 17.1.7 del informe, con la misma numeración:

1. MAC origen/destino e interfaces asociadas.
2. IP origen/destino e interfaces asociadas.
3. Puertos y puerto predeterminado de DNS.
4. Comparación entre terminal y Wireshark.
5. MAC/IP/puertos de respuesta y diferencias con consulta.
6. Disponibilidad de recursión.
7. Comparación de respuestas frente a nslookup.
8. Reflexión sobre lo observable sin filtro.
9. Reflexión sobre uso malicioso de Wireshark.

## Preguntas del laboratorio 10.2.7

Respuesta explícita en la subsección «Respuestas a todas las preguntas» del
laboratorio 10.2.7 del informe, con la misma numeración:

1. Coincidencia de MAC origen con configuración.
2. Identificación de IP/MAC de ambos dispositivos (consigna tabular).
3. Coincidencia de IP origen con configuración.
4. Comparación de IP destino y gateway.
5. Dispositivos correspondientes a las MAC de respuesta.
6. IP destino de respuesta.
7. IP origen de respuesta.
8. Inversión de roles de los extremos.
9. Reflexión sobre ventajas y límites de UDP frente a TCP.

Tablas originales completas:

- Configuración de IP/MAC/gateway/DNS: sección «Entorno y alcance».
- Dispositivos e IP/MAC: sección del laboratorio 10.2.7.
- Campos de consulta: tabla Google, ampliada con la respuesta.

## Adaptaciones y límites documentados

- LabVM Cisco instalada, perfil SOC Analyst; adaptador NAT preexistente.
- dig en lugar de navegador para Google; nslookup interactivo para Cisco.
- Captura con dumpcap, revisión gráfica con Wireshark y análisis con Python/rawshark.
- No se necesitó instalar tshark ni otro software.
- Dos namespaces dentro de una VM; no dos VM independientes.
- No se ejecutó DNSteal ni se envió la transferencia a Internet.
- Zeek, Suricata, SIEM, RPZ y controles de salida son propuestas no desplegadas.
- No se recibió la imagen de la consigna general mencionada en el texto adjunto.
- El primer intento aislado sin PCAP se conserva como incidencia.
- La regla no marca el último fragmento corto; no se afirma eficacia general.
