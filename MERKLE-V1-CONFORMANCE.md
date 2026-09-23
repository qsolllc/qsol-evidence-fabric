# QSOL Merkle V1 — Conformance Result

Date: 2026-09-21
Spec: specification/MERKLE-V1.md (SHA-256 596ad7225200b15aece0b29950e98ff69f1faffa9652a20aaae8fe70c2b16abf)

Vectors: vectors/v1/merkle-v1.json (4 cases)

Independent implementations:
- Python: python/verify_merkle_vectors.py — PASS on all fields
- Rust:   rust/src/main.rs (verify-merkle-v1) — PASS on all fields

Identical roots produced by both:

  one_leaf    adda39828d6063b44d2f9eabb27509acc92dc70919e997dc9c74aa2c35bb45a2
  two_leaf    3d4a331221c5073e218659589411e752430af6cc10c9745631f87f912707d650
  odd_leaf    407b47c2fc50111484afb0eac64c783eb2dd4d12272ab87777922bc5033ea02a
  multi_level 4ab89038e7c0bb5105f9026ad494895496908a4af618ba8f1a572e898566d2f6

Specification §16 promotion conditions:
  1. Hash suite reviewed                        — asserted
  2. Domain constants independently verified    — PASS (both verifiers)
  3. Normative Merkle vectors generated         — done
  4. Python and Rust reproduce every vector     — done, PASS
  5. Explicit FROZEN promotion                  — pending decision

Determinism (§14): satisfied for the four normative cases.

Note: this result concerns the qsol-merkle-v1 specification only. It does
not bear on other QSol artifacts (tombstone, recovery seal, Stage-9 gate)
or on authorship, ownership, or content truth of any artifact.
