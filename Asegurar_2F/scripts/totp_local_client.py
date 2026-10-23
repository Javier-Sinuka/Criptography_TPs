#!/usr/bin/env python3
"""Cliente TOTP para el clon de laboratorio; nunca imprime claves ni códigos."""

import argparse
import base64
import hashlib
import hmac
from pathlib import Path
import struct
import time

import pexpect


def totp(secret: str, counter: int) -> str:
    key = base64.b32decode(secret + "=" * (-len(secret) % 8), casefold=True)
    digest = hmac.new(key, struct.pack(">Q", counter), hashlib.sha1).digest()
    offset = digest[-1] & 15
    number = struct.unpack(">I", digest[offset : offset + 4])[0] & 0x7FFFFFFF
    return f"{number % 1_000_000:06d}"


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("mode", choices=("valid", "wrong", "expired", "wrong-key"))
    args = parser.parse_args()

    # Este archivo permanece dentro del invitado. No se copia al host.
    secret = Path.home().joinpath(".google_authenticator").read_text().splitlines()[0]
    counter = int(time.time() // 30)
    code = totp(secret, counter)
    if args.mode == "wrong":
        code = f"{(int(code) + 1) % 1_000_000:06d}"
    elif args.mode == "expired":
        code = totp(secret, counter - 10)

    key_path = Path.home() / ".ssh" / (
        "id_ed25519_wrong" if args.mode == "wrong-key" else "id_ed25519_mfa_lab"
    )
    command = [
        "-p", "22", "-v", "-o", "StrictHostKeyChecking=accept-new",
        "-o", "UserKnownHostsFile=/tmp/ssh2fa-loopback-known_hosts",
        "-o", "IdentitiesOnly=yes", "-o", "IdentityAgent=none",
        "-o", "PasswordAuthentication=no", "-o", "NumberOfPasswordPrompts=1",
        "-i", str(key_path),
        "cisco@127.0.0.1", "printf MFA_LOGIN_OK",
    ]
    child = pexpect.spawn("ssh", command, encoding="utf-8", timeout=15)
    prompt_seen = False
    try:
        result = child.expect([r"(?i)verification code:", pexpect.EOF])
        before = child.before
        if result == 0:
            prompt_seen = True
            child.sendline(code)
            child.expect(pexpect.EOF)
            before += child.before
        child.close()
        print(f"mode={args.mode}")
        print(f"otp_prompt_seen={str(prompt_seen).lower()}")
        print(f"command_marker_seen={str('MFA_LOGIN_OK' in before).lower()}")
        print(f"ssh_exit={child.exitstatus}")
    except pexpect.TIMEOUT:
        child.close(force=True)
        print(f"mode={args.mode}")
        print("result=timeout")


if __name__ == "__main__":
    main()
