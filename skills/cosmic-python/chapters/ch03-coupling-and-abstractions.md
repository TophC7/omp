# Chapter 3: A Brief Interlude: On Coupling and Abstractions

## Core Idea
Coupling increases globally and superlinearly as systems grow; introducing simplifying abstractions separates *what* decisions to make from *how* to carry them out, enabling the "Functional Core, Imperative Shell" pattern where core logic is tested without mocks or external I/O.

## Frameworks Introduced
- **Functional Core, Imperative Shell (FCIS)**: An architectural design pattern coined by Gary Bernhardt dividing programs into pure decision logic and external side-effects.
  - When to use: When writing complex business logic that interacts with filesystems, networks, databases, or subprocesses.
  - How:
    1. *Imperative Shell (Input)*: Gather state from the external world into simple Python data structures (dicts, tuples, primitives).
    2. *Functional Core*: Pass the state into pure functions that calculate decisions, yielding a list of intent-revealing action commands.
    3. *Imperative Shell (Output)*: Iterate over the action commands and execute external I/O mutations (copy, delete, HTTP POST, database commit).
  - Why it works: The functional core contains all branching and edge cases and can be exhaustively unit-tested in microseconds using plain in-memory structures without mocking frameworks.
  - Failure mode: Interleaving I/O calls (e.g., fetching additional data or writing logs) directly inside the functional core.

- **Separating What from How**: Decoupling the generation of an operational plan from its physical execution.
  - When to use: When operations perform irreversible side effects (deleting files, charging credit cards, sending emails).
  - How: Model the system's output as declarative commands (e.g., `("COPY", src, dst)`, `("DELETE", path)`) instead of executing them inline.
  - Why it works: Allows inspecting, validating, filtering, and asserting on intended side effects before any external mutation occurs.

- **Mocking Smells as Architectural Diagnostics**: Using test friction to identify broken architectural boundaries.
  - When to use: Whenever a unit test requires patching multiple functions or modules (`mock.patch('os.walk')`, `mock.patch('shutil.copy')`).
  - How: Treat mock complexity as feedback that the code under test is tangled with I/O; refactor into an abstraction rather than adding more mock assertions.
  - Why it works: Tests that mock implementation details break whenever internal code changes, even if external behavior remains identical.

## Key Concepts
- **Coupling**: The degree of mutual dependency between components; when component A cannot change without risking breaking component B.
- **Cohesion**: The degree to which elements within a single component belong together and collaborate toward a single, focused purpose.
- **Local vs. Global Coupling**: Local coupling between highly cohesive components is healthy; global coupling between disparate subsystems creates a fragile Big Ball of Mud.
- **Simplifying Abstraction**: An interface that hides messy implementation mechanics behind an expressive, minimal contract.
- **Side Effects**: State modifications outside the local function scope (modifying global variables, writing to disk, mutating database rows).
- **Pure Function**: A deterministic function whose return value depends exclusively on its input arguments with zero side effects.

## Mental Models
- **Clock Gears vs. Tangles**: Local coupling is like the interlocking gears of a mechanical clock (high cohesion, precise fit); global coupling is like headphone cables tangled in a pocket (chaotic, hard to untangle).
- **The Sandwich Pattern**: The Imperative Shell acts as the two slices of bread (I/O read at the top, I/O write at the bottom), sandwiching the delicious meat of the Functional Core in the middle.
- **Declarative Command Streams**: Instead of executing side effects imperatively, have the core output a "recipe" of commands that an executor interprets.

## Anti-patterns
- **Mock Hell / Over-mocking**: Patching half a dozen external libraries (`os`, `requests`, `boto3`) inside a unit test. Tests become tightly coupled to private implementation details and fail on simple refactors.
- **I/O in the Core**: Embedding database queries, filesystem reads, or API requests inside calculation loops, making isolated unit testing impossible.
- **Premature Abstraction / Cargo-Cult Interfaces**: Abstracting before understanding the domain variations, creating vacuous wrappers that add indirection without reducing coupling.
- **Testing the Mock**: Writing assertions that merely verify mock methods were called in a specific sequence rather than testing observable outcomes.

## Code Examples

### Tangled Implementation with Mocking Pain

Tangled script interleaving filesystem I/O and business logic:
```python
# Anti-pattern: Interleaved I/O and business rules
import os, shutil, hashlib
from pathlib import Path

def sync(source, dest):
    for root, dirs, files in os.walk(source):
        for fn in files:
            sourcepath = Path(root) / fn
            destpath = Path(dest) / fn
            if not destpath.exists():
                shutil.copyfile(sourcepath, destpath)
            elif hashlib.md5(sourcepath.read_bytes()).hexdigest() != hashlib.md5(destpath.read_bytes()).hexdigest():
                shutil.copyfile(sourcepath, destpath)
    # Deleting missing files requires a second walk...
```

