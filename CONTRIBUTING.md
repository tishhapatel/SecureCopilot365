# Contributing to SecureCopilot 365

Thank you for your interest in contributing to SecureCopilot 365! This document outlines our setup, branching, pull request, and coding standards.

---

## 1. Setup Guidelines

1.  **Fork the Repository**: Create a fork of the repository under your own GitHub profile.
2.  **Clone the Project**: Clone your fork locally:
    ```bash
    git clone https://github.com/<your-username>/SecureCopilot365.git
    cd SecureCopilot365
    ```
3.  **Configure remotes**: Add the upstream repository:
    ```bash
    git remote add upstream https://github.com/tishhapatel/SecureCopilot365.git
    ```

---

## 2. Branching & Git Commit Policies

*   **Main branch**: The `main` branch represents the stable production code. No direct changes are permitted.
*   **Feature Branches**: Branch names should follow standard naming conventions:
    *   `feature/feature-name` for new features.
    *   `bugfix/bug-description` for bug fixes.
    *   `docs/doc-description` for documentation additions.
*   **Commit Messages**: Keep commit messages clear and descriptive:
    *   `feat: add Azure Key Vault integration`
    *   `fix: resolve SQLite database thread lock`

---

## 3. Pull Request Guidelines

Before submitting a pull request, ensure:
1.  **Tests pass**: Run the backend and frontend tests locally:
    ```bash
    pytest
    ```
2.  **Linting**: Format your code to align with style requirements (such as PEP 8 for Python and ESLint for TypeScript).
3.  **Detailed description**: Complete the provided [pull request template](file:///d:/SecureCopilot365/.github/PULL_REQUEST_TEMPLATE.md) detailing the changes and verification steps.

---

## 4. Coding Standards

*   **Python**: Format python code using standard practices (PEP 8 alignment). Expose clear docstrings and typing parameters.
*   **TypeScript/React**: Use functional components, explicit TypeScript typings, and Tailwind CSS.
*   **Security Gating**: Secure all backend endpoints using standard dependency gates (`verify_zero_trust`). Ensure all data models have a `tenant_id` column.
