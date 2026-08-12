# Security policy

## Supported versions

DocuRule is currently pre-1.0. Security fixes are applied to the latest release on the `main` branch.

## Report a vulnerability

Please do not open a public issue for a suspected vulnerability. Use GitHub's **Security → Report a vulnerability** private reporting flow after the repository is published.

Include the affected version, reproduction steps, impact, and any suggested mitigation. Do not include live credentials or non-synthetic documents. We aim to acknowledge reports within 72 hours and will coordinate disclosure after a fix is available.

## Deployment boundary

The MVP is designed for trusted local or private-network use. It does not yet provide authentication, tenant isolation, malware scanning, or hardened internet-facing deployment. Do not expose it directly to the public internet. Treat uploaded documents and exported audit records as sensitive data, and protect the Docker volume accordingly.
