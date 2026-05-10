from __future__ import annotations

from publicstack_contracts.diff.jsonschema import diff_jsonschema
from publicstack_contracts.diff.report import has_breaking

_BASE = {
    "title": "x",
    "description": "y",
    "x-publicstack-contract-name": "x",
    "x-publicstack-contract-version": "v1",
    "type": "object",
}


def _with(props=None, required=None, **extra):
    return {**_BASE, **extra, "properties": props or {}, "required": list(required or [])}


# --- JS001 -----------------------------------------------------------------

def test_js001_removed_required_field():
    old = _with(props={"name": {"type": "string"}}, required=["name"])
    new = _with(props={}, required=[])
    findings = diff_jsonschema(old, new)
    assert any(f.rule == "JS001" for f in findings)
    assert has_breaking(findings)


# --- JS002 -----------------------------------------------------------------

def test_js002_added_required_no_default():
    old = _with(props={"name": {"type": "string"}}, required=[])
    new = _with(props={"name": {"type": "string"}, "age": {"type": "integer"}}, required=["age"])
    findings = diff_jsonschema(old, new)
    assert any(f.rule == "JS002" for f in findings)
    assert has_breaking(findings)


def test_js002_added_required_with_default_ok():
    old = _with(props={}, required=[])
    new = _with(props={"flag": {"type": "boolean", "default": False}}, required=["flag"])
    findings = diff_jsonschema(old, new)
    assert not has_breaking(findings)


# --- JS003 -----------------------------------------------------------------

def test_js003_type_change_breaking():
    old = _with(props={"x": {"type": "string"}})
    new = _with(props={"x": {"type": "integer"}})
    findings = diff_jsonschema(old, new)
    assert any(f.rule == "JS003" for f in findings)
    assert has_breaking(findings)


def test_js003_integer_to_number_whitelisted():
    old = _with(props={"x": {"type": "integer"}})
    new = _with(props={"x": {"type": "number"}})
    findings = diff_jsonschema(old, new)
    assert not has_breaking(findings)


# --- JS004 / JS007 ---------------------------------------------------------

def test_js004_enum_value_removed():
    old = _with(props={"status": {"type": "string", "enum": ["a", "b", "c"]}})
    new = _with(props={"status": {"type": "string", "enum": ["a", "b"]}})
    findings = diff_jsonschema(old, new)
    assert any(f.rule == "JS004" for f in findings)
    assert has_breaking(findings)


def test_js007_enum_value_added_info():
    old = _with(props={"status": {"type": "string", "enum": ["a", "b"]}})
    new = _with(props={"status": {"type": "string", "enum": ["a", "b", "c"]}})
    findings = diff_jsonschema(old, new)
    assert any(f.rule == "JS007" for f in findings)
    assert not has_breaking(findings)


# --- JS005 / JS008 ---------------------------------------------------------

def test_js005_maxlength_shrunk():
    old = _with(props={"s": {"type": "string", "maxLength": 100}})
    new = _with(props={"s": {"type": "string", "maxLength": 50}})
    findings = diff_jsonschema(old, new)
    assert any(f.rule == "JS005" for f in findings)
    assert has_breaking(findings)


def test_js008_maxlength_grown():
    old = _with(props={"s": {"type": "string", "maxLength": 50}})
    new = _with(props={"s": {"type": "string", "maxLength": 100}})
    findings = diff_jsonschema(old, new)
    assert any(f.rule == "JS008" for f in findings)
    assert not has_breaking(findings)


def test_js005_minimum_raised():
    old = _with(props={"n": {"type": "integer", "minimum": 0}})
    new = _with(props={"n": {"type": "integer", "minimum": 10}})
    findings = diff_jsonschema(old, new)
    assert any(f.rule == "JS005" for f in findings)
    assert has_breaking(findings)


# --- JS006 -----------------------------------------------------------------

def test_js006_added_optional_property():
    old = _with(props={"name": {"type": "string"}})
    new = _with(props={"name": {"type": "string"}, "nickname": {"type": "string"}})
    findings = diff_jsonschema(old, new)
    assert any(f.rule == "JS006" for f in findings)
    assert not has_breaking(findings)


# --- recursion -------------------------------------------------------------

def test_nested_property_breaking():
    old = _with(props={"actor": {"type": "object", "properties": {"id": {"type": "string"}}, "required": ["id"]}})
    new = _with(props={"actor": {"type": "object", "properties": {}, "required": []}})
    findings = diff_jsonschema(old, new)
    assert any(f.rule == "JS001" for f in findings)
    assert any("/actor/" in f.path for f in findings)


def test_array_items_recurse():
    old = _with(props={"xs": {"type": "array", "items": {"type": "string"}}})
    new = _with(props={"xs": {"type": "array", "items": {"type": "integer"}}})
    findings = diff_jsonschema(old, new)
    assert any(f.rule == "JS003" for f in findings)
    assert any("/items" in f.path for f in findings)
