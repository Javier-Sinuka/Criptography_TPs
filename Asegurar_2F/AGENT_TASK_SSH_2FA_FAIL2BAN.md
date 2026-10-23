# Agent Assignment — SSH Access Control, Two-Factor Authentication, and Fail2ban Laboratory

## 1. Role and primary objective

You are an autonomous coding and systems-engineering agent operating from VS Code on the user's computer. Your task is to **perform, verify, capture evidence of, and document** a Linux security laboratory covering all requirements in the following two user-provided references:

1. `Control de acceso en ssh sin todas las vm.pdf` — SSH access control, SSH keys, PAM authorization, and Fail2ban.
2. `Copia de Two-factor authentication (2FA).pdf` — SSH two-factor authentication using PAM and time-based one-time passwords.

Also follow the instructor's instructions: show the **sequence of actions performed and the actual results**, supply authentic screenshots, include a short introduction and conclusion, explain the importance and appropriate use cases of the tools, and organize scripts/resources in a repository.

**MANDATORY LANGUAGE REQUIREMENT: The entire final academic report must be written in SPANISH (es-AR).** This assignment file is in English only to instruct the agent. The final deliverable is **ONE UNIFIED REPORT**, not separate reports for SSH, PAM, 2FA, and Fail2ban. Use a formal but readable academic style in Spanish; commands, configuration keys, output excerpts, and technical proper nouns may remain in their original form.

## 2. Critical instruction about the LaTeX report

**The user will subsequently tell you which existing LaTeX `.tex` file or LaTeX project to use.**

- Do **not** arbitrarily select, replace, or create a competing main LaTeX template before the user identifies the target file/project.
- You may immediately inspect the references, prepare the lab, collect evidence, and draft report content in intermediate files.
- Once the user specifies the LaTeX target, **edit that exact target**, respecting its class, packages, layout, cover, university branding, author fields, sectioning conventions, bibliography mechanism, and build workflow.
- If the user has not yet supplied the file, request it **only when you reach the report integration step**; do not let this block independent lab work.
- Produce **one compilable Spanish-language LaTeX report and its corresponding PDF**, with all activities integrated coherently, after the target is identified. Do not overwrite unrelated files.

## 3. Execution requirements and boundaries

1. **Actually execute the laboratory, not merely describe it.** Command logs, service states, login tests, screenshots, and conclusions must correspond to real executions.
2. Before modifying anything, discover the host OS, virtualization availability, existing VM(s), available memory/disk, required tools, network configuration, and user privileges. Prefer Debian or a Debian-derived guest VM, as recommended by the instructor. Use existing suitable infrastructure if present.
3. **Protect the host machine.** Never alter the host's SSH/PAM login policy, host firewall, or real user accounts for the sake of the exercise. Carry out access restrictions, lockout tests, and blocking **inside an isolated guest VM**. VM creation, package installation, and any sudo/superuser operations must follow the user's permission/approval policy. Do not assume you have unconditional privileges.
4. Prefer VirtualBox + `VBoxManage` when installed and usable; otherwise evaluate another supported virtualization solution. Take a **pre-lab VM snapshot** and snapshots before significant authentication changes. Back up every configuration file before editing it.
5. Ensure a viable network path between a test client and the server. The references suggest NAT, but basic VirtualBox NAT does not necessarily allow direct host-to-guest SSH without port forwarding. Configure **NAT with appropriate forwarding, NAT Network, or host-only networking** as appropriate; explain the actual topology, IPs, port mappings, and any deviations. Use a second guest only when necessary, not merely because the example mentions a second server.
6. Keep a working VM console or pre-existing SSH session while changing authentication. Use a **second connection** to test changes. Before reloading SSH, validate its config with `sshd -t`; where feasible inspect effective settings with `sshd -T`. Provide a rollback method and preserve a recovery path.
7. No real-world brute forcing or unauthorized third-party targets. All failed login attempts must be controlled and directed only at the local lab VM from an authorized lab client. Do not risk banning your only management channel; use the guest console or an allowlisted management source for recovery.
8. **Do not disclose secrets** in screenshots, commits, logs, report, or chat: private SSH keys, TOTP shared secrets, live QR codes / `otpauth://` URLs, recovery codes, real passwords, and usable current OTPs. Redact evidence as needed. Store any transient test secrets securely outside version control; remove them when no longer needed.
9. Never fabricate screenshot images, command output, successful test results, timestamps, firewall bans, or measurements. If something cannot run, say exactly why, keep reproducible scripts, and mark it as not verified rather than claiming success.
10. Keep changes repeatable and reviewable. Prefer small configuration overlays (for example `/etc/fail2ban/jail.d/sshd.local`) rather than cloning entire vendor defaults, unless reproducing the instructions requires demonstrating the alternative. Record justified differences from older tutorial syntax.

