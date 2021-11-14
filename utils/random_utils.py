import hashlib
import random
from typing import Any
key = 'fkseriluhwophfalweosfchaeihucfnlakshuoaidcupawihuai'
from django.utils.crypto import get_random_string

Hash = {i: chr(97 + i) for i in range(27)}


def random_str(length: int = 10, charset: str = 'str') -> str:
    """
    :param length:
    :param charset:
    :return:
    """
    if charset == 'str':
        return get_random_string(length=length, allowed_chars='abcdefghijklmnopqrstuvwxyzA')
    elif charset == 'lower_str':
        return get_random_string(length=length, allowed_chars='abcdefghijklmnopqrstuvwxyz')
    elif charset == 'upper_str':
        return get_random_string(length=length, allowed_chars='ABCDEFGHIJKLMNOPQRSTUVWXYZ')
    else:
        return random.choice('123456789') + get_random_string(length=length, allowed_chars='0123456789')


def number_hash(origin: Any) -> str:
    return ''.join(Hash.get(int(i), random.choice('abcdefghijklmnopqrstuvwxyz')) for i in origin)

def sha512_hash(x):
    y = hashlib.sha256(x.encode('utf-8'))
    y.update(key.encode('utf-8'))
    z = y.hexdigest()
    y = hashlib.sha512(z.encode('utf-8'))
    y.update(key.encode('utf-8'))
    return y.hexdigest()