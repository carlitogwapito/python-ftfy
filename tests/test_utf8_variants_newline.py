# Tests for ftfy's codec. ftfy is by Robyn Speer.
# SPDX-License-Identifier: Apache-2.0

import codecs

import pytest

from ftfy import bad_codecs

bad_codecs.ok()


def _decode(payload: bytes, incremental: bool) -> str:
    if not incremental:
        return payload.decode("utf-8-variants")
    decoder = codecs.getincrementaldecoder("utf-8-variants")()
    parts = [decoder.decode(bytes([value]), final=False) for value in payload]
    parts.append(decoder.decode(b"", final=True))
    return "".join(parts)


@pytest.mark.parametrize("incremental", [False, True])
@pytest.mark.parametrize("payload", [b"\xc0\n", b"\xed\xa0\xbd\xed\xb8\n"])
def test_newline_cannot_complete_truncated_sequence(payload: bytes, incremental: bool) -> None:
    with pytest.raises(UnicodeDecodeError):
        _decode(payload, incremental)


@pytest.mark.parametrize("incremental", [False, True])
@pytest.mark.parametrize(
    "payload,expected",
    [(b"\xc0\x80\n", "\x00\n"), (b"\xed\xa0\xbd\xed\xb8\x8d\n", "\U0001f60d\n")],
)
def test_complete_sequence_keeps_newline(payload: bytes, expected: str, incremental: bool) -> None:
    assert _decode(payload, incremental) == expected
