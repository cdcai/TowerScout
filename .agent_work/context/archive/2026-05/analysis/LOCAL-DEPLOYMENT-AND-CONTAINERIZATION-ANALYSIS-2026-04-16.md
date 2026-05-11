# Local Deployment and Containerization Analysis

**Created**: April 16, 2026  
**Audience**: Reviewers and collaborators who do not have direct codebase access or prior TowerScout context  
**Purpose**: Explain TowerScout's current deployment and containerization planning in a single, reviewer-friendly document, including what has already been done, what decisions have been made, what remains open, and where the main risks still sit

---

## Executive Summary

TowerScout is moving toward containerization because the project has outgrown its current install model. The application is no longer best understood as an experimental academic prototype. It is now a practical, locally run investigation tool with a setup wizard, in-app settings, a stabilized detection workflow, and a clearer push toward deployment readiness.

The current plan is to treat Docker as the **first deployment layer**, not the final end-user experience. The agreed direction is:

- first release success should be **Docker-first**
- the next layer should be **launcher-first**
- a fully managed installer remains a possible later phase, but is not current scope
- first release support should be **AMD64 first**
- CPU support is required, and NVIDIA/CUDA acceleration should be supported on compatible AMD64 hosts
- Mac support remains a deliberate follow-on target rather than a first-release promise
- large runtime assets should use a **first-run download** strategy
- application updates and model updates should be **separate but manual**
- user-facing distribution should be a **GitHub release package**, with container images hosted in a registry behind the scenes

This is a sound direction, but several planning risks remain open. The most important one is organizational: if many intended users are blocked from installing or running Docker Desktop or WSL2 on their machines, then Docker remains a valid engineering and packaging milestone, but it should not be treated as the long-term end-user delivery mechanism. That does not invalidate the current Sprint 05 work. It changes how that work should be framed.

The practical recommendation is:

- keep `TASK-025` focused on a reliable Docker baseline
- keep `TASK-054` focused on a launcher-driven local experience
- explicitly preserve a future path to a non-Docker-managed installer
- resolve a short list of remaining planning risks before the Docker plan is treated as locked

---

## 1. Project Context

### What TowerScout Is

TowerScout is a Flask web application used to identify cooling towers in satellite and aerial imagery. It supports outbreak investigation and registry-building workflows by combining:

- YOLOv5 object detection
- an EfficientNet secondary classifier
- Google Maps and Azure Maps provider support
- manual review and correction workflows
- CSV, KML, and dataset export/restore flows

It is intended to be run locally by public-health and investigation users, not as a cloud-hosted multi-tenant application.

### Why Local Deployment Matters

The project is explicitly trying to support users who need:

- a practical local tool they can run on their own machine
- a setup process that does not require manual editing of configuration files
- stable support for both provider-backed detection and follow-up review workflows

This local-deployment framing matters because it changes what "good architecture" means. For TowerScout, success is less about cloud-style infrastructure patterns and more about:

- installation simplicity
- predictable startup
- persistence of user-entered configuration
- survivable updates
- supportability for non-technical users

---

## 2. Why Containerization Is Being Considered Now

Containerization is not being pursued in a vacuum. It is being considered now because recent work changed the maturity of the application.

### What Changed Recently

The repo has already completed a substantial amount of pre-containerization work:

- a first-launch Setup Wizard and in-app Settings flow now exist
- API keys no longer require manual file editing in normal use
- configuration is persisted to `webapp/config/.env`
- the detection workflow now exposes progress and cancellation behavior
- the active YOLO runtime no longer depends on Torch Hub or GitHub at runtime
- a current smoke-test baseline now exists and is intended to be reused for Docker validation
- runtime paths were normalized so that current persistent and temporary surfaces resolve under `webapp/`

In other words, Docker is now being considered after the application crossed from "usability and setup are still unstable" into "the core user-facing flow is present and the next major concern is deployment readiness."

### Why the Team Is Not Starting with Launch UX

The current sprint plan intentionally separates:

- **Docker baseline work**: build, run, persistence, validation
- **launch UX work**: browser orchestration, launcher scripts, startup messaging

