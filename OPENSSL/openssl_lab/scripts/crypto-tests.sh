#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")/.."
mkdir -p data outputs evidence/logs
umask 077
LOG=evidence/logs/crypto-tests.txt
exec > >(tee "$LOG") 2>&1
printf 'Fecha UTC: '; date -u -Is
printf 'Sistema: Ubuntu 24.04.5 LTS\nOpenSSL: '; openssl version
cat > data/letter_to_grandma.txt <<'TXT'
Hola abuela,

Te escribo esta carta para agradecerte el pan casero con
chicharrones y el salame de Colonia Caroya que me enviaste.
¡Los probé esta mañana en el desayuno y son absolutamente
deliciosos!

Te deseo lo mejor.
Tu nieto feliz.
TXT
printf 'vim or emacs ?' > data/top_secret.txt
python3 - <<'PY'
from pathlib import Path
Path('data/file_secret').write_bytes(bytes(range(256))*8192)
PY
printf '\nE01 Texto plano, PDF p. 2\n'; cat data/letter_to_grandma.txt; file -bi data/letter_to_grandma.txt; wc -c data/letter_to_grandma.txt; sha256sum data/letter_to_grandma.txt
openssl rand -hex 32 > outputs/.pass-aes
printf '\nE02 AES-256-CBC con KDF heredada; se usa passfile para no revelar el secreto\n'
openssl aes-256-cbc -in data/letter_to_grandma.txt -out outputs/message_binary.enc -pass file:outputs/.pass-aes
file outputs/message_binary.enc; wc -c outputs/message_binary.enc; xxd -l 48 outputs/message_binary.enc
printf '\nE03 AES-256-CBC + Base64\n'
openssl aes-256-cbc -a -in data/letter_to_grandma.txt -out outputs/message_base64.enc -pass file:outputs/.pass-aes
file outputs/message_base64.enc; wc -c outputs/message_base64.enc; head -c 72 outputs/message_base64.enc; printf '\n'
printf '\nE04 Descifrado, -a decodifica Base64\n'
openssl aes-256-cbc -d -a -in outputs/message_base64.enc -out outputs/decrypted_letter.txt -pass file:outputs/.pass-aes
cmp data/letter_to_grandma.txt outputs/decrypted_letter.txt && echo 'cmp: PASS'; sha256sum data/letter_to_grandma.txt outputs/decrypted_letter.txt
openssl rand -hex 32 > outputs/.pass-wrong
printf '\nE04-N Contraseña incorrecta\n'
if openssl aes-256-cbc -d -a -in outputs/message_base64.enc -out outputs/wrong_password.txt -pass file:outputs/.pass-wrong 2>outputs/wrong_password.stderr; then echo 'Descifrado terminó (CBC no autentica)'; cmp -s data/letter_to_grandma.txt outputs/wrong_password.txt && echo 'coincide' || echo 'bytes no coinciden'; else echo 'Error de descifrado'; fi
printf '\nE05 Claves RSA cifradas de Alice y Bob, 3072 bits\n'
for who in alice bob; do
  openssl rand -hex 32 > "outputs/.pass-${who}"
  openssl genpkey -algorithm RSA -aes-256-cbc -pkeyopt rsa_keygen_bits:3072 -pass file:"outputs/.pass-${who}" -out "outputs/${who}_private.pem" 2>/dev/null
  chmod 600 "outputs/${who}_private.pem"
  openssl pkey -in "outputs/${who}_private.pem" -passin file:"outputs/.pass-${who}" -pubout -out "outputs/${who}_public.pem"
  ls -l "outputs/${who}_private.pem" "outputs/${who}_public.pem"; file "outputs/${who}_private.pem" "outputs/${who}_public.pem"
  openssl pkey -in "outputs/${who}_private.pem" -passin file:"outputs/.pass-${who}" -noout -text 2>/dev/null | sed -n '1p'
