from pathlib import Path
import json
from src.engine.models import ExperimentConfig, SweepManifest, ExperimentResult

SCHEMAS = {
    "schemas/experiment_config.schema.json": ExperimentConfig,
    "schemas/manifest.schema.json": SweepManifest,
    "schemas/results.schema.json": ExperimentResult,
}


def main():
    root = Path(__file__).resolve().parents[1]
    for rel_path, model in SCHEMAS.items():
        schema = model.model_json_schema()
        out = root / rel_path
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(json.dumps(schema, indent=2), encoding="utf-8")
        print(f"wrote {out}")


if __name__ == "__main__":
    main()
