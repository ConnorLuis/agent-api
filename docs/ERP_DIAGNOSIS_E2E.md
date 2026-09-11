# ERP Diagnosis HTTP E2E

## Purpose

The ERP diagnosis reference application is derived from recurring enterprise
ECP/ERP permission and workflow troubleshooting scenarios, but this repository
does **not** contain former-employer source code, production APIs, customer data,
or production configuration.

The committed `Synthetic ERP Service` is a fully fictional read-only service.
It is used to validate that the business contract can cross a microservice
boundary while the Agent-API workflow and MCP tool contracts stay unchanged.

## Two adapters, one business port

```text
ERPReadService
  ├─ SyntheticERPReadService
  │    └─ in-process JSON repository
  │
  └─ SyntheticERPHttpReadService
       └─ HTTP → Synthetic ERP FastAPI service
```

Normal tests and business Golden Cases use the in-process adapter so the
default path remains deterministic and does not silently require a network
service.

The HTTP adapter is selected explicitly for E2E validation.

## Security boundary

The HTTP path is not allowed merely because it is read-only.

The final E2E path applies two independent restrictions:

1. `SyntheticERPHttpReadService` accepts only loopback hosts:
   `127.0.0.1`, `localhost`, or `::1`.
2. MCP execution declares `requested_network=true`; the ordinary
   `erp-diagnosis-readonly-principal` is therefore denied.
3. The trusted loopback adapter selects the dedicated
   `erp-diagnosis-loopback-http-principal`, which has the same ERP read scopes,
   no write permission, no live Neo4j permission, and network access only in
   combination with the adapter's loopback restriction.
4. No ERP write tool exists in the MCP registry.

This is defense in depth rather than a prompt-level instruction.

## Run manually

Terminal A:

```bash
python -m uvicorn examples.synthetic_erp_service.app:app \
  --host 127.0.0.1 \
  --port 8010
```

Terminal B:

```bash
python scripts/run_erp_http_e2e.py
```

The script also starts its own ephemeral loopback Uvicorn server, so Terminal A
is optional; the explicit command is useful only for manual inspection.

Expected high-level result:

```text
all_passed = true
network_requested = true
network_boundary_marked = true
no_write_capability = true
root_cause_exact_match = true
verification_pass = true
```

## What this proves

It proves:

- the synthetic microservice boundary is real HTTP rather than only a shared
  in-process repository;
- the same `ERPReadService` contract can back MCP business tools;
- MCP authorization sees the network request;
- the end-to-end diagnosis still combines real-time business facts with ERP
  policy citations;
- the default Agent workflow can remain CI-safe and network-free.

It does **not** prove:

- compatibility with a former employer's production service;
- production authentication, TLS, service mesh, HA, or rate limits;
- correctness on real customer data;
- statistical generalization beyond the frozen synthetic contract.
