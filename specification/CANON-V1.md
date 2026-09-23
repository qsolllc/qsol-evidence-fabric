# QSOL Canonicalization V1

Status: DRAFT

## 1. Scope

QSOL Canonicalization V1 (`qsol-canon-v1`) defines the deterministic
byte representation used when QSOL Evidence Fabric objects are hashed,
committed, signed, or included in conformance test vectors.

The canonicalization function is:

C_v1(O) -> bytes

The output is a deterministic UTF-8 byte sequence.

## 2. Character Encoding

1. Canonical output MUST be encoded as UTF-8.
2. No byte-order mark (BOM) is permitted.
3. Unicode normalization MUST NOT be performed.
4. Canonicalization operates on Unicode scalar values represented by the
   input data model and produces UTF-8 bytes.

## 3. Supported Data Model

The canonical data model consists only of:

- object
- array
- string
- boolean
- null
- integer

Floating-point values are prohibited.

The following are invalid:

- fractional numbers
- NaN
- Infinity
- negative Infinity
- implementation-specific numeric types

## 4. Objects

Object keys MUST be strings.

Duplicate object keys MUST be rejected before canonicalization.

Object members MUST be serialized in ascending order according to the
lexicographic ordering of their UTF-8 encoded key bytes.

The serialized form of an object is:

{member1,member2,...}

with no whitespace.

Each member is serialized as:

key:value

## 5. Arrays

Array element order is significant and MUST be preserved exactly.

Arrays MUST NOT be sorted.

The serialized form is:

[element1,element2,...]

with no whitespace.

## 6. Whitespace

Canonical output MUST contain no insignificant whitespace.

The canonical representation MUST contain:

- no indentation
- no spaces surrounding `:`
- no spaces following `,`
- no leading whitespace
- no trailing whitespace
- no trailing newline

Whitespace characters that occur inside JSON string values are data and
MUST be handled according to Section 7.

## 7. Strings

Strings MUST use JSON string syntax.

The following characters MUST use JSON escaping:

- quotation mark (`"`)
- reverse solidus (`\`)
- control characters U+0000 through U+001F

The required short escapes are:

- U+0008 -> `\b`
- U+0009 -> `\t`
- U+000A -> `\n`
- U+000C -> `\f`
- U+000D -> `\r`

Other control characters in U+0000 through U+001F MUST use lowercase
`\u00XX` hexadecimal notation.

The hexadecimal digits in `\u` escapes MUST be lowercase.

Characters outside the required escape set MUST be emitted as their UTF-8
representation rather than being converted to `\u` escapes.

Surrogate code points MUST NOT occur in canonical input.

## 8. Booleans and Null

Boolean values MUST be represented exactly as:

true

or:

false

Null MUST be represented exactly as:

null

## 9. Integers

Integers MUST use their shortest decimal representation.

No leading plus sign is permitted.

Zero MUST be represented as:

0

Negative zero is not a distinct canonical value and MUST NOT occur.

Negative integers MUST use a single leading minus sign followed by the
shortest decimal representation of the absolute value.

## 10. Canonical Output

The canonicalizer MUST return the exact byte sequence produced by the
rules in this specification.

For any valid object O, all conforming implementations MUST produce
byte-for-byte identical output:

C_v1^A(O) = C_v1^B(O)

where A and B are any two conforming implementations.

Any byte difference constitutes non-conformance.

## 11. Digest Relationship

When an EPF object defines an EPF digest:

D = H(C_v1(O_c))

The hash function H MUST be selected from the normative QSOL hash-suite
defined for the applicable protocol version.

The hash function MUST NOT be inferred from an implementation.

## 12. Test Vectors

Every normative canonicalization rule MUST be covered by one or more
deterministic conformance vectors.

A vector MUST provide sufficient information for an independent
implementation to reproduce:

1. the input object;
2. the canonical byte sequence; and
3. any applicable digest.

Expected canonical bytes MUST be treated as normative data.

## 13. Rejection Requirements

A conforming implementation MUST reject:

- duplicate object keys;
- floating-point values;
- unsupported numeric representations;
- invalid Unicode scalar values;
- malformed input;
- any value outside the defined canonical data model.

## 14. Status

This document remains DRAFT until:

1. the canonicalization rules are reviewed;
2. normative test vectors are generated;
3. an independent implementation reproduces every vector;
4. cross-language byte-for-byte agreement is demonstrated; and
5. the specification is explicitly promoted to FROZEN.
