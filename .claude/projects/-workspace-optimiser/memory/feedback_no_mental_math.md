---
name: feedback_no_mental_math
description: Never do hex/binary/numeric transformations by hand - always write a script
type: feedback
---

Never do "mental maths" for hex encoding, binary serialization, numeric conversions, or any data transformation. Always write a small Python script to do it correctly.

**Why:** LLMs make subtle errors in hex encoding, byte ordering, and copy-paste of long strings. A script is deterministic and verifiable. The user caught suspicious-looking edits in XMP hex params that were done by hand.

**How to apply:** Whenever you need to modify binary/hex data, serialized formats, or do bulk numeric transformations: write a Python script that reads the source, transforms programmatically, writes the output, and verifies the result. Never use Edit tool for hex/binary content.
