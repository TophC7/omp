# Chapter 19: Changing Web Pages Dynamically

## Core Idea
The Document Object Model (DOM) provides an in-memory, object-oriented representation of the active web document exposed to JavaScript via the global `document` interface. Dynamic client-side engineering revolves around selecting nodes (`querySelector`), mutating attributes and class tokens (`classList`), creating and mounting DOM elements (`createElement`, `appendChild`), and responding to user actions through an asynchronous, three-phase event propagation model (Capturing, Target, Bubbling).

## Frameworks Introduced
- **The Modern DOM Selection & Query Framework**:
  - When to use: Locating elements in the live document tree.
  - How:
    - Use `document.querySelector('css-selector')` to return the first matching single `Element` (or `null`).
    - Use `document.querySelectorAll('css-selector')` to return a static `NodeList` containing all matching nodes; iterate directly with `.forEach()`.
    - Use `document.getElementById('id')` for maximum performance on single unique ID lookups.
    - Avoid legacy live collections (`getElementsByTagName`, `getElementsByClassName`) whose mutation-driven auto-updates create performance bottlenecks and indexing bugs.
- **The Event Delegation Architecture**:
  - When to use: Handling events on large, repeating, or dynamically generated lists (e.g., todo lists, data tables, infinite scroll feeds).
  - How: Instead of attaching 1,000 separate event listeners to 1,000 individual `<li>` or `<button>` children, attach a single listener to their common parent container. Leverage event bubbling to intercept the event as it rises to the parent; inspect `event.target.closest('.item-btn')` to identify which child was clicked:
    ```javascript
    parentList.addEventListener('click', (event) => {
      const deleteBtn = event.target.closest('.btn-delete');
      if (deleteBtn) {
        deleteBtn.closest('li').remove();
      }
    });
    ```
- **The Safe Node Creation & Mutation Pipeline**:
  - When to use: Injecting user-supplied data or building dynamic UI components.
  - How: Never use `element.innerHTML` with un-sanitized user strings (exposes the application to Cross-Site Scripting / XSS attacks). Use programmatic DOM creation:
    1. Create element node: `const card = document.createElement('div')`.
    2. Set classes: `card.classList.add('user-card')`.
    3. Safely insert text: `card.textContent = userInput`.
    4. Mount into DOM: `container.appendChild(card)`.

## Key Concepts
- **Document Object Model (DOM)**: Hierarchical tree of objects representing HTML elements, attributes, and text nodes in browser memory.
- **Node vs. Element**: Every element is a node (`Node.ELEMENT_NODE`), but nodes also include text fragments (`Node.TEXT_NODE`) and comments (`Node.COMMENT_NODE`).
- **`textContent` vs. `innerHTML`**:
  - `textContent`: Sets or retrieves raw text content; safely treats markup strings as literal text without HTML parsing (XSS immune).
  - `innerHTML`: Parses markup strings into actual DOM elements; high XSS risk if given user-submitted text.
- **`classList`**: Dedicated interface for managing CSS class tokens on an element: `.add()`, `.remove()`, `.toggle()`, `.contains()`, `.replace()`.
- **`addEventListener(type, listener, options)`**: Standard method attaching event handlers to elements without overwriting existing listeners.
- **`event.preventDefault()`**: Method canceling the browser's default action associated with an event (e.g., preventing a form from submitting across the network or a link from navigating).
- **`event.stopPropagation()`**: Method halting the event from traveling further up or down the DOM tree during the propagation phases.
- **Event Bubbling**: The phase where an event triggered on a target child element bubbles up through parent ancestors up to `document` and `window`.

## Mental Models
- **Think of the DOM as an Organism and `innerHTML` as a Blunt Meat Cleaver**:
  - Setting `innerHTML += "<li>New</li>"` does not just append a node; it wipes out the *entire* existing child tree, re-parses raw HTML text from scratch, and destroys all attached event listeners and state on existing children.
  - `document.createElement()` and `appendChild()` are precision surgical scalpels: they graft a single new organ onto the body without disturbing existing tissue.
- **Think of Event Propagation as a Deep-Sea Submarine Dive and Ascent**:
  - **Capturing Phase**: The submarine dives from the ocean surface (`window` -> `document` -> `body`) down into the deep trench to locate the sunken shipwreck (`event.target`).
  - **Target Phase**: The submarine arrives at the wreck and triggers inspection sensors.
  - **Bubbling Phase**: The submarine surfaces back up to the ocean surface, firing alert signals at every depth level as it passes parent vessels along the way.

## Anti-patterns
- **Using `innerHTML` to Append Dynamic Content**: Writing `list.innerHTML += '<li>' + text + '</li>'`. Causes severe browser re-flow, wipes out input states on neighboring elements, and opens a severe XSS vulnerability if `text` contains `<script>` or `<img src=x onerror=alert()>`.
- **Inline HTML Event Attributes**: Writing `<button onclick="doAction()">`. Pollutes semantic markup, introduces global namespace scope bugs, and violates modern Content Security Policies (CSP). Always use `addEventListener` in external scripts.
- **Memory Leaks via Redundant Event Listeners in Loops**: Attaching individual listeners to thousands of table cells in an iterative loop. Bloats browser memory; use event delegation on the `<table>` element instead.
- **Direct Style Mutation (`element.style.color = "red"`)**: Hard-coding CSS properties directly via JavaScript. Violates separation of concerns and creates high-specificity inline styles that override stylesheets. Toggle semantic CSS classes via `element.classList.toggle('is-error')` instead.

