"""A tiny, sandboxed expression evaluator.

Decision logic from the Excel file (e.g. ``current_stock < minimum_stock``) is stored as
text and evaluated here. Only a whitelist of AST nodes / functions is allowed - no
imports, no attribute access to dunders, no arbitrary calls.
"""
from __future__ import annotations

import ast
import math
import operator as op

from .errors import WorkflowConfigError


def coalesce(*values):
    for v in values:
        if v is not None and v != "":
            return v
    return None


def _lower(v):
    return str(v).lower() if v is not None else None


FUNCS = {
    "abs": abs, "round": round, "min": min, "max": max, "len": len, "sum": sum,
    "any": any, "all": all, "bool": bool, "int": int, "float": float, "str": str,
    "coalesce": coalesce, "log": math.log, "sqrt": math.sqrt, "lower": _lower,
}
BIN = {ast.Add: op.add, ast.Sub: op.sub, ast.Mult: op.mul, ast.Div: op.truediv,
       ast.FloorDiv: op.floordiv, ast.Mod: op.mod}
CMP = {ast.Eq: op.eq, ast.NotEq: op.ne, ast.Lt: op.lt, ast.LtE: op.le, ast.Gt: op.gt,
       ast.GtE: op.ge, ast.Is: op.is_, ast.IsNot: op.is_not,
       ast.In: lambda a, b: a in b, ast.NotIn: lambda a, b: a not in b}


def safe_eval(expr: str, env: dict):
    try:
        tree = ast.parse(expr.strip(), mode="eval")
    except SyntaxError as e:
        raise WorkflowConfigError(f"Invalid expression '{expr}': {e}") from e
    return _ev(tree.body, env, expr)


def _ev(n, env, src):
    if isinstance(n, ast.Constant):
        return n.value
    if isinstance(n, ast.Name):
        if n.id in env:
            return env[n.id]
        raise WorkflowConfigError(f"Unknown name '{n.id}' in expression '{src}'")
    if isinstance(n, ast.BoolOp):
        vals = (_ev(v, env, src) for v in n.values)
        return all(vals) if isinstance(n.op, ast.And) else any(vals)
    if isinstance(n, ast.UnaryOp):
        v = _ev(n.operand, env, src)
        if isinstance(n.op, ast.Not):
            return not v
        if isinstance(n.op, ast.USub):
            return -v
        if isinstance(n.op, ast.UAdd):
            return +v
    if isinstance(n, ast.BinOp) and type(n.op) in BIN:
        return BIN[type(n.op)](_ev(n.left, env, src), _ev(n.right, env, src))
    if isinstance(n, ast.Compare):
        left = _ev(n.left, env, src)
        for o, comp in zip(n.ops, n.comparators):
            right = _ev(comp, env, src)
            if type(o) not in CMP or not CMP[type(o)](left, right):
                return False
            left = right
        return True
    if isinstance(n, ast.IfExp):
        return _ev(n.body, env, src) if _ev(n.test, env, src) else _ev(n.orelse, env, src)
    if isinstance(n, ast.Call) and isinstance(n.func, ast.Name) and n.func.id in FUNCS and not n.keywords:
        return FUNCS[n.func.id](*[_ev(a, env, src) for a in n.args])
    if isinstance(n, ast.Subscript):
        return _ev(n.value, env, src)[_ev(n.slice, env, src)]
    if isinstance(n, ast.Attribute) and not n.attr.startswith("_"):
        base = _ev(n.value, env, src)
        if isinstance(base, dict):
            return base.get(n.attr)
    if isinstance(n, ast.Dict):
        return {_ev(k, env, src): _ev(v, env, src) for k, v in zip(n.keys, n.values)}
    if isinstance(n, (ast.List, ast.Tuple)):
        return [_ev(e, env, src) for e in n.elts]
    raise WorkflowConfigError(f"Unsupported syntax in expression '{src}'")
