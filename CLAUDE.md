# CLAUDE.md

# FSAP AI Development Guide

This document defines the rules that every AI assistant must follow when working
on the FSAP project.

The goal is to ensure consistent development, documentation, and decision-making
throughout the entire lifecycle of the project.

---

# Project

## Project Name

FSAP

Flexible Sewing Automation Platform

---

## Current Product

Product Code

MAT-RS-001

Product Name (Korean)

자동차 매트 랏빠 자동 봉제 시스템

Product Name (English)

Automotive Mat Edge Binding Sewing System

---

# AI Mission

AI does not simply generate code.

AI participates as a project engineer.

Every response should help improve one or more of the following.

- Product Quality
- Platform Reusability
- Documentation
- Engineering Consistency
- Future Scalability

---

# Core Philosophy

The purpose of FSAP is NOT to build a single machine.

The purpose is to build a reusable sewing automation platform.

Every design decision should maximize future reuse.

Never optimize only for MAT-RS-001 if doing so reduces future platform value.

---

# Documentation Priority

The project is managed through four core documents.

## README.md

Purpose

Human documentation.

Contains

- Project Overview
- Vision
- Product Information
- Folder Structure

---

## CLAUDE.md

Purpose

AI development rules.

Contains

- Development Rules
- Workflow
- Engineering Standards
- AI Responsibilities

---

## CHANGELOG.md

Purpose

History of changes.

Contains (categories)

- Added
- Changed
- Fixed
- Removed
- Deprecated
- Documentation
- Security

Record only completed changes.

Whenever AI modifies the project,

AI should recommend updating CHANGELOG.md.

---

## DECISIONS.md

Purpose

ADR index.

Contains

- ADR number, title, status, scope, date
- Links to detailed ADR files

DECISIONS.md is an index only.

Detailed decision content is written in individual ADR files under

```text
docs/decisions/
```

Whenever an important decision is made,

AI should recommend creating an ADR and updating DECISIONS.md.

---

# Development Workflow

Every task must follow the project workflow.

Planning

↓

Concept

↓

Design

↓

Development

↓

Validation

↓

Business

Never skip a phase.

Phases may be repeated or partially overlapped when necessary.

However, results of a later phase must not be finalized before the key
requirements and technical decisions of earlier phases are confirmed.

---

# Phase Rules

## 01 Planning

Goal

Define what should be built.

Allowed

- Market Research
- Requirement Analysis
- Problem Definition
- Product Planning

Not Allowed

- CAD
- Mechanical Design
- Programming

---

## 02 Concept

Goal

Define how the problem should be solved.

Allowed

- System Architecture
- Functional Flow
- Patent Ideas
- Technology Concepts

Not Allowed

- Detailed Design
- CAD
- Manufacturing

---

## 03 Design

Goal

Transform concepts into engineering designs.

Allowed

- Mechanical Design
- Electrical Design
- Control Design
- Software Architecture

---

## 04 Development

Goal

Implement the design.

Allowed

- CAD
- PLC
- Motion
- Vision
- HMI
- Machine Assembly
- Software

---

## 05 Validation

Goal

Verify and improve.

Allowed

- Functional Test
- Reliability Test
- Failure Analysis
- Performance Evaluation

---

## 06 Business

Goal

Commercialization.

Allowed

- Patent
- Manufacturing
- Cost Analysis
- Marketing
- Investment Materials

---

# Engineering Principles

Always prefer

- Platform Design
- Modular Design
- Reusable Components
- Standard Interfaces
- Clear Documentation
- Maintainability
- Scalability

Avoid

- One-time Solutions
- Hard Coding
- Product-specific Design
- Unnecessary Complexity

---

# AI Behavior Rules

AI should

- Ask for missing information when necessary.
- Explain engineering reasoning.
- Suggest improvements.
- Consider future scalability.
- Keep documentation synchronized.

AI should never

- Invent specifications.
- Assume dimensions.
- Skip project phases.
- Ignore previous decisions.
- Remove documentation without reason.

---

# Change Management

Whenever AI creates or changes

- Design
- Software
- Documentation
- Folder Structure
- Naming Rules
- Engineering Standards

AI should recommend updating

CHANGELOG.md

If the modification changes engineering direction,

AI should also recommend updating

DECISIONS.md.

---

# ADR Management Rules

All ADRs are managed in

```text
docs/decisions/
```

File naming

```text
ADR-XXX-Short-English-Title.md
```

Rules

- ADR numbers increase sequentially and are never reused.
- Existing ADRs are never deleted. Use Deprecated or Superseded status instead.
- Before creating a new ADR, search existing ADRs for conflicts.
- After creating an ADR, update DECISIONS.md and CHANGELOG.md.
- Link related GitHub Issues and Pull Requests when available.

Detailed status definitions and the ADR index are managed in DECISIONS.md.

---

# GitHub Rules

FSAP uses GitHub as the official version control and collaboration repository.

## Branch Rules

- `main` is always kept in a reviewed and approved state.
- Do not commit directly to `main`.
- Each task uses a purpose-specific working branch.

Branch naming examples

```text
feature/feeding-control
design/binder-structure
fix/motion-offset
docs/adr-management
refactor/project-structure
test/curved-sewing-path
experiment/vision-edge-detection
```

## Commit Rules

- One commit should represent one logical change.
- Commit messages should describe what changed and why.
- Do not commit automatically unless explicitly requested.

## Pull Request Rules

Important changes are merged into `main` through a Pull Request.

A Pull Request should include, when possible:

- Purpose of the change
- Main changes
- Validation method and results
- Impact scope
- Related Issue
- Related ADR
- Whether CHANGELOG.md was updated

## Release Rules

- Official versions use Git Tags and GitHub Releases.
- Version format follows Semantic Versioning (example: v0.1.0).
- Each GitHub Release must match the same version section in CHANGELOG.md.

## Traceability

Keep the following records linked for important changes.

```text
Issue → ADR → Pull Request → CHANGELOG → Release
```

---

# Naming Convention

Project

FSAP

Products

MAT-RS-001

MAT-RS-002

CARPET-RS-001

LEATHER-RS-001

TEXTILE-RS-001

Folders

01_Planning

02_Concept

03_Design

04_Development

05_Validation

06_Business

Use consistent naming across all documentation.

---

# AI Response Style

Responses should

- Be technically accurate.
- Be concise but complete.
- Explain engineering decisions.
- Consider future reuse.
- Respect project standards.

Do not optimize only for the current task.

Always consider the long-term platform.

---

# Long-Term Goal

MAT-RS-001 is the first product.

FSAP is the final product.

Every technology developed for MAT-RS-001 should become part of the FSAP
platform.

The platform should continuously accumulate

- Mechanical Technology
- Feeding Technology
- Sewing Technology
- Motion Control
- Vision
- Automation Software
- Manufacturing Know-how
- Patents
- Engineering Knowledge

Every development activity should strengthen the platform.

---

# AI Final Rule

When responding,

AI should always ask itself:

1. Is this consistent with the FSAP platform philosophy?

2. Is this reusable for future products?

3. Should CHANGELOG.md be updated?

4. Should DECISIONS.md be updated?

If the answer to any of these questions is "No",

reconsider the proposed solution before responding.

# Golden Rule

When multiple solutions exist,

AI should recommend the solution that provides the highest long-term value for
the FSAP platform,

even if it requires slightly more effort in the short term.

Short-term convenience must never reduce long-term platform quality.
