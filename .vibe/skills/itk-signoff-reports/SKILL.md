---
name: itk-signoff-reports
description: Use when the user wants a per-module list of sign-off dates and stages, or a per-stage count of sign-offs, since a given date — e.g. "Since April 1st, for all modules in IRFU, give me sign-off dates and stage in a table with columns AtlasId, Alias, Stage, Sign-off date", "For each stage, how many modules have been signed off since March 1st?". For simple throughput counts without per-module detail, use itk-production-rate.
---

Follow the full recipe in `playbooks/SIGNOFF_REPORTS.md` (repository root). That file is the canonical, tool-agnostic version of this playbook — keep it in sync if you edit either copy.
