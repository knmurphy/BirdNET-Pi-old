# Agent Instructions

This project uses **bd** (beads) for issue tracking. Run `bd onboard` to get started.

## Quick Reference

```bash
bd ready              # Find available work
bd show <id>          # View issue details
bd update <id> --status in_progress  # Claim work
bd close <id>         # Complete work
bd sync               # Sync with git
```

<!-- BEGIN BEADS INTEGRATION -->
## Issue Tracking with bd (beads)

**IMPORTANT**: This project uses **bd (beads)** for ALL issue tracking. Do NOT use markdown TODOs, task lists, or other tracking methods.

### Why bd?

- Dependency-aware: Track blockers and relationships between issues
- Git-friendly: Auto-syncs to JSONL for version control
- Agent-optimized: JSON output, ready work detection, discovered-from links
- Prevents duplicate tracking systems and confusion

### Quick Start

**Check for ready work:**

```bash
bd ready --json
```

**Create new issues:**

```bash
bd create "Issue title" --description="Detailed context" -t bug|feature|task -p 0-4 --json
bd create "Issue title" --description="What this issue is about" -p 1 --deps discovered-from:bd-123 --json
```

**Claim and update:**

```bash
bd update bd-42 --status in_progress --json
bd update bd-42 --priority 1 --json
```

**Complete work:**

```bash
bd close bd-42 --reason "Completed" --json
```

### Issue Types

- `bug` - Something broken
- `feature` - New functionality
- `task` - Work item (tests, docs, refactoring)
- `epic` - Large feature with subtasks
- `chore` - Maintenance (dependencies, tooling)

### Priorities

- `0` - Critical (security, data loss, broken builds)
- `1` - High (major features, important bugs)
- `2` - Medium (default, nice-to-have)
- `3` - Low (polish, optimization)
- `4` - Backlog (future ideas)

### Workflow for AI Agents

1. **Check ready work**: `bd ready` shows unblocked issues
2. **Claim your task**: `bd update <id> --status in_progress`
3. **Work on it**: Implement, test, document
4. **Discover new work?** Create linked issue:
   - `bd create "Found bug" --description="Details about what was found" -p 1 --deps discovered-from:<parent-id>`
5. **Complete**: `bd close <id> --reason "Done"`

### Auto-Sync

bd automatically syncs with git:

- Exports to `.beads/issues.jsonl` after changes (5s debounce)
- Imports from JSONL when newer (e.g., after `git pull`)
- No manual export/import needed!

### Important Rules

- ✅ Use bd for ALL task tracking
- ✅ Always use `--json` flag for programmatic use
- ✅ Link discovered work with `discovered-from` dependencies
- ✅ Check `bd ready` before asking "what should I work on?"
- ❌ Do NOT create markdown TODO lists
- ❌ Do NOT use external issue trackers
- ❌ Do NOT duplicate tracking systems

For more details, see README.md and docs/QUICKSTART.md.

<!-- END BEADS INTEGRATION -->

## Development Commands

### Python Backend
```bash
# Run tests
pytest

# Run single test
pytest tests/test_analysis.py::TestRunAnalysis::test_run_analysis

# Run tests in specific file
pytest tests/test_web_app.py

# Lint code
flake8

# Lint specific file
flake8 scripts/analysis.py
```

### React Frontend (cd into frontend/)
```bash
# Development server
npm run dev

# Production build
npm run build

# Lint code
npm run lint

# Preview production build
npm run preview
```

## Code Style Guidelines

### Python
- **Imports**: Stdlib → Third-party → Local (each group sorted alphabetically)
- **Naming**: snake_case for functions/variables, PascalCase for classes
- **Line length**: 160 chars (configured in .flake8)
- **Complexity**: Max 15 (configured in .flake8)
- **Docstrings**: Use """ format for modules, classes, functions
- **Type hints**: Use Optional, List, Dict from typing module
- **Testing**: Use unittest.TestCase; mock external dependencies with unittest.mock
- **Error handling**: Try/except with specific exceptions; raise HTTPException in API routes

### TypeScript/React
- **Components**: PascalCase filenames (DetectionCard.tsx), export named functions
- **Hooks**: camelCase filenames (useDetections.ts), prefix with "use"
- **Types**: Centralized in src/types/index.ts; use interface for object shapes
- **Imports**: Type imports first (`import type { X }`), then regular imports
- **CSS**: Separate .css files with BEM naming (className="block__element--modifier")
- **Comments**: JSDoc /** */ for functions and components
- **Props**: Define interfaces above components with inline comments for props
- **Functions**: Arrow functions for components; regular functions for utilities
- **State**: React useState/useReducer for local, TanStack Query for server state
- **Icons**: Do NOT use emoji as icons. Use SVG icons for consistent, accessible, and professional appearance

### Backend API
- **FastAPI routers**: One file per domain (detections.py, species.py, system.py)
- **Pydantic models**: Separate models.py files for request/response schemas
- **Database**: DuckDB (primary), SQLite (legacy); use context managers for connections
- **Routes**: GET/POST/PUT/DELETE; async functions for I/O operations
- **Error handling**: HTTPException with appropriate status codes (400, 404, 500)

## Deployment Workflow

**IMPORTANT**: This project runs on a remote Raspberry Pi. Code changes are NOT deployed until you run the deploy script.

### Deployment Scripts

| Script | Use Case |
|--------|----------|
| `./deploy.sh` | Frontend-only changes (builds React, syncs dist) |
| `./deploy-full.sh` | Full deploy (frontend + backend API changes) |
### Required Workflow

**ALWAYS follow this order:**

1. **Make code changes**
2. **Commit**: `git add -A && git commit -m "..."`
3. **Push**: `git push` - MUST succeed before deploying
4. **Deploy**: `./deploy-full.sh` (or `./deploy.sh` for frontend-only)

### Critical Rules

- **git push ≠ deployed** - Pushing only updates the remote repo
- **Deploy script runs on the Pi** - It pulls from git and restarts services
- **Backend changes need deploy-full.sh** - Use this for API/config changes
- **Frontend-only can use deploy.sh** - Faster, doesn't restart FastAPI

### What Gets Deployed

The Pi runs:
- FastAPI backend at `http://10.0.0.177:8003/api/*`
- React PWA at `http://10.0.0.177:8003/`
- Old PHP system at `http://10.0.0.177/` (legacy, untouched)

## Landing the Plane (Session Completion)

**When ending a work session**, you MUST complete ALL steps below. Work is NOT complete until `git push` succeeds.

**MANDATORY WORKFLOW:**

1. **File issues for remaining work** - Create issues for anything that needs follow-up
2. **Run quality gates** (if code changed) - Tests, linters, builds
3. **Update issue status** - Close finished work, update in-progress items
4. **PUSH TO REMOTE** - This is MANDATORY:
   ```bash
   git pull --rebase
   bd sync
   git push
   git status  # MUST show "up to date with origin"
   ```
5. **Clean up** - Clear stashes, prune remote branches
6. **Verify** - All changes committed AND pushed
7. **Hand off** - Provide context for next session

**CRITICAL RULES:**
- Work is NOT complete until `git push` succeeds
- NEVER stop before pushing - that leaves work stranded locally
- NEVER say "ready to push when you are" - YOU must push
- If push fails, resolve and retry until it succeeds
