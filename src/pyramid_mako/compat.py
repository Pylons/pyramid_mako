PY2 = False

string_types = (str,)
integer_types = (int,)
class_types = (type,)
text_type = str
binary_type = bytes
long = int


def text_(s, encoding="latin-1", errors="strict"):
    """If ``s`` is an instance of ``binary_type``, return
    ``s.decode(encoding, errors)``, otherwise return ``s``"""
    if isinstance(s, binary_type):
        return s.decode(encoding, errors)
    return s


def is_nonstr_iter(v):
    if isinstance(v, str):
        return False
    return hasattr(v, "__iter__")


exec_ = exec


def reraise(tp, value, tb=None):  # pragma: no cover
    if value is None:
        value = tp
    if value.__traceback__ is not tb:
        raise value.with_traceback(tb)
    raise value
