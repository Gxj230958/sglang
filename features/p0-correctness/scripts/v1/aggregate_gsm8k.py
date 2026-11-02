import argparse
import gzip
import json
from collections import Counter
from pathlib import Path


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("predictions", type=Path)
    args = parser.parse_args()
    with gzip.open(args.predictions, "rt") as handle:
        rows = [json.loads(line) for line in handle]
    finish_reasons = Counter(row["finish_reason"] for row in rows)
    result = {
        "num_examples": len(rows),
        "num_correct": sum(bool(row["symbolic_correct"]) for row in rows),
        "score": sum(bool(row["symbolic_correct"]) for row in rows) / len(rows),
        "stop_rate": finish_reasons["stop"] / len(rows),
        "truncated_rate": finish_reasons["length"] / len(rows),
        "error_rate": sum(row.get("error") is not None for row in rows) / len(rows),
        "finish_reasons": dict(sorted(finish_reasons.items())),
    }
    print(json.dumps(result, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
