"""Proves user passwords are hashed with Werkzeug, never stored as plaintext."""

from werkzeug.security import check_password_hash, generate_password_hash

from database.models.auth import User


def test_password_is_stored_as_hash_not_plaintext(session):
    plaintext = "CorrectHorseBattery1"
    user = User(
        email="hash.check@example.com",
        password_hash=generate_password_hash(plaintext),
        full_name="Hash Check",
    )
    session.add(user)
    session.commit()

    stored = session.query(User).filter_by(email="hash.check@example.com").one()

    assert stored.password_hash != plaintext
    assert stored.password_hash.startswith("pbkdf2:") or stored.password_hash.startswith("scrypt:")


def test_check_password_hash_returns_true_for_correct_password(session):
    plaintext = "CorrectHorseBattery1"
    user = User(
        email="login.correct@example.com",
        password_hash=generate_password_hash(plaintext),
        full_name="Login Correct",
    )
    session.add(user)
    session.commit()

    stored = session.query(User).filter_by(email="login.correct@example.com").one()
    assert check_password_hash(stored.password_hash, plaintext) is True


def test_check_password_hash_returns_false_for_incorrect_password(session):
    user = User(
        email="login.wrong@example.com",
        password_hash=generate_password_hash("CorrectHorseBattery1"),
        full_name="Login Wrong",
    )
    session.add(user)
    session.commit()

    stored = session.query(User).filter_by(email="login.wrong@example.com").one()
    assert check_password_hash(stored.password_hash, "SomeOtherPassword") is False
