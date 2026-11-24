---
name: design-contracts
description: Vocabulary and rules for settling contracts while planning work - what a module guarantees and how it fails, which module owns each domain invariant, how to classify bad cases, and which decisions to settle now versus leave to implementation. Use when a plan or spec must fix the behaviour of a seam that more than one slice or module relies on. Not for changes inside one module, refactoring, or judging a module's shape.
---

# Design Contracts

Settle the contracts that separately built slices will rely on, and leave every other design decision to implementation. This builds on the vocabulary of the "codebase-design" skill: **module**, **interface**, **seam**, **adapter**, **depth**. A contract only makes sense once you know where its seam sits, so load the "codebase-design" skill whenever the module or seam in question is still unclear.

## Glossary

Use these terms exactly, alongside the codebase-design terms.

**Contract**: the behavioural part of a module's **interface**: what callers must do, what the module guarantees, and what callers see when it fails. Part of the interface, not a second thing beside it. _Avoid_: API contract, schema (both name only the type-level surface).

**Precondition**: an obligation a caller must meet before calling. Every precondition adds to what each caller must learn, so it makes the module shallower. Keep preconditions few and weak.

**Postcondition**: what the module guarantees after a successful call, observable through the interface. Make postconditions strong.

**Invariant**: a property that holds whenever a caller can observe the module. A contract holds only invariants a caller can observe through the interface. Invariants about internal state (the order of a private list) belong to the implementation: assert them in code, and keep them out of the contract and the spec.

**Domain invariant**: a business rule from the project glossary ("a balance is never negative"). A contract invariant is one module's promise to uphold a domain invariant.

**Owner**: the one module that upholds a given domain invariant. Every other module relies on the owner and does not check the rule again. A rule that applies to only some callers (a limit on ATM withdrawals only) is owned by the module for those callers, not pushed into the shared module behind a flag.

**Failure semantics**: what a caller sees when a call fails, and what state is left: nothing changed, partly applied, or safe to retry.

## Classify every bad case

Place each way a call can go wrong in one class before recording it:

- **Untrusted input** (from users or external systems): the module validates it and rejects it through its failure semantics.
- **Expected business failure** (insufficient funds): a normal result the module returns, part of its failure semantics.
- **Caller programming error** (an internal caller passes a negative amount): the only true precondition. Assert it in code; it rarely earns a line in the spec.

Most cases land in the first two classes, which keeps preconditions few.

## Settle now or leave

Settle a decision during planning when any of these holds:

- It crosses a seam that more than one slice relies on.
- It is expensive to reverse: schema, transaction boundary, public API, event shape.
- It affects security, consistency, or data integrity.
- Slices built in parallel must agree on it.

Leave a decision to implementation when it stays inside one module, is cheap to reverse, and changes no agreed contract. TDD and refactoring settle these. Record each left decision explicitly, so the implementer knows it is theirs to make. A question that blocks slicing the work is unresolved, not left: settle it.

Choose the enforcement of an owned invariant during planning only when the mechanism is expensive to reverse (a database constraint, a transaction boundary). Leave the rest (types, encapsulation, assertions, tests) to implementation.

Working out a contract often exposes a requirement nobody decided, such as whether a retried call may apply twice. Put it to the user as a question with your recommended answer; never settle a requirement silently.

## Done when

Contracts are settled when no planned slice forces its implementer to decide a contract that another slice also relies on. Check it this way:

1. List the planned slices, sketching them from the requirements if no breakdown exists yet.
2. Find every seam that more than one slice uses.
3. For each such seam, confirm that its failure semantics, the owner of each domain invariant it touches, and any expensive-to-reverse enforcement are settled or explicitly left to implementation.

A seam that only one slice uses needs none of this.

## Record a settled contract

Write each settled contract in prose, without code, so a spec can carry it:

- The seam, and the modules that rely on it.
- Its guarantees: postconditions and observable invariants.
- Its failure semantics.
- The owner of each domain invariant it touches, and how the owner enforces it.
- The decisions left to implementation.

## Rejected framings

- **A contract as a long precondition list** (classic Design by Contract): pushes checks onto every caller and makes the module shallow. Let the module handle the case and report it through failure semantics.
- **Contract-first as writing an interface type or port first**: a contract is agreed behaviour, and a plain function has one too. A port still needs two adapters to be a real seam.
- **Internal invariants in the contract**: leads tests to verify past the interface.
- **Settling every contract up front**: horizontal slicing moved into design. Settle only the shared seams.
