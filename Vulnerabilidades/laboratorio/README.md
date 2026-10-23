# Laboratorio de vulnerabilidades

Trabajo en curso. El objetivo es un contenedor Ubuntu propio, en una red Docker
interna sin puertos publicados en la red física. Las fallas de demostración se
preparan exclusivamente en ese objetivo y se identifican como tales en el informe.

La imagen base `hardy-base:ubuntu24.04` ya existía en este equipo. El Dockerfile
instala Lynis, SSH y Redis. El usuario `auditor` utiliza una clave exclusiva del
laboratorio; no se usan credenciales personales.

OpenVAS requiere al menos 20 GB libres según Greenbone. Al preparar el laboratorio
había 6,7 GB disponibles: no se inicia su descarga hasta disponer de espacio.
