"""Minimale NBT schrijver/lezer voor Minecraft structure-bestanden (.nbt, gzip)."""
import gzip
import io
import struct

END, BYTE, SHORT, INT, LONG, FLOAT, DOUBLE, BYTE_ARRAY, STRING, LIST, COMPOUND, INT_ARRAY, LONG_ARRAY = range(13)


class TagList(list):
    """Lijst met een vast element-type."""

    def __init__(self, elem_type, items=()):
        super().__init__(items)
        self.elem_type = elem_type


def _tag_type(value):
    if isinstance(value, bool):
        return BYTE
    if isinstance(value, int):
        return INT
    if isinstance(value, float):
        return DOUBLE
    if isinstance(value, str):
        return STRING
    if isinstance(value, TagList):
        return LIST
    if isinstance(value, dict):
        return COMPOUND
    raise TypeError(f"Onbekend NBT type: {type(value)}")


def _write_str(buf, s):
    data = s.encode("utf-8")
    buf.write(struct.pack(">H", len(data)))
    buf.write(data)


def _write_payload(buf, tag, value):
    if tag == BYTE:
        buf.write(struct.pack(">b", int(value)))
    elif tag == INT:
        buf.write(struct.pack(">i", value))
    elif tag == DOUBLE:
        buf.write(struct.pack(">d", value))
    elif tag == STRING:
        _write_str(buf, value)
    elif tag == LIST:
        buf.write(struct.pack(">bi", value.elem_type if value else END, len(value)))
        for item in value:
            _write_payload(buf, value.elem_type, item)
    elif tag == COMPOUND:
        for key, item in value.items():
            t = _tag_type(item)
            buf.write(struct.pack(">b", t))
            _write_str(buf, key)
            _write_payload(buf, t, item)
        buf.write(struct.pack(">b", END))
    else:
        raise TypeError(tag)


def to_bytes(root):
    """Ongecomprimeerde NBT-bytes."""
    buf = io.BytesIO()
    buf.write(struct.pack(">b", COMPOUND))
    _write_str(buf, "")
    _write_payload(buf, COMPOUND, root)
    return buf.getvalue()


def write_gzip(path, root):
    with open(path, "wb") as f:
        f.write(gzip.compress(to_bytes(root), mtime=0))


def read_gzip(path):
    data = io.BytesIO(gzip.decompress(open(path, "rb").read()))

    def rd(fmt):
        return struct.unpack(fmt, data.read(struct.calcsize(fmt)))[0]

    def rstr():
        return data.read(rd(">H")).decode("utf-8")

    def payload(t):
        if t == BYTE:
            return rd(">b")
        if t == SHORT:
            return rd(">h")
        if t == INT:
            return rd(">i")
        if t == LONG:
            return rd(">q")
        if t == FLOAT:
            return rd(">f")
        if t == DOUBLE:
            return rd(">d")
        if t == STRING:
            return rstr()
        if t == LIST:
            et, n = rd(">b"), rd(">i")
            return [payload(et) for _ in range(n)]
        if t == COMPOUND:
            out = {}
            while True:
                tt = rd(">b")
                if tt == END:
                    return out
                k = rstr()
                out[k] = payload(tt)
        raise ValueError(t)

    assert rd(">b") == COMPOUND
    rstr()
    return payload(COMPOUND)