## 4. Phase A — Laboratory discovery and preparation

- Inspect the two PDFs completely, including their screenshots and any optional sections. Treat them as the assignment's source of truth for **scope**, while identifying outdated commands, typos, inconsistencies, or unsafe practices and explaining justified corrections.
- Record host and guest platform versions (OS, kernel, OpenSSH, Fail2ban, PAM module, VM platform), plus network arrangement.
- Provision/configure Debian guest (or explain a suitable Debian-derived alternative); install and enable OpenSSH server and required supporting tools. Verify IP addresses using `ip address`/`ip addr`.
- Create an initial snapshot and configuration backups; set up an evidence directory with ordered filenames, command transcripts, and a dated test log. Screenshots should contain legible terminal output and relevant contextual identifiers, but no secrets.
- Create a working repository layout such as `scripts/`, `configs/`, `evidence/screenshots/`, `evidence/logs/`, `report/`, and `README.md`. Provide reproducible setup, test, recovery, and clean-up instructions. Do not commit confidential values, VM disks, or private credentials.

## 5. Phase B — SSH keys and access control (first PDF)

Perform and document the following, with explicit **expected vs. observed** results:

1. Explain how SSH encrypts communication, how asymmetric SSH key authentication works, how a private-key passphrase differs from an account password, and the role of `ssh-agent`.
2. Generate a **dedicated lab** Ed25519 key pair (`ssh-keygen -t ed25519`), ideally with a passphrase, without overwriting personal existing keys. Inspect only the **public** key (`.pub`) and verify correct permissions. Demonstrate the use of `ssh-agent` when practical.
3. Answer the PDF's question: **Which algorithms does SSH support, and is RSA still supported/relevant?** Distinguish RSA key material from deprecated SHA-1 `ssh-rsa` signatures; describe the modern alternatives and compatibility caveats. Validate supported algorithms on the installed version when possible.
4. Test SSH from the client to the guest using a normal lab user. Test `root` access and explain why it is enabled or denied by the guest's effective policy. Test the accounts available in the lab and record results, without exposing passwords.
5. Install the client's **public** key on the guest with `ssh-copy-id` (including the `-i` identity option when appropriate), inspect `~/.ssh/authorized_keys`, and verify verbose key-based login (`ssh -v`, with focused, sanitized excerpts). Demonstrate use of `-i` and `IdentitiesOnly=yes`.
6. Disable SSH **password authentication** (`PasswordAuthentication no`) only **after** proving key-based login and preserving recovery access; test that key-based login still works and a password-only attempt fails. Document why `PasswordAuthentication no` does not, on its own, necessarily disable PAM keyboard-interactive authentication.
7. Explain SSH client config precedence: command-line options, `~/.ssh/config`, `/etc/ssh/ssh_config`. Explicitly distinguish the client `ssh_config` from server `sshd_config`.
8. Create the example unprivileged user `nonpriv`; test local switching (`su`) and remote login before and after granting this account appropriate SSH access; explain why the initial SSH connection may fail and how to authorize a public key for this account.
9. Examine `AuthorizedKeysFile` and demonstrate or document a centrally managed authorized-key path such as `/etc/ssh/authorized-keys/%u` if feasible, including required directory ownership and permissions. Explain management trade-offs. Discuss `AuthorizedKeysCommand` and `AuthorizedKeysCommandUser` as centralized lookup mechanisms, including audit/security implications; no external LDAP is required.
10. Configure a creative ASCII-art SSH **pre-authentication banner** with the `Banner` directive and a correctly located file (on Debian typically `/etc/ssh/sshd_config` rather than `/etc/sshd_config`). Verify it appears during SSH negotiation. Keep it professional and appropriate for an academic exercise.
11. Demonstrate PAM `pam_listfile.so` **denylist** access control with a file such as `/etc/ssh/ssh.deny`, including entries such as `nonpriv` or a designated lab user. Check that an account can be valid for local login but denied for SSH and inspect relevant `auth.log` or `journalctl` evidence.
12. Demonstrate the **allowlist** alternative with `sense=allow`, e.g. `/etc/ssh/ssh.allow`. Test one authorized and one unauthorized account. Explain when denylist vs. allowlist makes more sense.
13. For PAM authorization, inspect `UsePAM`, public-key authentication, `KbdInteractiveAuthentication`/legacy `ChallengeResponseAuthentication`, and `AuthenticationMethods`. Ensure the configured methods **actually invoke** the intended PAM checks. Avoid relying on PAM `auth` rules that could be bypassed by successful public-key-only authentication. Document the exact verified arrangement and avoid incompatible combinations with the later 2FA experiment.
14. Answer the reflection questions from the first PDF with evidence and security rationale.

