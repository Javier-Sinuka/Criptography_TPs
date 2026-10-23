# Laboratorio SSH, PAM/TOTP y Fail2ban

El informe unificado está en `Asegurar_2F.tex` y su PDF compilado en `Asegurar_2F.pdf`. Los dos PDF originales de esta carpeta son las consignas. Las pruebas reales están resumidas en `evidence/matrix.csv`; cada fila remite a transcripciones de `evidence/logs/` o capturas de `evidence/screenshots/`.

## Entorno ejecutado

- Host: Ubuntu 24.04.5, VirtualBox 7.2.14, cliente OpenSSH 9.6p1.
- Invitado: clon aislado de la VM Cisco Workstation existente, Ubuntu 22.04.1, OpenSSH 8.9p1, 2 GiB de RAM, 2 CPU. La VM original no fue modificada.
- Red: NAT de VirtualBox. El invitado recibió `10.0.2.15/24`; el host se conectó a `127.0.0.1:2222`, redirigido al puerto 22 del invitado. En los registros del invitado, el host aparece como `10.0.2.2`.
- VM clonada: `vm/Crypto SSH 2FA Fail2ban Lab/`, excluida mediante `.gitignore`. Snapshots: `pre-lab`, `pre-ssh-auth-change`, `pre-pam-access-control` y `pre-mfa-offline`.
- Estado final verificado antes del apagado: SSH con clave pública y TOTP obligatorio para el usuario protegido; Fail2ban activo; IP de prueba desbaneada. El clon quedó **apagado** al entregar para liberar memoria del host; se puede iniciar desde VirtualBox.

## Orden de reproducción

1. Crear un clon o una VM Debian/Ubuntu para pruebas. Mantener su consola disponible. Configurar una conexión desde otro cliente; NAT con redirección de puerto es una opción. Tomar un snapshot antes de editar SSH/PAM.
2. Copiar `scripts/` y `configs/` al invitado. Dentro del invitado, ejecutar `LAB_GUEST_CONFIRMED=yes sudo -E bash scripts/guest-phase.sh prepare`. El script crea una copia de `sshd_config` y `pam.d/sshd` en `/root/ssh2fa-lab-backup` y comprueba que `sshd_config.d` esté incluido.
3. En el cliente, generar una clave Ed25519 exclusiva con `ssh-keygen -t ed25519 -f <ruta-privada-lab>` y frase de paso. Instalar **solo** el archivo `.pub` mediante `ssh-copy-id -i <ruta-privada-lab>.pub -p <puerto> <usuario>@<destino>`. Comprobar la clave con `ssh -i <ruta-privada-lab> -o IdentitiesOnly=yes` antes de desactivar contraseñas.
4. En el invitado, aplicar por fases `key-only`, `central-keys`, `banner`, `pam-deny` y `pam-allow` con `guest-phase.sh`. Crear las listas de usuarios como archivos `root:root` y `0600`. Instalar las claves públicas centrales en `/etc/ssh/authorized-keys/<usuario>` como `root:root` y `0644`. Después de cada fase, probar desde una **segunda sesión**; no cerrar la consola.
5. Restaurar PAM con la fase `key-only` antes de MFA. Como usuario protegido, ejecutar `google-authenticator --time-based --disallow-reuse --force --quiet --qr-mode=NONE --no-confirm --rate-limit=3 --rate-time=30 --window-size=3 --emergency-codes=5`. Esta invocación evita imprimir el QR o los códigos. Proteger `~/.google_authenticator` y recuperar el acceso solo desde la consola o un mecanismo de recuperación custodiado.
6. Con TOTP enrolado, aplicar `mfa`. El script instala `AuthenticationMethods publickey,keyboard-interactive` sin `nullok` y quita `common-auth` para que la segunda etapa pida TOTP en este ensayo. Probar clave válida con código correcto, incorrecto, vencido y clave errónea. `scripts/totp_local_client.py` es un cliente automatizado que **debe ejecutarse dentro del clon**; lee el secreto localmente y no lo imprime. En producción, usar una aplicación en otro dispositivo.
7. Aplicar `fail2ban`. El jail monitoriza `/var/log/auth.log` con backend `polling`; esta VM tiene `rsyslog`. Desde una IP cliente separada, generar fallos controlados contra el invitado hasta observar el ban. Confirmar con `fail2ban-client status sshd` y `iptables -L f2b-sshd -n`. Desbanear desde la consola con `sudo fail2ban-client set sshd unbanip <IP_DE_LAB>` y volver a comprobar la conexión.

Cada cambio de SSH ejecuta `sshd -t` antes de recargar. `sshd -T` permite revisar las opciones efectivas. `PasswordAuthentication no` no desactiva automáticamente la autenticación interactiva de PAM; se valida la combinación real de directivas en cada fase.

## Recuperación

Dentro del invitado, después de copiar `scripts/`: `LAB_GUEST_CONFIRMED=yes sudo -E bash scripts/guest-phase.sh rollback`. Esto restaura SSH/PAM y detiene Fail2ban; conserva cuentas y claves. El clon también conserva las copias iniciales en `/root/ssh2fa-backup-2026-10-13/`; se preparó `/root/ssh2fa-lab-backup/` para el script. Si no hay acceso por SSH, usar la consola de VirtualBox o el snapshot `pre-mfa-offline`. La restauración de snapshot pierde cambios posteriores del clon.

La ejecución del laboratorio se hizo con comandos registrados en `evidence/logs/`. `guest-phase.sh` reúne esos cambios para repetirlos; su sintaxis se comprobó, pero no se ejecutó de punta a punta sobre una segunda VM.

## Seguridad y límites

No se incorporan claves privadas, secretos TOTP, QR, códigos de recuperación, contraseñas ni OTP a este directorio. La clave temporal del host se creó fuera de esta carpeta. Las capturas proceden de la TTY real de la VM, mediante `VBoxManage controlvm screenshotpng`. Se descartó una captura inicial porque la pantalla de la VM mostraba credenciales de ejemplo.

Al finalizar se detuvo `ssh-agent` y se eliminó la clave privada temporal del host junto con su frase de paso. Para repetir el acceso desde el host se debe crear una nueva clave de laboratorio y autorizar su archivo público desde la consola del clon. El cliente TOTP local permanece solo dentro de la VM.

La prueba de TOTP válido usó un cliente emulado dentro de la misma VM, no un teléfono físico. Tras el unban, el host volvió a la etapa de solicitud TOTP; un ingreso completo desde el host no se ejecutó porque el secreto no salió del invitado. El cliente interno sí volvió a completar MFA. El modo opcional de tercer factor no se aplicó.
