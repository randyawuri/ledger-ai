                   ┌──────────────────────┐
                   │    Flutter Mobile    │
                   │   (iOS / Android)    │
                   └──────────┬───────────┘
                              │ HTTPS
                              ▼
                     ┌──────────────────┐
                     │      Nginx       │
                     │ Reverse Proxy    │
                     └────────┬─────────┘
                              │
                              ▼
                   ┌─────────────────────┐
                   │      FastAPI        │
                   │       Backend       │
                   └────────┬────────────┘
                            │
      ┌──────────────┬──────┼──────────────┬─────────────┐
      ▼              ▼      ▼              ▼             ▼
 Authentication  Transactions Analytics   AI        Import Service
 Service         Service      Service     Service
      │              │          │          │             │
      └──────────────┴──────────┴──────────┴─────────────┘
                            │
                     PostgreSQL Database
                            │
             ┌──────────────┴──────────────┐
             ▼                             ▼
        Redis Cache                 Google Cloud Storage