done
printf '\nE06 Alice cifra a Bob con RSA-OAEP-SHA256\n'
openssl pkeyutl -encrypt -pubin -inkey outputs/bob_public.pem -in data/top_secret.txt -out outputs/top_secret.enc -pkeyopt rsa_padding_mode:oaep -pkeyopt rsa_oaep_md:sha256 -pkeyopt rsa_mgf1_md:sha256
openssl pkeyutl -decrypt -inkey outputs/bob_private.pem -passin file:outputs/.pass-bob -in outputs/top_secret.enc -out outputs/top_secret.dec -pkeyopt rsa_padding_mode:oaep -pkeyopt rsa_oaep_md:sha256 -pkeyopt rsa_mgf1_md:sha256
cmp data/top_secret.txt outputs/top_secret.dec && echo 'Alice->Bob cmp: PASS'; file outputs/top_secret.enc; wc -c data/top_secret.txt outputs/top_secret.enc; xxd -l 32 outputs/top_secret.enc
printf 'Clave privada equivocada: '
if openssl pkeyutl -decrypt -inkey outputs/alice_private.pem -passin file:outputs/.pass-alice -in outputs/top_secret.enc -out outputs/wrong_rsa.dec -pkeyopt rsa_padding_mode:oaep -pkeyopt rsa_oaep_md:sha256 -pkeyopt rsa_mgf1_md:sha256 2>outputs/wrong_rsa.stderr; then echo 'aceptada inesperadamente'; else echo 'rechazada'; fi
printf 'Mensaje de Bob para Alice' > outputs/bob_message.txt
openssl pkeyutl -encrypt -pubin -inkey outputs/alice_public.pem -in outputs/bob_message.txt -out outputs/bob_message.enc -pkeyopt rsa_padding_mode:oaep -pkeyopt rsa_oaep_md:sha256 -pkeyopt rsa_mgf1_md:sha256
openssl pkeyutl -decrypt -inkey outputs/alice_private.pem -passin file:outputs/.pass-alice -in outputs/bob_message.enc -out outputs/bob_message.dec -pkeyopt rsa_padding_mode:oaep -pkeyopt rsa_oaep_md:sha256 -pkeyopt rsa_mgf1_md:sha256
cmp outputs/bob_message.txt outputs/bob_message.dec && echo 'Bob->Alice cmp: PASS'
printf '\nE07 Sobre híbrido, adaptación explícita a clave de alta entropía\n'
# R es una frase aleatoria en hexadecimal. Se cifra exactamente el mismo archivo con PBKDF2 en ambas direcciones.
openssl rand -hex 32 > outputs/key.pass
openssl pkeyutl -encrypt -pubin -inkey outputs/bob_public.pem -in outputs/key.pass -out outputs/key.pass.enc -pkeyopt rsa_padding_mode:oaep -pkeyopt rsa_oaep_md:sha256 -pkeyopt rsa_mgf1_md:sha256
openssl enc -aes-256-cbc -salt -pbkdf2 -iter 200000 -in data/file_secret -out outputs/file_secret.enc -pass file:outputs/key.pass
openssl pkeyutl -decrypt -inkey outputs/bob_private.pem -passin file:outputs/.pass-bob -in outputs/key.pass.enc -out outputs/key.pass.recovered -pkeyopt rsa_padding_mode:oaep -pkeyopt rsa_oaep_md:sha256 -pkeyopt rsa_mgf1_md:sha256
openssl enc -d -aes-256-cbc -pbkdf2 -iter 200000 -in outputs/file_secret.enc -out outputs/file_secret.restored -pass file:outputs/key.pass.recovered
cmp data/file_secret outputs/file_secret.restored && echo 'Archivo híbrido cmp: PASS'; sha256sum data/file_secret outputs/file_secret.restored; wc -c data/file_secret outputs/file_secret.enc outputs/key.pass.enc
printf '\nE07-N Alteración de ciphertext CBC\n'
cp outputs/file_secret.enc outputs/file_secret.corrupt.enc
printf '\001' | dd of=outputs/file_secret.corrupt.enc bs=1 seek=50 conv=notrunc status=none
if openssl enc -d -aes-256-cbc -pbkdf2 -iter 200000 -in outputs/file_secret.corrupt.enc -out outputs/corrupt.restored -pass file:outputs/key.pass.recovered 2>outputs/corrupt.stderr; then cmp -s data/file_secret outputs/corrupt.restored && echo 'no cambió' || echo 'alteración no autenticada: archivo distinto'; else echo 'fallo de padding/descifrado'; fi
chmod 600 outputs/.pass-* outputs/key.pass
