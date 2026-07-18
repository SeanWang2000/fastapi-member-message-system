from password_utils import hash_password, password_hash


def test_hash_password():
    password = "secret123"
    hashed = hash_password(password)

    assert hashed != password
    assert password_hash.verify(password, hashed)
    assert not password_hash.verify("wrong12345", hashed)
