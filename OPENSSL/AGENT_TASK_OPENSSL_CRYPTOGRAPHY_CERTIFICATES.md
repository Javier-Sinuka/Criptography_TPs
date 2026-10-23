# Agent Assignment — OpenSSL Cryptography, Digital Certificates, PKI, and HTTPS

## 1. Role and objective

You are an autonomous engineering and academic-laboratory assistant operating through VS Code and its integrated terminal. Complete **all activities, questions, demonstrations, and verifications** contained in the two accompanying course PDFs, and prepare the work for **one unified, academically rigorous report written entirely in Spanish**.

**Source documents (mandatory, authoritative for assignment scope):**
1. `9 Cifrar y Descifrar datos y archivos con OpenSSL.docx.pdf` (9 pages): symmetric encryption, asymmetric encryption, and hybrid encryption of large files.
2. `Criptografía y Certificados Digitales en la Práctica.pdf` (2 pages): X.509/PKI theory, deployment of a real Let's Encrypt certificate on a controlled domain, and analysis of the HTTPS trust chain.

Read both PDFs in full before starting. Use their precise questions and original progression as a completeness checklist. The instructions here are an execution specification, not a substitute for the original PDFs. If an inconsistency exists, document both the assigned instruction and the safe, working adaptation.

The instructor requests **execution of the commands, completion of the guides, and an evidence-based report**. Real terminal screenshots, output files, verification logs, and well-argued explanations are required. **Do not fabricate any command execution, certificate, success, screenshot, experimental result, domain ownership, or browser observation.**

## 2. Working agreement: single report, Spanish, and LaTeX handoff

- **ALL final academic prose must be in Spanish** (formal, technical, impersonal academic style), including abstract/resumen, objectives, methods, figure captions, tables, discussion, conclusions, and answers to every question.
- Shell commands, terminal outputs, proper nouns, standard protocol terms, and literal identifiers may remain in their original language.
- Produce **ONE integrated report**, not one report per PDF. Organize it into logically distinct sections: introduction, background, environment, symmetric cryptography, asymmetric cryptography, hybrid encryption, PKI and certificates, Let's Encrypt/HTTPS, trust-chain verification, security analysis, results, discussion, conclusions, bibliography, and appendices as appropriate.
- **The user will later identify the specific LaTeX `.tex` file/project you must edit. Do not choose, create, or overwrite the final main `.tex` file before receiving that instruction.** First inspect the existing project (when supplied), preserve its class, formatting, metadata, packages, and structure, and then integrate all Spanish material into the user-specified LaTeX document. You may prepare staging Markdown/structured notes, evidence manifests, BibTeX suggestions, and draft Spanish sections meanwhile.
- Do not assume the user's name, university metadata, course title, instructor, date of submission, or domain. Leave placeholders or ask where essential.
- When the user supplies the LaTeX target, build it if the toolchain permits, correct compilation warnings/errors, verify images and references, and produce one final PDF with its editable LaTeX sources.

## 3. Operational boundaries and reproducibility

1. Start by inspecting the host OS, versions (`openssl version -a`, relevant distribution version), available virtualization/container capabilities, permitted access, and existing project files.
2. Favor a disposable and isolated laboratory directory, VM, or container. Do not change the host's production web server, TLS credentials, trust store, firewall, DNS, or privileged settings without explicit approval.
3. Before nontrivial system changes, provide the user a short proposed plan and request approval if an action involves sudo, installing packages, altering public DNS, exposing ports, managing credentials, or potentially spending money.
4. Never print or commit private keys, secret passphrases, actual credentials, ACME account keys, complete secret environment files, or full confidential payloads. Keep private key permissions restrictive (`chmod 600`), use temporary demonstration-only secrets, redact sensitive information from screenshots, and keep secrets out of Git.
5. Record tested software versions, exact commands, purpose, exit codes, paths of artifacts, SHA-256 checksums where appropriate, and timestamps. Prefer reproducible scripts with clear comments and fail-fast checks.
6. Include meaningful **positive and negative tests** (successful decryption/verification, wrong password, wrong key, corrupted ciphertext, invalid/untrusted certificate or name mismatch in a controlled manner where feasible), and explain the expected security property being tested.
7. Take screenshots of **actual running terminals or browser windows**, legible and chronologically organized; save accompanying raw text logs and a mapping from each image to its corresponding command and outcome. Synthetic/mock screenshots must never be presented as experiment evidence.
8. If a task is blocked by unavailable Internet, ports, DNS, domain ownership, privileges, program versions, or GUI access, document the exact constraint and leave the experiment marked **PENDIENTE / NO VERIFICADO**, with instructions the user can execute. Never claim completion from a simulated substitute.

