# OnnxVoice integration brief

The MVP `inflectsynth` can consume this catalog directly, so an OnnxVoice change is not required
for the three-repository bootstrap. If Inflect is promoted into OnnxVoice, keep the same ownership
boundary used by Kitten: **InflectSynth owns raw text -> token IDs; OnnxVoice owns ONNX execution.**

## Catalog parser

Add an `inflect` source and parser for `kind = "inflect-onnx-model-catalog"`. Each catalog model
maps naturally to one `CatalogItem`:

```text
system          = inflect
id              = model.id
kind            = model
sample_rate     = model.sample_rate
voices          = ("default",)
artifact roles  = duration | decode
metadata        = language, controls, runtime, upstream, voices, metadata
```

Keep full 40-character Hugging Face revisions and artifact size/SHA-256 verification intact.

## Runtime adapter

A minimal adapter needs two lazily opened sessions and this semantic API:

```python
runtime.infer(token_ids, speed=1.0, variation=0.667, seed=0)
```

The published split graph ABI is:

```text
duration.onnx
  inputs:  tokens[int64, 1 x T], lengths[int64, 1], length_scale[float32]
  outputs: m_p_exp, logs_p_exp, y_mask

decode.onnx
  inputs:  m_p_exp, logs_p_exp, y_mask, zp_noise[float32], noise_scale[float32]
  output:  waveform
```

Generate `zp_noise` with `numpy.random.default_rng(seed).standard_normal(..., dtype=float32)` after
running the duration graph. Add CPU fallback after CUDA/DirectML exactly as the official runner does.

Do not put normalization or phonemization in the adapter. `inflectg2p` reproduces the public
Inflect v2 English frontend and blank-interspersed token IDs.

## Suggested OnnxVoice files

```text
onnxvoice/catalog_tools/inflect.py
onnxvoice/systems/inflect.py
tests/test_inflect_catalog.py
tests/test_inflect_adapter.py
tests/test_inflect_local_open.py
docs/systems/inflect.md
```
