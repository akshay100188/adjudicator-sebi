# backend

FastAPI service. Populated from Phase 1 onward.

Planned layout:
```
backend/
  app/
    main.py             # FastAPI app
    config.py           # pydantic settings
    db.py               # Supabase / Postgres client
    models/             # pydantic schemas (obligation, scenario, finding, trajectory)
    routes/             # scenarios, obligations, eval
    agent/              # hand-rolled ReAct tool-loop (Phase 4)
    tools/              # T1 temporal_filter … T5 rerank (Phase 3)
    ingest/             # fetch/parse/extract/enrich/index (Phase 2)
    synthesis/          # grounded findings (Phase 5)
  requirements.txt
  .env.example
```
Nothing here yet — Phase 1 adds the data model + DDL first.