The resulting painful, brittle mock test:
```python
# Brittle test coupled to implementation mechanics
from unittest.mock import patch, call

def test_sync_copies_file_with_mocks():
    with patch("os.walk") as mock_walk, patch("shutil.copyfile") as mock_copy, patch("pathlib.Path.exists") as mock_exists:
        mock_walk.return_value = [("/src", [], ["file.txt"])]
        mock_exists.return_value = False
        
        sync("/src", "/dst")
        
        assert mock_copy.call_count == 1
        # Test breaks if we switch from copyfile to copy2 or refactor os.walk!
```
- **What it demonstrates**: Brittle assertions verifying internal calls rather than domain outcomes.

### Functional Core, Imperative Shell Refactoring

Pure Functional Core:
```python
# Pure domain logic: takes dicts, yields declarative commands
from pathlib import Path
from typing import Dict, Tuple, Iterator

def determine_actions(
    source_hashes: Dict[str, str],
    dest_hashes: Dict[str, str],
    source_folder: Path,
    dest_folder: Path,
) -> Iterator[Tuple[str, Path, ...]]:
    for sha, filename in source_hashes.items():
        if sha not in dest_hashes:
            yield ("COPY", source_folder / filename, dest_folder / filename)
        elif dest_hashes[sha] != filename:
            yield ("MOVE", dest_folder / dest_hashes[sha], dest_folder / filename)

    for sha, filename in dest_hashes.items():
        if sha not in source_hashes:
            yield ("DELETE", dest_folder / filename)
```

Imperative Shell:
```python
# Thin imperative shell: gathers state and applies side effects
import os, shutil, hashlib

def hash_file(path: Path) -> str:
    return hashlib.sha1(path.read_bytes()).hexdigest()

def read_paths_and_hashes(root: Path) -> Dict[str, str]:
    hashes = {}
    for folder, _, files in os.walk(root):
        for fn in files:
            p = Path(folder) / fn
            hashes[hash_file(p)] = str(p.relative_to(root))
    return hashes

def sync(source: Path, dest: Path) -> None:
    # 1. Gather inputs
    src_hashes = read_paths_and_hashes(source)
    dst_hashes = read_paths_and_hashes(dest)

    # 2. Functional core decision
    actions = determine_actions(src_hashes, dst_hashes, source, dest)

    # 3. Apply outputs
    for action, *paths in actions:
        if action == "COPY":
            shutil.copyfile(paths[0], paths[1])
        elif action == "MOVE":
            shutil.move(paths[0], paths[1])
        elif action == "DELETE":
            os.remove(paths[0])
```
- **What it demonstrates**: Separation of pure domain decisions from external I/O execution.

## Reference Tables

### Mock-Heavy Unit Tests vs. Functional Core Unit Tests

| Dimension | Mock-Heavy Approach | Functional Core (FCIS) Approach |
|---|---|---|
| **Test Inputs** | Mocked objects, patched module functions | Plain Python dicts, strings, value objects |
| **Test Assertions** | `mock.assert_called_with(...)` | Exact comparison on returned data structures |
| **Refactoring Safety** | Low; changing internal calls breaks tests | High; tests only depend on inputs and returned decisions |
| **Execution Speed** | Moderate; overhead of patching context managers | Blindingly fast; pure in-memory execution |
| **Failure Diagnosis** | Hard; cryptic mock assertion mismatch | Easy; standard data structure diff (`assert [('COPY', ...)] == ...`) |

## Worked Example

### Testing the Functional Core with Zero Mocks

```python
from pathlib import Path

def test_when_a_file_exists_in_source_but_not_destination():
    src_hashes = {"hash1": "doc.pdf"}
    dst_hashes = {}
    actions = list(determine_actions(src_hashes, dst_hashes, Path("/src"), Path("/dst")))
    assert actions == [("COPY", Path("/src/doc.pdf"), Path("/dst/doc.pdf"))]

def test_when_a_file_has_been_renamed_in_source():
    src_hashes = {"hash1": "new_name.pdf"}
    dst_hashes = {"hash1": "old_name.pdf"}
    actions = list(determine_actions(src_hashes, dst_hashes, Path("/src"), Path("/dst")))
    assert actions == [("MOVE", Path("/dst/old_name.pdf"), Path("/dst/new_name.pdf"))]

def test_when_a_file_is_deleted_from_source():
    src_hashes = {}
    dst_hashes = {"hash1": "redundant.tmp"}
    actions = list(determine_actions(src_hashes, dst_hashes, Path("/src"), Path("/dst")))
    assert actions == [("DELETE", Path("/dst/redundant.tmp"))]
```

## Key Takeaways
1. Global coupling destroys maintainability; simplifying abstractions protect components from ripple effects.
2. Use "Functional Core, Imperative Shell" to isolate complex decision logic from messy external I/O.
3. Separate *what* to do (returning intent-revealing command tuples) from *how* to do it (executing side effects).
4. Difficulty in writing unit tests is an architectural signal: heavy mocking indicates that I/O and business logic are tangled.
5. Pure functions that accept simple data structures and return simple data structures are trivial to test and reason about.

## Connects To
- **Ch 02**: Repository Pattern — the abstraction separating domain logic from the imperative shell of database I/O.
- **Ch 04**: Service Layer — the imperative shell orchestrating domain logic, repositories, and API entry points.
- **Ch 10**: Commands and Command Handlers — scaling the "separating what from how" pattern to application-wide architecture.
