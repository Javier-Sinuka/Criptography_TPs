#!/usr/bin/env python3
"""Ejecuta un comando sin shell y conserva su salida auténtica y código de retorno."""
import datetime
import pathlib
import shlex
import subprocess
import sys

ROOT = pathlib.Path(__file__).resolve().parents[1]

def run(args, timeout=60):
    stamp = datetime.datetime.now().astimezone().isoformat()
    try:
        p = subprocess.run(args, cwd=ROOT, stdout=subprocess.PIPE,
                           stderr=subprocess.STDOUT, text=True, encoding='utf-8',
                           errors='backslashreplace', timeout=timeout)
        output, code = p.stdout, p.returncode
    except (OSError, subprocess.TimeoutExpired) as error:
        output, code = str(error) + '\n', -1
    shown = list(args)
    if '--password' in shown:
        shown[shown.index('--password') + 1] = '<clave predeterminada de la VM educativa>'
    record = f'\n=== FECHA ===\n{stamp}\n=== COMANDO ===\n{shlex.join(shown)}\n=== RESULTADO ===\n{output}\n=== RETORNO ===\n{code}\n'
    with (ROOT / 'resultados/comandos.txt').open('a') as f:
        f.write(record)
    print(record, flush=True)
    return code

if __name__ == '__main__':
    sys.exit(run(sys.argv[1:]))
