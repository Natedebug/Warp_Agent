# Warp_Agent

# Warp “Start From Zero” Project Builder Plan

## Summary
Create a Warp agent that **sets up a project correctly from nothing after asking intake questions** by:
1. asking beginner-friendly startup questions,
2. asking simple follow-ups based on answers,
3. generating and executing a full setup plan, and
4. generating a specialist-agent map for delegated setup tasks.

The intake is designed for someone with no coding background.

## Core Product Behavior
- Start-of-project flow begins with plain-language questions.
- Questions avoid technical jargon and include examples.
- Answers are mostly multiple-choice, with `I’m not sure`.
- Agent translates answers into technical setup decisions internally.
- Agent creates a project scaffold/configuration from zero (or near-zero) based on answers.
- Agent proposes specialist agents automatically; execution remains approval-gated unless you choose auto-run later.
- Per-project state is saved in `.warp/project-intake.yaml`.

## Beginner-Friendly Intake Design

### Question-writing rules
- Use everyday wording.
- One idea per question.
- No unexplained acronyms.
- Max 5 options per question.
- Always include:
  - `I’m not sure`
  - `Skip for now`

### Fixed Questions (always asked, plain language)
1. “Where should this new project live?”
2. “What do you want to build?”
   - Website / Backend service / Automation scripts / Mixed / Not sure
3. “What should this project do first?”
   - Short goal in plain language
4. “How should success be checked?”
   - “Open in browser”, “Run a command”, “Both”, “Not sure”
5. “Where will this run?”
   - Local only / Test environment / Production / Not sure

### Adaptive Follow-ups
- Website path: UI framework preference or “choose for me”.
- Backend path: API style and storage choice or “choose for me”.
- Script path: execution cadence and input/output expectations.
- If unsure often: guided yes/no mode and sensible defaults.

## From Answers to Setup (Main Change)
The orchestrator now does **project creation**, not just auditing:
- Creates folder structure.
- Initializes runtime/tooling.
- Adds dependency management files.
- Creates starter scripts (`dev`, `build`, `test`, `lint` when relevant).
- Adds basic CI workflow.
- Adds `.env.example`, README, and onboarding notes.
- Adds baseline quality gates.
- Produces first-run validation steps.

## Output Contracts (Public Interfaces/Types)
1. `ProjectIntakeState`
- plain-language answers
- normalized technical setup decisions
- confidence + unknowns
- timestamps

2. `ProjectBootstrapPlan`
- ordered setup actions
- generated files list
- command sequence
- validation checklist

3. `AgentMap`
- specialist agents
- why selected
- exact setup responsibilities
- dependencies between specialists

4. `ExecutionProposal`
- bootstrap plan + agent map
- approval settings
- run order

## Specialist-Agent Rules
Auto-select specialists based on intake:
- Project Scaffold Agent
- Environment Setup Agent
- Build Pipeline Agent
- Test Baseline Agent
- Quality Gate Agent
- CI/CD Baseline Agent
- Docs/Onboarding Agent

Each rule stores trigger + confidence + plain-language reason.

## Workflow
1. Ask fixed plain-language questions.
2. Ask adaptive follow-ups.
3. Save `.warp/project-intake.yaml`.
4. Generate bootstrap plan.
5. Generate specialist-agent map.
6. Request approval.
7. On approval, execute scaffold/setup tasks and specialists.
8. Run final validation checks and record outcomes.

## Test Cases and Acceptance
1. Non-technical user can complete intake without tool knowledge.
2. “I’m not sure” still produces a complete starter project.
3. New empty folder becomes runnable project after execution.
4. Generated project includes scripts, README, and baseline CI.
5. No specialist runs before approval (current default).
6. Re-run updates missing setup parts without destructive overwrite.

## Assumptions and Defaults
- Primary goal is **build from zero** after intake.
- User may have no coding experience.
- Technical choices are auto-selected when confidence is sufficient.
- Approval gate remains enabled by default for safety.
