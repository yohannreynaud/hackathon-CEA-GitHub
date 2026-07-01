---
name: itk-production-rate
description: Use for aggregate production-throughput questions about a time period — e.g. "How many production modules were wirebonded in Paris in April 2026?", "How many modules were assembled at LPNHE last month?". Answers are broken down per institution when the user says "Paris" (a regional grouping of IRFU + LPNHE + IJCLab, not a single institution code) or names one institute. For per-module lists rather than counts, use itk-signoff-reports.
---

Follow the full recipe in `playbooks/PRODUCTION_RATE.md` (repository root). That file is the canonical, tool-agnostic version of this playbook — keep it in sync if you edit either copy.
