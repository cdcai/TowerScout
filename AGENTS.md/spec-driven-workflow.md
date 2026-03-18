# Spec Driven Workflow v1

**Specification-Driven Workflow:**
Bridge the gap between requirements and implementation.

**Maintain these artifacts at all times:**

- **`requirements.md`**: User stories and acceptance criteria in structured EARS notation.
- **`design.md`**: Technical architecture, sequence diagrams, implementation considerations.
- **Task Management Files**: Multi-file task organization for optimal workflow support:
  - **`current-tasks.md`**: Active sprint tasks and immediate work (primary source of truth for current work)
  - **`task-backlog.md`**: Future tasks organized by priority and dependencies
  - **`completed-tasks.md`**: Historical task completion record (last 4 weeks + archived)
- **Individual task files**: `.agent_work/tasks/TASK-XXX-brief-name.md` for detailed task execution tracking (Type B/C only).
- **Context Documentation**: Organized supporting documentation:
  - **`context/guides/`**: User-facing documentation, setup guides, deployment instructions
  - **`context/analysis/`**: Technical reality checks, provider comparisons, architecture assessments
  - **`context/status/`**: Progress tracking, workflow documents, commit readiness reports

## Integration Guidelines

### Request Classification

**Type A (Quick Fixes):**
- Bug fixes, typos, small configuration changes
- Use abbreviated workflow focusing on implementation
- Document with streamlined action logs
- Skip formal requirements.md/design.md creation
- Examples: Fix import errors, update dependencies, correct documentation

**Type B (Feature Development):**
- New functionality, UI enhancements, API endpoints
- Full spec-driven approach with all 6 phases per `AGENTS.md/spec-driven-workflow.md`
- Follow multi-file task management and context organization protocols
- Comprehensive testing and validation required
- Examples: Add new map providers, create new detection algorithms, implement advanced UI features

**Type C (Architecture Changes):**
- Security fixes, performance optimization, major refactoring
- Enhanced documentation requirements
- Create decision records for all architectural choices
- Full impact analysis and migration planning
- Examples: API key security fix, model optimization, major refactoring

### User Interaction Protocol

**Confirmation Points:**
- Always confirm before IMPLEMENT phase for Type B/C requests
- Ask for approval when Confidence Score < 85% for any request type
- Provide progress updates during operations exceeding 30 seconds
- Request clarification when requirements are ambiguous

**Autonomous Execution:**
- Type A requests can proceed without confirmation if Confidence Score > 85%
- Continue through VALIDATE and REFLECT phases without interruption
- Auto-create technical debt issues and decision records

**Communication Style:**
- Use clear phase indicators: "ANALYZING", "DESIGNING", "IMPLEMENTING", etc.
- Provide estimated completion times for multi-step operations
- Summarize key decisions and trade-offs made

### TowerScout Workspace Integration

**Follow `AGENTS.md/spec-driven-workflow.md` for:**
- Task management protocols (current-tasks.md, task-backlog.md, completed-tasks.md)
- File organization and context documentation structure
- Maintenance schedules and archival strategies

**TowerScout-Specific Constraints:**
- **ML Model Protection**: Never modify core detection logic in `ts_yolov5.py` or `ts_en.py`
- **Legacy Feature Preservation**: All production-critical features must remain operational
- **Performance Requirements**: Support <100 tiles in approx. 30 seconds, 8GB RAM constraints
- **Context Priorities**: Prioritize outbreak investigation workflow documentation

**Project Structure Reference:**
```
.agent_work/
  current-tasks.md                   # Active sprint tasks (primary source for current work)
  task-backlog.md                    # Future tasks prioritization
  completed-tasks.md                 # Historical completions (last 4 weeks)
  requirements.md
  design.md
  decisions/
  context/
    guides/                          # Setup guides, deployment docs
    analysis/                        # Technical assessments
    status/                          # Progress tracking
    archive/                         # Archived context files
  tasks/
    active/                          # Symlinks to current individual task files
    completed/                       # Completed individual task files
    [transition files]               # New tasks before organization
```

## Universal Documentation Framework

**Documentation Rule:**
Use the detailed templates as the **primary source of truth** for all documentation.

**Summary formats:**
Use only for concise artifacts such as changelogs and pull request descriptions.

### Detailed Documentation Templates

#### Action Documentation Template (All Steps/Executions/Tests)