## 4. Laboratory A — Symmetric cryptography with OpenSSL (PDF 1, pp. 1–3)

### A1. Setup and plaintext
- Reproduce the equivalent of the CyberOps Workstation laboratory under a dedicated workspace (do not require the identical VM if a compatible Linux environment is sufficient; state the deviation).
- Create `letter_to_grandma.txt` with the Spanish sample letter given in the PDF (the greeting and references to pan casero con chicharrones and salame de Colonia Caroya), preserving its content as closely as possible.
- Display the plaintext with `cat`; record encoding, size, and SHA-256 hash; capture real evidence.

### A2. AES-256-CBC encryption, binary output, and Base64
- Run and explain the assigned AES-256-CBC password-based encryption exercise, equivalent to:
  `openssl aes-256-cbc -in letter_to_grandma.txt -out message.enc`
- Enter an isolated demo passphrase interactively; **do not expose it in the report**. Explain what the password does, cipher/mode, salt, key derivation, and the warnings associated with the guide's legacy method.
- Inspect the encrypted output with `cat message.enc` **only in a controlled terminal**; additionally use `file`, `xxd` or `hexdump -C` to explain why raw encrypted bytes are not human-readable. Save a screenshot of the output, redacting if required.
- Repeat the assigned exercise with Base64 (`openssl aes-256-cbc -a -in letter_to_grandma.txt -out message.enc`), ideally keeping distinct binary and Base64 filenames so both results remain available.
- Show and compare their outputs, sizes, and content presentation. Answer explicitly: **What is the advantage of Base64 encoding encrypted output?** Clarify emphatically that Base64 is encoding, **not another encryption algorithm** and does not add confidentiality.

### A3. Decryption and verification
- Decrypt the Base64 version with the corresponding `-d -a` options into `decrypted_letter.txt`; show plaintext, compare with the original using `cmp` and SHA-256, and document PASS/FAIL.
- Answer explicitly: **Why is `-a` used during decryption?**
- Try a wrong password and controlled tampering; record what OpenSSL actually detects and emphasize that CBC encryption alone does **not** provide authenticated integrity (and padding failures are not a robust authenticity check).
- Discuss weaknesses explicitly called out in the source: legacy password-based KDF and lack of guaranteed integrity. Where possible, repeat the experiment using a modern supported KDF (`-pbkdf2` with documented iterations) as a **separate, labeled improvement**, without replacing the originally required demonstration. Explain why an authenticated-encryption design is preferable for sensitive real-world data.

## 5. Laboratory B — Asymmetric cryptography with OpenSSL (PDF 1, pp. 4–7)

