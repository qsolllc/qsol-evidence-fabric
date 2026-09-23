# QSOL Merkle V1

Status: DRAFT

## 1. Scope

QSOL Merkle V1 (`qsol-merkle-v1`) defines the deterministic Merkle
commitment used by QSOL Evidence Fabric V1.

The Merkle commitment is distinct from the EPF object digest.

The EPF digest is:

D = H(C_v1(O_c))

The Merkle commitment is:

R = MerkleRoot(E)

where E is the ordered set of committed artifact entries.

D and R MUST NOT be treated as interchangeable values.

## 2. Hash Suite

The normative V1 Merkle hash function is:

SHA3-256

The output is exactly 32 bytes.

No truncation is permitted.

No alternate hash function is permitted within the `qsol-merkle-v1`
profile.

Historical QSOL Merkle constructions using SHA-256 or SHA3-512 are
outside this profile and MUST NOT be silently interpreted as V1.

## 3. File Hash

For an artifact with byte sequence B:

FILE_HASH = SHA3-256(B)

The resulting digest is exactly 32 bytes.

The file hash operates on the exact artifact bytes.

No text decoding, Unicode normalization, newline conversion, or other
transformation is permitted before hashing.

## 4. Artifact Entry

Each committed artifact entry contains:

- path
- size
- file_hash

`path` is the canonical relative path of the artifact.

`size` is the exact unsigned 64-bit byte length of the artifact.

`file_hash` is the 32-byte SHA3-256 digest of the artifact bytes.

Paths MUST use `/` as the path separator.

Absolute paths are prohibited.

`.` and `..` path components are prohibited.

Empty paths are prohibited.

Duplicate canonical paths are prohibited.

## 5. Path Encoding

The path is encoded as UTF-8 bytes.

The UTF-8 path byte sequence MUST be used exactly as supplied by the
canonical manifest.

No Unicode normalization is performed.

## 6. Leaf Domain Separation

The literal leaf domain is the ASCII byte sequence:

QSOL-EVIDENCE-FABRIC-V1/LEAF

Its hexadecimal representation is:

51 53 4f 4c 2d 45 56 49 44 45 4e 43 45 2d 46 41 42 52 49 43
2d 56 31 2f 4c 45 41 46

The leaf preimage is:

DOMAIN_LEAF ||
UTF8(path) ||
0x00 ||
UINT64_BE(size) ||
0x00 ||
FILE_HASH

where:

- `DOMAIN_LEAF` is the literal byte sequence above;
- `UTF8(path)` is the canonical UTF-8 path;
- `0x00` is one zero byte;
- `UINT64_BE(size)` is an unsigned 64-bit big-endian integer;
- `FILE_HASH` is the 32-byte SHA3-256 file digest.

The leaf digest is:

LEAF_HASH =
SHA3-256(leaf_preimage)

## 7. Leaf Ordering

Leaves MUST be ordered by the canonical UTF-8 byte sequence of their
paths, in ascending lexicographic order.

The ordering MUST be performed before leaf hashing is assembled into
the Merkle tree.

Two implementations receiving the same artifact set MUST therefore
produce the same leaf ordering.

## 8. Node Domain Separation

The literal node domain is the ASCII byte sequence:

QSOL-EVIDENCE-FABRIC-V1/NODE

Its hexadecimal representation is:

51 53 4f 4c 2d 45 56 49 44 45 4e 43 45 2d 46 41 42 52 49 43
2d 56 31 2f 4e 4f 44 45

For two child digests LEFT and RIGHT:

NODE_HASH =
SHA3-256(
    DOMAIN_NODE ||
    LEFT ||
    RIGHT
)

`LEFT` and `RIGHT` MUST each be exactly 32 bytes.

Child ordering is significant.

`NODE_HASH(LEFT, RIGHT)` MUST NOT be treated as equivalent to
`NODE_HASH(RIGHT, LEFT)`.

## 9. Tree Construction

The ordered leaf hashes form level zero.

For each level:

1. Adjacent pairs are combined into parent nodes.
2. The left child occupies the first 32 bytes.
3. The right child occupies the second 32 bytes.
4. Parent nodes are computed using `NODE_HASH`.

If a level contains an odd number of nodes, the final unpaired node is
promoted unchanged to the next level.

No duplicate-last-node operation is performed.

No zero-padding operation is performed.

No special empty-node hash is introduced for an odd final node.

Construction continues until exactly one 32-byte root remains.

## 10. Empty Tree

An empty artifact set is invalid for a conforming Evidence Fabric
V1 evidence package.

Therefore `qsol-merkle-v1` does not define an empty-tree root.

An implementation MUST reject an attempt to construct a V1 evidence
Merkle root from zero artifact entries.

## 11. Root Representation

The Merkle root is exactly 32 bytes internally.

When represented as text, the root MUST use lowercase hexadecimal
encoding.

The textual representation therefore contains exactly 64 hexadecimal
characters.

No `0x` prefix is permitted.

## 12. Relationship to Manifest

The manifest MUST identify the Merkle profile:

merkle_profile = "qsol-merkle-v1"

The manifest MUST contain the resulting Merkle root.

The Merkle root commits to the exact artifact paths, sizes, and file
contents represented by the committed entries.

The Merkle root does not replace the EPF digest.

## 13. Historical Compatibility

Historical QSOL artifacts may contain Merkle constructions using
different hash functions, domain rules, ordering rules, or root
representations.

Such artifacts MUST be identified by an explicit compatibility or
legacy profile.

Historical behavior MUST NOT be silently mapped to
`qsol-merkle-v1`.

The previously identified SHA-256/SHA3-512 discrepancy remains an
unresolved historical conformance issue until the original vectors and
construction rules are independently reconstructed.

## 14. Determinism

For the same ordered artifact set:

R_A = R_B

MUST hold for every pair of conforming implementations A and B.

Any difference in:

- file hash
- path encoding
- size encoding
- leaf encoding
- leaf ordering
- node encoding
- odd-node handling
- root encoding

constitutes non-conformance.

## 15. Test Vectors

Normative vectors MUST include at minimum:

1. one-leaf tree;
2. two-leaf tree;
3. odd-leaf tree;
4. multi-level tree;
5. exact file hashes;
6. exact leaf preimages or their independently reconstructible inputs;
7. exact leaf hashes;
8. exact node hashes; and
9. exact Merkle root.

Every vector MUST be independently reproducible.

## 16. Status

This document remains DRAFT until:

1. the hash suite is reviewed;
2. domain constants are independently verified;
3. normative Merkle vectors are generated;
4. Python and Rust implementations reproduce every vector; and
5. the specification is explicitly promoted to FROZEN.