```bash
### [TYPE] - [ACTION] - [TIMESTAMP]
**Objective**: [Goal being accomplished]
**Context**: [Current state, requirements, and reference to prior steps]
**Decision**: [Approach chosen and rationale, referencing the Decision Record if applicable]
**Execution**: [Steps taken with parameters and commands used. For code, include file paths.]
**Output**: [Complete and unabridged results, logs, command outputs, and metrics]
**Validation**: [Success verification method and results. If failed, include a remediation plan.]
**Next**: [Automatic continuation plan to the next specific action]
```

#### Decision Record Template (All Decisions)

```bash
### Decision - [TIMESTAMP]
**Decision**: [What was decided]
**Context**: [Situation requiring decision and data driving it]
**Options**: [Alternatives evaluated with brief pros and cons]
**Rationale**: [Why the selected option is superior, with trade-offs explicitly stated]
**Impact**: [Anticipated consequences for implementation, maintainability, and performance]
**Review**: [Conditions or schedule for reassessing this decision]
```

### Summary Formats (for Reporting)

#### Streamlined Action Log

For generating concise changelogs. Each log entry is derived from a full Action Document.

`[TYPE][TIMESTAMP] Goal: [X] -> Action: [Y] -> Result: [Z] -> Next: [W]`

#### Compressed Decision Record

For use in pull request summaries or executive summaries.

`Decision: [X] | Rationale: [Y] | Impact: [Z] | Review: [Date]`

## Execution Workflow (6-Phase Loop)

**Never skip any step. Use consistent terminology. Reduce ambiguity.**

### **Phase 1: ANALYZE**

**Objective:**

- Understand the problem.
- Analyze the existing system.
- Produce a clear, testable set of requirements.
- Think about the possible solutions and their implications.

**Checklist:**

- [ ] Read all provided code, documentation, tests, and logs.
      - Document file inventory, summaries, and initial analysis results.
- [ ] Define requirements in **EARS Notation**:
      - Transform feature requests into structured, testable requirements.
      - Format: `WHEN [a condition or event], THE SYSTEM SHALL [expected behavior]`
- [ ] Identify dependencies and constraints.
      - Document a dependency graph with risks and mitigation strategies.
- [ ] Map data flows and interactions.
      - Document system interaction diagrams and data models.
- [ ] Catalog edge cases and failures.
      - Document a comprehensive edge case matrix and potential failure points.
- [ ] Assess confidence.
      - Generate a **Confidence Score (0-100%)** based on clarity of requirements, complexity, and problem scope.
      - Document the score and its rationale.

**Critical Constraint:**

- **Do not proceed until all requirements are clear and documented.**

### **Phase 2: DESIGN**

**Objective:**

- Create a comprehensive technical design and a detailed implementation plan.

**Checklist:**

- [ ] **Define adaptive execution strategy based on Confidence Score:**
  - **High Confidence (>85%)**
    - Draft a comprehensive, step-by-step implementation plan.
    - Skip proof-of-concept steps.
    - Proceed with full, automated implementation.
    - Maintain standard comprehensive documentation.
  - **Medium Confidence (66-85%)**
    - Prioritize a **Proof-of-Concept (PoC)** or **Minimum Viable Product (MVP)**.
    - Define clear success criteria for PoC/MVP.
    - Build and validate PoC/MVP first, then expand plan incrementally.
    - Document PoC/MVP goals, execution, and validation results.
  - **Low Confidence (<66%)**
    - Dedicate first phase to research and knowledge-building.
    - Use semantic search and analyze similar implementations.
    - Synthesize findings into a research document.
    - Re-run ANALYZE phase after research.
    - Escalate only if confidence remains low.

- [ ] **Document technical design in `design.md`:**
  - **Architecture:** High-level overview of components and interactions.
  - **Data Flow:** Diagrams and descriptions.
  - **Interfaces:** API contracts, schemas, public-facing function signatures.
  - **Data Models:** Data structures and database schemas.

- [ ] **Document error handling:**
  - Create an error matrix with procedures and expected responses.

- [ ] **Define unit testing strategy.**

- [ ] **Create implementation plan in `current-tasks.md` and `task-backlog.md`:**
  - For each task, include description, expected outcome, and dependencies.

**Critical Constraint:**

