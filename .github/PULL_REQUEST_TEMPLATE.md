## Description

Please include a summary of the changes and the related issue. List any dependencies that are required for this change.

---

## Type of Change

- [ ] Bug fix (non-breaking change which fixes an issue)
- [ ] New feature (non-breaking change which adds functionality)
- [ ] Breaking change (fix or feature that would cause existing functionality to not work as expected)
- [ ] Documentation update

---

## Security Validation Checklist

- [ ] All database models contain a `tenant_id` column where applicable.
- [ ] SQLAlchemy event listeners and database-level RLS policies are applied.
- [ ] All new endpoints consume `verify_zero_trust` authentication gates.
- [ ] File uploads are validated via security scans and scripts are stripped.
- [ ] Prompts are sanitized using prompt injection protection utilities.
- [ ] Secrets and credentials are not hardcoded or committed to source control.

---

## Verification & Testing

- [ ] Pytest suite completes successfully with all tests passing.
- [ ] React frontend builds without compilation warnings.
- [ ] Manual test scenarios verified (e.g. device compliance blocking).
