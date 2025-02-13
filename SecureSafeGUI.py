import tkinter as tk
from tkinter import messagebox, simpledialog
from secure_safe import SecureSafe
import pyperclip


class SecureSafeGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("SecureSafe Password Manager")

        # Initialize UI elements
        self.website_entry = tk.Entry(self.root)
        self.username_entry = tk.Entry(self.root)
        self.password_entry = tk.Entry(self.root)

        tk.Label(root, text="Master Password:").pack()
        self.master_entry = tk.Entry(root, show="*")
        self.master_entry.pack()

        tk.Button(root, text="Login", command=self.authenticate).pack()

    def authenticate(self):
        master_password = self.master_entry.get()
        self.safe = SecureSafe(master_password)
        self.load_main_ui()

    def load_main_ui(self):
        for widget in self.root.winfo_children():
            widget.destroy()

        tk.Label(self.root, text="Website:").pack()
        self.website_entry = tk.Entry(self.root)
        self.website_entry.pack()

        tk.Label(self.root, text="Username:").pack()
        self.username_entry = tk.Entry(self.root)
        self.username_entry.pack()

        tk.Label(self.root, text="Password:").pack()
        self.password_entry = tk.Entry(self.root)
        self.password_entry.pack()

        tk.Button(self.root, text="Store Password", command=self.store_password).pack()
        tk.Button(
            self.root, text="Retrieve Password", command=self.retrieve_password
        ).pack()
        tk.Button(
            self.root, text="Generate Password", command=self.generate_password
        ).pack()
        tk.Button(
            self.root, text="Delete Password", command=self.delete_password
        ).pack()  # New delete button

    def store_password(self):
        website = self.website_entry.get()
        username = self.username_entry.get()
        password = self.password_entry.get()

        if not website or not username or not password:
            messagebox.showerror(
                "Error", "Website, Username, and Password are required."
            )
            return

        self.safe.store_password(website, username, password)
        messagebox.showinfo("Success", "Password stored securely!")

    def delete_password(self):
        """Deletes a stored password for a specific username on a website."""
        website = self.website_entry.get()
        username = self.username_entry.get()

        if not website or not username:
            messagebox.showerror("Error", "Please enter both website and username.")
            return

        stored_passwords = self.safe.retrieve_password(website)

        if not stored_passwords:
            messagebox.showerror("Error", "No passwords found for this website.")
            return

        # Filter passwords for the entered username
        filtered_passwords = [
            entry for entry in stored_passwords if entry["username"] == username
        ]

        if not filtered_passwords:
            messagebox.showerror(
                "Error", f"No passwords found for username: {username}"
            )
            return

        if len(filtered_passwords) > 1:
            password_list = "\n".join(
                [
                    f"{idx + 1}. {entry['password']}"
                    for idx, entry in enumerate(filtered_passwords)
                ]
            )
            choice = simpledialog.askinteger(
                "Select Password",
                f"Multiple passwords found for {username}:\n{password_list}\n\nEnter the number to delete:",
            )

            if choice and 1 <= choice <= len(filtered_passwords):
                selected_entry = filtered_passwords[choice - 1]
                self.safe.delete_password(website, username, selected_entry["password"])
                messagebox.showinfo(
                    "Success", f"Deleted password for {username} on {website}!"
                )
            else:
                messagebox.showerror("Error", "Invalid selection.")
        else:
            self.safe.delete_password(
                website, username, filtered_passwords[0]["password"]
            )
            messagebox.showinfo(
                "Success", f"Password deleted for {username} on {website}!"
            )

    def retrieve_password(self):
        """Retrieves passwords for a website and a specific username."""
        website = self.website_entry.get()
        username = self.username_entry.get()

        if not website or not username:
            messagebox.showerror("Error", "Please enter both website and username.")
            return

        stored_passwords = self.safe.retrieve_password(website)

        if not stored_passwords:
            messagebox.showerror("Error", "No passwords found for this website.")
            return

        # Filter by username
        filtered_passwords = [
            entry["password"]
            for entry in stored_passwords
            if entry["username"] == username
        ]

        if not filtered_passwords:
            messagebox.showerror(
                "Error", f"No passwords found for username: {username}"
            )
            return

        # If multiple passwords exist for the same username
        if len(filtered_passwords) > 1:
            password_list = "\n".join(
                [
                    f"{idx + 1}. {password}"
                    for idx, password in enumerate(filtered_passwords)
                ]
            )
            choice = simpledialog.askinteger(
                "Select Password",
                f"Multiple passwords found:\n{password_list}\n\nEnter the number to copy:",
            )

            if choice and 1 <= choice <= len(filtered_passwords):
                selected_password = filtered_passwords[choice - 1]
                pyperclip.copy(selected_password)
                messagebox.showinfo("Success", "Password copied to clipboard! ✅")
            else:
                messagebox.showerror("Error", "Invalid selection.")
        else:
            pyperclip.copy(filtered_passwords[0])
            messagebox.showinfo("Success", "Password copied to clipboard! ✅")

    def generate_password(self):
        password = self.safe.generate_password()
        self.password_entry.delete(0, tk.END)
        self.password_entry.insert(0, password)


if __name__ == "__main__":
    root = tk.Tk()
    SecureSafeGUI(root)
    root.mainloop()