- **Do not proceed to implementation until design and plan are complete and validated.**
- **Always ask for approval before moving to the IMPLEMENT phase for each task.**

### **Phase 3: IMPLEMENT**

**Objective:**

- Write production-quality code according to the design and plan.

**Checklist:**

- [ ] Code in small, testable increments.
      - Document each increment with code changes, results, and test links.
- [ ] Implement from dependencies upward.
      - Document resolution order, justification, and verification.
- [ ] Follow conventions.
      - Document adherence and any deviations with a Decision Record.
- [ ] Add meaningful comments.
      - Focus on intent ("why"), not mechanics ("what").
- [ ] Create files as planned.
      - Document file creation log.
- [ ] Update task status in real time.

**Critical Constraint:**

- **Do not merge or deploy code until all implementation steps are documented and tested.**

### **Phase 4: VALIDATE**

**Objective:**

- Verify that implementation meets all requirements and quality standards.

**Checklist:**

- [ ] Execute automated tests.
      - Document outputs, logs, and coverage reports.
      - For failures, document root cause analysis and remediation.
- [ ] Perform manual verification if necessary.
      - Document procedures, checklists, and results.
- [ ] Test edge cases and errors.
      - Document results and evidence of correct error handling.
- [ ] Verify performance.
      - Document metrics and profile critical sections.
- [ ] Log execution traces.
      - Document path analysis and runtime behavior.

**Critical Constraint:**

- **Do not proceed until all validation steps are complete and all issues are resolved.**

### **Phase 5: REFLECT**

**Objective:**

- Improve codebase, update documentation, and analyze performance.

**Checklist:**

- [ ] Refactor for maintainability.
      - Document decisions, before/after comparisons, and impact.
- [ ] Update all project documentation.
      - Ensure all READMEs, diagrams, and comments are current.
- [ ] Identify potential improvements.
      - Document backlog with prioritization.
- [ ] Validate success criteria.
      - Document final verification matrix.
- [ ] Perform meta-analysis.
      - Reflect on efficiency, tool usage, and protocol adherence.
- [ ] Auto-create technical debt issues.
      - Document inventory and remediation plans.

**Critical Constraint:**

- **Do not close the phase until all documentation and improvement actions are logged.**

### **Phase 6: HANDOFF**

**Objective:**

- Package work for review and deployment, and transition to next task.

**Checklist:**

- [ ] Generate executive summary.
      - Use **Compressed Decision Record** format.
- [ ] Prepare pull request (if applicable):
    1. Executive summary.
    2. Changelog from **Streamlined Action Log**.
    3. Links to validation artifacts and Decision Records.
    4. Links to final `requirements.md`, `design.md`, `current-tasks.md`, and `completed-tasks.md`.
- [ ] Finalize workspace.
      - Archive intermediate files, logs, and temporary artifacts to `.agent_work/`.
- [ ] Continue to next task.
      - Document transition or completion.

**Critical Constraint:**

- **Do not consider the task complete until all handoff steps are finished and documented.**

## Troubleshooting and Retry Protocol

**If you encounter errors, ambiguities, or blockers:**

**Checklist:**

1. **Re-analyze**:
   - Revisit the ANALYZE phase.
   - Confirm all requirements and constraints are clear and complete.
2. **Re-design**:
   - Revisit the DESIGN phase.
   - Update technical design, plans, or dependencies as needed.
3. **Re-plan**:
   - Adjust the implementation plan in `tasks.md` to address new findings.
4. **Retry execution**:
   - Re-execute failed steps with corrected parameters or logic.
5. **Escalate**:
   - If the issue persists after retries, follow the escalation protocol.

**Critical Constraint:**

- **Never proceed with unresolved errors or ambiguities. Always document troubleshooting steps and outcomes.**

## Technical Debt Management (Automated)

### Identification and Documentation

- **Code Quality**: Continuously assess code quality during implementation using static analysis.
- **Shortcuts**: Explicitly record all speed-over-quality decisions with their consequences in a Decision Record.
- **Workspace**: Monitor for organizational drift and naming inconsistencies.
- **Documentation**: Track incomplete, outdated, or missing documentation.

### Auto-Issue Creation Template

