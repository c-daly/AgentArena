"""Random source code mutations for agent exploration (epsilon).

Injects real utility functions, reorders code, adds documentation,
extracts constants, and creates function variants. Mutations are
AST-based where possible, falling back to returning the original
source unchanged if parsing fails. Mutations are meant to occasionally
produce useful variations — they don't need to be correct every time.
"""

import ast
import random
import string
import textwrap
from typing import Callable


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------

def should_mutate() -> bool:
    """Returns True ~25% of the time."""
    return random.random() < 0.25


def mutate(source_code: str) -> str:
    """Apply a single random mutation to *source_code* and return the result.

    If the chosen mutation fails for any reason the original source is
    returned unchanged — mutations should never break what they can't
    improve.
    """
    mutation = random.choice(MUTATIONS)
    try:
        return mutation(source_code)
    except Exception:
        return source_code


# ---------------------------------------------------------------------------
# Utility snippet bank (inject_utility draws from these)
# ---------------------------------------------------------------------------

_UTILITY_SNIPPETS: list[str] = [
    # 0 — memoization decorator
    textwrap.dedent("""\
    def memoize(func):
        \"\"\"Simple memoization decorator for pure functions.\"\"\"
        _cache: dict = {}
        def wrapper(*args, **kwargs):
            key = (args, tuple(sorted(kwargs.items())))
            if key not in _cache:
                _cache[key] = func(*args, **kwargs)
            return _cache[key]
        wrapper._cache = _cache
        return wrapper
    """),

    # 1 — timer decorator
    textwrap.dedent("""\
    def timed(func):
        \"\"\"Decorator that prints elapsed wall-clock time for each call.\"\"\"
        import time as _time
        def wrapper(*args, **kwargs):
            _t0 = _time.perf_counter()
            result = func(*args, **kwargs)
            _elapsed = _time.perf_counter() - _t0
            print(f"{func.__name__} took {_elapsed:.4f}s")
            return result
        return wrapper
    """),

    # 2 — error classifier
    textwrap.dedent("""\
    def classify_error(exc: Exception) -> str:
        \"\"\"Return a coarse category string for an exception.\"\"\"
        mapping = {
            TypeError: "type_error",
            ValueError: "value_error",
            KeyError: "key_error",
            IndexError: "index_error",
            AttributeError: "attribute_error",
            RuntimeError: "runtime_error",
            StopIteration: "exhausted",
        }
        for cls, label in mapping.items():
            if isinstance(exc, cls):
                return label
        return "unknown"
    """),

    # 3 — AST node counter
    textwrap.dedent("""\
    def count_ast_nodes(source: str) -> dict[str, int]:
        \"\"\"Count occurrences of each AST node type in *source*.\"\"\"
        import ast as _ast
        tree = _ast.parse(source)
        counts: dict[str, int] = {}
        for node in _ast.walk(tree):
            name = type(node).__name__
            counts[name] = counts.get(name, 0) + 1
        return counts
    """),

    # 4 — retry with backoff
    textwrap.dedent("""\
    def retry(max_attempts: int = 3, backoff: float = 0.5):
        \"\"\"Decorator that retries on exception with exponential backoff.\"\"\"
        import time as _time
        def decorator(func):
            def wrapper(*args, **kwargs):
                last_exc = None
                for attempt in range(max_attempts):
                    try:
                        return func(*args, **kwargs)
                    except Exception as exc:
                        last_exc = exc
                        if attempt < max_attempts - 1:
                            _time.sleep(backoff * (2 ** attempt))
                raise last_exc  # type: ignore[misc]
            return wrapper
        return decorator
    """),

    # 5 — flatten nested iterables
    textwrap.dedent("""\
    def flatten(iterable):
        \"\"\"Recursively flatten nested lists/tuples into a single list.\"\"\"
        result = []
        for item in iterable:
            if isinstance(item, (list, tuple)):
                result.extend(flatten(item))
            else:
                result.append(item)
        return result
    """),

    # 6 — chunked iteration
    textwrap.dedent("""\
    def chunked(seq, size: int):
        \"\"\"Yield successive *size*-length chunks from *seq*.\"\"\"
        for i in range(0, len(seq), size):
            yield seq[i:i + size]
    """),

    # 7 — safe dictionary deep-get
    textwrap.dedent("""\
    def deep_get(mapping: dict, *keys, default=None):
        \"\"\"Traverse nested dicts by *keys*, returning *default* on any miss.\"\"\"
        current = mapping
        for k in keys:
            if isinstance(current, dict):
                current = current.get(k, default)
            else:
                return default
        return current
    """),

    # 8 — frequency counter
    textwrap.dedent("""\
    def frequency(iterable) -> dict:
        \"\"\"Return a dict mapping each element to its count.\"\"\"
        counts: dict = {}
        for item in iterable:
            counts[item] = counts.get(item, 0) + 1
        return counts
    """),

    # 9 — LRU cache with max-size (stdlib-free)
    textwrap.dedent("""\
    def lru(maxsize: int = 128):
        \"\"\"Least-recently-used cache decorator (no functools dependency).\"\"\"
        from collections import OrderedDict
        def decorator(func):
            cache: OrderedDict = OrderedDict()
            def wrapper(*args):
                if args in cache:
                    cache.move_to_end(args)
                    return cache[args]
                result = func(*args)
                cache[args] = result
                if len(cache) > maxsize:
                    cache.popitem(last=False)
                return result
            wrapper.cache = cache
            return wrapper
        return decorator
    """),
]


