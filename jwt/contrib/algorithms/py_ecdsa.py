# Note: This file is named py_ecdsa.py because import behavior in Python 2
# would cause ecdsa.py to squash the ecdsa library that it depends upon.

import hashlib

import ecdsa

from jwt.algorithms import Algorithm
from jwt.compat import string_types, text_type


class ECAlgorithm(Algorithm):
    """
    Performs signing and verification operations using
    ECDSA and the specified hash function

    This class requires the ecdsa package to be installed.

    This is based off of the implementation in PyJWT 0.3.2
    """
    def __init__(self, hash_alg):
        self.hash_alg = hash_alg

    SHA256, SHA384, SHA512 = hashlib.sha256, hashlib.sha384, hashlib.sha512

    def prepare_key(self, key):

        if isinstance(key, ecdsa.SigningKey) or \
           isinstance(key, ecdsa.VerifyingKey):
            return key

        if isinstance(key, string_types):
            if isinstance(key, text_type):
                key = key.encode('utf-8')

            # Attempt to load key. We don't know if it's
            # a Signing Key or a Verifying Key, so we try
            # the Verifying Key first.
            try:
                key = ecdsa.VerifyingKey.from_pem(key)
            except ecdsa.der.UnexpectedDER:
                key = ecdsa.SigningKey.from_pem(key)

        else:
            raise TypeError('Expecting a PEM-formatted key.')

        return key

    def sign(self, msg, key):
        return key.sign(msg, hashfunc=self.hash_alg,
                        sigencode=ecdsa.util.sigencode_der)

    def verify(self, msg, key, sig):
        try:
            return key.verify(sig, msg, hashfunc=self.hash_alg,
                              sigdecode=ecdsa.util.sigdecode_der)
        except ecdsa.der.UnexpectedDER:
            return False