```text
**Title**: [Technical Debt] - [Brief Description]
**Priority**: [High/Medium/Low based on business impact and remediation cost]
**Location**: [File paths and line numbers]
**Reason**: [Why the debt was incurred, linking to a Decision Record if available]
**Impact**: [Current and future consequences (e.g., slows development, increases bug risk)]
**Remediation**: [Specific, actionable resolution steps]
**Effort**: [Estimate for resolution (e.g., T-shirt size: S, M, L)]
```

### Remediation (Auto-Prioritized)

- Risk-based prioritization with dependency analysis.
- Effort estimation to aid in future planning.
- Propose migration strategies for large refactoring efforts.

## Quality Assurance (Automated)

### Continuous Monitoring

- **Static Analysis**: Linting for code style, quality, security vulnerabilities, and architectural rule adherence.
- **Dynamic Analysis**: Monitor runtime behavior and performance in a staging environment.
- **Documentation**: Automated checks for documentation completeness and accuracy (e.g., linking, format).

### Quality Metrics (Auto-Tracked)

- Code coverage percentage and gap analysis.
- Cyclomatic complexity score per function/method.
- Maintainability index assessment.
- Technical debt ratio (e.g., estimated remediation time vs. development time).
- Documentation coverage percentage (e.g., public methods with comments).

## EARS Notation Reference

**EARS (Easy Approach to Requirements Syntax)** - Standard format for requirements:

- **Ubiquitous**: `THE SYSTEM SHALL [expected behavior]`
- **Event-driven**: `WHEN [trigger event] THE SYSTEM SHALL [expected behavior]`
- **State-driven**: `WHILE [in specific state] THE SYSTEM SHALL [expected behavior]`
- **Unwanted behavior**: `IF [unwanted condition] THEN THE SYSTEM SHALL [required response]`
- **Optional**: `WHERE [feature is included] THE SYSTEM SHALL [expected behavior]`
- **Complex**: Combinations of the above patterns for sophisticated requirements

Each requirement must be:

- **Testable**: Can be verified through automated or manual testing
- **Unambiguous**: Single interpretation possible
- **Necessary**: Contributes to the system's purpose
- **Feasible**: Can be implemented within constraints
- **Traceable**: Linked to user needs and design elements

## Task File Management

### Multi-File Task Organization

**Task Management Files:**
- **`current-tasks.md`**: Active sprint tasks and immediate work (primary source for current work)
- **`task-backlog.md`**: Future tasks organized by priority and dependencies
- **`completed-tasks.md`**: Historical task completion record (last 4 weeks)

**When to Create Individual Task Files:**
- Type B or Type C tasks requiring detailed documentation
- Task moves from NOT_STARTED to IN_PROGRESS status in `current-tasks.md`
- Type A tasks use abbreviated entries in Action Documentation Template format

**Workspace Structure:**
```
.agent_work/
  current-tasks.md                   # Active sprint tasks (primary source for current work)
  task-backlog.md                    # Future tasks prioritization
  completed-tasks.md                 # Historical completions (last 4 weeks)
  requirements.md
  design.md
  decisions/
  context/
    guides/                          # Setup guides, deployment docs
    analysis/                        # Technical assessments
    status/                          # Progress tracking
    archive/                         # Archived context files
  tasks/
    active/                          # Symlinks to current individual task files
    completed/                       # Completed individual task files
    [transition files]               # New tasks before organization
```

**Individual Task File Organization:**
- **Active work**: Individual task files accessible via `tasks/active/` (symlinked for quick access)
- **Completed work**: Files moved to `tasks/completed/` upon task completion
- **Complex tasks**: Maintain subfolder structure (e.g., `TASK-008/`) for multi-phase work

**Task File Naming Convention:**
- Format: `TASK-XXX-brief-name.md` (e.g., `TASK-008-azure-maps-provider.md`)
- Use task number from current-tasks.md or task-backlog.md as primary identifier
- Brief name should be 2-4 words describing the task
- Use hyphens instead of spaces or underscores

**Task File Template (Type B/C):**

