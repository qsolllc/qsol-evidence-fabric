#!/usr/bin/env python3

import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
VECTOR_FILE = ROOT / "vectors" / "v1" / "merkle-v1.json"

DOMAIN_LEAF = b"QSOL-EVIDENCE-FABRIC-V1/LEAF"
DOMAIN_NODE = b"QSOL-EVIDENCE-FABRIC-V1/NODE"

EXPECTED_DOMAIN_LEAF_HEX = (
    "51534f4c2d45564944454e43452d4641425249432d56312f4c454146"
)
EXPECTED_DOMAIN_NODE_HEX = (
    "51534f4c2d45564944454e43452d4641425249432d56312f4e4f4445"
)


def sha3_256(data: bytes) -> bytes:
    return hashlib.sha3_256(data).digest()


def file_hash(data: bytes) -> bytes:
    return sha3_256(data)


def leaf_preimage(path: str, data: bytes) -> bytes:
    path_bytes = path.encode("utf-8")
    size = len(data).to_bytes(8, "big")
    return (
        DOMAIN_LEAF
        + path_bytes
        + b"\x00"
        + size
        + b"\x00"
        + file_hash(data)
    )


def leaf_hash(path: str, data: bytes) -> bytes:
    return sha3_256(leaf_preimage(path, data))


def node_hash(left: bytes, right: bytes) -> bytes:
    assert len(left) == 32
    assert len(right) == 32
    return sha3_256(DOMAIN_NODE + left + right)


def reconstruct_tree(artifacts):
    ordered = sorted(
        artifacts,
        key=lambda item: item["path"].encode("utf-8"),
    )

    leaves = []

    for artifact in ordered:
        path = artifact["path"]
        data = bytes.fromhex(artifact["file_bytes_hex"])

        leaves.append(leaf_hash(path, data))

    levels = [leaves]
    operations = []

    while len(levels[-1]) > 1:
        current = levels[-1]
        nxt = []
        ops = []

        for i in range(0, len(current) - 1, 2):
            left = current[i]
            right = current[i + 1]
            parent = node_hash(left, right)

            ops.append(
                {
                    "left": left.hex(),
                    "right": right.hex(),
                    "parent": parent.hex(),
                }
            )

            nxt.append(parent)

        if len(current) % 2:
            promoted = current[-1]
            ops.append({"promoted": promoted.hex()})
            nxt.append(promoted)

        operations.append(ops)
        levels.append(nxt)

    return levels, operations


def check(condition, message):
    if not condition:
        raise AssertionError(message)


def verify_case(case):
    name = case["case"]

    check(case["hash"] == "SHA3-256", f"{name}: wrong hash suite")
    check(
        case["domain_leaf"] == EXPECTED_DOMAIN_LEAF_HEX,
        f"{name}: leaf domain mismatch",
    )
    check(
        case["domain_node"] == EXPECTED_DOMAIN_NODE_HEX,
        f"{name}: node domain mismatch",
    )

    artifacts = case["artifacts"]

    check(len(artifacts) > 0, f"{name}: empty artifact set")

    for artifact in artifacts:
        path = artifact["path"]
        data = bytes.fromhex(artifact["file_bytes_hex"])

        expected_size = len(data)
        expected_file_hash = file_hash(data).hex()
        expected_preimage = leaf_preimage(path, data).hex()
        expected_leaf_hash = leaf_hash(path, data).hex()

        check(
            artifact["size"] == expected_size,
            f"{name}/{path}: size mismatch",
        )

        check(
            artifact["file_hash"] == expected_file_hash,
            f"{name}/{path}: file hash mismatch",
        )

        check(
            artifact["leaf_preimage_hex"] == expected_preimage,
            f"{name}/{path}: leaf preimage mismatch",
        )

        check(
            artifact["leaf_hash"] == expected_leaf_hash,
            f"{name}/{path}: leaf hash mismatch",
        )

    levels, operations = reconstruct_tree(artifacts)

    expected_levels = [
        [digest.hex() for digest in level]
        for level in levels
    ]

    check(
        case["levels"] == expected_levels,
        f"{name}: level reconstruction mismatch",
    )

    check(
        case["node_operations"] == operations,
        f"{name}: node operation mismatch",
    )

    expected_root = levels[-1][0].hex()

    check(
        case["merkle_root"] == expected_root,
        f"{name}: Merkle root mismatch",
    )

    check(
        len(expected_root) == 64,
        f"{name}: root is not 32-byte hexadecimal",
    )

    print(f"PASS: {name} root={expected_root}")


def main():
    print("=== QSOL MERKLE V1 INDEPENDENT VECTOR VERIFIER ===")

    check(
        DOMAIN_LEAF.hex() == EXPECTED_DOMAIN_LEAF_HEX,
        "leaf domain constant self-check failed",
    )

    check(
        DOMAIN_NODE.hex() == EXPECTED_DOMAIN_NODE_HEX,
        "node domain constant self-check failed",
    )

    check(VECTOR_FILE.is_file(), f"missing vector file: {VECTOR_FILE}")

    document = json.loads(VECTOR_FILE.read_text(encoding="utf-8"))

    check(
        document["schema"] == "QSOL-MERKLE-VECTOR-SET-V1",
        "vector-set schema mismatch",
    )

    check(
        document["profile"] == "qsol-merkle-v1",
        "vector-set profile mismatch",
    )

    cases = document["cases"]

    check(len(cases) == 4, "expected exactly four normative cases")

    for case in cases:
        verify_case(case)

    print()
    print("DOMAIN LEAF: PASS")
    print("DOMAIN NODE: PASS")
    print("SCHEMA: PASS")
    print("PROFILE: PASS")
    print("ALL VECTOR CASES: PASS")
    print("INDEPENDENT RECONSTRUCTION: PASS")


if __name__ == "__main__":
    try:
        main()
    except Exception as exc:
        print(f"FAIL: {exc}")
        raise SystemExit(1)
