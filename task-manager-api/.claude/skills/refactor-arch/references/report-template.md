# Template do relatório de auditoria

```markdown
# Architecture Audit — <project>

- Generated at: <ISO-8601>
- Stack: <language/framework/runtime>
- Files analyzed: <n>
- Architecture before: <summary>

## Summary
- CRITICAL: <n>
- HIGH: <n>
- MEDIUM: <n>
- LOW: <n>
- Total: <n>

## Findings

### [<SEVERITY>] <ID> — <title>
- File: `<path>:<start>-<end>`
- Evidence: `<sanitized evidence>`
- Description: <fact observed>
- Impact: <risk>
- Recommendation: <concrete action>
- Deprecated API: <not applicable or API/equivalent>

## Confirmation Gate
`Proceed with refactoring (Phase 3)? [y/n]`
Human confirmation: <answer and timestamp>

## Refactoring and validation
- Before/after structure: <summary>
- Boot: PASS/FAIL + command/result
- Health: PASS/FAIL + command/result
- Endpoint checks: PASS/FAIL + list
- Remaining risks: <list>
```