```markdown
# TASK-XXX: [Task Title]

**Status**: [IN_PROGRESS/COMPLETED]
**Priority**: [CRITICAL/HIGH/MEDIUM/LOW]
**Type**: [B/C]
**Estimated Effort**: [X days]

## Objective
[Clear statement of what this task accomplishes]

## Requirements (EARS Notation)
[Detailed requirements using EARS notation]

## Acceptance Criteria
- [ ] [Specific, testable criteria]
- [ ] [Each criterion must be verifiable]

## Dependencies
[List of blocking tasks or external dependencies]

## Implementation Plan
[High-level approach and key steps]

---

## Implementation Log

### [Date] - [Phase/Step Name]
**Objective**: [What this step accomplishes]
**Context**: [Current state and requirements]
**Decision**: [Approach chosen and rationale]
**Execution**: [Detailed steps taken]
**Output**: [Results, logs, and metrics]
**Validation**: [How success was verified]
**Next**: [Next planned action]

---
[Continue with additional entries chronologically]

---

## Validation Results

### Test Summary
**Test Date**: [Date]
**Test Environment**: [Environment details]
**Test Status**: [PASS/FAIL/PARTIAL]

### Acceptance Criteria Validation
- [ ] **Criteria 1**: [Description] - [PASS/FAIL] - [Evidence]
- [ ] **Criteria 2**: [Description] - [PASS/FAIL] - [Evidence]

### Test Results
[Detailed test outputs, screenshots, logs]

### Issues Identified
[Any problems found during validation]

### Remediation Actions
[Steps taken to address issues]

### Sign-off
[Final approval and completion confirmation]
```

**Type A Task Documentation:**

Use abbreviated entries in Action Documentation Template format for tracking Type A work:

```markdown
### TYPE A - [ACTION] - [TIMESTAMP]
**Objective**: [Brief goal]
**Execution**: [What was done]
**Output**: [Results]
**Next**: [Follow-up if needed]
```

### Workflow Integration

**Task Lifecycle:**

1. **Task Creation**: Task added to `task-backlog.md` with NOT_STARTED status
2. **Sprint Planning**: Move 3-5 tasks from `task-backlog.md` to `current-tasks.md`
3. **Task Start (Type B/C)**:
   - Update status to IN_PROGRESS in `current-tasks.md`
   - Create task file: `.agent_work/tasks/TASK-XXX-brief-name.md`
   - Create symlink in `tasks/active/` for quick access
4. **Implementation**:
   - Log all work in Implementation Log section of task file
   - Update `current-tasks.md` status to reflect progress
   - Create task-specific decision records in `.agent_work/decisions/` if needed
5. **Validation**:
   - Document all testing in Validation Results section of task file
   - Ensure all acceptance criteria are verified
6. **Completion**:
   - Update status to COMPLETED in `current-tasks.md`
   - Move individual task file from `tasks/active/` to `tasks/completed/`
   - During sprint retrospective, move entry to `completed-tasks.md`

**Task Start (Type A):**
- Document work using abbreviated Action Documentation Template entries
- Update `current-tasks.md` status
- No separate task file required

**Primary Source of Truth:**
- **`current-tasks.md`** is the authoritative list for active work and sprint planning
- **`task-backlog.md`** is the authoritative list for future work prioritization
- **`completed-tasks.md`** is the authoritative record of historical completions
- Individual task files provide detailed execution documentation for Type B/C tasks
- Task files supplement but do not replace the three-file task tracking system

**Multi-File Task Management Protocol:**
- **Current Sprint**: Focus on `current-tasks.md` for day-to-day work decisions
- **Sprint Planning**: Use `task-backlog.md` to plan next sprint priorities
- **Progress Review**: Reference `completed-tasks.md` for recent context and lessons learned
- **Maintenance**: Weekly archival from `completed-tasks.md` to reduce cognitive load

**Task File Organization:**
- **Active tasks**: Keep individual task files in `tasks/active/` (symlinked for quick access)
- **Completed tasks**: Move individual task files to `tasks/completed/` upon completion
- **Complex tasks**: Maintain subfolder structure (e.g., `TASK-008/`) for multi-phase work
- **Preservation**: All detailed task documentation preserved for historical reference

**Context File Organization:**

**Context Documentation Strategy:**
- **`context/guides/`**: User-facing documentation, setup guides, deployment instructions
- **`context/analysis/`**: Technical reality checks, provider comparisons, architecture assessments
- **`context/status/`**: Progress tracking, workflow documents, commit readiness reports
- **`context/archive/`**: Outdated context files organized by month (YYYY-MM)

**Context File Purpose Clarification:**
- **`context/status/`**: Project-wide progress reports and workflow documentation (e.g., PROGRESS-STATUS.md, COMMIT_READY.md)
- **Task status tracking**: Individual task completion status within `current-tasks.md`, `completed-tasks.md`
- **Individual task status**: Detailed execution logs within individual task files

