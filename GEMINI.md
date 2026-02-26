# GEMINI.md: Project Overview and Context

This document provides an overview of the SecID project for Gemini, outlining its purpose, structure, and key components.

## Directory Overview

This is a non-code project that defines the **SecID (Security Identifier)** specification. SecID is a federated identifier system for security knowledge, modeled after [Package URL (PURL)](https://github.com/package-url/purl-spec). Its primary goal is to provide a unified, machine-readable way to reference disparate security concepts like vulnerability advisories, weaknesses, attack techniques, and compliance controls.

The project is "AI-first," designed to be easily parsed and understood by AI agents to enable autonomous navigation and correlation of security information.

**Type overloading:** Some types intentionally contain related concepts to allow evolution based on real usage. For example, `advisory` includes incident reports (AIID, NHTSA, FDA adverse events) and `control` includes prescriptive benchmarks (HarmBench, WMDP) and documentation standards (Model Cards). If these diverge enough in practice, they may become separate types later.

The repository contains the specification documents and a central `registry` of all supported SecID namespaces.

## Key Files

The project is composed of Markdown files that define the specification and the registry.

*   **`README.md`**: The main entry point that provides a high-level introduction to SecID, its vision, and its structure.
*   **`SPEC.md`**: The complete technical specification for the SecID identifier format, including grammar, types, and normalization rules.
*   **`docs/explanation/RATIONALE.md`**: A critical document explaining the "why" behind key design decisions, such as the choice of PURL grammar and the "advisory-centric" model.
*   **`docs/future/USE-CASES.md`**: Contains concrete examples of how SecID can be used to solve real-world security problems, such as correlating vulnerability data or mapping controls to standards.
*   **`registry/`**: This directory is the functional heart of the project. It contains a hierarchy of Markdown files that define all valid SecID types and namespaces.
    *   **`registry/<type>.md`**: Describes a top-level type (e.g., `advisory.md`, `weakness.md`).
    *   **`registry/<type>/<tld>/<domain>.md`**: Defines a specific namespace using reverse-DNS directory layout, including its resolution rules, ID patterns, and relevant URLs. For example, `registry/advisory/org/mitre.md` defines how to handle `secid:advisory/mitre.org/cve#...` and other MITRE advisory identifiers.

Each file in the `registry/` uses a consistent format of **YAML frontmatter** for structured, machine-readable data (like URLs and ID patterns) and a **Markdown body** for human- and AI-readable context and documentation.

## Usage

This directory serves as the canonical source for the SecID specification. There is no code to build or run. Its contents are meant to be used as a reference for:

1.  **Developers** building security tools, platforms, or AI agents that need to produce or consume security identifiers.
2.  **Security professionals** who need to understand and use SecID for documentation, compliance mapping, or threat modeling.
3.  **AI agents** that need to parse the registry files to learn how to resolve SecIDs and understand the relationships between different security entities.

Interaction with this project primarily involves reading the documentation and querying the contents of the `registry/` directory to understand and implement the SecID standard.
