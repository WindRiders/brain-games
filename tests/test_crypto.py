"""加密/解密工具测试"""
import sys
import os

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, PROJECT_ROOT)

from src.utils.crypto import (
    caesar_cipher, rot13, reverse_text,
    base64_encode, base64_decode,
    to_morse, from_morse, MORSE_CODE,
    vigenere_encrypt, vigenere_decrypt,
    to_binary_ascii, from_binary_ascii,
)


class TestCaesarCipher:
    @staticmethod
    def run_all():
        TestCaesarCipher.test_encrypt_shift3()
        TestCaesarCipher.test_decrypt_shift3()
        TestCaesarCipher.test_roundtrip()
        TestCaesarCipher.test_non_alpha_unchanged()
        TestCaesarCipher.test_wrap_around()
        TestCaesarCipher.test_spaces()
        print("  [PASS] All CaesarCipher tests")

    @staticmethod
    def test_encrypt_shift3():
        assert caesar_cipher("ABC", 3, encrypt=True) == "DEF"

    @staticmethod
    def test_decrypt_shift3():
        assert caesar_cipher("DEF", 3, encrypt=False) == "ABC"

    @staticmethod
    def test_roundtrip():
        for text in ["Hello", "World", "Test123", "abcXYZ"]:
            encrypted = caesar_cipher(text, 5, encrypt=True)
            decrypted = caesar_cipher(encrypted, 5, encrypt=False)
            assert decrypted == text, f"Roundtrip failed for '{text}'"

    @staticmethod
    def test_non_alpha_unchanged():
        assert caesar_cipher("123 !@#", 3) == "123 !@#"

    @staticmethod
    def test_wrap_around():
        assert caesar_cipher("XYZ", 3) == "ABC"
        assert caesar_cipher("xyz", 3) == "abc"

    @staticmethod
    def test_spaces():
        assert caesar_cipher("A B", 1, encrypt=True) == "B C"


class TestRot13:
    @staticmethod
    def run_all():
        TestRot13.test_identity()
        TestRot13.test_hello()
        print("  [PASS] All Rot13 tests")

    @staticmethod
    def test_identity():
        """ROT13两次应还原。"""
        assert rot13(rot13("Hello")) == "Hello"

    @staticmethod
    def test_hello():
        assert rot13("Hello") == "Uryyb"


class TestReverseText:
    @staticmethod
    def run_all():
        TestReverseText.test_simple()
        TestReverseText.test_palindrome()
        print("  [PASS] All ReverseText tests")

    @staticmethod
    def test_simple():
        assert reverse_text("Hello") == "olleH"

    @staticmethod
    def test_palindrome():
        assert reverse_text("aba") == "aba"


class TestBase64:
    @staticmethod
    def run_all():
        TestBase64.test_roundtrip()
        TestBase64.test_hello()
        print("  [PASS] All Base64 tests")

    @staticmethod
    def test_roundtrip():
        for text in ["Hello", "Brain Games", "Test123"]:
            encoded = base64_encode(text)
            decoded = base64_decode(encoded)
            assert decoded == text

    @staticmethod
    def test_hello():
        assert base64_encode("Hello") == "SGVsbG8="


class TestMorseCode:
    @staticmethod
    def run_all():
        TestMorseCode.test_encode_hello()
        TestMorseCode.test_roundtrip()
        TestMorseCode.test_dict_complete()
        print("  [PASS] All MorseCode tests")

    @staticmethod
    def test_encode_hello():
        # H=.... E=. L=.-.. L=.-.. O=---
        result = to_morse("HELLO")
        assert "...." in result  # H
        assert ".-.." in result  # L

    @staticmethod
    def test_roundtrip():
        for text in ["HELLO", "SOS", "TEST"]:
            encoded = to_morse(text)
            decoded = from_morse(encoded)
            assert decoded == text, f"Morse roundtrip failed: {text} -> {encoded} -> {decoded}"

    @staticmethod
    def test_dict_complete():
        """MORSE_CODE 应包含所有26个字母。"""
        for letter in "ABCDEFGHIJKLMNOPQRSTUVWXYZ":
            assert letter in MORSE_CODE, f"Missing Morse for {letter}"


class TestVigenere:
    @staticmethod
    def run_all():
        TestVigenere.test_roundtrip()
        TestVigenere.test_key_longer()
        print("  [PASS] All Vigenere tests")

    @staticmethod
    def test_roundtrip():
        for text, key in [("Hello", "KEY"), ("ABC", "A"), ("Test", "SECRET")]:
            encrypted = vigenere_encrypt(text, key)
            decrypted = vigenere_decrypt(encrypted, key)
            assert decrypted == text, f"Vigenere roundtrip failed: {text}"

    @staticmethod
    def test_key_longer():
        encrypted = vigenere_encrypt("A", "LONGKEY")
        decrypted = vigenere_decrypt(encrypted, "LONGKEY")
        assert decrypted == "A"


class TestBinaryAscii:
    @staticmethod
    def run_all():
        TestBinaryAscii.test_roundtrip()
        TestBinaryAscii.test_hello()
        print("  [PASS] All BinaryAscii tests")

    @staticmethod
    def test_roundtrip():
        for text in ["Hello", "A", "Test123"]:
            encoded = to_binary_ascii(text)
            decoded = from_binary_ascii(encoded)
            assert decoded == text, f"Binary ASCII roundtrip failed: {text}"

    @staticmethod
    def test_hello():
        encoded = to_binary_ascii("A")
        assert encoded == "01000001", f"Expected 01000001, got {encoded}"


if __name__ == "__main__":
    print("Running crypto tests...")
    TestCaesarCipher.run_all()
    TestRot13.run_all()
    TestReverseText.run_all()
    TestBase64.run_all()
    TestMorseCode.run_all()
    TestVigenere.run_all()
    TestBinaryAscii.run_all()
    print("\nAll crypto tests passed!")