That sequencing is intentional. The team is trying to avoid solving the "few-click" experience before the underlying runtime and persistence model are stable enough to support it.

---

## 3. Work Already Completed to Prepare for Docker

The current Docker discussion is only possible because several earlier technical risks were addressed first.

### Key Preparatory Tasks and Why They Matter

- `TASK-046` delivered the Setup Wizard and Settings flow. This matters because a containerized app is not useful if first-time users still need to edit files manually just to get started.
- `TASK-051` clarified the runtime dependency story. This matters because Docker should package a truthful runtime contract, not a partially misunderstood one.
- `TASK-055` hardened the older YOLO Torch Hub path enough to expose what still needed to change. This mattered as a short-term stabilization step before the deeper runtime ownership work.
- `TASK-056` addressed first-run reliability and runtime determinism. This matters because Docker should not freeze first-run instability into an image and call that progress.
- `TASK-057` moved the active YOLO runtime away from Torch Hub / GitHub dependence at startup. This matters because container startup should not depend on mutable upstream bootstrap behavior that the project does not control.
- `TASK-052` established the current smoke-test baseline. This matters because Docker validation should prove that the containerized app behaves like the corrected host baseline instead of inventing a different ad hoc check.
- `TASK-062` handled pre-Docker cleanup and loader hardening after senior-review feedback. This matters because the team intentionally wanted that cleanup to land on the host baseline before containerization began.

### Setup and Configuration Readiness

The app now supports a degraded startup mode where it can boot into setup-required state instead of exiting when configuration is missing. This matters because a containerized first launch must still allow the user to open the app, enter provider keys, and save configuration without manual file editing.

This work also established that configuration persistence is a real runtime requirement, not just a documentation concern.

### Runtime Determinism and First-Run Stability

Sprint 05 has already invested in making the runtime more predictable before containerization:

- runtime dependencies were audited and corrected
- the active YOLO path no longer uses a mutable Hub bootstrap process
- first-run blockers and deployment-hostile runtime behavior were addressed
- the maintained smoke baseline was rebuilt around the live route surface

This sequence matters because Docker should package a corrected baseline, not freeze a fragile one into a container image.

### Runtime Path Normalization

One of the most important recent changes was path normalization. Current runtime writes now resolve under `webapp/`, which gives Docker planning a clearer persistence contract.

The currently recognized runtime surfaces include:

- `webapp/config/`
- `webapp/flask_session/`
- `webapp/logs/`
- `webapp/temp/`
- `webapp/uploads/`
- `webapp/cache/`

This makes container planning much cleaner than it would have been earlier, when repo-root and app-root write paths were mixed.

---

## 4. How the Current Containerization Strategy Was Developed

The current thinking was shaped by two inputs:

1. the active Sprint 05 task structure in the repo
2. a separate roadmap brainstorming conversation focused on local deployment concerns

### What the Roadmap Brainstorm Added

The roadmap-generation conversation was useful because it asked broader product questions that the sprint tracker alone does not fully capture:

- Is TowerScout meant to feel like a local desktop-style tool rather than a cloud service?
- Should users be shielded from unnecessary infrastructure complexity?
- How should large runtime assets be handled?
- How should application updates differ from model updates?
- What should first launch look like when internet access is acceptable?
- How should future installer-like packaging be preserved as an option?

The roadmap did not replace the current sprint plan. It broadened it. It shifted the framing from:

- "How do we Dockerize the app?"

to:

- "How do we make TowerScout into a locally deployable product, with Docker as the first phase?"

That broader framing is worth keeping.

---

## 5. Current Agreed Direction

The following decisions have effectively been made through the planning discussion.

### Release Model

- First release success should be **Docker-first**
- Second-layer success should be **launcher-first**
- A fully managed installer remains a later possibility, not current scope

This means Docker is being treated as the foundation for local deployment rather than the polished final user experience.

### Platform Strategy

- First release should be **AMD64 first**
- CPU support is required
- NVIDIA/CUDA acceleration should be supported on compatible AMD64 hosts
- Mac support should remain an explicit follow-on target

This is a deliberate narrowing of scope. It allows the team to support GPU-capable hosts without promising full cross-platform parity in the first milestone.

### Large File Strategy

