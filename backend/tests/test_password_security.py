"""Password hashing: Argon2 for new secrets, legacy sha256_crypt still verifies."""

from passlib.hash import sha256_crypt

from backend.app.core.security import get_password_hash, verify_password


def test_new_hashes_use_argon2() -> None:
    h = get_password_hash("correct horse battery staple")
    assert h.startswith("$argon2")


def test_verify_argon2_round_trip() -> None:
    h = get_password_hash("p4ssw0rd!")
    assert verify_password("p4ssw0rd!", h) is True
    assert verify_password("wrong", h) is False


def test_verify_legacy_sha256_crypt() -> None:
    legacy = sha256_crypt.hash("old-dev-password")
    assert verify_password("old-dev-password", legacy) is True
    assert verify_password("nope", legacy) is False
