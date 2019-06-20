from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.backends import default_backend
import wordlist
import encoding
import error
# get the wordlist
wordList = wordlist.wordListRaw().split("\n")

def fromKey(key):
    """
    Returns the mnemonic for the key or address (bytes).
    """
    if not len(key) == 58:
        raise error.WrongKeyLengthError
    key = encoding.decodeAddress(key)
    chksum = checksum(key)
    nums = to11Bit(key)
    words = applyWords(nums)
    return " ".join(words) + " " + chksum


def toKey(mnemonic):
    """
    Gives the corresponding address (bytes) for the mnemonic.
    """
    mnemonic = mnemonic.split(" ")
    if not len(mnemonic) == 25:
        raise error.WrongMnemonicLengthError
    mChecksum = mnemonic[-1]
    mnemonic = fromWords(mnemonic[:-1])
    mBytes = toBytes(mnemonic)
    if not mBytes[-1:len(mBytes)] == bytes([0]):
        raise error.WrongChecksumError
    chksum = checksum(mBytes[:32])
    if chksum.__eq__(mChecksum):
        return encoding.encodeAddress(mBytes[:32])
    else:
        raise error.WrongChecksumError


def checksum(data):
    """
    Computes the mnemonic checksum of data (bytes).
    """
    hash = hashes.Hash(hashes.SHA512_256(), default_backend())
    hash.update(data)
    chksum = hash.finalize()
    temp = chksum[0:2]
    nums = to11Bit(temp)
    return applyWords(nums)[0]


def applyWords(nums):
    words = []
    for n in nums:
        words.append(wordList[n])
    return words


def fromWords(words):
    nums = []
    for w in words:
        nums.append(wordList.index(w))
    return nums


def to11Bit(data):
    """
    Converts a bytearray to an list of 11-bit numbers.
    """
    buffer = 0
    num_of_bits = 0
    output = []
    for i in range(len(data)):
        buffer |= data[i] << num_of_bits
        num_of_bits += 8
        if num_of_bits >= 11:
            output.append(buffer&2047)
            buffer = buffer >> 11
            num_of_bits -= 11
    if num_of_bits != 0:
        output.append(buffer&2047)
    return output


def toBytes(nums):
    """
    Converts a list of 11-bit numbers to a bytearray
    """
    buffer = 0
    num_of_bits = 0
    output = []
    for i in range(len(nums)):
        buffer |= nums[i] << num_of_bits
        num_of_bits += 11
        while num_of_bits >= 8:
            output.append(buffer&255)
            buffer = buffer >> 8
            num_of_bits -= 8
    if num_of_bits != 0:
        output.append(buffer&255)
    return bytes(output)