# InflectSynth integration contract

InflectSynth consumes this catalog shape directly. A model installation consists of exactly two
artifacts, `duration.onnx` and `decode.onnx`, both verified by size and SHA-256 before opening.
The frontend is supplied by `inflectg2p`, not copied into the model cache.
