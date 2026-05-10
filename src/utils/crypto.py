"""加密/解密工具"""

import base64


# Morse 电码字典
MORSE_CODE = {
    "A": ".-",
    "B": "-...",
    "C": "-.-.",
    "D": "-..",
    "E": ".",
    "F": "..-.",
    "G": "--.",
    "H": "....",
    "I": "..",
    "J": ".---",
    "K": "-.-",
    "L": ".-..",
    "M": "--",
    "N": "-.",
    "O": "---",
    "P": ".--.",
    "Q": "--.-",
    "R": ".-.",
    "S": "...",
    "T": "-",
    "U": "..-",
    "V": "...-",
    "W": ".--",
    "X": "-..-",
    "Y": "-.--",
    "Z": "--..",
    "0": "-----",
    "1": ".----",
    "2": "..---",
    "3": "...--",
    "4": "....-",
    "5": ".....",
    "6": "-....",
    "7": "--...",
    "8": "---..",
    "9": "----.",
    ".": ".-.-.-",
    ",": "--..--",
    "?": "..--..",
    "!": "-.-.--",
    " ": "/",
}

# 反向 Morse 字典
_REVERSE_MORSE = {v: k for k, v in MORSE_CODE.items()}


def caesar_cipher(text: str, shift: int, encrypt: bool = True) -> str:
    """凯撒密码加密/解密

    Args:
        text: 原文/密文
        shift: 偏移量
        encrypt: True=加密, False=解密
    """
    if not encrypt:
        shift = -shift
    result = []
    for ch in text:
        if ch.isalpha():
            base = ord("A") if ch.isupper() else ord("a")
            result.append(chr((ord(ch) - base + shift) % 26 + base))
        else:
            result.append(ch)
    return "".join(result)


def rot13(text: str) -> str:
    """ROT13 加密（凯撒移位13）"""
    return caesar_cipher(text, 13)


def reverse_text(text: str) -> str:
    """反转文本"""
    return text[::-1]


def base64_encode(text: str) -> str:
    """Base64 编码"""
    return base64.b64encode(text.encode("utf-8")).decode("utf-8")


def base64_decode(text: str) -> str:
    """Base64 解码"""
    return base64.b64decode(text.encode("utf-8")).decode("utf-8")


def to_morse(text: str) -> str:
    """文本转 Morse 电码"""
    parts = []
    for ch in text.upper():
        if ch in MORSE_CODE:
            parts.append(MORSE_CODE[ch])
        else:
            parts.append("?")
    return " ".join(parts)


def from_morse(morse: str) -> str:
    """Morse 电码转文本"""
    parts = []
    for code in morse.split():
        if code in _REVERSE_MORSE:
            parts.append(_REVERSE_MORSE[code])
        else:
            parts.append("?")
    return "".join(parts)


def vigenere_encrypt(text: str, key: str) -> str:
    """维吉尼亚密码加密"""
    result = []
    key_upper = key.upper()
    key_len = len(key_upper)
    ki = 0
    for ch in text:
        if ch.isalpha():
            base = ord("A") if ch.isupper() else ord("a")
            shift = ord(key_upper[ki % key_len]) - ord("A")
            result.append(chr((ord(ch) - base + shift) % 26 + base))
            ki += 1
        else:
            result.append(ch)
    return "".join(result)


def vigenere_decrypt(text: str, key: str) -> str:
    """维吉尼亚密码解密"""
    result = []
    key_upper = key.upper()
    key_len = len(key_upper)
    ki = 0
    for ch in text:
        if ch.isalpha():
            base = ord("A") if ch.isupper() else ord("a")
            shift = ord(key_upper[ki % key_len]) - ord("A")
            result.append(chr((ord(ch) - base - shift) % 26 + base))
            ki += 1
        else:
            result.append(ch)
    return "".join(result)


def to_binary_ascii(text: str) -> str:
    """文本转二进制 ASCII 表示"""
    return " ".join(format(ord(ch), "08b") for ch in text)


def from_binary_ascii(text: str) -> str:
    """二进制 ASCII 表示转文本"""
    chars = []
    for byte in text.split():
        chars.append(chr(int(byte, 2)))
    return "".join(chars)