- Large runtime assets should use **first-run download**
- The application should persist those assets across restarts and updates
- Application updates and model updates should be **separate but manual**

This separates code delivery from model delivery and avoids forcing every model update to become a full application rebuild and rerelease.

### Distribution Strategy

- Users should receive a **GitHub release package**
- Container images should live in a registry behind the scenes
- This structure should preserve a later path to a more managed installer

This is an important product choice. It means the user-facing artifact is not expected to be "figure out the registry and pull the image yourself." Instead, the release package becomes the user-facing entry point.

### UX Scope

- `TASK-025` should remain focused on container build/run behavior and persistence correctness
- `TASK-054` should deliver a moderate launcher experience
- Browser launch should happen only after the app is actually reachable
- Startup messaging should explain first-run download delays rather than hide them

This is an appropriate separation of concerns.

---

## 6. How the Team Currently Plans to Implement This

### Phase 1: Docker Baseline (`TASK-025`)

The Docker baseline is intended to deliver:

- a reproducible build/run environment
- persistence for configuration and session-dependent behavior
- compatibility with the existing Setup Wizard and Settings flows
- support for the current runtime contract and smoke baseline
- a workable first local deployment layer that future launch UX can target

The core work in this phase includes:

- image/build design
- compose or equivalent local orchestration
- runtime persistence decisions
- large-file bootstrapping strategy
- container validation using the maintained smoke baseline
- documentation sufficient for a first internal/external release package

The baseline should not try to solve every later product concern. It should produce a stable target for the next UX layer.

### Phase 2: Launcher-First UX (`TASK-054`)

The next layer is expected to make the Docker baseline feel more like a local application. This likely includes:

- host-side start script(s)
- browser opening only after the app is reachable
- clearer separation between "container started" and "app ready"
- basic stop/update support surfaces
- clearer communication around first-run downloads and startup delays

This phase turns Docker from a technical mechanism into a more user-friendly experience without yet becoming a full installer project.

### Phase 3: Possible Managed Installer

This is not current work, but the current decisions are intentionally being shaped so it remains possible later.

If the team later decides to move beyond raw Docker plus scripts, the desired end state would likely wrap the same underlying pieces:

- release package
- image pull/update behavior
- persistent data locations
- launcher behavior
- startup checks

That is why current planning should avoid choices that make Docker highly specialized or difficult to wrap with a later installer.

---

## 7. Remaining Open Planning Risks

This section is the practical "what is still hanging in the balance" list.

### A. Must Resolve Before Treating the Docker Plan as Locked

#### 1. End-User Docker Access May Be Limited by IT Policy

This is now the most important strategic risk.

If many intended users are on managed machines where Docker Desktop, WSL2, virtualization, or admin rights are restricted, then Docker cannot be assumed to be the durable long-term delivery mechanism for end users.

**Why it matters**

- it affects whether Docker is the user-facing product or an engineering delivery phase
- it affects how much effort should be invested in Docker-specific polish
- it affects whether a future non-Docker installer path is optional or necessary

**Current direction**

Treat Docker as a valid first deployment layer, but do not assume it is the final long-term end-user path.

**Recommended planning treatment**

- acknowledge this explicitly in `TASK-025`
- avoid over-specializing around Docker as if it will be the permanent user-facing answer
- preserve the installer path deliberately

#### 2. The Secret-Key Persistence Story Needs to Be Explicit

The application requires a stable `FLASK_SECRET_KEY` for sessions to behave correctly across restarts, but the planning discussion has not fully finalized how that should be handled in the containerized local deployment model.

**Why it matters**

- unstable secret keys can invalidate session behavior across restart/update events
- this affects setup flow continuity and general predictability

**Recommended planning treatment**

Choose one clear persistence approach and document it as part of the Docker baseline rather than leaving it implicit.

#### 3. The Full First-Run Asset Inventory Is Not Yet Fully Locked

The large-file discussion has focused primarily on:

- YOLO weights
- EfficientNet classifier weights
- ZIP-code boundary data

However, there is still at least one hidden runtime dependency to account for: the EfficientNet path currently relies on a pretrained base model mechanism that can use Torch cache state. This means the actual first-run asset story is broader than "download two project `.pt` files."

