#!/data/data/com.termux/files/usr/bin/bash

# ============================================================
# QSOL MERKLE V1 — EXACT GIT OBJECT PROVENANCE AUDIT
# ============================================================
#
# PURPOSE
# -------
# Trace the exact MERKLE-V1 specification through Git object
# history and determine whether any historical revision contains
# explicit promotion/status evidence.
#
# CANONICAL SPECIFICATION
# -----------------------
# Path:
#   specification/MERKLE-V1.md
#
# Current expected SHA-256:
#   596ad7225200b15aece0b29950e98ff69f1faffa9652a20aaae8fe70c2b16abf
#
# IMPORTANT EVIDENTIARY RULE
# --------------------------
# A Git commit containing MERKLE-V1.md does not itself prove that
# the specification was authoritative or FROZEN.
#
# A tag does not itself prove promotion.
#
# A branch does not itself prove promotion.
#
# Promotion requires an explicit status/provenance event connected
# to the specification.
#
# This audit therefore records the Git facts without interpreting
# them as authority unless the repository explicitly provides that
# connection.
#
# ============================================================

set -euo pipefail

cd "$HOME/qsol-evidence-fabric"

SPEC="specification/MERKLE-V1.md"
OUT="evidence/conformance/merkle-v1-git-object-audit.txt"

EXPECTED_SHA256="596ad7225200b15aece0b29950e98ff69f1faffa9652a20aaae8fe70c2b16abf"

mkdir -p evidence/conformance

# ------------------------------------------------------------
# 1. Verify repository and current specification identity.
# ------------------------------------------------------------

git rev-parse --is-inside-work-tree >/dev/null

ACTUAL_SHA256="$(sha256sum "$SPEC" | awk '{print $1}')"

if [ "$ACTUAL_SHA256" != "$EXPECTED_SHA256" ]; then
    echo "ERROR: current specification SHA-256 mismatch" >&2
    echo "expected=$EXPECTED_SHA256" >&2
    echo "actual=$ACTUAL_SHA256" >&2
    exit 1
fi

# ------------------------------------------------------------
# 2. Record Git repository identity.
# ------------------------------------------------------------

{
    echo "============================================================"
    echo "QSOL MERKLE V1 — EXACT GIT OBJECT PROVENANCE AUDIT"
    echo "============================================================"

    printf 'workspace=%s\n' "$PWD"
    printf 'specification=%s\n' "$SPEC"
    printf 'current_spec_sha256=%s\n' "$ACTUAL_SHA256"

    echo
    echo "============================================================"
    echo "1. REPOSITORY IDENTITY"
    echo "============================================================"

    git rev-parse --show-toplevel
    git rev-parse --is-inside-work-tree
    git rev-parse HEAD

    echo
    echo "============================================================"
    echo "2. CURRENT FILE OBJECT"
    echo "============================================================"

    # Git's blob identity is distinct from the external SHA-256
    # of the working-tree file. Both are recorded.
    git hash-object "$SPEC"
    sha256sum "$SPEC"
    wc -c "$SPEC"

    echo
    echo "============================================================"
    echo "3. COMPLETE FILE HISTORY"
    echo "============================================================"

    # --follow tracks the path through ordinary Git renames.
    git log \
        --follow \
        --date=iso-strict \
        --format='commit=%H%nparent=%P%nauthor=%an%nauthor_email=%ae%nauthor_date=%aI%ncommitter=%cn%ncommitter_email=%ce%ncommit_date=%cI%nsubject=%s%n---' \
        -- "$SPEC" 2>&1 || true

    echo
    echo "============================================================"
    echo "4. COMMITS TOUCHING MERKLE-V1"
    echo "============================================================"

    git log \
        --all \
        --date=iso-strict \
        --format='commit=%H%nauthor=%an%nauthor_date=%aI%nsubject=%s%n---' \
        -- "$SPEC" 2>&1 || true

    echo
    echo "============================================================"
    echo "5. HISTORICAL CONTENT STATUS SEARCH"
    echo "============================================================"

    # Examine every revision of the specification that Git can
    # resolve through its path history. The output records only
    # actual historical content matching status terminology.
    #
    # This does NOT treat a match as promotion automatically.
    git log \
        --all \
        --follow \
        -p \
        -- "$SPEC" 2>/dev/null \
        | grep -nEi \
            'FROZEN|STATUS[[:space:]]*[:=]|PROMOT|RATIF|APPROV|ADOPT|EFFECTIVE|DRAFT|MERKLE_V1_STATUS' \
        || true

    echo
    echo "============================================================"
    echo "6. TAGS CONTAINING FILE HISTORY"
    echo "============================================================"

    # For each tag, determine whether the specification exists at
    # that tagged revision and record its SHA-256 when possible.
    for TAG in $(git tag --list --sort=creatordate); do

        if git cat-file -e "${TAG}:${SPEC}" 2>/dev/null; then

            echo "TAG=$TAG"

            git rev-list -n 1 "$TAG" 2>/dev/null || true

            git show "${TAG}:${SPEC}" \
                | sha256sum \
                | awk '{print "sha256=" $1}'

            git show "${TAG}:${SPEC}" \
                | wc -c \
                | awk '{print "size_bytes=" $1}'

            echo "---"
        fi

    done

    echo
    echo "============================================================"
    echo "7. BRANCHES CONTAINING CURRENT FILE"
    echo "============================================================"

    # Record branches where the current specification path exists.
    for REF in $(git for-each-ref \
        --format='%(refname)' \
        refs/heads refs/remotes 2>/dev/null); do

        if git cat-file -e "${REF}:${SPEC}" 2>/dev/null; then
            echo "$REF"
        fi

    done

    echo
    echo "============================================================"
    echo "8. PROMOTION-RELATED COMMIT SUBJECTS"
    echo "============================================================"

    git log \
        --all \
        --date=iso-strict \
        --format='commit=%H%nauthor=%an%nauthor_date=%aI%nsubject=%s%n---' \
        --grep='MERKLE-V1\|MERKLE V1\|qsol-merkle-v1\|FROZEN\|PROMOT\|RATIF\|APPROV\|ADOPT\|EFFECTIVE' \
        -i 2>&1 || true

    echo
    echo "============================================================"
    echo "9. EVIDENTIARY CLASSIFICATION RULE"
    echo "============================================================"

    echo "Git lineage establishes provenance facts."
    echo
    echo "Git lineage alone does NOT establish specification authority."
    echo
    echo "A valid promotion finding requires:"
    echo "  1. exact MERKLE-V1 identity;"
    echo "  2. explicit promotion/status event;"
    echo "  3. explicit connection between the event and the specification."
    echo
    echo "authority_inference=DISABLED"
    echo "promotion_inference=DISABLED"

    echo
    echo "============================================================"
    echo "10. AUDIT COMPLETION"
    echo "============================================================"

    echo "git_object_audit_completed=true"

} > "$OUT"

# ------------------------------------------------------------
# 3. Report the evidence artifact's cryptographic identity.
# ------------------------------------------------------------

echo
echo "============================================================"
echo "GIT OBJECT AUDIT ARTIFACT"
echo "============================================================"

printf 'path=%s\n' "$OUT"
wc -c "$OUT"
sha256sum "$OUT"

echo
echo "CURRENT SPECIFICATION"
sha256sum "$SPEC"