## Code Examples
```javascript
"use strict";

// 1. Querying DOM Nodes
const taskForm = document.querySelector("#todo-form");
const taskInput = document.querySelector("#task-input");
const taskList = document.querySelector("#task-list");
const clearCompletedBtn = document.querySelector("#clear-completed");

// 2. Handling Form Submit with preventDefault
taskForm.addEventListener("submit", (event) => {
  event.preventDefault(); // Stop default browser page refresh/navigation

  const title = taskInput.value.trim();
  if (title === "") {
    return;
  }

  // 3. Safe Dynamic Node Creation (XSS-proof)
  const listItem = document.createElement("li");
  listItem.classList.add("task-item");

  const taskText = document.createElement("span");
  taskText.classList.add("task-label");
  taskText.textContent = title; // Safe literal text assignment

  const completeBtn = document.createElement("button");
  completeBtn.type = "button";
  completeBtn.classList.add("btn-toggle");
  completeBtn.textContent = "Done";

  const deleteBtn = document.createElement("button");
  deleteBtn.type = "button";
  deleteBtn.classList.add("btn-delete");
  deleteBtn.textContent = "Delete";

  // Assemble and mount into DOM
  listItem.append(taskText, completeBtn, deleteBtn);
  taskList.appendChild(listItem);

  // Reset form field
  taskInput.value = "";
  taskInput.focus();
});

// 4. Event Delegation Pattern on Parent Container
taskList.addEventListener("click", (event) => {
  const target = event.target;

  // Check if click was on the toggle button
  if (target.classList.contains("btn-toggle")) {
    const parentItem = target.closest(".task-item");
    parentItem.classList.toggle("is-completed");
  }

  // Check if click was on the delete button
  if (target.classList.contains("btn-delete")) {
    const parentItem = target.closest(".task-item");
    parentItem.remove(); // Native clean removal from DOM tree
  }
});
```
- **What it demonstrates**: `querySelector` node acquisition, `event.preventDefault()` on form submit, safe XSS-proof element construction (`createElement`, `textContent`, `append`), class toggling via `classList`, and parent-level event delegation (`closest`).

## Reference Tables

### Modern DOM Node Selection API
| Method | Returns | Argument Syntax | Live Collection? | Primary Use Case |
|---|---|---|---|---|
| `document.querySelector()` | Single `Element` (or `null`) | Any valid CSS selector (e.g., `.nav > li.active`) | No | First single matching element |
| `document.querySelectorAll()` | Static `NodeList` | Any valid CSS selector (e.g., `tbody tr`) | **No** (Safe snapshot) | Multi-element batch iteration |
| `document.getElementById()` | Single `Element` (or `null`) | Plain ID string without `#` (e.g., `'main-nav'`) | No | High-speed single ID lookup |
| `element.closest()` | Nearest ancestor `Element` | CSS selector | No | Ascending DOM traversal in event delegation |

### Event Object Properties & Methods
| Feature | Type | Purpose / Description |
|---|---|---|
| `event.target` | Property (`Element`) | The actual lowest-level element that received the interaction |
| `event.currentTarget`| Property (`Element`) | The element to which the event handler is currently attached |
| `event.preventDefault()` | Method | Suppresses default browser behavior (form submit, link jump) |
| `event.stopPropagation()`| Method | Prevents event from bubbling up or capturing down to other nodes |
| `event.key` | Property (`string`) | Name of keyboard key pressed (e.g., `"Enter"`, `"Escape"`) |
| `event.clientX / clientY`| Property (`number`) | Coordinates of mouse pointer relative to browser viewport |

## Worked Example
A table with 500 product inventory rows requires a "Remove" button per row. Attaching listeners individually wastes memory and fails on newly fetched rows.
```html
<table id="inventory-table">
  <tbody>
    <tr><td>Apples</td><td><button class="remove-btn">Remove</button></td></tr>
    <!-- 500 more rows -->
  </tbody>
</table>
```
**Implementing Event Delegation**:
```javascript
"use strict";

const table = document.querySelector("#inventory-table");

// Single listener attached to the <table> element
table.addEventListener("click", (event) => {
  // Check if click originated from or inside a remove button
  const button = event.target.closest(".remove-btn");
  if (!button) return; // Ignore clicks elsewhere on table

  const row = button.closest("tr");
  if (row) {
    row.remove(); // Safely removes the entire table row
    console.log("Row deleted via delegation.");
  }
});
```
**Advantage**: Memory consumption drops from 500 closures to 1 listener; dynamically inserted rows added in the future work immediately without manual rebinding.

## Key Takeaways
1. Always prefer `querySelector` and `querySelectorAll` for modern, CSS-compatible DOM selection.
2. Use `textContent` instead of `innerHTML` when displaying user input to prevent Cross-Site Scripting (XSS).
3. Manage styling state through `element.classList.add()`, `.remove()`, and `.toggle()` rather than inline styles.
4. Call `event.preventDefault()` on form submissions to prevent unwanted full-page browser reloads.
5. Use event delegation on parent containers to handle dynamic lists efficiently and prevent memory leaks.
6. Modern element removal is clean and direct via `element.remove()`.

## Connects To
- **Ch 02**: Manipulates the exact DOM tree nodes described in the document structure foundations.
- **Ch 07**: Intercepts, validates, and processes `<form>` elements and interactive `<dialog>` controls.
- **Ch 20**: Provides the rendering mechanisms to inject asynchronous Ajax data into the page.
