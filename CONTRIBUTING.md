# Contributing to ARENA Python

The general Contribution Guide for all ARENA projects can be found [here](https://docs.arenaxr.org/content/contributing.html).

This document covers **development rules and conventions** specific to this repository. These rules are mandatory for all contributors, including automated/agentic coding tools.

## Development Rules

### 1. MQTT Topics — Always Use the `TOPICS` Constructor

**Never hardcode MQTT topic strings.** All topic paths must be constructed using the local `TOPICS` string constructor for ease of future topics modulation. This enables future topic format refactoring without scattered string updates.

### 2. Dependencies — Pin All Versions

**All dependencies must use exact, pegged versions** (no `^`, `~`, or `*` ranges). This prevents version drift across environments and ensures reproducible builds for security.

### 3. PyPI Compatibility — Avoid Relative Links in README

**Do not use relative markdown links inside the `README.md`.** Because the README is ingested and rendered on external package indices like PyPI, relative links (e.g., `[Contributing](CONTRIBUTING.md)`) will break. Always use absolute URLs pointing back to the GitHub repository.