**Context File Lifecycle:**
1. **Creation**: Place in appropriate `context/` subdirectory based on purpose and naming convention
2. **Maintenance**: Update references during bi-weekly sprint planning
3. **Archival**: Move outdated status reports to `context/archive/YYYY-MM/` monthly
4. **Cross-referencing**: Maintain links between context files and related tasks

**Context File Naming Conventions:**
- **Guides**: Title-Case-With-Purpose.md (e.g., `Azure-Maps-Local-Setup-Guide.md`)
- **Analysis**: ALL-CAPS-ATTENTION-GRABBING.md (e.g., `PROVIDER-INDEPENDENCE-REALITY.md`)
- **Status**: ALL-CAPS-WORKFLOW.md (e.g., `PROGRESS-STATUS.md`, `COMMIT_READY.md`)

**Integration with Task Management:**
- Task files reference relevant context documents for background information
- Context guides updated when task implementations change user-facing procedures
- Analysis documents created when task assumptions need verification
- Status documents track cross-task progress and workflow state

**Archival Strategy:**
- **Task files**: Review archival at completion of each Phase (milestone)
- **Context files**: Monthly archival of status reports older than 4 weeks
- **Completed tasks**: Keep last 4 weeks in `completed-tasks.md`, archive older to `context/archive/`
- Archive decisions made collaboratively based on value and future reference needs

## Task File Maintenance Protocol

### Weekly Maintenance (Fridays, 15 minutes)
**Purpose**: Keep current work visible and reduce cognitive load

**Task Management:**
- [ ] **Archive completed tasks** older than 4 weeks from `completed-tasks.md` to `context/archive/YYYY-MM-completed-tasks.md`
- [ ] **Update sprint progress** - verify all task statuses in `current-tasks.md` are accurate
- [ ] **Review blocked tasks** - identify and document any new blockers or dependency changes
- [ ] **Sync task files** - ensure individual task files in `tasks/active/` match current sprint

**Context File Management:**
- [ ] **Update guides** - Review any setup guides affected by week's task completions
- [ ] **Clean up references** - Remove obsolete links, fix broken internal references
- [ ] **Status consolidation** - Update `PROGRESS-STATUS.md` with week's achievements

### Bi-Weekly Sprint Planning (Every other Monday, 30 minutes)
**Purpose**: Plan next sprint and maintain backlog organization

**Sprint Management:**
- [ ] **Sprint retrospective** - move completed current sprint tasks to `completed-tasks.md`
- [ ] **Sprint planning** - select 3-5 tasks from `task-backlog.md` to move to `current-tasks.md`
- [ ] **Priority review** - reassess task priorities based on recent learnings and changing requirements
- [ ] **Dependency update** - verify all task dependencies are still valid and update blocking relationships
- [ ] **Effort estimation** - refine effort estimates based on recent completion times

**File Organization:**
- [ ] **Task file movement** - move completed individual task files from `tasks/active/` to `tasks/completed/`
- [ ] **Context file review** - update any analysis documents affected by sprint work
- [ ] **Cross-reference validation** - ensure all links between task files and context files are valid

### Monthly Maintenance (1st of month, 45 minutes)
**Purpose**: Strategic planning and file organization

**Strategic Review:**
- [ ] **Archive quarterly** - move tasks >3 months old to `context/archive/YYYY-QX-completed-tasks.md`
- [ ] **Metrics review** - analyze sprint velocity, completion rates, effort estimation accuracy
- [ ] **Template updates** - standardize any new task formats discovered during month
- [ ] **Backup verification** - confirm all task and context documentation is committed to git

**File Organization:**
- [ ] **Context archival** - move status reports older than 1 month to `context/archive/YYYY-MM/`
- [ ] **Guide consolidation** - merge redundant analysis documents, update outdated guides
- [ ] **Structure validation** - ensure folder organization remains clean and navigable

### Automated Maintenance Triggers
**Setup**: Add these to development workflow

- [ ] **Git pre-commit hook**: Validate task file formatting and internal links
- [ ] **Sprint transition**: Template for moving tasks between files and folders
- [ ] **Task creation**: Standard template application and proper folder placement
- [ ] **Status change**: Automatic timestamp updates for task transitions and file movements
