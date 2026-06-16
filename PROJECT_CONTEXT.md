# GeoInsight API - Project Context

This document is the working product context for GeoInsight API. It is intended to keep future feature requests, implementation plans, and ownership-training exercises aligned with the actual roadmap instead of drifting into random feature work.

## Product Goal

GeoInsight API is a backend-only FastAPI service for geospatial analysis workflows.

The product goal is to provide a small but coherent geospatial backend that can:

- manage projects and Areas of Interest (AOIs),
- store AOI geometries in PostGIS,
- manage vector layer metadata,
- run AOI-based spatial analysis,
- expose analysis outputs through clear API contracts,
- remain testable and understandable as the geospatial workflow grows.

The portfolio goal is not just to show repository activity. The project should demonstrate end-to-end ownership: clarifying ambiguous requests, limiting scope, designing API behavior, handling edge cases, implementing safely, testing spatial correctness, and documenting decisions.

## Target Users

Primary target users for the current phase:

- a technical API consumer who wants to manage geospatial projects and AOIs,
- a geospatial analyst or product stakeholder who wants reproducible AOI-based spatial insights,
- a future frontend/dashboard client that will consume project, AOI, vector layer, and analysis result endpoints.

Current assumption: this is a backend-first portfolio product. The API contract, data model, spatial correctness, and tests matter more than UI polish at this stage.

## Current Scope

The service currently supports:

- health checks,
- project CRUD,
- AOI CRUD,
- PostGIS-backed AOI geometry storage,
- vector layer metadata CRUD,
- controlled demo land-use seed data,
- AOI-based land-use composition analysis using PostGIS.

The API is intentionally backend-only while the core geospatial workflow is being validated.

## Current Milestone

Expose persisted vector analysis results.

This milestone is focused on:

- result detail endpoint,
- AOI-level result listing endpoint,
- stronger spatial correctness tests.

The milestone should make analysis results easier to retrieve, inspect, test, and later consume from a frontend or dashboard.

## Near-Term Roadmap

1. Stabilize persisted vector analysis result access.
2. Improve spatial correctness test coverage around AOI/layer intersections and area calculations.
3. Strengthen API response contracts for analysis outputs.
4. Add small, realistic quality and validation checks only when they directly support the analysis workflow.
5. Keep the backend ready for a future dashboard/client without building the frontend prematurely.

## Non-Goals for the Current Phase

The following are intentionally out of scope unless explicitly promoted into the roadmap:

- frontend dashboard implementation,
- authentication, authorization, billing, or multi-tenant account management,
- external provider integrations,
- large-scale production deployment,
- async job queues beyond what the current workflow requires,
- raster analysis,
- AI/ML-based recommendations,
- complex dataset marketplace features,
- real-time collaboration,
- user notifications,
- advanced reporting/export features.

These may become future product directions, but adding them now would likely create scope drift.

## Core Entities

Current and near-term domain entities:

- `Project`: container for geospatial work.
- `AOI`: Area of Interest belonging to a project, stored with geometry.
- `VectorLayer`: metadata for a vector dataset/layer.
- `LandUseFeature`: controlled demo feature data used for land-use analysis.
- `AnalysisResult`: persisted output of an analysis workflow; result access is part of the current milestone.

Before implementing changes, confirm the exact current model names and relationships in the codebase.

## Core Workflows

### 1. Project and AOI setup

A user creates a project, then creates one or more AOIs under that project.

Ownership focus:

- validate geometry input,
- keep project/AOI relationships clear,
- avoid leaking implementation details in API responses,
- test missing project/AOI and invalid geometry cases.

### 2. Vector layer preparation

A user or seed script creates vector layer metadata and controlled demo land-use data.

Ownership focus:

- keep metadata contracts explicit,
- avoid pretending demo data is production ingestion,
- define what is validated now versus deferred.

### 3. AOI-based land-use composition analysis

A user runs land-use composition analysis for an AOI and vector layer.

Ownership focus:

- handle missing AOI/layer cases,
- handle no-intersection cases,
- test spatial correctness, not only status codes,
- define numeric precision/rounding expectations,
- keep analysis response shape stable.

### 4. Persisted result retrieval

A user retrieves analysis results by detail endpoint or AOI-level listing endpoint.

Ownership focus:

- define result identity and ownership clearly,
- prevent cross-AOI/project confusion,
- define ordering and pagination assumptions if needed,
- make response contracts usable for a future dashboard.

## Feature Request Rules

Future feature requests should be accepted only if they are traceable to at least one of:

- the product goal,
- the current milestone,
- a core workflow,
- a known risk,
- a deliberate out-of-scope/scope-control exercise.

A feature request should not be implemented just because it sounds realistic or technically interesting.

Every accepted feature should include:

- problem statement,
- user or stakeholder need,
- assumptions,
- non-goals,
- acceptance criteria,
- affected API/model/service/test areas,
- edge cases,
- test plan,
- smallest useful implementation.

## Ownership Training Rules

For each meaningful feature, bug, or refactor, answer these before coding:

1. What is the actual problem?
2. What is the smallest useful version?
3. What could break?
4. How will we know it works?

Clarification discipline:

- Ask at most three clarification questions.
- Make explicit assumptions when the risk is low.
- Do not block on alignment for low-risk, reversible decisions.
- Ask for alignment only when the decision affects scope, architecture, data correctness, API contracts, user-visible behavior, release risk, or future project direction.

## Quality Bar

A change is not considered complete only because the code runs.

Expected quality bar:

- API behavior is explicit and documented when needed.
- Tests cover meaningful behavior and edge cases.
- Spatial tests verify correctness, not only successful responses.
- Database migrations are included and checked when models change.
- Errors are predictable and useful for API consumers.
- The implementation avoids unnecessary abstraction.
- The change is small enough to review.

## Definition of Done

A task is done when:

- the minimal useful version is implemented,
- relevant tests pass,
- migrations are added or confirmed unnecessary,
- API contract changes are reflected in docs or examples when relevant,
- edge cases are either handled or explicitly documented as limitations,
- follow-up work is separated from the current scope,
- the decision/trade-off is clear enough to explain in an interview.

## Alignment Triggers

Require explicit alignment before implementation when a change:

- changes public API response shape,
- changes database schema or persisted result semantics,
- affects spatial correctness or numeric interpretation,
- expands the project beyond the current milestone,
- introduces external services or providers,
- adds infrastructure or deployment complexity,
- creates user-visible behavior that a future frontend would rely on.

## Parking Lot

Potential future directions that should not interrupt the current milestone:

- frontend analytics dashboard,
- external dataset ingestion,
- dataset quality classification,
- raster analysis,
- async processing pipeline,
- authentication and user accounts,
- deployment hardening,
- report generation/export,
- map visualization endpoints.

Parking lot items should be promoted only after the current milestone is stable or when they directly unblock the core workflow.

## Operating Principle

Keep GeoInsight API coherent.

Prefer a small, explainable, tested feature that advances the current milestone over a large impressive feature that weakens the roadmap.
