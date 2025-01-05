import zlib
import six

# From https://github.com/carlos-jenkins/plantweb/blob/master/lib/plantweb/plantuml.py

def encode(content:str) -> str:
    """
    Compress the plantuml text and encode it for the plantuml server.

    :param str content: Content to compress and encode.
    :return: The compressed and encoded content.
    :rtype: str
    """
    zlibbed_str = zlib.compress(content.strip().encode('utf-8'))
    compressed_string = zlibbed_str[2:-4]
    
    return custom_base64(compressed_string)

def custom_base64(data):
    """
    Encode given data into PlantUML server encoding.

    This algorithm is similar to the base64 but custom for the plantuml server.

    :param bytes data: Data to encode.
    :return: The encoded data as printable ASCII.
    :rtype: str
    """
    res = ''
    for i in range(0, len(data), 3):
        if i + 2 == len(data):
            res += _encode3bytes(
                six.indexbytes(data, i),
                six.indexbytes(data, i + 1),
                0
            )
        elif i + 1 == len(data):
            res += _encode3bytes(
                six.indexbytes(data, i),
                0, 0
            )
        else:
            res += _encode3bytes(
                six.indexbytes(data, i),
                six.indexbytes(data, i + 1),
                six.indexbytes(data, i + 2)
            )
    return res

def _encode6bit(b):
    if b < 10:
        return six.unichr(48 + b)
    b -= 10
    if b < 26:
        return six.unichr(65 + b)
    b -= 26
    if b < 26:
        return six.unichr(97 + b)
    b -= 26
    if b == 0:
        return '-'
    if b == 1:
        return '_'

def _encode3bytes(b1, b2, b3):
    c1 = b1 >> 2
    c2 = ((b1 & 0x3) << 4) | (b2 >> 4)
    c3 = ((b2 & 0xF) << 2) | (b3 >> 6)
    c4 = b3 & 0x3F
    res = ''
    res += _encode6bit(c1 & 0x3F) # type: ignore
    res += _encode6bit(c2 & 0x3F) # type: ignore
    res += _encode6bit(c3 & 0x3F) # type: ignore
    res += _encode6bit(c4 & 0x3F) # type: ignore
    return res
