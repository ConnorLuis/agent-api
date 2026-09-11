# ERP Diagnosis Business Evaluation

## Purpose

This evaluation turns the ERP diagnosis reference application into a business-verifiable system rather than a demo with only happy-path examples.

The dataset and all Golden Cases are fully synthetic. They contain no former-employer source code, production APIs, customer data, or production configuration.

## Golden Case set

The frozen business set is stored at:

```text
eval_cases/erp_diagnosis_golden.jsonl
```

It contains 20 deterministic cases covering:

- role missing;
- organization scope denial;
- data permission denial;
- invalid document state;
- approval flow unbound;
- approver unresolved;
- transfer rule missing;
- known-good submit / approve / transfer / view cases;
- multiple simultaneous root causes;
- missing input and unknown document abstention;
- deterministic dependency-failure injection for permission, approval, transfer, and user-access reads.

## What each case checks

A case does not pass merely because a natural-language answer looks plausible. The evaluator checks machine-verifiable contracts:

```text
expected status
+ exact Root Cause Code set
+ required read-only MCP tools
+ forbidden tool absence
+ expected ERP policy source
+ controlled abstention behavior
+ workflow verification_pass
+ trace-node coverage
+ business audit event count
+ no raw MCP argument values in audit events
```

This keeps the evaluation aligned with the actual business workflow rather than relying on subjective answer grading.

## Metrics

The report includes:

- `case_pass_rate`
- `diagnostic_task_completion_rate`
- `controlled_abstention_accuracy`
- `failure_trace_coverage_rate`
- `root_cause_exact_match`
- `required_tools_hit`
- `read_only_tool_set_only`
- `policy_source_hit`
- `policy_fallback_boundary`
- `verification_pass`
- `trace_coverage`
- `audit_event_count_match`
- `audit_raw_arguments_absent`

`diagnostic_task_completion_rate` is calculated only on cases whose expected result is `diagnosed` or `no_issue`. Missing-input and dependency-failure cases are evaluated separately as controlled abstention, rather than being mislabeled as successful diagnoses.

## Failure injection

`FaultInjectingERPReadService` is a deterministic read-only decorator around the synthetic ERP service. It can fail exactly one read boundary:

```text
user_access
document_context
permission_check
approval_context
transfer_context
```

The workflow must convert real-time dependency failure into:

```text
DEPENDENCY_UNAVAILABLE
```

and must not call Policy RAG to fabricate a real-time permission or approval fact. This enforces the project rule:

> Fallback must not cross evidence types.

## Run

```bash
python scripts/run_erp_diagnosis_eval.py
```

Optionally persist a local report:

```bash
python scripts/run_erp_diagnosis_eval.py \
  --output reports/erp_diagnosis_eval.json
```

The script exits non-zero if any Golden Case fails, so it can be used as a CI/release gate.

## Interpretation boundary

A 20/20 result on this frozen synthetic set demonstrates deterministic correctness against the committed business contracts and failure scenarios. It is not evidence of production-scale ERP coverage, statistical generalization, or accuracy on a former employer's real systems.
