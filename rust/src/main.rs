use serde::Deserialize;
use sha3::{Digest, Sha3_256};
use std::fs;
use std::path::Path;

const VECTOR_FILE: &str = "vectors/v1/merkle-v1.json";

const DOMAIN_LEAF: &[u8] = b"QSOL-EVIDENCE-FABRIC-V1/LEAF";
const DOMAIN_NODE: &[u8] = b"QSOL-EVIDENCE-FABRIC-V1/NODE";

const EXPECTED_DOMAIN_LEAF_HEX: &str =
    "51534f4c2d45564944454e43452d4641425249432d56312f4c454146";

const EXPECTED_DOMAIN_NODE_HEX: &str =
    "51534f4c2d45564944454e43452d4641425249432d56312f4e4f4445";

#[derive(Debug, Deserialize)]
struct VectorSet {
    schema: String,
    profile: String,
    cases: Vec<Case>,
}

#[derive(Debug, Deserialize)]
struct Case {
    case: String,
    artifacts: Vec<Artifact>,
    levels: Vec<Vec<String>>,
    node_operations: Vec<Vec<NodeOperation>>,
    merkle_root: String,
}

#[derive(Debug, Deserialize)]
struct Artifact {
    path: String,
    size: usize,
    file_bytes_hex: String,
    file_hash: String,
    leaf_preimage_hex: String,
    leaf_hash: String,
}

#[derive(Debug, Deserialize)]
#[serde(untagged)]
enum NodeOperation {
    Pair {
        left: String,
        right: String,
        parent: String,
    },
    Promoted {
        promoted: String,
    },
}

fn sha3_256(data: &[u8]) -> Vec<u8> {
    let mut h = Sha3_256::new();
    h.update(data);
    h.finalize().to_vec()
}

fn hex_encode(bytes: &[u8]) -> String {
    bytes.iter().map(|b| format!("{b:02x}")).collect()
}

fn hex_decode(s: &str) -> Result<Vec<u8>, String> {
    if s.len() % 2 != 0 {
        return Err(format!("odd-length hex: {s}"));
    }

    (0..s.len())
        .step_by(2)
        .map(|i| {
            u8::from_str_radix(&s[i..i + 2], 16)
                .map_err(|_| format!("invalid hex: {s}"))
        })
        .collect()
}

fn file_hash(data: &[u8]) -> Vec<u8> {
    sha3_256(data)
}

fn leaf_preimage(path: &str, data: &[u8]) -> Vec<u8> {
    let fh = file_hash(data);

    let mut out = Vec::new();
    out.extend_from_slice(DOMAIN_LEAF);
    out.extend_from_slice(path.as_bytes());
    out.push(0);
    out.extend_from_slice(&(data.len() as u64).to_be_bytes());
    out.push(0);
    out.extend_from_slice(&fh);
    out
}

fn leaf_hash(path: &str, data: &[u8]) -> Vec<u8> {
    sha3_256(&leaf_preimage(path, data))
}

fn node_hash(left: &[u8], right: &[u8]) -> Vec<u8> {
    assert_eq!(left.len(), 32);
    assert_eq!(right.len(), 32);

    let mut preimage = Vec::with_capacity(DOMAIN_NODE.len() + 64);
    preimage.extend_from_slice(DOMAIN_NODE);
    preimage.extend_from_slice(left);
    preimage.extend_from_slice(right);

    sha3_256(&preimage)
}

fn reconstruct_tree(
    artifacts: &[Artifact],
) -> (Vec<Vec<Vec<u8>>>, Vec<Vec<NodeOperation>>) {
    let mut leaves: Vec<Vec<u8>> = artifacts
        .iter()
        .map(|artifact| {
            let data = hex_decode(&artifact.file_bytes_hex)
                .expect("vector contains invalid file bytes");
            leaf_hash(&artifact.path, &data)
        })
        .collect();

    let mut levels = vec![leaves.clone()];
    let mut operations = Vec::new();

    while leaves.len() > 1 {
        let mut next = Vec::new();
        let mut ops = Vec::new();

        let mut i = 0;

        while i + 1 < leaves.len() {
            let left = &leaves[i];
            let right = &leaves[i + 1];
            let parent = node_hash(left, right);

            ops.push(NodeOperation::Pair {
                left: hex_encode(left),
                right: hex_encode(right),
                parent: hex_encode(&parent),
            });

            next.push(parent);
            i += 2;
        }

        if i < leaves.len() {
            let promoted = leaves[i].clone();

            ops.push(NodeOperation::Promoted {
                promoted: hex_encode(&promoted),
            });

            next.push(promoted);
        }

        operations.push(ops);
        leaves = next;
        levels.push(leaves.clone());
    }

    (levels, operations)
}

fn check(condition: bool, message: &str) {
    if !condition {
        panic!("{message}");
    }
}

