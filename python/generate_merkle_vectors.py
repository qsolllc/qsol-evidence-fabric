#!/usr/bin/env python3

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "python"))

from qsol_evidence.merkle_v1 import (
    DOMAIN_LEAF,
    DOMAIN_NODE,
    file_hash,
    leaf_preimage,
    leaf_hash,
    node_hash,
    merkle_root,
)


CASES = {
    "one_leaf": [
        ("a.txt", b"A"),
    ],
    "two_leaf": [
        ("a.txt", b"A"),
        ("b.txt", b"B"),
    ],
    "odd_leaf": [
        ("a.txt", b"A"),
        ("b.txt", b"B"),
        ("c.txt", b"C"),
    ],
    "multi_level": [
        ("a.txt", b"A"),
        ("b.txt", b"B"),
        ("c.txt", b"C"),
        ("d.txt", b"D"),
        ("e.txt", b"E"),
    ],
}


def make_case(name, artifacts):
    ordered = sorted(
        artifacts,
        key=lambda item: item[0].encode("utf-8"),
    )

    leaves = []

    for path, data in ordered:
        preimage = leaf_preimage(path, data)

        leaves.append({
            "path": path,
            "size": len(data),
            "file_bytes_hex": data.hex(),
            "file_hash": file_hash(data).hex(),
            "leaf_preimage_hex": preimage.hex(),
            "leaf_hash": leaf_hash(path, data).hex(),
        })

    levels = [
        [bytes.fromhex(x["leaf_hash"]) for x in leaves]
    ]

    node_levels = []

    while len(levels[-1]) > 1:
        current = levels[-1]
        nxt = []
        nodes = []

        for i in range(0, len(current) - 1, 2):
            left = current[i]
            right = current[i + 1]
            parent = node_hash(left, right)

            nodes.append({
                "left": left.hex(),
                "right": right.hex(),
                "parent": parent.hex(),
            })

            nxt.append(parent)

        if len(current) % 2:
            promoted = current[-1]
            nodes.append({
                "promoted": promoted.hex(),
            })
            nxt.append(promoted)

        node_levels.append(nodes)
        levels.append(nxt)

    return {
        "schema": "QSOL-MERKLE-VECTOR-V1",
        "case": name,
        "hash": "SHA3-256",
        "domain_leaf": DOMAIN_LEAF.hex(),
        "domain_node": DOMAIN_NODE.hex(),
        "artifacts": leaves,
        "levels": [
            [x.hex() for x in level]
            for level in levels
        ],
        "node_operations": node_levels,
        "merkle_root": merkle_root(ordered).hex(),
    }


def main():
    output = ROOT / "vectors" / "v1" / "merkle-v1.json"

    document = {
        "schema": "QSOL-MERKLE-VECTOR-SET-V1",
        "profile": "qsol-merkle-v1",
        "cases": [
            make_case(name, artifacts)
            for name, artifacts in CASES.items()
        ],
    }

    output.write_text(
        json.dumps(document, indent=2) + "\n",
        encoding="utf-8",
    )

    print(output)


if __name__ == "__main__":
    main()
