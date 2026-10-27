import json
from pathlib import Path


def load_document_cdc_schema() -> dict:
    schema_path = Path(__file__).resolve().parent / "document_cdc.schema.json"
    return json.loads(schema_path.read_text(encoding="utf-8"))
