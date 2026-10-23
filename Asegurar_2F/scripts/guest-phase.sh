#!/usr/bin/env bash
# Ejecutar solamente dentro de un invitado de laboratorio con consola disponible.
set -euo pipefail

if [[ $EUID -ne 0 ]]; then
  echo 'Se requieren privilegios de root dentro de la VM.' >&2
  exit 1
fi
if [[ ${LAB_GUEST_CONFIRMED:-} != yes ]]; then
  echo 'Definir LAB_GUEST_CONFIRMED=yes solo dentro del invitado de laboratorio.' >&2
  exit 1
fi

phase=${1:-}
project_dir=$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")/.." && pwd)
backup_dir=${LAB_BACKUP_DIR:-/root/ssh2fa-lab-backup}
sshd_main=/etc/ssh/sshd_config
pam_sshd=/etc/pam.d/sshd
dropin_dir=/etc/ssh/sshd_config.d

prepare() {
  install -d -m 700 "$backup_dir"
  [[ -e $backup_dir/sshd_config ]] || cp -a "$sshd_main" "$backup_dir/sshd_config"
  [[ -e $backup_dir/pam_sshd ]] || cp -a "$pam_sshd" "$backup_dir/pam_sshd"
  grep -q '^Include /etc/ssh/sshd_config.d/\*.conf' "$sshd_main" || {
    echo 'El archivo sshd_config no incluye sshd_config.d; revisar antes de aplicar.' >&2
    exit 1
  }
}

validate_reload_ssh() {
  /usr/sbin/sshd -t
  systemctl reload ssh
  systemctl is-active --quiet ssh
  /usr/sbin/sshd -T | grep -E '^(usepam|pubkeyauthentication|passwordauthentication|kbdinteractiveauthentication|authenticationmethods|banner|authorizedkeysfile)'
}

restore_pam() {
  test -f "$backup_dir/pam_sshd" || { echo 'Falta el respaldo de PAM.' >&2; exit 1; }
  cp -a "$backup_dir/pam_sshd" "$pam_sshd"
}

case "$phase" in
  prepare)
    prepare
    apt-get update
    DEBIAN_FRONTEND=noninteractive apt-get install -y openssh-server libpam-google-authenticator fail2ban
    ;;
  key-only)
    prepare
    install -o root -g root -m 644 "$project_dir/configs/10-key-only.conf" "$dropin_dir/10-lab-ssh.conf"
    restore_pam
    validate_reload_ssh
    ;;
  central-keys)
    prepare
    install -d -o root -g root -m 755 /etc/ssh/authorized-keys
    install -o root -g root -m 644 "$project_dir/configs/20-central-keys.conf" "$dropin_dir/20-central-keys.conf"
    echo 'Copiar despues cada clave publica a /etc/ssh/authorized-keys/<usuario> (root:root, 0644).'
    validate_reload_ssh
    ;;
  banner)
    prepare
    install -o root -g root -m 644 "$project_dir/configs/ssh-banner.txt" /etc/ssh/ssh2fa-banner
    install -o root -g root -m 644 "$project_dir/configs/30-banner.conf" "$dropin_dir/30-banner.conf"
    validate_reload_ssh
    ;;
  pam-deny|pam-allow)
    prepare
    restore_pam
    if [[ $phase == pam-deny ]]; then
      test -f /etc/ssh/ssh.deny || { echo 'Crear /etc/ssh/ssh.deny (root:root, 0600).' >&2; exit 1; }
      rule=$project_dir/configs/pam-deny.account
    else
      test -f /etc/ssh/ssh.allow || { echo 'Crear /etc/ssh/ssh.allow (root:root, 0600).' >&2; exit 1; }
      rule=$project_dir/configs/pam-allow.account
    fi
    { cat "$rule"; cat "$backup_dir/pam_sshd"; } > "$pam_sshd"
    chmod 644 "$pam_sshd"
    validate_reload_ssh
    ;;
  mfa)
    prepare
    test -s /home/cisco/.google_authenticator || {
      echo 'Primero enrolar TOTP como cisco, sin imprimir el secreto.' >&2
      exit 1
    }
    restore_pam
    sed -i 's/^@include common-auth/#@include common-auth/' "$pam_sshd"
    sed -i '/^#@include common-auth/a auth required pam_google_authenticator.so' "$pam_sshd"
    install -o root -g root -m 644 "$project_dir/configs/10-lab-ssh.conf" "$dropin_dir/10-lab-ssh.conf"
    validate_reload_ssh
    ;;
  fail2ban)
    prepare
    install -d -o root -g root -m 755 /etc/fail2ban/jail.d
    install -o root -g root -m 644 "$project_dir/configs/sshd.local" /etc/fail2ban/jail.d/sshd.local
    fail2ban-client -t
    systemctl enable --now fail2ban
    fail2ban-client status sshd
    ;;
  rollback)
    restore_pam
    cp -a "$backup_dir/sshd_config" "$sshd_main"
    rm -f "$dropin_dir/10-lab-ssh.conf" "$dropin_dir/20-central-keys.conf" "$dropin_dir/30-banner.conf"
    rm -f /etc/fail2ban/jail.d/sshd.local
    /usr/sbin/sshd -t
    systemctl reload ssh
    systemctl stop fail2ban || true
    echo 'SSH y PAM restaurados. Se conservaron cuentas, claves y secretos del invitado.'
    ;;
  *)
    echo 'Uso: LAB_GUEST_CONFIRMED=yes sudo -E bash scripts/guest-phase.sh {prepare|key-only|central-keys|banner|pam-deny|pam-allow|mfa|fail2ban|rollback}' >&2
    exit 2
    ;;
esac