There is also a data-version coordination issue to resolve: the current code and current local data point to 2025 ZIP-code data, while earlier container planning assumptions referenced an older year.

**Why it matters**

- incomplete first-run asset accounting can create startup surprises
- data version mismatch can create broken ZIP-code behavior in the containerized build

**Recommended planning treatment**

- lock the asset inventory before finalizing the bootstrap strategy
- make the ZIP-code data version part of the explicit Docker plan

#### 4. Persistence Policy Needs to Be More Precise

The runtime surfaces under `webapp/` are known, but the team still needs to decide more explicitly:

- what must survive restarts
- what must survive updates
- what only needs to be writable during a single container lifetime

**Why it matters**

- it affects support expectations
- it affects cleanup behavior and disk growth
- it affects how portable later installer work will be

**Recommended planning treatment**

Document persistence categories rather than treating every writable path the same way.

#### 5. Release Ownership and Rollback Process Are Not Yet Fully Operationalized

The planning direction now includes:

- release package for users
- registry-hosted images
- separate manual model updates

What still needs to be made concrete is the release operation itself:

- who publishes releases
- how model assets are versioned
- how bad releases are rolled back
- how users are told to recover from a broken update

**Why it matters**

This becomes a real support problem as soon as the first release package leaves the development environment.

---

### B. Should Be Acknowledged in the Planning Update, but Can Be Resolved During Implementation

#### 6. GPU Support Is Best Treated as an Accelerated Path, Not the Baseline Contract

Supporting CUDA-capable AMD64 machines is realistic, but only if the release language is careful.

**Why it matters**

- GPU support depends on host setup outside the application
- it is easy to overpromise "GPU support" in a way that creates support burden

**Recommended planning treatment**

Describe GPU support as supported on compatible AMD64 hosts, while keeping CPU as the required baseline path.

#### 7. Network Environment Problems Will Affect Real Users

TowerScout depends on provider-backed services and first-run downloads. Some users will be behind:

- proxies
- outbound filtering
- TLS inspection
- firewall rules

The project has already seen local TLS/proxy-related issues during setup validation work. That means network environment problems are not hypothetical.

**Why it matters**

- users may interpret environment failures as application bugs
- setup validation and first-run download behavior both depend on outbound connectivity

**Recommended planning treatment**

Plan simple troubleshooting guidance and support-friendly logging rather than assuming a normal unrestricted network path.

#### 8. Distribution and Redistribution Terms Should Be Reviewed Deliberately

The repository is licensed under CC-BY-NC-SA-4.0, and the project also depends on external providers and external data sources. This does not automatically block the plan, but it should be consciously reviewed in the context of:

- packaging
- release artifacts
- model redistribution
- data redistribution
- user-facing attribution

**Why it matters**

This affects how release packages are assembled and described.

#### 9. TowerScoutSite Is Still a Live Runtime Surface

The current application still serves `/site/` from `TowerScoutSite/`. That means the runtime image/content decision for that surface is still open.

**Why it matters**

- if it is excluded from the runtime image, that should be a deliberate product decision
- if it stays, it should be treated as part of the release surface

#### 10. Support and Troubleshooting Workflow Should Be Planned Early

Once users receive a release package, the project needs simple answers to:

- where logs live
- what to do when startup fails
- how to retry or recover first-run downloads
- how to distinguish app problems from environment problems

This is especially important if the team expects non-technical local users.

---

### C. Important, but Safe to Defer Beyond the Docker Baseline

#### 11. Detection Still Runs Synchronously in the Request Path

This is a real architecture concern, but it should not derail the current Docker baseline.

The current app still performs long-running detection work within the HTTP request lifecycle. That is not ideal for a more production-style deployment model, but it is already understood and tracked separately.

**Why it matters later**

- it affects long-running request handling
- it becomes more important as deployment ambitions expand

**Why it is deferrable now**

The current goal is a stable local baseline, not a background-job redesign.

#### 12. Filesystem Sessions and Local-Disk Coupling Are Still Architectural Debt

This is also real and already known. The current app stores local-disk-dependent workflow state through filesystem-backed sessions.

**Why it matters later**

