# inflect-onnx-bundles

A small, reproducible catalog for the official **Inflect v2** ONNX bundles.
This is deliberately **not a Python package** and it does **not mirror model weights**.
It follows the same catalog/tooling pattern as `kitten-onnx-bundles`.

## Bootstrap catalog

```text
nano-v2   -> owensong/Inflect-Nano-v2-ONNX
micro-v2  -> owensong/Inflect-Micro-v2-ONNX
```

Both entries are Apache-2.0, FP32, ONNX opset 17, 24 kHz, and use the same split ABI:

```text
duration.onnx: tokens + lengths + length_scale -> m_p_exp + logs_p_exp + y_mask
decode.onnx:   acoustic tensors + seeded noise + noise_scale -> waveform
```

The catalog pins full Hugging Face commit SHAs and records exact artifact sizes and SHA-256 values.

## Voices

The upstream v2 base releases are fixed-voice models. Each catalog entry therefore exposes exactly
one canonical voice, `default`. This is the complete upstream runtime voice inventory; the catalog
does not invent speaker names or imply voice cloning.

## Validate

```bash
python scripts/check_catalog.py
```

`docs/onnxvoice-integration.md` describes the small parser/runtime adapter needed to promote this
catalog into OnnxVoice later. The bundle repository itself remains data + tooling only.

## Canonical files

```text
catalog/models.json
catalog/source.json
schemas/model-catalog.schema.json
```
