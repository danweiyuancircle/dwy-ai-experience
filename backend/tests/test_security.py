"""Tests for dwyeapi.security."""

from dwyeapi.security import create_token, decode_token, hash_password, verify_password


class TestPasswordHashing:
    def test_hash_returns_bcrypt_string(self):
        hashed = hash_password("secret123")
        assert hashed.startswith("$2b$")

    def test_verify_correct_password(self):
        hashed = hash_password("mypassword")
        assert verify_password("mypassword", hashed) is True

    def test_verify_wrong_password(self):
        hashed = hash_password("mypassword")
        assert verify_password("wrongpassword", hashed) is False

    def test_different_hashes_for_same_password(self):
        h1 = hash_password("same")
        h2 = hash_password("same")
        assert h1 != h2


class TestJWTTokens:
    SECRET = "test-secret-key-for-unit-tests"

    def test_create_and_decode_token(self):
        data = {"sub": "42", "username": "alice"}
        token = create_token(data, secret=self.SECRET, expires_minutes=30)
        payload = decode_token(token, secret=self.SECRET)
        assert payload is not None
        assert payload["sub"] == "42"
        assert payload["username"] == "alice"

    def test_decode_with_wrong_secret_returns_none(self):
        token = create_token({"sub": "1"}, secret=self.SECRET, expires_minutes=30)
        assert decode_token(token, secret="wrong-secret") is None

    def test_expired_token_returns_none(self):
        token = create_token({"sub": "1"}, secret=self.SECRET, expires_minutes=-1)
        assert decode_token(token, secret=self.SECRET) is None

    def test_invalid_token_string_returns_none(self):
        assert decode_token("not-a-jwt", secret=self.SECRET) is None

    def test_create_does_not_mutate_input(self):
        data = {"sub": "1"}
        original = data.copy()
        create_token(data, secret=self.SECRET, expires_minutes=30)
        assert data == original
