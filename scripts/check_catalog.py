#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

DEFAULT_CATALOG = Path(__file__).resolve().parents[1] / "catalog" / "models.json"
SHA256_RE = re.compile(r"^[0-9a-f]{64}$")
REVISION_RE = re.compile(r"^[0-9a-f]{40}$")
SAFE_RE = re.compile(r"^[A-Za-z0-9][A-Za-z0-9_.-]*$")


def main() -> int:
    parser = argparse.ArgumentParser(description="Validate the committed Inflect ONNX catalog")
    parser.add_argument("--catalog", type=Path, default=DEFAULT_CATALOG)
    args = parser.parse_args()

    catalog = json.loads(args.catalog.read_text(encoding="utf-8"))
    errors: list[str] = []

    if catalog.get("schema") != 1:
        errors.append("schema must be 1")
    if catalog.get("kind") != "inflect-onnx-model-catalog":
        errors.append("kind must be inflect-onnx-model-catalog")
    models = catalog.get("models")
    if not isinstance(models, dict) or not models:
        errors.append("models must be a non-empty object")
        models = {}

    identifiers: dict[str, str] = {}
    artifact_count = 0
    for key, model in models.items():
        label = f"models.{key}"
        if not SAFE_RE.fullmatch(key):
            errors.append(f"{label}: unsafe model key")
        if model.get("id") != key:
            errors.append(f"{label}: id must equal object key")
        for identifier in [key, *model.get("aliases", [])]:
            previous = identifiers.get(identifier)
            if previous is not None:
                errors.append(f"{label}: identifier {identifier!r} already used by {previous}")
            else:
                identifiers[identifier] = key
        if model.get("sample_rate") != 24000:
            errors.append(f"{label}: sample_rate must be 24000")
        if model.get("voice_mode") != "fixed" or model.get("default_voice") != "default":
            errors.append(f"{label}: MVP requires the upstream fixed default voice")
        voices = model.get("voices")
        if not isinstance(voices, dict) or set(voices) != {"default"}:
            errors.append(f"{label}: expected exactly the upstream fixed default voice")
        else:
            voice = voices["default"]
            if voice.get("id") != "default" or voice.get("synthetic") is not True:
                errors.append(f"{label}: invalid fixed voice metadata")

        upstream = model.get("upstream") or {}
        repository = upstream.get("repository")
        revision = upstream.get("revision")
        source_revision = upstream.get("source_revision")
        if not isinstance(repository, str) or repository.count("/") != 1:
            errors.append(f"{label}: invalid upstream repository")
        if not isinstance(revision, str) or REVISION_RE.fullmatch(revision) is None:
            errors.append(f"{label}: upstream revision must be a 40-char lowercase SHA")
        if not isinstance(source_revision, str) or REVISION_RE.fullmatch(source_revision) is None:
            errors.append(f"{label}: source revision must be a 40-char lowercase SHA")
        if upstream.get("license") != "Apache-2.0":
            errors.append(f"{label}: upstream license must be Apache-2.0")

        artifacts = model.get("artifacts")
        if not isinstance(artifacts, list):
            errors.append(f"{label}: artifacts must be a list")
            artifacts = []
        roles = [a.get("role") for a in artifacts if isinstance(a, dict)]
        if sorted(roles) != ["decode", "duration"]:
            errors.append(f"{label}: expected exactly duration and decode artifact roles")
        for index, artifact in enumerate(artifacts):
            artifact_count += 1
            alabel = f"{label}.artifacts[{index}]"
            if not isinstance(artifact, dict):
                errors.append(f"{alabel}: artifact must be an object")
                continue
            filename = artifact.get("filename")
            role = artifact.get("role")
            expected_filename = f"{role}.onnx"
            if filename != expected_filename:
                errors.append(f"{alabel}: filename must be {expected_filename}")
            size = artifact.get("size")
            digest = artifact.get("sha256")
            url = artifact.get("url")
            if not isinstance(size, int) or isinstance(size, bool) or size <= 0:
                errors.append(f"{alabel}: size must be positive")
            if not isinstance(digest, str) or SHA256_RE.fullmatch(digest) is None:
                errors.append(f"{alabel}: sha256 must be lowercase 64-char hex")
            if isinstance(repository, str) and isinstance(revision, str):
                expected = f"https://huggingface.co/{repository}/resolve/{revision}/onnx/{filename}"
                if url != expected:
                    errors.append(f"{alabel}: URL must be pinned exactly to upstream revision")

    if errors:
        print("Inflect catalog validation failed:", file=sys.stderr)
        for error in errors:
            print(f"- {error}", file=sys.stderr)
        return 1
    print(
        f"Inflect catalog validation passed: models={len(models)} "
        f"identifiers={len(identifiers)} artifacts={artifact_count}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
