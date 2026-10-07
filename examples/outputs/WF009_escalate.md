# WF009_escalate - No suitable employee -> escalation

```text
==============================================================================
USER REQUEST: Assign a Kubernetes migration task that needs about 20 hours
==============================================================================

Selected Workflow:
  WF009 - Employee Task Assignment
  (router: keyword-tfidf, confidence 0.93) Best keyword/TF-IDF match with 'Employee Task Assignment' (score 0.42, runner-up 0.06)

Inputs resolved:
  - task_description = Assign a Kubernetes migration task that needs about 20 hours  [extracted]
  - employees_path = data/employees.csv  [default]

Steps Executed:
  1. [OK]   Understand task requirements  <analyze_task, 0.00s> - keys: description, skills, role, priority, effort_hours
  2. [OK]   Compare employee skills  <match_employee_skills, 0.00s> - count=8
  3. [OK]   Check current workload  <check_workload, 0.00s> - count=8
  4. [OK]   Rank candidates  <rank_candidates, 0.00s> - count=8
  5. [ESC]  Select employee  <select_employee, 0.00s> - No suitable employee found: nobody has the required skills/role (kubernetes). Escalating …

Conditions / Decisions:
  - [Understand task requirements] Requirements (rules): skills=['kubernetes'], role=any, priority=medium, effort=20h (parsed from request), deadline=2026-10-12 (assumed medium-priority SLA (5 days))

STATUS: ESCALATION REQUIRED - No suitable employee found: nobody has the required skills/role (kubernetes). Escalating to the manager.

## Task assignment - escalated

No suitable employee found: nobody has the required skills/role (kubernetes). Escalating to the manager.

### Task
Assign a Kubernetes migration task that needs about 20 hours

### Suggested next steps
- Re-prioritise someone's current work to free capacity
- Approve overtime or contractor support
- Relax the skill requirement / split the task

### Closest candidates (5)
| name | role | skills_matched | skills_missing | remaining_hours | has_capacity | score |
|---|---|---|---|---|---|---|
| Meera Iyer | UX Designer | - | kubernetes | 28 | yes | 51 |
| Arjun Mehta | Developer | - | kubernetes | 22 | yes | 46.5 |
| Karan Singh | QA Engineer | - | kubernetes | 20 | yes | 45 |
| Lena Fischer | Developer | - | kubernetes | 30 | no | 42.5 |
| Vikram Rao | Data Analyst | - | kubernetes | 18 | no | 33.5 |
```
