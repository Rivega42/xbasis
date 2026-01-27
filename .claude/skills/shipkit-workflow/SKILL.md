---
name: shipkit-workflow
description: ShipKit documentation workflow for xbasis. Auto-loaded when working with docs/ files.
---

# ShipKit Documentation Workflow

## Document Hierarchy

```
Priority reading order:
1. CLAUDE.md        → Entry point, quick commands
2. docs/CONTEXT.md  → What is xbasis, architecture
3. docs/FEATURES.md → What's done, what's next
4. docs/SESSION.md  → Current session state
```

## When to Update Each Document

### docs/SESSION.md — EVERY session
```markdown
## Session: YYYY-MM-DD

### Completed
- [x] What was done

### In Progress
- [ ] What's being worked on

### Next Session TODO
- [ ] What to continue

### Blockers
- Any issues encountered
```

### docs/FEATURES.md — When feature status changes
```markdown
## Feature Name
- Status: 🔲 Planned | 🔄 In Progress | ✅ Done | ❌ Blocked
- Priority: P0 | P1 | P2
- Description: What it does
```

Status transitions:
- Starting work → 🔲 → 🔄
- Completing work → 🔄 → ✅
- Hit blocker → 🔄 → ❌

### docs/DECISIONS.md — When making architectural choices
```markdown
## ADR-XXX: Decision Title

**Date:** YYYY-MM-DD
**Status:** Proposed | Accepted | Deprecated

### Context
Why this decision is needed

### Decision
What we decided

### Alternatives Considered
- Option A: pros/cons
- Option B: pros/cons

### Consequences
- Positive: benefits
- Negative: tradeoffs
```

### docs/PROBLEMS.md — When encountering/solving issues
```markdown
## PROB-XXX: Problem Title

**Status:** 🔴 Open | 🟡 Investigating | 🟢 Resolved
**Severity:** Critical | High | Medium | Low

### Description
What's wrong

### Steps to Reproduce
1. Step one
2. Step two

### Solution (when resolved)
How it was fixed
```

### docs/CONTEXT.md — When architecture changes
- New service added
- Stack change
- Major refactoring
- New integration

### CHANGELOG.md — When releasing
```markdown
## [X.Y.Z] - YYYY-MM-DD

### Added
- New features

### Changed
- Modifications

### Fixed
- Bug fixes
```

## End of Session Checklist

```
□ docs/SESSION.md updated with:
  - What was completed
  - Current state
  - TODO for next session

□ docs/FEATURES.md — if any feature status changed

□ docs/DECISIONS.md — if any architectural decision was made

□ docs/PROBLEMS.md — if any problem found or resolved

□ Git commit with docs/ changes
```

## Quick Commands

```bash
# See what's changed
git diff docs/

# Commit documentation
git add docs/
git commit -m "docs: update session and features"
```