## 6. Phase C — SSH two-factor authentication (second PDF)

Perform an end-to-end **SSH public key + TOTP** test in the guest. Include the following:

1. Explain MFA/2FA, the factor categories (knowledge, possession, inherence), why public-key-only SSH is still a single authentication factor, and the operation of TOTP, including its usual 30-second refresh interval.
2. Explain Linux PAM's purpose and modular architecture. Install `libpam-google-authenticator` in Debian and verify installation.
3. For a designated test user, initialize `google-authenticator` with **time-based** tokens. Follow/document the questions in the guide: write the per-user `~/.google_authenticator` file; disallow token reuse; retain the normal time-skew window rather than expanding it unnecessarily; enable rate limiting. Describe recovery-code protection.
4. Where a physical phone is available, the guide suggests **FreeOTP+**. If a mobile-authenticator QR enrollment requires user action, ask the user to do only that action when needed. Alternatively, for an authorized and clearly labeled automated lab, use a locally generated TOTP verifier/client **only if** it demonstrably performs the same cryptographic TOTP step. Never represent a software-emulated authenticator as having been used on a physical phone.
5. Back up `/etc/pam.d/sshd` and `/etc/ssh/sshd_config`. Configure PAM's `pam_google_authenticator.so` and the necessary OpenSSH options (including `UsePAM yes`, `PubkeyAuthentication yes`, `KbdInteractiveAuthentication yes` on modern releases, and `AuthenticationMethods publickey,keyboard-interactive`). Examine and justify the use of `nullok` (optional rollout vs. mandatory 2FA); **the final tested protected user must not be able to bypass the second factor**. If password authentication is not desired, carefully adjust PAM `common-auth` behavior for this controlled test and explain the effect.
6. Test access from a second client session. Show that a recognized public key alone is insufficient; that a correct, current TOTP permits login; that a wrong/expired token fails; and that an absent/incorrect SSH private key fails even with a valid TOTP. Capture sanitized verbose SSH and authentication logs showing the multi-stage process.
7. If feasible, demonstrate the guide's **optional third-factor** mode (SSH key + account password + TOTP), then return to a known, functioning required 2FA configuration. Avoid unnecessarily locking out lab users.
8. Explain and, when safe, demonstrate recovery paths: VM console access, safeguarded recovery codes, securely re-enrolling/recreating a TOTP secret, and the consequence of losing the device. **Never print or commit the actual secret/recovery codes**.
9. Cover the guide's **optional configuration-management** topics: modifications to `~/.google_authenticator` (reuse, token window, rate limits, emergency codes), per-account MFA exceptions (`nullok`) and their security consequences, and unattended automation via supported `google-authenticator --help` arguments. A conceptual or sandbox demonstration is sufficient for optional exceptions/automation, but distinguish demonstrated vs. explained features.
10. Document which PAM and SSH settings belong to the particular phase being tested. **Do not combine denylist, allowlist, 2FA and third-factor changes blindly**; use staged snapshots or reversible configurations so every positive/negative test is interpretable.

