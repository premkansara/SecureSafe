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
    """Test if a password is correctly stored."""
    secure_safe.store_password("test.com", "testuser", "Test@123")
    assert "test.com" in secure_safe.passwords


def test_retrieve_password(secure_safe):
    """Test if a stored password can be retrieved correctly."""
    secure_safe.store_password("test.com", "testuser", "Test@123")
    retrieved_password = secure_safe.retrieve_password("test.com")
    assert retrieved_password == "Test@123"


def test_retrieve_non_existent_password(secure_safe):
    """Test retrieving a password that does not exist."""
    retrieved_password = secure_safe.retrieve_password("unknown.com")
    assert retrieved_password is None  # Should return None for non-existent passwords


def test_delete_password(secure_safe):
    """Test deleting a stored password."""
    secure_safe.store_password("test.com", "testuser", "Test@123")
    secure_safe.delete_password("test.com")
    assert "test.com" not in secure_safe.passwords


def test_delete_non_existent_password(secure_safe):
    """Test deleting a password that doesn't exist."""
    secure_safe.delete_password("nonexistent.com")
    assert "nonexistent.com" not in secure_safe.passwords
