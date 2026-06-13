# Security Policy — SecureCopilot 365

We take the security of SecureCopilot 365 seriously. This document outlines our vulnerability disclosure policy and security response guidelines.

---

## 1. Supported Versions

We actively maintain and support the current major release:

| Version | Supported |
| :--- | :--- |
| **1.x** | Yes |
| **< 1.0** | No |

---

## 2. Reporting a Vulnerability

**Please do not report security vulnerabilities via public GitHub issues.** 

If you discover a security vulnerability, please report it privately:
1.  **Email**: Send reports to [security@securecopilot365.com](mailto:security@securecopilot365.com).
2.  **Details**: Include a detailed description of the vulnerability, steps to reproduce, and a proof of concept (PoC) if available.

### 2.1 Encryption Key
To encrypt your message, please use our PGP key:
```
-----BEGIN PGP PUBLIC KEY BLOCK-----
Version: OpenPGP.js v4.10.1
Comment: SecureCopilot Security PGP Key
[MOCK-PGP-PUBLIC-KEY-DATA]
-----END PGP PUBLIC KEY BLOCK-----
```

---

## 3. Our Response Timeline

*   **Acknowledgment**: We will acknowledge receipt of your report within **48 hours**.
*   **Assessment**: We will evaluate the vulnerability and assign a risk rating (e.g. CVSS) within **5 business days**.
*   **Remediation**: We aim to resolve vulnerabilities and publish patches within **30 days** of disclosure.
*   **Disclosure**: We coordinates public disclosures with reporters after a patch has been released.
