# Chapter 18: Arrays, Functions, and Objects in JavaScript

## Core Idea
JavaScript is a multi-paradigm language built on first-class functions, prototype-based object orientation, and high-performance collection abstractions. Organizing logic requires mastering function declarations vs. arrow functions (and their lexical `this` behavior), immutable array transformation pipelines (`map`, `filter`, `reduce`), and object-oriented encapsulation using modern ES6 `class` syntax.

## Frameworks Introduced
- **The Function Selection Protocol (Declaration vs. Arrow Function)**:
  - When to use: Defining subroutines, methods, or event callbacks.
  - How:
    - Use standard `function name() { ... }` declarations for top-level module routines (supports hoisting) or object methods where dynamic, caller-bound `this` is required.
    - Use arrow functions `const fn = () => { ... }` for functional array callbacks (`.map()`, `.filter()`), asynchronous timer intervals (`setTimeout`), or class property handlers where lexical capture of the enclosing parent `this` context is essential.
- **The Functional Array Transformation Pipeline**:
  - When to use: Processing, filtering, and summarizing data lists without mutating source arrays.
  - How: Chain pure, non-mutating array methods rather than writing imperative for-loops:
    1. Filter out unwanted items via `.filter(predicateFn)`.
    2. Transform surviving items via `.map(transformFn)`.
    3. Aggregate into a final primitive or object via `.reduce(reducerFn, initialValue)`.
    - Avoid mutating methods (`push`, `splice`, `sort`) on shared state without creating a shallow copy (`[...items]`) first.
- **ES6 Class Architecture Framework**:
  - When to use: Modeling business domain entities, state stores, and UI component controllers.
  - How: Define entities with `class Name { constructor(...) { ... } }`. Encapsulate internal state with private fields (`#property`) or getter/setter accessors (`get`, `set`). Attach methods directly inside the class body; instantiate via `const instance = new Name()`.

## Key Concepts
- **First-Class Functions**: In JavaScript, functions are objects; they can be assigned to variables, passed as arguments into other functions, and returned from functions.
- **Lexical Scope**: Scope determined by the physical placement of code blocks in source text; inner functions retain access to variables declared in outer enclosing scopes (closures).
- **Arrow Function (`() => {}`)**: Compact function syntax that does not bind its own `this`, `arguments`, or `super`; inherits `this` lexically from the surrounding scope.
- **Array**: Ordered, zero-indexed list collection capable of holding mixed data types.
- **Array Mutators vs. Accessors**:
  - Mutators modify the array in place: `push()`, `pop()`, `shift()`, `unshift()`, `splice()`, `reverse()`, `sort()`.
  - Accessors/Iterators return new values without mutating source: `slice()`, `concat()`, `join()`, `map()`, `filter()`, `reduce()`, `find()`, `includes()`.
- **`this` Keyword**: Context reference determined by *how* a function is called:
  - In a method: points to the owner object.
  - In a standalone function: points to `undefined` (in strict mode).
  - In an arrow function: points to the enclosing lexical scope's `this`.
- **`Map` and `Set`**: Dedicated collection types. `Map` holds keyed key-value pairs of arbitrary types; `Set` stores unique values with zero duplicates.

## Mental Models
- **Think of Array Pipeline Methods as Factory Assembly Lines**:
  - `.filter()` is the quality inspector tossing broken parts into the bin.
  - `.map()` is the painting machine applying a fresh coat of lacquer to every surviving part.
  - `.reduce()` is the packaging worker packing all finished parts into a single shipping crate.
- **Think of `this` in Arrow Functions vs. Regular Functions as a Cell Phone vs. a Payphone**:
  - A regular function is a public payphone: whoever walks up and dials (`obj.method()`) determines whose call it is (`this = obj`).
  - An arrow function is your personal cell phone: wherever you carry it, it is permanently tied to your personal identity (`this` stays bound to where you created it).

## Anti-patterns
- **Using Arrow Functions as Object Methods**: Writing `const user = { name: "Alice", greet: () => console.log(this.name) };`. Because the arrow function inherits `this` from the global module scope, `this.name` is undefined. Use shorthand method syntax: `greet() { console.log(this.name); }`.
- **In-Place Sorting of Source State**: Calling `state.products.sort()`. In JavaScript, `.sort()` mutates the original array in memory, causing unexpected side effects in reactive frameworks. Copy before sorting: `[...state.products].sort()`.
- **Imperative Loop Accumulation for Simple Mapping**: Writing 10 lines of `let results = []; for (...) { results.push(...); }` when a single readable `.map()` chain accomplishes the transformation immutably.
- **Modifying Objects Inside a `forEach` without Pure Returns**: Using `.forEach()` to mutate global variables instead of using `.map()` or `.reduce()`.

