# East edge QA

Four local unit tests passed with synthetic image fixtures. Source art JPEG was not executed through new QA in CI. Candidate endpoint [1100,704] lies on the east image boundary, outside actual JPEG pixel coordinates. Neighboring road artwork and bridge continuation remain unverified. Do not enable production movement.

Next: run python scripts/audit_octagon_1_edge.py against the original embedded JPEG and inspect six unpainted crops. No main/live changes.