### B1. Alice and Bob keys
- Explain public vs. private keys, asymmetric encryption, confidentiality, and the Alice/Bob exchange scenario in the PDF.
- Demonstrate the PDF's requested RSA key workflow for **Alice and Bob**, noting that the legacy example uses `openssl genrsa -aes128 ... 1024` and that **1024-bit RSA is obsolete/inappropriate for present-day security**. If the installed OpenSSL disallows it or policy prevents its use, document the reason and use a secure modern key size such as RSA-3072 for the successful test. Do not imply that modern commands are exact copies of the source.
- Generate encrypted demo private keys, inspect filenames, format and filesystem permissions (`ls -l`, `file`). If inspecting PEM headers, **show only nonsecret metadata**, never paste full private keys into evidence or report.
- Inspect key metadata with `openssl rsa ... -noout -text` or `openssl pkey` where supported, without exposing private components in saved outputs.
- Extract and inspect both public keys (`openssl rsa -in alice_private.pem -pubout -out alice_public.pem` and equivalent for Bob; use supported modern alternatives if needed). Demonstrate why public keys can be shared and private keys cannot.
- Show public-key exchange as separate actors/directories or isolated user roles; clearly distinguish what each party holds.

### B2. Encrypted messages and decryption
- Create the exact sample `top_secret.txt` containing `vim or emacs ?`.
- Have Alice encrypt the message for Bob with **Bob's public key**, and Bob decrypt it with **Bob's private key**. The source uses deprecated `openssl rsautl`; **prefer `openssl pkeyutl` with explicit RSA-OAEP padding** when supported, while recording the original command, obsolescence and security difference. If demonstrating the legacy command is possible and safe in the disposable laboratory, label it clearly as historical.
- Use `file` and `hexdump -C` (or `xxd`) on ciphertext, record sizes, and compare the decrypted bytes to the initial message (`cmp`/SHA-256).
- Reverse the roles: Bob encrypts a message for Alice with Alice's public key, Alice decrypts it with Alice's private key.
- Attempt controlled decryption with the wrong recipient's private key; record actual failure, and explain why both confidentiality and public-key identity validation matter.
- Avoid claiming that RSA directly encrypts arbitrary-size messages; explain the algorithm's input-size limits and padding.

## 6. Laboratory C — Hybrid encryption of large files (PDF 1, pp. 8–9)

- Reproduce and explain the source's hybrid workflow and diagram: file `F`; randomly generated secret `R`; symmetric encryption `EF = Sym(F,R)`; asymmetric protection of `R` for Bob; transmission of both encrypted artifacts; Bob recovers `R` and then `F`.
- Prepare a demonstrably larger deterministic or generated sample file, record its size and SHA-256 hash.
- Use a **proper random key material/secret-generation method** and show how Bob's RSA public key protects that material. The source suggests `openssl rand -base64 32 > key.bin`; explain that this yields Base64 text and distinguish text-based passphrases from raw binary keys.
- Critically audit the source's sample `-k key.bin` syntax: with OpenSSL `enc`, `-k` treats `key.bin` as the literal passphrase string, **not automatically as the bytes contained in that file**. Do not silently claim the sample implements file-based key transport. Use a coherent, explicitly documented method to pass the actual recovered key or passphrase to encryption/decryption, minimizing secret leakage; carefully explain any adaptation.
- Audit the source's inconsistent `-pbkdf2` usage (encryption lists it while decryption omits it). Configure **matching options** at both ends and clearly state the actual tested command sequence and any deviation.
- Use secure modern RSA encryption padding where practical (OAEP via `pkeyutl`), and a sensible symmetric approach for this educational lab. If using AES-256-CBC to match the guide, explicitly document lack of authenticated integrity and include a controlled corruption test; optional modern AEAD demonstration may be added but must be separate from the guide's commands.
- Capture each stage: random material generation (without showing the secret), RSA-encrypted secret, symmetrically encrypted file, Bob's recovered secret, restored file, and hash/bytewise equality PASS. Explain **why hybrid encryption is preferable for large datasets** and what the original diagram leaves unspecified (integrity/authentication, metadata, algorithm negotiation, secure key handling).
- Include a clear, original, labeled workflow figure for hybrid encryption in the report, separate from the screenshots.

## 7. Laboratory D — Digital certificates and PKI theory (PDF 2, Part 1)

