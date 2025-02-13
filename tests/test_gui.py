import sys
import unittest
import tkinter as tk
from tkinter import TclError
from unittest.mock import patch, MagicMock

# Conditionally import and start the virtual display on non-Windows systems.
if sys.platform != "win32":
    from pyvirtualdisplay import Display

# Import your SecureSafeGUI class.
from SecureSafeGUI import SecureSafeGUI  # Make sure the file is named SecureSafeGUI.py

class TestSecureSafeGUI(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        # On Linux (or non-Windows), start a virtual display.
        if sys.platform != "win32":
            cls.display = Display(visible=0, size=(800, 600))
            cls.display.start()
        else:
            cls.display = None  # No virtual display on Windows.

    @classmethod
    def tearDownClass(cls):
        if cls.display is not None:
            cls.display.stop()

    def setUp(self):
        try:
            self.root = tk.Tk()
            self.root.withdraw()  # Prevent the window from showing.
        except TclError as e:
            self.skipTest("Tkinter is not available: " + str(e))
        self.gui = SecureSafeGUI(self.root)

    def tearDown(self):
        if hasattr(self, "root"):
            self.root.destroy()

    # Update the patch target from "gui.SecureSafe" to "SecureSafeGUI.SecureSafe"
    @patch("SecureSafeGUI.SecureSafe")
    def test_authenticate_load_main_ui(self, mock_secure_safe):
        """Test that after entering a master password and clicking login,
        the GUI creates a SecureSafe instance and loads the main UI."""
        test_master = "testpassword"
        self.gui.master_entry.insert(0, test_master)
        self.gui.authenticate()

        # Ensure SecureSafe is instantiated with the correct master password.
        mock_secure_safe.assert_called_with(test_master)
        # Check that a label with "Website:" is now present.
        labels = [child for child in self.root.winfo_children() if isinstance(child, tk.Label)]
        texts = [lbl.cget("text") for lbl in labels]
        self.assertIn("Website:", texts)

    @patch("tkinter.messagebox.showerror")
    @patch("tkinter.messagebox.showinfo")
    def test_store_password_success(self, mock_showinfo, mock_showerror):
        """Test that store_password calls the safe’s store_password method
        and shows a success message when all fields are provided."""
        # Replace safe with a MagicMock.
        self.gui.safe = MagicMock()
        website = "example.com"
        username = "user"
        password = "pass123"

        # Insert test data.
        self.gui.website_entry.delete(0, tk.END)
        self.gui.website_entry.insert(0, website)
        self.gui.username_entry.delete(0, tk.END)
        self.gui.username_entry.insert(0, username)
        self.gui.password_entry.delete(0, tk.END)
        self.gui.password_entry.insert(0, password)

        self.gui.store_password()

        # Verify the safe’s store_password was called.
        self.gui.safe.store_password.assert_called_with(website, username, password)
        # Verify that the success messagebox was shown.
        mock_showinfo.assert_called_with("Success", "Password stored securely!")
        # No error should be shown.
        mock_showerror.assert_not_called()

    @patch("tkinter.messagebox.showerror")
    def test_store_password_missing_data(self, mock_showerror):
        """Test that store_password shows an error message if required data is missing."""
        self.gui.safe = MagicMock()
        # Provide missing website (empty string).
        self.gui.website_entry.delete(0, tk.END)
        self.gui.username_entry.delete(0, tk.END)
        self.gui.password_entry.delete(0, tk.END)
        self.gui.website_entry.insert(0, "")
        self.gui.username_entry.insert(0, "user")
        self.gui.password_entry.insert(0, "pass123")

        self.gui.store_password()

        mock_showerror.assert_called_with("Error", "Website, Username, and Password are required.")

    @patch("pyperclip.copy")
    @patch("tkinter.messagebox.showinfo")
    @patch("tkinter.messagebox.showerror")
    def test_retrieve_password_single(self, mock_showerror, mock_showinfo, mock_pyperclip_copy):
        """Test that when a single matching password exists,
        it is copied to the clipboard and a success message is shown."""
        self.gui.safe = MagicMock()
        # Simulate safe.retrieve_password returning one entry.
        self.gui.safe.retrieve_password.return_value = [
            {"username": "user", "password": "pass123"}
        ]
        self.gui.website_entry.delete(0, tk.END)
        self.gui.website_entry.insert(0, "example.com")
        self.gui.username_entry.delete(0, tk.END)
        self.gui.username_entry.insert(0, "user")

        self.gui.retrieve_password()

        mock_pyperclip_copy.assert_called_with("pass123")
        mock_showinfo.assert_called_with("Success", "Password copied to clipboard! ✅")
        mock_showerror.assert_not_called()

    @patch("tkinter.simpledialog.askinteger")
    @patch("pyperclip.copy")
    @patch("tkinter.messagebox.showinfo")
    @patch("tkinter.messagebox.showerror")
    def test_retrieve_password_multiple_valid(self, mock_showerror, mock_showinfo, mock_pyperclip_copy, mock_askinteger):
        """Test that when multiple matching passwords exist and a valid selection is made,
        the selected password is copied to the clipboard."""
        self.gui.safe = MagicMock()
        entries = [
            {"username": "user", "password": "pass1"},
            {"username": "user", "password": "pass2"},
        ]
        self.gui.safe.retrieve_password.return_value = entries
        self.gui.website_entry.delete(0, tk.END)
        self.gui.website_entry.insert(0, "example.com")
        self.gui.username_entry.delete(0, tk.END)
        self.gui.username_entry.insert(0, "user")

        # Simulate user choosing the second password.
        mock_askinteger.return_value = 2

        self.gui.retrieve_password()

        mock_pyperclip_copy.assert_called_with("pass2")
        mock_showinfo.assert_called_with("Success", "Password copied to clipboard! ✅")
        mock_showerror.assert_not_called()

    @patch("tkinter.simpledialog.askinteger")
    @patch("tkinter.messagebox.showerror")
    def test_retrieve_password_multiple_invalid(self, mock_showerror, mock_askinteger):
        """Test that if an invalid selection is made when multiple passwords exist,
        an error message is shown."""
        self.gui.safe = MagicMock()
        entries = [
            {"username": "user", "password": "pass1"},
            {"username": "user", "password": "pass2"},
        ]
        self.gui.safe.retrieve_password.return_value = entries
        self.gui.website_entry.delete(0, tk.END)
        self.gui.website_entry.insert(0, "example.com")
        self.gui.username_entry.delete(0, tk.END)
        self.gui.username_entry.insert(0, "user")

        # Simulate an invalid selection (None).
        mock_askinteger.return_value = None

        self.gui.retrieve_password()

        mock_showerror.assert_called_with("Error", "Invalid selection.")

    @patch("tkinter.messagebox.showerror")
    def test_retrieve_password_missing_data(self, mock_showerror):
        """Test that retrieve_password shows an error if website or username is missing."""
        self.gui.safe = MagicMock()
        # Ensure both fields are empty.
        self.gui.website_entry.delete(0, tk.END)
        self.gui.username_entry.delete(0, tk.END)

        self.gui.retrieve_password()

        mock_showerror.assert_called_with("Error", "Please enter both website and username.")

    @patch("tkinter.messagebox.showinfo")
    @patch("tkinter.messagebox.showerror")
    def test_delete_password_single(self, mock_showerror, mock_showinfo):
        """Test that delete_password removes a single stored password and shows a success message."""
        self.gui.safe = MagicMock()
        # Simulate safe.retrieve_password returning one entry.
        entry = {"username": "user", "password": "pass123"}
        self.gui.safe.retrieve_password.return_value = [entry]
        self.gui.website_entry.delete(0, tk.END)
        self.gui.website_entry.insert(0, "example.com")
        self.gui.username_entry.delete(0, tk.END)
        self.gui.username_entry.insert(0, "user")

        self.gui.delete_password()

        self.gui.safe.delete_password.assert_called_with("example.com", "user", "pass123")
        mock_showinfo.assert_called_with("Success", "Password deleted for user on example.com!")
        mock_showerror.assert_not_called()

    @patch("tkinter.simpledialog.askinteger")
    @patch("tkinter.messagebox.showinfo")
    @patch("tkinter.messagebox.showerror")
    def test_delete_password_multiple_valid(self, mock_showerror, mock_showinfo, mock_askinteger):
        """Test that when multiple matching passwords exist and a valid selection is made,
        the selected password is deleted."""
        self.gui.safe = MagicMock()
        entries = [
            {"username": "user", "password": "pass1"},
            {"username": "user", "password": "pass2"},
        ]
        self.gui.safe.retrieve_password.return_value = entries
        self.gui.website_entry.delete(0, tk.END)
        self.gui.website_entry.insert(0, "example.com")
        self.gui.username_entry.delete(0, tk.END)
        self.gui.username_entry.insert(0, "user")

        # Simulate choosing the first entry.
        mock_askinteger.return_value = 1

        self.gui.delete_password()

        self.gui.safe.delete_password.assert_called_with("example.com", "user", "pass1")
        mock_showinfo.assert_called_with("Success", "Deleted password for user on example.com!")
        mock_showerror.assert_not_called()

    @patch("tkinter.simpledialog.askinteger")
    @patch("tkinter.messagebox.showerror")
    def test_delete_password_multiple_invalid(self, mock_showerror, mock_askinteger):
        """Test that if an invalid selection is made when multiple passwords exist,
        an error message is shown."""
        self.gui.safe = MagicMock()
        entries = [
            {"username": "user", "password": "pass1"},
            {"username": "user", "password": "pass2"},
        ]
        self.gui.safe.retrieve_password.return_value = entries
        self.gui.website_entry.delete(0, tk.END)
        self.gui.website_entry.insert(0, "example.com")
        self.gui.username_entry.delete(0, tk.END)
        self.gui.username_entry.insert(0, "user")

        # Simulate an invalid selection (e.g. index 3, which is out of range).
        mock_askinteger.return_value = 3

        self.gui.delete_password()

        mock_showerror.assert_called_with("Error", "Invalid selection.")

    @patch("tkinter.messagebox.showerror")
    def test_delete_password_missing_data(self, mock_showerror):
        """Test that delete_password shows an error if website or username is missing."""
        self.gui.safe = MagicMock()
        # Provide missing website.
        self.gui.website_entry.delete(0, tk.END)
        self.gui.website_entry.insert(0, "")
        self.gui.username_entry.delete(0, tk.END)
        self.gui.username_entry.insert(0, "user")

        self.gui.delete_password()

        mock_showerror.assert_called_with("Error", "Please enter both website and username.")

    def test_generate_password(self):
        """Test that generate_password updates the password_entry with the generated password."""
        self.gui.safe = MagicMock()
        # Set a predictable password.
        self.gui.safe.generate_password.return_value = "generatedPass123!"
        # Clear any existing text.
        self.gui.password_entry.delete(0, tk.END)
        self.gui.generate_password()
        # Check that the password_entry now contains the generated password.
        self.assertEqual(self.gui.password_entry.get(), "generatedPass123!")


if __name__ == "__main__":
    unittest.main()