## Code Examples
```javascript
"use strict";

// 1. Functional Array Processing Pipeline (Filter, Map, Reduce)
const products = [
  { id: 101, name: "Wireless Mouse", price: 29.99, category: "Electronics", inStock: true },
  { id: 102, name: "Mechanical Keyboard", price: 89.99, category: "Electronics", inStock: false },
  { id: 103, name: "Coffee Beans (1kg)", price: 18.50, category: "Groceries", inStock: true },
  { id: 104, name: "Noise-Cancelling Headphones", price: 199.99, category: "Electronics", inStock: true }
];

// Calculate total value of in-stock electronic goods
const totalElectronicsValue = products
  .filter(product => product.inStock && product.category === "Electronics")
  .map(product => product.price)
  .reduce((accumulator, currentPrice) => accumulator + currentPrice, 0);

console.log(`In-Stock Electronics Valuation: $${totalElectronicsValue.toFixed(2)}`);

// 2. Object-Oriented Domain Entity with ES6 Class
class ShoppingCart {
  constructor(customerName) {
    this.customer = customerName;
    this.items = []; // Internal collection
  }

  // Method to add item
  addItem(product, quantity = 1) {
    this.items.push({ ...product, quantity });
    console.log(`Added ${quantity}x ${product.name} to cart.`);
  }

  // Computed getter property
  get subtotal() {
    return this.items.reduce((sum, item) => sum + (item.price * item.quantity), 0);
  }

  // Lexical arrow function ensuring safe callback execution
  printReceipt = () => {
    console.log(`Receipt for: ${this.customer}`);
    this.items.forEach(item => {
      console.log(`- ${item.quantity}x ${item.name} ($${item.price} each)`);
    });
    console.log(`Subtotal: $${this.subtotal.toFixed(2)}`);
  };
}

// Instantiate and exercise the class
const cart = new ShoppingCart("Gabriel");
cart.addItem(products[0], 2); // 2 mice
cart.addItem(products[3], 1); // 1 headphones
cart.printReceipt();

// 3. Collection Deduplication with Set
const rawTags = ["html", "css", "javascript", "css", "web", "html"];
const uniqueTags = [...new Set(rawTags)];
console.log("Unique Tags:", uniqueTags); // ["html", "css", "javascript", "web"]
```
- **What it demonstrates**: Immutable array method chaining (`filter`, `map`, `reduce`), ES6 class encapsulation with constructor and getters, lexical arrow method binding, and array deduplication with `Set`.

## Reference Tables

### Common Array Methods Cheat Sheet
| Method | Type | Return Value | Mutates Original Array? | Primary Purpose |
|---|---|---|---|---|
| `.filter(fn)` | Iteration | New filtered array | **No** | Retains items satisfying boolean predicate |
| `.map(fn)` | Iteration | New transformed array | **No** | Transforms each item 1-to-1 into new shape |
| `.reduce(fn, init)` | Iteration | Single accumulated value | **No** | Condenses list into sum, object, or map |
| `.find(fn)` | Search | First matching element | **No** | Locates single object matching condition |
| `.includes(val)` | Search | Boolean (`true`/`false`) | **No** | Checks primitive existence in list |
| `.slice(start, end)` | Accessor | Shallow slice array | **No** | Extracts subsection of array |
| `.splice(start, del)` | Mutator | Array of deleted items | **YES** | In-place insertion, replacement, deletion |
| `.push(val)` | Mutator | New array length | **YES** | Appends item to end of array |
| `.pop()` | Mutator | Removed last item | **YES** | Removes and returns last element |

### Function Syntax Variants
| Syntax Style | Example | Hoisted? | Has Own `this`? | Best Used For |
|---|---|---|---|---|
| **Declaration** | `function add(a, b) { return a + b; }` | **Yes** | Yes (Caller bound) | Top-level routines, utilities |
| **Expression** | `const add = function(a, b) { ... };` | No (TDZ) | Yes (Caller bound) | Conditional function definitions |
| **Arrow Function** | `const add = (a, b) => a + b;` | No (TDZ) | **No** (Lexical parent) | Callbacks, array pipelines, closures |
| **Class Method** | `class Calc { add(a, b) { ... } }` | No | Yes (Instance bound) | OOP object behaviors |

## Worked Example
A shopping application receives a dirty array of customer orders with negative quantities and strings:
```javascript
const rawOrders = [
  { item: "Widget", qty: "3", unitPrice: 10 },
  { item: "Gadget", qty: -1, unitPrice: 20 },
  { item: "Doodad", qty: 2, unitPrice: 15 }
];
```
**Refactoring to a clean data transformation**:
```javascript
"use strict";

const validProcessedOrders = rawOrders
  .map(order => ({
    item: order.item,
    qty: Number(order.qty),
    unitPrice: order.unitPrice
  }))
  .filter(order => !isNaN(order.qty) && order.qty > 0)
  .map(order => ({
    ...order,
    lineTotal: order.qty * order.unitPrice
  }));

console.log(validProcessedOrders);
// Outputs clean array with 2 valid line items, normalized quantities, and line totals.
```

## Key Takeaways
1. Prefer arrow functions for array callbacks and asynchronous handlers to preserve lexical `this`.
2. Master the array triumvirate: `.filter()` to prune, `.map()` to transform, and `.reduce()` to summarize.
3. Treat state as immutable; avoid mutator methods (`splice`, `sort`, `reverse`) on shared state without copying.
4. Use ES6 `class` syntax to create well-structured object models with constructors and getters.
5. Use `Set` to instantly deduplicate arrays: `[...new Set(array)]`.
6. Distinguish between lexical scope (where code is written) and execution context (how `this` is called).

## Connects To
- **Ch 17**: Builds directly upon JavaScript variable bindings and primitive data types.
- **Ch 19**: These arrays and functions provide the logic behind dynamic DOM element generation.
- **Ch 20**: Used to iterate through JSON API payloads returned from asynchronous Ajax network requests.
