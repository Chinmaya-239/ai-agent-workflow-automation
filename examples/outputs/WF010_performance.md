# WF010_performance - Performance report (test question)

```text
==============================================================================
USER REQUEST: Which workflows are failing most often?
==============================================================================

Selected Workflow:
  WF010 - Workflow Performance Report
  (router: keyword-tfidf, confidence 1.00) Best keyword/TF-IDF match with 'Workflow Performance Report' (score 0.38, runner-up 0.00)

Inputs resolved:
  - log_files = ['data/execution_logs.csv', 'logs/runtime_logs.csv']  [default]
  - failure_rate_threshold_pct = 10  [default]
  - exec_time_threshold_sec = 20  [default]
  - slow_step_threshold_sec = 5  [default]

Steps Executed:
  1. [OK]   Load execution logs  <load_table, 0.03s> - row_count=2499
  2. [OK]   Calculate success/failure rate  <calc_failure_rates, 0.00s> - count=11
  3. [OK]   Calculate average execution time  <calc_execution_times, 0.00s> - count=11
  4. [OK]   Identify frequent errors  <frequent_errors, 0.00s> - count=5
  5. [OK]   Identify slow steps  <slow_steps, 0.00s> - count=3
  6. [OK]   Generate recommendations  <generate_recommendations, 0.00s> - keys: flagged, recommendations, flagged_count
  7. [OK]   Generate performance report  <make_report, 0.00s> - report built: Workflow performance report

Conditions / Decisions:
  - [Identify slow steps] 3 step(s) have average duration above 5s
  - [Generate recommendations] Flag rule: failure rate > 10% OR average execution time > 20s -> 5 workflow(s) flagged

Result:
## Workflow performance report

5 of 11 workflows are flagged (failure rate > 10% or average time > 20s), based on 408 runs.

### Recommendations
- WF004 Product Description Generator: most frequent error 'LLMError: rate limit exceeded (N)' (11x) - throttle/queue requests and cache repeated LLM or API calls.
- WF004 Product Description Generator: step 'Create product description' averages 12.63s - cache, batch or parallelise this step.
- WF003 Vendor File Processing: most frequent error 'ValidationError: missing required column 'sku'' (5x) - add schema validation up-front and return a clear, fixable message to the user.
- WF005 Customer Order Status: most frequent error 'TimeoutError: carrier API timed out after Ns' (6x) - add retries with exponential backoff and a circuit breaker for the flaky dependency.
- WF007 Marketing Campaign Brief: most frequent error 'LLMError: rate limit exceeded (N)' (11x) - throttle/queue requests and cache repeated LLM or API calls.
- WF007 Marketing Campaign Brief: step 'Create messaging' averages 12.89s - cache, batch or parallelise this step.
- WF008 SEO Keyword Classification: most frequent error 'LLMError: invalid JSON in classifier response' (2x) - harden parsing and quarantine bad rows instead of failing the whole run.
- WF008 SEO Keyword Classification: step 'Classify search intent' averages 19.14s - cache, batch or parallelise this step.

### Failure rate by workflow (worst first) (11)
| workflow_id | workflow | runs | failed | failure_rate_pct |
|---|---|---|---|---|
| WF004 | Product Description Generator | 33 | 8 | 24.2 |
| WF003 | Vendor File Processing | 38 | 5 | 13.2 |
| WF005 | Customer Order Status | 64 | 6 | 10.2 |
| WF002 | Product Price Validation | 35 | 3 | 8.6 |
| WF007 | Marketing Campaign Brief | 38 | 3 | 7.9 |
| WF008 | SEO Keyword Classification | 37 | 2 | 5.4 |
| WF010 | Workflow Performance Report | 38 | 2 | 5.3 |
| WF006 | Duplicate Product Detection | 36 | 1 | 2.8 |
| WF009 | Employee Task Assignment | 43 | 1 | 2.6 |
| WF001 | Inventory Restock Check | 45 | 1 | 2.2 |
| WF011 | WF011 | 1 | 0 | 0 |

### Flagged workflows (5)
| workflow_id | workflow | failure_rate_pct | avg_exec_sec | flags |
|---|---|---|---|---|
| WF004 | Product Description Generator | 24.2 | 20.97 | failure rate 24.2% > 10%; avg time 20.97s >… |
| WF003 | Vendor File Processing | 13.2 | 1.66 | failure rate 13.2% > 10% |
| WF005 | Customer Order Status | 10.2 | 5.15 | failure rate 10.2% > 10% |
| WF007 | Marketing Campaign Brief | 7.9 | 26.53 | avg time 26.53s > 20s |
| WF008 | SEO Keyword Classification | 5.4 | 36.21 | avg time 36.21s > 20s |

### Average execution time (11)
| workflow_id | avg_exec_sec | max_exec_sec |
|---|---|---|
| WF008 | 36.21 | 54.81 |
| WF007 | 26.53 | 44.82 |
| WF004 | 20.97 | 34.97 |
| WF006 | 7.96 | 11.64 |
| WF005 | 5.15 | 11.01 |
| WF010 | 2.22 | 2.99 |
| WF003 | 1.66 | 2.55 |
| WF009 | 0.9 | 1.71 |
| WF002 | 0.87 | 1.61 |
| WF001 | 0.39 | 0.69 |

_… 1 more row(s) not shown (full data in exported file)_

### Most frequent errors (5)
| error | occurrences | workflows |
|---|---|---|
| LLMError: rate limit exceeded (N) | 11 | WF004, WF007 |
| TimeoutError: carrier API timed out after Ns | 6 | WF005 |
| ValidationError: missing required column 's… | 5 | WF003 |
| ValidationError: missing required column 'v… | 3 | WF002 |
| LLMError: invalid JSON in classifier respon… | 2 | WF008 |

### Slow steps (3)
| workflow_id | step | avg_sec | samples |
|---|---|---|---|
| WF008 | Classify search intent | 19.14 | 37 |
| WF007 | Create messaging | 12.89 | 38 |
| WF004 | Create product description | 12.63 | 33 |

**Files written:**
- outputs/wf010_failure_rate_by_workflow_worst_first.csv
```
