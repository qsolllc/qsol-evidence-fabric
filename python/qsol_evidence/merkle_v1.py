#!/usr/bin/env python3

import hashlib
import struct


DOMAIN_LEAF = b"QSOL-EVIDENCE-FABRIC-V1/LEAF"
DOMAIN_NODE = b"QSOL-EVIDENCE-FABRIC-V1/NODE"


def sha3_256(data: bytes) -> bytes:
    return hashlib.sha3_256(data).digest()


def file_hash(data: bytes) -> bytes:
    return sha3_256(data)


def leaf_preimage(path: str, data: bytes) -> bytes:
    path_bytes = path.encode("utf-8")
    size = len(data)
    fh = file_hash(data)

    return (
        DOMAIN_LEAF
        + path_bytes
        + b"\x00"
        + struct.pack(">Q", size)
        + b"\x00"
        + fh
    )


def leaf_hash(path: str, data: bytes) -> bytes:
    return sha3_256(leaf_preimage(path, data))


def node_hash(left: bytes, right: bytes) -> bytes:
    if len(left) != 32 or len(right) != 32:
        raise ValueError("Merkle children must be exactly 32 bytes")

    return sha3_256(DOMAIN_NODE + left + right)


def merkle_root(artifacts):
    """
    artifacts: iterable of (canonical_path, bytes)
    """

    entries = list(artifacts)

    if not entries:
        raise ValueError("empty artifact set is invalid")

    paths = [path for path, _ in entries]

    if len(paths) != len(set(paths)):
        raise ValueError("duplicate artifact path")

    entries.sort(key=lambda item: item[0].encode("utf-8"))

    leaves = [
        leaf_hash(path, data)
        for path, data in entries
    ]

    level = leaves

    while len(level) > 1:
        next_level = []

        for i in range(0, len(level) - 1, 2):
            next_level.append(
                node_hash(level[i], level[i + 1])
            )

        if len(level) % 2:
            next_level.append(level[-1])

        level = next_level

    return level[0]


def hex_digest(value: bytes) -> str:
    return value.hex()