Research and answer **all four original questions in academic Spanish**, preferably with precise standards and primary references:
1. **X.509 certificate:** definition, subject/public-key binding, digital signature, and how certificate authentication mitigates man-in-the-middle attacks when validation succeeds.
2. **Certificate Authority:** what a CA does, why browsers trust certain issuers, and distinction between a trust anchor and a certificate merely received from a server.
3. **CA hierarchy:** respective responsibilities and differences between Root CA, Intermediate CA, and End-Entity/Leaf certificate, including path-building and key-protection rationale.
4. **Revocation:** CRLs vs OCSP, why revocation matters before expiry, and practical limitations of revocation checks in different clients.

Explicitly distinguish encryption from signing, identity authentication from confidentiality, public-key trust from mere possession, and the role of the trust store. Sources must be cited (e.g., X.509/RFC 5280, relevant ACME RFC, Let's Encrypt documentation, OpenSSL manual). Do not assert that an expired, revoked, wrong-hostname or self-signed leaf certificate is automatically trusted.

## 8. Laboratory E — HTTPS deployment using Let's Encrypt (PDF 2, Part 2)

**This source specifically requires Nginx or Apache on a server, a domain controlled by the user, and a real certificate issued by Let's Encrypt through Certbot.** A local self-signed demonstration is NOT equivalent to this requirement.

### E1. Preflight: ask for required user inputs before public deployment
- Confirm ownership/control of the domain/subdomain, DNS-management ability, reachable server or VM, public IP or suitable validation architecture, allowed ports 80/443, and whether DNS-01 is available. Request only necessary user information; do not request account passwords or private keys in chat.
- Explain the difference between local-only and Internet-reachable services. If a domain/server or required privileges are unavailable, fully complete the offline cryptography/PKI exercises where possible and mark the Let's Encrypt section **BLOCKED / PENDIENTE DE DOMINIO O ACCESO**, with a reproducible checklist. Do not borrow someone else's domain or claim a real issuance from a mock server.

### E2. Configure and verify
- With explicit authorization, configure Nginx or Apache with a simple lab virtual host for the user's domain. Document DNS evidence, HTTP connectivity, service status, and firewall/port assumptions.
- Install supported Certbot packages/integration, select and document a challenge (**HTTP-01** or **DNS-01**), obtain an actual publicly trusted certificate using the documented ACME flow, and set up HTTPS.
- Record issuer, SAN hostnames, validity dates, certificate files (without showing private-key content), served chain, web-server TLS configuration, HTTPS response, and certificate validation by a client.
- Capture terminal evidence and, if possible, the browser's certificate details (browser interfaces vary; do not assume a padlock always appears).
- Test `certbot renew --dry-run` or the installed equivalent, inspect the actual renewal mechanism (systemd timer or cron), and record the result. Do **not** force repeated production issuance that may trigger rate limits.
- If testing a self-signed or local CA certificate for comparison, keep it explicitly separate from the public Let's Encrypt result.

### E3. Answer all original conceptual questions
1. Which ACME challenge was used, exactly how it establishes domain control, and why it does **not** prove the applicant's personal or organizational identity.
2. The security benefits of short certificate lifetimes, including limiting exposure after key compromise and lowering dependence on revocation; **verify current Let's Encrypt validity policy as of execution** instead of blindly repeating the guide's historical "maximum 90 days" claim if it has changed.
3. Why renewal automation is essential and how operational failure can lead to TLS outages.

## 9. Laboratory F — Certificate inspection and chain-of-trust analysis (PDF 2, Part 3)

After the authorized HTTPS setup is genuinely reachable, execute and carefully document equivalent commands such as:

```bash
openssl s_client -connect DOMAIN:443 -servername DOMAIN -showcerts -verify_return_error </dev/null
openssl x509 -in CERTIFICATE_FILE -text -noout
openssl x509 -in CERTIFICATE_FILE -noout -subject -issuer -dates -ext subjectAltName
```

Replace placeholders only with actual known paths/domain. Be careful to distinguish the **served certificate/chain** from the actual **OS/browser trust store**; the TLS server usually does not transmit a root certificate, and the browser may construct different valid paths.

Answer **all five required questions**:
1. Exact Leaf certificate **Subject** and **Issuer**, public-key algorithm, size or named curve, SANs, validity, and relevant signature algorithm; show evidence.
2. The exact observed **Leaf -> Intermediate(s) -> trusted Root** path for the chosen domain/trust environment. Record exact intermediate/root names and applicable fingerprints, not merely an example like "ISRG Root X1". Explain any cross-sign or alternate-chain behavior.
3. Why intermediates sign operational end-entity certificates instead of exposing the Root CA signing key online; explain operational isolation and offline root-key protection.
4. How certificate signature verification mathematically works (signed `TBSCertificate`, hash/signature algorithm, issuer public key, verification, chain validation); distinguish this from hostname matching, validity checking, constraints, revocation, and endpoint key possession.
5. Where the OS/browser obtains its root trust anchors. **Inspect the actual machine's trust store** (e.g., Debian/Ubuntu CA bundle, `/etc/ssl/certs`, `trust` utility, browser certificate settings as relevant). Search for the *actual relevant root* and demonstrate whether it is trusted locally; don't falsely infer browser trust from the mere presence of a PEM file.

Include a legible chain diagram, annotated screenshots, and relevant redacted OpenSSL output. Use trusted references for any claim about certificate policy or current CA hierarchy.

## 10. Required evidence and experiments

For every meaningful exercise, provide:
- **Experiment ID**, purpose, assigned PDF and page/section, command(s), environment/version, expected behavior, observed behavior, result (PASS/FAIL/BLOCKED), explanation, and file(s) containing raw output.
- One or more **authentic screenshots** showing the actual terminal/browser state. Use filenames such as `E01_plaintext.png`, `E02_aes_binary.png`, `E03_aes_base64.png`, `E04_aes_decrypt_compare.png`, `E05_rsa_key_metadata.png`, `E06_alice_bob_encryption.png`, `E07_hybrid_hash_match.png`, `E08_https_certificate.png`, `E09_trust_chain.png`, `E10_trust_store.png`. These are illustrative filenames, not proof that those steps have run.
- A machine-readable/Markdown **evidence index** linking experiment IDs, images, logs, and corresponding report sections.
- A concise results table showing test, expected result, actual result, verification command, and status.
- Explicit separation of commands taken verbatim from the PDFs, compatibility replacements, and supplementary tests. Identify deprecated/unsafe legacy practice rather than promoting it for real deployments.

**Never generate attractive fake terminal images.** If real screenshot capture is impossible, retain genuine command transcripts and mark graphical screenshots as missing, stating what the user must capture locally. Mask all secrets and private key material.

## 11. Academic report quality criteria (Spanish)

The unified report must include:
1. Title/metadata appropriate to the user's forthcoming LaTeX project; **resumen**, keywords, introduction, scope, specific objectives.
2. Concise theory supporting—not displacing—the practical work: symmetric vs asymmetric vs hybrid systems, AES-CBC, RSA/padding, KDF, entropy and key handling, X.509, CA, PKI, TLS, ACME, and trust stores.
3. Laboratory environment and repeatability: OS, versions, topology, dependencies, directory layout, and any necessary domain/authorization considerations.
4. **Chronological, reproducible procedures** for every section of both PDFs, with appropriately chosen real screenshots and enough terminal output to prove each claim.
5. Explicit answers to **all** questions asked in the PDFs (including those embedded within procedural paragraphs), in Spanish, directly adjacent to the relevant practice or in a clearly referenced section.
6. Critical security discussion: no integrity with legacy AES-CBC; Base64 vs encryption; weak password-derived keys; obsolete RSA-1024 and `rsautl`; RSA message-size limitations; authenticity requirements in public-key exchange; hybrid-envelope integrity; risks of exposing secrets; certificate validity, revocation, hostname checks, CA hierarchy, and automation.
7. A comparative evaluation of expected and actual results, negative-test findings, limitations, and justified recommendations.
8. A **single coherent conclusion** connecting confidentiality, integrity, authenticity, operational TLS deployment, and trust validation; do not claim a property not demonstrated.
9. Real bibliography/references (prefer standards, official OpenSSL manual, Let's Encrypt/Certbot documentation; include accessed dates for dynamic online documentation); no fabricated citations.
10. Appendices with annotated command listings/scripts and an experiment/evidence index, without private keys or passphrases.

Use numbered figures and tables with informative Spanish captions and in-text references; avoid long unannotated screenshot dumps. Ensure legibility, correct spelling, consistency of terminology and units, and the ability to compile the final LaTeX document without missing dependencies or figures.

## 12. Suggested workspace output (not the final LaTeX target)

```text
openssl-academic-lab/
  README.md
  requirements-and-progress.md
  scripts/
  data/                 # sample/demo input only
  outputs/              # encrypted/decrypted demonstration artifacts
  evidence/
    screenshots/
    logs/
    evidence-index.md
  notes/
    report-draft-es.md
    references.md
    compatibility-and-limitations.md
  .gitignore
```

Keep `.gitignore` protective of `*_private.pem`, passphrase files, ACME account material, real cert private keys, credentials, and sensitive outputs. Do not commit large generated files unless useful, approved, and harmless. Preserve user-owned directories and files.

## 13. Execution order and stopping conditions

1. Read and inventory **both PDF guides**, extract every action and question into `requirements-and-progress.md` with page references.
2. Inspect the host environment and obtain approval for any privileged or public-domain actions.
3. Implement and verify symmetric, asymmetric, and hybrid cryptography, gathering genuine evidence continuously.
4. Draft/research the PKI theory and check its technical accuracy against authoritative sources.
5. Validate public HTTPS prerequisites with the user; if available, deploy Let's Encrypt, inspect the certificate chain, trust store, and renewal; otherwise document the precise blocker and follow-up commands without claiming completion.
6. Review all results, test failures, warnings, and source-guide inconsistencies. Produce a Spanish academic staging draft, figures/evidence index, scripts, and a completion table.
7. **Pause for the user to supply the LaTeX main file/project and instructions for integration.** Do not invent a target or modify unrelated `.tex` files.
8. Once supplied, integrate all content into **one** report in Spanish, compile it, inspect the generated PDF visually, and correct layout/bibliography/cross-references.
9. Give a brief status summary distinguishing **verified**, **blocked**, **requires approval**, and **not yet executed** tasks. Never state that the entire assignment is complete until the original requirements and genuine proof have been checked.

## 14. Acceptance checklist

- [ ] Full PDF 1 symmetric section executed, evidenced, and analyzed.
- [ ] Full PDF 1 Alice/Bob asymmetric section executed and evidenced, including reverse exchange.
- [ ] Full PDF 1 large-file hybrid section executed, with honest corrections of legacy command problems.
- [ ] All four PKI theory questions answered academically in Spanish.
- [ ] Real web-server/domain/Certbot challenge and HTTPS demonstrated **or explicitly blocked** with reason.
- [ ] All three Let's Encrypt questions answered, with validity-policy verification.
- [ ] All five certificate/chain/trust-store questions answered with evidence from the actual environment.
- [ ] Negative tests and exact original-vs-modern command differences documented.
- [ ] All screenshots and log outputs are real, annotated, redacted where necessary, and indexed.
- [ ] One Spanish academic report is drafted; later integrated into **the exact LaTeX file the user identifies**.
- [ ] Final LaTeX/PDF, when requested, compiles cleanly and includes figures, references, discussion, and conclusions.