- it limits portability
- it complicates more advanced deployment models

**Why it is deferrable now**

It can be preserved explicitly for the first Docker milestone as long as that constraint is documented rather than ignored.

#### 13. `towerscout.py` Is Still a Large Multi-Responsibility Module

This increases change risk, but it should remain a later decomposition task rather than a prerequisite for containerization.

**Why it matters later**

- broader runtime and deployment changes are riskier in a monolithic file

**Why it is deferrable now**

The immediate goal is deployment readiness, not a broad refactor.

---

## 8. Is the Current Plan Well-Developed or Problematic?

The plan is well-directed. It is not a fragile or poorly reasoned plan. It has several strengths:

- it is sequencing work in the right order
- it distinguishes runtime stabilization from deployment work
- it avoids trying to solve installer UX too early
- it recognizes the local-user nature of the product
- it now has a sensible stance on large-file handling and update strategy
- it preserves a path to future installer work

The plan's weaknesses are not signs that the direction is wrong. They are signs that a few practical edges still need to be made explicit:

- Docker access on user machines may be constrained
- secret persistence and asset inventory need to be finalized
- support and release operations need clearer ownership
- some older planning surfaces in the repo still reflect outdated assumptions

The conclusion is:

- the plan is implementable
- it does not appear to contain a hidden fatal flaw
- it should not yet be treated as fully locked until the open planning risks above are deliberately resolved or consciously accepted

---

## 9. Recommended Planning Adjustment

The strongest single adjustment to the current planning language is this:

### Docker Should Be Framed as Phase 1 of Local Deployment, Not the Final Delivery Model

That framing would better match:

- the current sprint boundaries
- the roadmap brainstorming value
- the likelihood that some users will be blocked from Docker on managed machines
- the desire to preserve a future launcher-first and installer-capable path

This means:

- `TASK-025` should remain focused and disciplined
- `TASK-054` should become the explicit user-experience bridge
- a future installer should remain an intentional possibility, not an accidental afterthought

---

## 10. Reviewer Questions

These are the most useful questions for a reviewer to pressure-test.

1. Is Docker being used as the right **first phase**, even if it may not be the right long-term end-user delivery model?
2. Is the narrowed first-release platform contract realistic and supportable?
3. Is first-run download the right tradeoff for large assets, given the project's actual usage model?
4. Is the release-package-plus-registry direction the right bridge toward a later installer-capable future?
5. Have the team explicitly accounted for the real-world issues users will hit on managed machines: Docker restrictions, proxies, TLS inspection, and outbound filtering?
6. Are secret handling, persistence, and first-run asset inventory sufficiently explicit to avoid last-minute surprises?
7. Does the plan preserve a clear path from:
   - Docker baseline
   - to launcher-first experience
   - to possible installer

---

## 11. Practical Next Step

Before updating the formal task plan, the team should do two things:

1. Incorporate the agreed strategic decisions into `TASK-025` and `TASK-054`
2. Resolve or explicitly accept the "Must Resolve Before Treating the Docker Plan as Locked" risks in this document

If that is done, the project will have a deployment plan that is:

- logically sequenced
- appropriately scoped
- reviewer-ready
- honest about current constraints
- strong enough to guide implementation without pretending uncertainty does not exist

---

## Appendix: Condensed Remaining Open Planning Risks

### Must Resolve

- End-user Docker access may be blocked by IT policy
- Stable secret-key persistence mechanism needs to be made explicit
- First-run asset inventory needs to be fully locked, including hidden model/bootstrap dependencies
- ZIP-code data version and expected runtime path need to be aligned
- Persistence policy needs to distinguish restart/update durability from temporary write requirements
- Release ownership, rollback, and user recovery process need to be defined

### Should Acknowledge in Plan

- GPU support is an accelerated host-dependent path, not the baseline support contract
- Real users will hit proxies, TLS interception, and restricted networks
- License and redistribution implications should be reviewed deliberately
- `TowerScoutSite/` is still a live runtime surface and should be included or excluded intentionally
- Support/troubleshooting workflow should be planned early

### Safe to Defer

- Background-job redesign for long-running detection
- Session/state redesign away from local-disk coupling
- Large-scale backend decomposition