fn verify_case(case: &Case) {
    let (levels, operations) = reconstruct_tree(&case.artifacts);

    for artifact in &case.artifacts {
        let data = hex_decode(&artifact.file_bytes_hex)
            .expect("invalid vector file bytes");

        check(
            data.len() == artifact.size,
            &format!(
                "{}/{}: size mismatch",
                case.case, artifact.path
            ),
        );

        let expected_file_hash = hex_encode(&file_hash(&data));

        check(
            artifact.file_hash == expected_file_hash,
            &format!(
                "{}/{}: file hash mismatch",
                case.case, artifact.path
            ),
        );

        let expected_preimage = hex_encode(&leaf_preimage(&artifact.path, &data));

        check(
            artifact.leaf_preimage_hex == expected_preimage,
            &format!(
                "{}/{}: leaf preimage mismatch",
                case.case, artifact.path
            ),
        );

        let expected_leaf_hash = hex_encode(&leaf_hash(&artifact.path, &data));

        check(
            artifact.leaf_hash == expected_leaf_hash,
            &format!(
                "{}/{}: leaf hash mismatch",
                case.case, artifact.path
            ),
        );
    }

    let expected_levels: Vec<Vec<String>> = levels
        .iter()
        .map(|level| level.iter().map(|x| hex_encode(x)).collect())
        .collect();

    check(
        case.levels == expected_levels,
        &format!("{}: level reconstruction mismatch", case.case),
    );

    check(
        case.node_operations.len() == operations.len(),
        &format!("{}: node-operation level count mismatch", case.case),
    );

    for (expected, actual) in case.node_operations.iter().zip(operations.iter()) {
        check(
            expected.len() == actual.len(),
            &format!("{}: node-operation count mismatch", case.case),
        );

        for (expected_op, actual_op) in expected.iter().zip(actual.iter()) {
            match (expected_op, actual_op) {
                (
                    NodeOperation::Pair {
                        left: el,
                        right: er,
                        parent: ep,
                    },
                    NodeOperation::Pair {
                        left: al,
                        right: ar,
                        parent: ap,
                    },
                ) => {
                    check(el == al, "node left mismatch");
                    check(er == ar, "node right mismatch");
                    check(ep == ap, "node parent mismatch");
                }

                (
                    NodeOperation::Promoted { promoted: ep },
                    NodeOperation::Promoted { promoted: ap },
                ) => {
                    check(ep == ap, "promoted node mismatch");
                }

                _ => panic!("node operation type mismatch"),
            }
        }
    }

    let expected_root = hex_encode(levels.last().unwrap().first().unwrap());

    check(
        case.merkle_root == expected_root,
        &format!("{}: Merkle root mismatch", case.case),
    );

    check(
        expected_root.len() == 64,
        &format!("{}: root is not 32-byte hexadecimal", case.case),
    );

    println!("PASS: {} root={}", case.case, expected_root);
}

fn main() {
    println!("=== QSOL MERKLE V1 RUST INDEPENDENT VECTOR VERIFIER ===");

    check(
        hex_encode(DOMAIN_LEAF) == EXPECTED_DOMAIN_LEAF_HEX,
        "leaf domain constant self-check failed",
    );

    check(
        hex_encode(DOMAIN_NODE) == EXPECTED_DOMAIN_NODE_HEX,
        "node domain constant self-check failed",
    );

    check(
        Path::new(VECTOR_FILE).is_file(),
        "missing normative vector file",
    );

    let document_text =
        fs::read_to_string(VECTOR_FILE).expect("unable to read vector file");

    let document: VectorSet =
        serde_json::from_str(&document_text).expect("invalid vector JSON");

    check(
        document.schema == "QSOL-MERKLE-VECTOR-SET-V1",
        "vector-set schema mismatch",
    );

    check(
        document.profile == "qsol-merkle-v1",
        "vector-set profile mismatch",
    );

    check(
        document.cases.len() == 4,
        "expected exactly four normative cases",
    );

    for case in &document.cases {
        verify_case(case);
    }

    println!();
    println!("DOMAIN LEAF: PASS");
    println!("DOMAIN NODE: PASS");
    println!("SCHEMA: PASS");
    println!("PROFILE: PASS");
    println!("SHA3-256 RECONSTRUCTION: PASS");
    println!("FILE HASHES: PASS");
    println!("LEAF PREIMAGES: PASS");
    println!("LEAF HASHES: PASS");
    println!("NODE HASHES: PASS");
    println!("ODD-NODE PROMOTION: PASS");
    println!("TREE LEVELS: PASS");
    println!("MERKLE ROOTS: PASS");
    println!("ALL VECTOR CASES: PASS");
    println!("INDEPENDENT RECONSTRUCTION: PASS");
}