# ---------------------------------------------------------------------------
# Mutation implementations
# ---------------------------------------------------------------------------

def _inject_utility(source: str) -> str:
    """Insert a random utility function at the top of the module."""
    tree = ast.parse(source)
    snippet_source = random.choice(_UTILITY_SNIPPETS)
    snippet_tree = ast.parse(snippet_source)

    # Check if a function with the same name already exists
    existing_names = {
        node.name
        for node in ast.walk(tree)
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef))
    }
    for node in ast.walk(snippet_tree):
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            if node.name in existing_names:
                # Already has a function by that name — skip
                return source

    # Find insertion point: after imports, before first function/class
    insert_idx = 0
    for i, node in enumerate(tree.body):
        if isinstance(node, (ast.Import, ast.ImportFrom)):
            insert_idx = i + 1
        elif isinstance(node, ast.Expr) and isinstance(
            getattr(node, "value", None), (ast.Constant, ast.Str)
        ):
            # module docstring
            insert_idx = i + 1

    for new_node in reversed(snippet_tree.body):
        ast.fix_missing_locations(new_node)
        tree.body.insert(insert_idx, new_node)

    return ast.unparse(tree)


def _reorder_functions(source: str) -> str:
    """Randomly reorder top-level function definitions."""
    tree = ast.parse(source)

    # Separate function defs from everything else, preserving order of
    # non-function nodes (imports, assignments, etc.)
    func_indices: list[int] = []
    funcs: list[ast.stmt] = []
    for i, node in enumerate(tree.body):
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            func_indices.append(i)
            funcs.append(node)

    if len(funcs) < 2:
        return source  # nothing to reorder

    random.shuffle(funcs)

    for idx, func in zip(func_indices, funcs):
        tree.body[idx] = func

    return ast.unparse(tree)


def _add_docstring(source: str) -> str:
    """Add a simple docstring to a random function that lacks one."""
    tree = ast.parse(source)

    candidates: list[ast.FunctionDef | ast.AsyncFunctionDef] = []
    for node in ast.walk(tree):
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            if not ast.get_docstring(node):
                candidates.append(node)

    if not candidates:
        return source  # every function already has one

    target = random.choice(candidates)

    # Build argument description
    arg_names = [a.arg for a in target.args.args if a.arg != "self"]
    if arg_names:
        params_note = f" Accepts: {', '.join(arg_names)}."
    else:
        params_note = ""

    doc_text = f"Auto-generated docstring for {target.name}.{params_note}"
    doc_node = ast.Expr(value=ast.Constant(value=doc_text))
    ast.fix_missing_locations(doc_node)
    target.body.insert(0, doc_node)

    return ast.unparse(tree)


def _extract_constant(source: str) -> str:
    """Find a magic number or string literal inside a function and extract
    it as a module-level constant."""
    tree = ast.parse(source)

    # Collect candidate literals inside functions
    candidates: list[tuple[ast.FunctionDef | ast.AsyncFunctionDef, ast.Constant]] = []
    for node in ast.walk(tree):
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            for child in ast.walk(node):
                if isinstance(child, ast.Constant) and isinstance(
                    child.value, (int, float, str)
                ):
                    # Skip trivial values (0, 1, "", True/False, docstrings)
                    if isinstance(child.value, (int, float)) and child.value in (0, 1, -1):
                        continue
                    if isinstance(child.value, str) and len(child.value) < 2:
                        continue
                    # Skip if this constant is a docstring (first expr in body)
                    if (
                        node.body
                        and isinstance(node.body[0], ast.Expr)
                        and isinstance(node.body[0].value, ast.Constant)
                        and node.body[0].value is child
                    ):
                        continue
                    candidates.append((node, child))

    if not candidates:
        return source

    func_node, const_node = random.choice(candidates)

    # Generate a constant name
    if isinstance(const_node.value, str):
        # Derive name from value
        slug = const_node.value[:20].upper().replace(" ", "_")
        slug = "".join(c for c in slug if c in string.ascii_uppercase + "_" + string.digits)
        const_name = f"_CONST_{slug}" if slug else "_CONST_STR"
    else:
        const_name = f"_CONST_{abs(int(const_node.value))}"

    # Avoid collisions
    existing_names = {
        node.id
        for node in ast.walk(tree)
        if isinstance(node, ast.Name)
    }
    while const_name in existing_names:
        const_name += "_"

    # Replace the literal with a Name reference
    const_node_replacement = ast.Name(id=const_name, ctx=ast.Load())
    ast.copy_location(const_node_replacement, const_node)

    # Walk the function body and replace (simple pointer swap via parent tracking)
    class _Replacer(ast.NodeTransformer):
        def __init__(self):
            self.replaced = False

        def visit_Constant(self, node: ast.Constant) -> ast.AST:
            if not self.replaced and node is const_node:
                self.replaced = True
                return const_node_replacement
            return node

    _Replacer().visit(tree)

    # Insert assignment at module level (after imports)
    insert_idx = 0
    for i, stmt in enumerate(tree.body):
        if isinstance(stmt, (ast.Import, ast.ImportFrom)):
            insert_idx = i + 1
        elif isinstance(stmt, ast.Expr) and isinstance(
            getattr(stmt, "value", None), (ast.Constant, ast.Str)
        ):
            insert_idx = i + 1

    assign = ast.Assign(
        targets=[ast.Name(id=const_name, ctx=ast.Store())],
        value=ast.Constant(value=const_node.value),
        lineno=0,
    )
    ast.fix_missing_locations(assign)
    tree.body.insert(insert_idx, assign)

    ast.fix_missing_locations(tree)
    return ast.unparse(tree)


