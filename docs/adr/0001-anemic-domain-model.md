# ADR-0001: Anemic Domain Model for YeahTube

- **Status:** Accepted
- **Date:** 2026-05-09

## Context

We need domain models that:

- don’t depend on the database / SQLAlchemy
- are distinct from ORM entities (`Entity/ORM-model ≠ domain model`)
- can be mapped to/from ORM entities in the Infrastructure layer

The current codebase uses:

- SQLAlchemy ORM models in `app/db/models.py`
- repositories returning ORM entities directly
- Pydantic schemas (`app/schemas/schemas.py`) as API DTOs

## Decision

We will implement an **Anemic Domain Model**:

- domain models are simple dataclasses with identity and data
- invariants are validated at construction time using lightweight Value Objects
- business flows remain orchestrated in Services / Use-cases (application layer)

Mapping between domain and ORM will live in **Infrastructure** (`app/infrastructure/mappers`).

## Rationale

- Fits the existing architecture: services already contain most orchestration logic.
- Keeps refactor scope reasonable for Lab 2 (minimal disruption of repositories/services).
- Avoids coupling domain objects to persistence (no SQLAlchemy imports, no session awareness).
- Still enables explicit invariants through Value Objects (e.g., `Email`, bounded strings).

## Consequences

- Some domain rules will remain in services (not encapsulated as rich behaviors).
- Developers must be disciplined about creating domain objects through constructors / factories to enforce invariants.
- To prevent “pure DTO domain”, we will still use Value Objects for core constraints.