## 7. Phase D — Fail2ban (first PDF and explicit instructor requirement)

The first PDF labels Fail2ban as an extension, but **the instructor's overarching request explicitly requires configuring Fail2ban**, so it is mandatory for this submission.

1. Explain what Fail2ban does, how jails, log filters and firewall actions relate, and what threats it can mitigate even when SSH keys make password guessing impractical.
2. Install `fail2ban` and an appropriate firewall backend (`iptables` where appropriate; on modern Debian determine whether nftables/iptables-nft is active). Verify the service is running.
3. Configure an enabled `[sshd]` jail with **`bantime = 10m`, `findtime = 10m`, and `maxretry = 5`**, reflecting the guide, or document a justified small lab-specific variant. Use the correct property **`enabled = true`** (the PDF shows `enable = true`, which should be checked/corrected). On systems with systemd journaling and no `/var/log/auth.log`, configure an appropriate `backend = systemd` if necessary.
4. Run `fail2ban-client status` and `fail2ban-client status sshd`. Demonstrate actual detection of failed SSH authentication attempts, originating from a **separate client IP** with an available recovery path. Since password login may already be disabled, choose a test method that produces log events recognized by the active Fail2ban SSH filter; do not silently assume failed passwords are available. Explain and show that the jail reaches its threshold.
5. Verify the ban using `fail2ban-client status sshd`, Fail2ban logs, and the actual firewall backend (`iptables -L` or relevant nftables listings). Show that the blocked connection is prevented, with a genuine client-side result. Do not infer a firewall rule exists from logs alone.
6. Demonstrate a controlled unban using `sudo fail2ban-client set sshd unbanip <LAB_CLIENT_IP>`, verify the rule was removed, and retest access.
7. Answer the first PDF's questions: What happens after repeated failed logins? What does the firewall listing show? Which other services may Fail2ban monitor? Can it issue alerts when a jail triggers, and how?
8. Describe deployment scenarios where Fail2ban adds value, and its limitations (e.g., distributed attacks, shared/NAT source IPs, accidental lockouts, log dependencies).

## 8. Required experiment matrix and evidentiary standard

Create a test matrix covering **at least** these scenarios, preserving real outputs and pass/fail observations:

- Guest reachability and OpenSSH service availability.
- Normal-user SSH login before key configuration.
- Root SSH login result under the effective policy.
- Successful public-key login; failure when the key is absent/wrong.
- Password-only SSH failure after password login is disabled.
- `nonpriv` initial login behavior and login after deliberate authorization.
- SSH banner display.
- PAM denylist rejects listed user; permits suitable unlisted user.
- PAM allowlist permits listed user; rejects unlisted user.
- MFA: valid SSH key + correct TOTP succeeds.
- MFA: valid SSH key without correct TOTP fails.
- MFA: wrong SSH key + correct TOTP fails.
- Fail2ban jail starts and reports status.
- Failed logins trigger an actual Fail2ban source-IP ban.
- Firewall backend exhibits the ban; subsequent request is blocked.
- Manual unban succeeds; authorized connection recovers.
- Any optional three-factor or recovery experiments that were genuinely performed.

For each row record: test ID, purpose, starting config/snapshot, command or reproducible procedure, expected result, **actual** result, evidence file names, and pass/fail/blocker. Identify whether an output belongs to the host, VM server, or VM/client. Capture both positive and negative outcomes, including configuration validation and service restarts. Prefer actual desktop screenshots (`gnome-screenshot`, `scrot`, or comparable screenshot utilities) where possible; otherwise provide accurate terminal captures exported with a clearly labeled tool, not mocked GUI screenshots. Use redaction on copies of actual evidence.

