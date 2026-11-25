"""Write the one-word ex verdict to the make.fun output file.

Writes exactly one word, ``Unmatched``, to ``$MAKEFUN_OUTPUT_DIR/entry.txt``
(or ``/output/entry.txt`` when the variable is unset), as a single line with
no trailing newline. The write is atomic (temp file in the same directory,
then :func:`os.replace`), and the file is read back afterwards to verify the
bytes on disk match what was written.
"""

import os
import sys
import tempfile

WORD = "Unmatched"


def main() -> int:
    if not WORD or len(WORD) > 111:
        print(f"error: word must be 1-111 characters, got {len(WORD)}", file=sys.stderr)
        return 1
    if any(ch.isspace() for ch in WORD):
        print("error: entry must be exactly one word (no whitespace)", file=sys.stderr)
        return 1

    out_dir = os.environ.get("MAKEFUN_OUTPUT_DIR") or "/output"
    os.makedirs(out_dir, exist_ok=True)
    target = os.path.join(out_dir, "entry.txt")
    data = WORD.encode("utf-8")

    fd, tmp_path = tempfile.mkstemp(dir=out_dir, prefix=".entry-", suffix=".tmp")
    try:
        with os.fdopen(fd, "wb") as fh:
            fh.write(data)
        os.replace(tmp_path, target)
    except BaseException:
        try:
            os.unlink(tmp_path)
        except OSError:
            pass
        raise

    # Read-back verification: the bytes on disk must match what was written.
    with open(target, "rb") as fh:
        if fh.read() != data:
            raise RuntimeError("read-back verification failed: entry.txt bytes differ")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
