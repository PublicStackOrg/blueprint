from __future__ import annotations

import pytest

from publicstack_contracts.detect import AmbiguousFormatError, detect


def test_openapi_doc():
    assert detect({"openapi": "3.1.0", "info": {}, "paths": {}}) == "openapi"


def test_jsonschema_via_dollar_schema():
    assert detect({"$schema": "https://json-schema.org/draft/2020-12/schema"}) == "jsonschema"


def test_jsonschema_via_top_type():
    assert detect({"type": "object", "properties": {}}) == "jsonschema"


def test_ambiguous_both():
    with pytest.raises(AmbiguousFormatError):
        detect({"openapi": "3.1.0", "type": "object"})


def test_ambiguous_neither():
    with pytest.raises(AmbiguousFormatError):
        detect({"random": "stuff"})