def _add_error_handling(source: str) -> str:
    """Wrap a random function body in try/except with a fallback."""
    tree = ast.parse(source)

    candidates = [
        node
        for node in ast.walk(tree)
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef))
        # skip functions whose entire body is already a single try
        and not (len(node.body) == 1 and isinstance(node.body[0], ast.Try))
    ]

    if not candidates:
        return source

    target = random.choice(candidates)

    # Preserve docstring outside the try block
    docstring_node = None
    body_to_wrap = target.body
    if (
        body_to_wrap
        and isinstance(body_to_wrap[0], ast.Expr)
        and isinstance(getattr(body_to_wrap[0], "value", None), ast.Constant)
        and isinstance(body_to_wrap[0].value.value, str)
    ):
        docstring_node = body_to_wrap[0]
        body_to_wrap = body_to_wrap[1:]

    if not body_to_wrap:
        return source

    # Build: except Exception as _exc: raise
    handler = ast.ExceptHandler(
        type=ast.Name(id="Exception", ctx=ast.Load()),
        name="_exc",
        body=[
            ast.Expr(
                value=ast.Call(
                    func=ast.Name(id="print", ctx=ast.Load()),
                    args=[
                        ast.JoinedStr(
                            values=[
                                ast.Constant(value=f"{target.name} failed: "),
                                ast.FormattedValue(
                                    value=ast.Name(id="_exc", ctx=ast.Load()),
                                    conversion=-1,
                                ),
                            ]
                        )
                    ],
                    keywords=[],
                )
            ),
            ast.Raise(),
        ],
    )

    try_node = ast.Try(
        body=list(body_to_wrap),
        handlers=[handler],
        orelse=[],
        finalbody=[],
    )
    ast.fix_missing_locations(try_node)

    new_body: list[ast.stmt] = []
    if docstring_node:
        new_body.append(docstring_node)
    new_body.append(try_node)
    target.body = new_body

    return ast.unparse(tree)


def _duplicate_and_modify(source: str) -> str:
    """Copy a random function, rename it with a ``_v2`` suffix, and apply
    a small modification to the copy (creates variation for natural
    selection)."""
    tree = ast.parse(source)

    funcs = [
        (i, node)
        for i, node in enumerate(tree.body)
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef))
    ]

    if not funcs:
        return source

    idx, original = random.choice(funcs)

    # Deep-copy via round-trip (ast has no built-in deepcopy that is safe)
    original_src = ast.unparse(original)
    clone = ast.parse(original_src).body[0]

    # Rename
    existing_names = {
        node.name
        for node in ast.walk(tree)
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef))
    }
    new_name = f"{original.name}_v2"
    counter = 2
    while new_name in existing_names:
        counter += 1
        new_name = f"{original.name}_v{counter}"
    clone.name = new_name  # type: ignore[attr-defined]

    # Apply a small modification to the clone: swap comparison operators
    class _Tweaker(ast.NodeTransformer):
        _swaps = {
            ast.Lt: ast.LtE,
            ast.LtE: ast.Lt,
            ast.Gt: ast.GtE,
            ast.GtE: ast.Gt,
            ast.Eq: ast.NotEq,
            ast.NotEq: ast.Eq,
        }
        def __init__(self):
            self.applied = False

        def visit_Compare(self, node: ast.Compare) -> ast.AST:
            if not self.applied and node.ops:
                op_type = type(node.ops[0])
                if op_type in self._swaps:
                    node.ops[0] = self._swaps[op_type]()
                    self.applied = True
            return self.generic_visit(node)

    _Tweaker().visit(clone)

    ast.fix_missing_locations(clone)
    tree.body.insert(idx + 1, clone)

    return ast.unparse(tree)


# ---------------------------------------------------------------------------
# Mutation registry
# ---------------------------------------------------------------------------

MUTATIONS: list[Callable[[str], str]] = [
    _inject_utility,
    _reorder_functions,
    _add_docstring,
    _extract_constant,
    _add_error_handling,
    _duplicate_and_modify,
]
