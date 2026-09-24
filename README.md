# QSOL Evidence Fabric

Deterministic, independently verifiable computational evidence for QSOL.

This repository specifies and implements **MERKLE-V1** — a Merkle tree
construction with frozen domain separation, canonical leaf encoding, and
two independent reference implementations that produce byte-identical roots
on a normative vector set.

## What is in this repository

| Directory | Contents |
|---|---|
| `specification/` | MERKLE-V1, CANON-V1, CONFORMANCE-V1, EPF-V1, PROVENANCE-V1, VERIFICATION-V1 |
| `vectors/v1/` | Four normative vector cases (`one_leaf`, `two_leaf`, `odd_leaf`, `multi_level`) |
| `python/` | Reference verifier and vector generator in Python |
| `rust/` | Reference verifier in Rust (binary: `verify-merkle-v1`) |
| `evidence/` | Audit records supporting the conformance claims |
| `profiles/` | Named conformance profiles |
| `MERKLE-V1-CONFORMANCE.md` | The conformance result |
| `MERKLE-V1-CONFORMANCE.md.ots` | OpenTimestamps Bitcoin anchor of the result |
| `MERKLE-V1-CONFORMANCE.sha256` | Package hash manifest |

## Verification

    sha256sum -c MERKLE-V1-CONFORMANCE.sha256
    python python/verify_merkle_vectors.py
    cargo build --release && ./target/release/verify-merkle-v1

Both implementations must produce these roots:

    one_leaf    adda39828d6063b44d2f9eabb27509acc92dc70919e997dc9c74aa2c35bb45a2
    two_leaf    3d4a331221c5073e218659589411e752430af6cc10c9745631f87f912707d650
    odd_leaf    407b47c2fc50111484afb0eac64c783eb2dd4d12272ab87777922bc5033ea02a
    multi_level 4ab89038e7c0bb5105f9026ad494895496908a4af618ba8f1a572e898566d2f6

## Bitcoin anchor

`MERKLE-V1-CONFORMANCE.md.ots` is an OpenTimestamps proof binding the
conformance result to the Bitcoin blockchain. Verify with any OTS client:

    ots verify MERKLE-V1-CONFORMANCE.md.ots

## License

Apache License 2.0. See `LICENSE`.

## Company

QSOL LLC — Pocatello, Idaho — qsol.llc@gmail.com
