# LocalDB Analysis Tools - Quick Guide

## Welcome to the LocalDB Analysis Tools Documentation

This guide helps you quickly find the right documentation for your needs.

## Component Documentation

**For information about specific components:**

- **Modules (Quad Modules)**: Read `MODULE.md`
  - Covers: `module`, `20UPGM*`, `Paris*`, quad modules, assembly stages
- **Bare Modules**: Read `BARE_MODULE.md`
  - Covers: `bare_module`, `20UPGB*`, `20UPGBQ*`, FE chips, sensors
- **PCBs (Flex PCBs)**: Read `PCB.md`
  - Covers: `module_pcb`, `20UPGPQ*`, flex PCBs, PCB design versions
- **Child-Parent Relationships**: Read `CPR.md`
  - Covers: component hierarchy, navigation patterns, relationship types

## Common Queries

**For query patterns and examples:**

- **Finding Comments**: Read `COMMENTS_QUERY_METHOD.md`
  - Covers: comment retrieval by module, user, date range, keywords (5 specialized tools available)
- **Production Stages**: Check component-specific docs (MODULE.md, BARE_MODULE.md, PCB.md)
- **Test Types**: Check component-specific docs for stage-specific tests

## Question Playbooks

For recurring question patterns (production rate, sign-off reports, current-stage census, recent completions, GridFS uploads, UNHAPPY/GRAVEYARD investigation), read the matching file in [`../playbooks/`](../playbooks/) **before** improvising a multi-step query — they encode step-by-step tool call sequences and non-obvious conventions (e.g. what "Paris" means as an institution grouping). See [AGENT_SYSTEM_PROMPT.md](AGENT_SYSTEM_PROMPT.md) § "Question Playbooks" for the full list.

## Common Requests from the user

- **Requests to understand when a specific component passed a certain stage or how many of them passed a certain stages within a given time window**
  - the user expects only a date without a time, unless specified
  - find out to which stage the user is referring to
    - ex: 'when was ParisXXXX assembled?' refers to the `MODULE/ASSEMBLY` stage
    - ex: 'when was ParisXXXX wirebonded?' refers to the `MODULE/WIREBONDING` stage
    - ex: 'when did ParisXXXX receive its OBWBP?' refers to the `MODULE/WIREBOND_PROTECTION` stage
  - in case the current stage of the module is earlier or equal to the requested stage, 
    - the stage has not yet been passed for the component
  - otherwise, the date should correspond to the upload timestamp to localDB of the latest test of the requested stage

## Quick Reference

### By Component Type

| Component Type | Serial Pattern | Documentation |
|---------------|----------------|---------------|
| Quad Module | `20UPGM*` | `MODULE.md` |
| Bare Module | `20UPGB*` | `BARE_MODULE.md` |
| Flex PCB | `20UPGPQ*` | `PCB.md` |
| Digital Bare Module | `20UPGBQ*` | `BARE_MODULE.md` |

### By Task

| Task | Documentation/Examples |
|------|----------------------|
| Find component | Component-specific docs |
| Find tests | Component-specific docs |
| Check relationships | `CPR.md` |
| Find comments | `COMMENTS_QUERY_METHOD.md`, `find_comments_by_*_tool` |

## Getting Started

1. **Understand the component**: Read the relevant component documentation
2. **Review existing tools**: Check if there's already a tool for your analysis
4. **Test thoroughly**: Use the testing patterns shown in existing scripts

## Support

For issues or questions:
- Check existing documentation first
- Review similar scripts in the repository
- Verify MCP server connectivity
- Consult the best practices guide

## Quick Links

- [Module Documentation](components/MODULE.md) - Quad module information
- [Bare Module Documentation](components/BARE_MODULE.md) - Bare module information
- [PCB Documentation](components/PCB.md) - Flex PCB information
- [Child-Parent Relationships](components/CPR.md) - Component hierarchy guide
- [Question Playbooks](../playbooks/) - Step-by-step recipes for recurring question patterns
- [Agent System Prompt](AGENT_SYSTEM_PROMPT.md) - Full knowledge base index and safety rules
