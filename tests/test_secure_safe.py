import pytest
import os
from secure_safe import SecureSafe


@pytest.fixture
def secure_safe():
    """Creates a test instance of SecureSafe with a test master password."""
    test_instance = SecureSafe("TestMasterKey")
    yield test_instance
    # Cleanup: Remove the test password file after tests
    if os.path.exists("passwords.json"):
        os.remove("passwords.json")


def test_store_password(secure_safe):
    """Test storing multiple passwords per website and username."""
    secure_safe.store_password("test.com", "user1", "Test@123")
    secure_safe.store_password("test.com", "user2", "Pass@456")

    assert "test.com" in secure_safe.passwords
    assert len(secure_safe.passwords["test.com"]) == 2  # Should store two passwords


def test_retrieve_password(secure_safe):
    """Test retrieving only passwords belonging to a specific username."""
    secure_safe.store_password("test.com", "user1", "Test@123")
    secure_safe.store_password("test.com", "user2", "Pass@456")

    retrieved_passwords = secure_safe.retrieve_password("test.com")
    assert isinstance(retrieved_passwords, list)
    assert len(retrieved_passwords) == 2
    assert any(entry["password"] == "Test@123" for entry in retrieved_passwords)
    assert any(entry["password"] == "Pass@456" for entry in retrieved_passwords)


def test_delete_password(secure_safe):
    """Test deleting a specific password entry without affecting others."""
    secure_safe.store_password("test.com", "user1", "Test@123")
    secure_safe.store_password("test.com", "user2", "Pass@456")

    secure_safe.delete_password("test.com", "user1", "Test@123")

    remaining_passwords = secure_safe.retrieve_password("test.com")
    assert len(remaining_passwords) == 1  # Only one password should remain
    assert remaining_passwords[0]["username"] == "user2"
    assert remaining_passwords[0]["password"] == "Pass@456"


def test_delete_non_existent_password(secure_safe):
    """Ensure deleting a non-existent password does not crash."""
    secure_safe.store_password("test.com", "user1", "Test@123")
    secure_safe.delete_password("test.com", "user2", "FakePass")

    retrieved_passwords = secure_safe.retrieve_password("test.com")
    assert len(retrieved_passwords) == 1  # Password should remain unchanged