## 9. ONE final report: required Spanish structure

Once the user designates the LaTeX file, integrate all findings into **one cohesive academic report in Spanish**. Follow the supplied LaTeX template above all stylistic preferences. Suggested headings (adapt to the template):

1. **Portada** — retain original template metadata and placeholders unless the user provides real details.
2. **Resumen y objetivos** — scope of the complete exercise.
3. **Introducción y fundamentos teóricos** — SSH, asymmetric keys, PAM, 2FA/TOTP, Fail2ban, defense in depth, and appropriate use cases.
4. **Entorno de trabajo y metodología** — host/guest, versions, VM snapshots, network topology, security precautions, backups, reproducibility.
5. **Desarrollo: control de acceso SSH** — chronological actions, configuration, screenshots and outcomes, user/key management, SSH banner, allow/deny policies.
6. **Desarrollo: autenticación de dos factores** — PAM setup, registration procedure (without exposing secrets), SSH integration, successful/failed MFA tests, recovery and relevant optional aspects.
7. **Desarrollo: protección mediante Fail2ban** — jail setup, failed-login experiment, source-IP ban, firewall verification, unban and reconnection.
8. **Resultados y análisis** — consolidate all experimental outcomes into one concise matrix; explain anomalies and important limitations; distinguish observed from theoretical claims.
9. **Discusión y respuestas a las preguntas de las guías** — supported SSH algorithms/RSA, root login, `nonpriv`, denylist vs. allowlist, PAM and factor interactions, Fail2ban scope and alerts, optional recovery and third-factor considerations.
10. **Conclusiones** — importance, trade-offs, where each mechanism does/does not make sense, practical lessons, and what the experiments actually demonstrated.
11. **Referencias** — both supplied guides and any vendor/manpage documentation genuinely used; distinguish sources from personal test findings.
12. **Anexos (as appropriate)** — commands, abbreviated sanitized configuration snippets, script references, supplementary screenshots; avoid unnecessarily duplicating the entire command transcript in the body.

Each main stage should show the **sequence of actions and outcomes**, not simply paste a list of shell commands. Use numbered figures with useful Spanish captions, readable screenshots, cross-references and tables. Do not include the same screenshot repeatedly. Ensure image paths work when the LaTeX document is compiled. Compile with the template's existing build system, resolve errors and overfull/illegible elements, and inspect the final PDF for readability. Aim for thoroughness without padding.

## 10. Deliverables and completion conditions

- One **final `.tex`-based Spanish report** integrated into the exact LaTeX target supplied in a subsequent instruction, plus **one compiled final PDF**.
- Reproducible setup/configuration/test and rollback scripts, with README instructions.
- Sanitized, genuine screenshots and relevant command/log excerpts.
- A single test matrix with real observed results and any limitations explicitly noted.
- A clean repository layout and `.gitignore` protecting keys, tokens, recovery material, `.env` secrets, VM artifacts, and temporary files.
- A short closing status for the user: which phases passed, which were partially verified or blocked, where to find evidence, and where the unified LaTeX/PDF report was generated.

**Do not declare the work finished unless the experiments have actually run, evidence has been captured, the specified LaTeX file has been updated, and the single Spanish PDF has been successfully compiled.** If a step needs user intervention (VM permission, sudo authorization, phone enrollment, or LaTeX target selection), clearly state the minimal concrete action required, then proceed with independent tasks.

## 11. Suggested workflow

Start by inspecting the two PDFs and auditing the local execution environment. Present a brief implementation plan and any unavoidable approval requests. Then build and snapshot the isolated Debian lab, run the SSH/PAM/2FA/Fail2ban tests incrementally, collect sanitized evidence, and prepare the Spanish report content. **Wait for the user's later instruction identifying the exact LaTeX file before integrating or compiling the final report.**
