import os
import json
import base64
import random
import string
from Crypto.Cipher import AES
from Crypto.Util.Padding import pad, unpad
from getpass import getpass


class SecureSafe:
    def __init__(self, master_password):
        self.file = "passwords.json"
        self.key = self.derive_key(master_password)
        self.passwords = self.load_passwords()

    def derive_key(self, password):
        """Derives a 16-byte AES key from the master password."""
        return base64.urlsafe_b64encode(password.ljust(16).encode()[:16])

    def encrypt(self, plaintext):
        """Encrypts a given plaintext using AES encryption."""
        cipher = AES.new(self.key, AES.MODE_CBC)
        encrypted_data = cipher.encrypt(pad(plaintext.encode(), AES.block_size))
        return base64.b64encode(cipher.iv + encrypted_data).decode()

    def decrypt(self, encrypted_text):
        """Decrypts a given ciphertext using AES encryption."""
        encrypted_bytes = base64.b64decode(encrypted_text)
        iv = encrypted_bytes[: AES.block_size]
        cipher = AES.new(self.key, AES.MODE_CBC, iv)
        return unpad(
            cipher.decrypt(encrypted_bytes[AES.block_size:]), AES.block_size
        ).decode()

    def load_passwords(self):
        """Loads passwords from the JSON file and ensures they are stored as lists."""
        if os.path.exists(self.file):
            with open(self.file, "r") as f:
                try:
                    data = json.load(f)
                    # Ensure that each website entry is stored as a list
                    for website, entries in data.items():
                        decrypted_entries = json.loads(self.decrypt(entries))
                        if isinstance(
                            decrypted_entries, dict
                        ):  # If a single entry exists, convert to list
                            decrypted_entries = [decrypted_entries]
                        data[website] = decrypted_entries
                    return data
                except Exception:
                    return {}
        return {}

    def save_passwords(self):
        """Encrypts and saves passwords, ensuring list format is maintained."""
        encrypted_data = {
            k: self.encrypt(json.dumps(v)) for k, v in self.passwords.items()
        }
        with open(self.file, "w") as f:
            json.dump(encrypted_data, f)

    def store_password(self, website, username, password):
        """Ensures passwords are stored as a list per website."""
        if website not in self.passwords or not isinstance(
            self.passwords[website], list
        ):
            self.passwords[website] = (
                []
            )  # Initialize as list if it’s missing or corrupted

        self.passwords[website].append({"username": username, "password": password})
        self.save_passwords()

    def retrieve_password(self, website):
        """Retrieves all stored passwords for a website."""
        passwords = self.passwords.get(website, [])

        # Ensure it's a list (convert single string entries)
        if isinstance(passwords, str):
            passwords = [{"username": "default", "password": passwords}]

        return passwords

    def delete_password(self, website, username, password):
        """Deletes a specific password entry for a website while keeping others."""
        if website in self.passwords:
            # Filter out only the selected password, keeping others
            self.passwords[website] = [
                entry
                for entry in self.passwords[website]
                if not (entry["username"] == username and entry["password"] == password)
            ]

            # If no passwords remain for this website, remove the website entry
            if not self.passwords[website]:
                del self.passwords[website]

            self.save_passwords()

    def generate_password(self, length=12, use_symbols=True, use_numbers=True):
        """Generates a strong random password."""
        characters = string.ascii_letters
        if use_symbols:
            characters += string.punctuation
        if use_numbers:
            characters += string.digits
        return "".join(random.choice(characters) for _ in range(length))


def main_cli():
    """CLI for SecureSafe"""
    print("Welcome to SecureSafe v2!")
    master_password = getpass("Enter your master password: ")
    safe = SecureSafe(master_password)

    while True:
        print("\nOptions:")
        print("1. Store Password")
        print("2. Retrieve Password")
        print("3. Delete Password")
        print("4. Generate Password")
        print("5. Exit")
        choice = input("Choose an option: ")

        if choice == "1":
            website = input("Enter website: ")
            password = input("Enter password: ")
            safe.store_password(website, password)
            print("Password stored securely!")

        elif choice == "2":
            website = input("Enter website: ")
            password = safe.retrieve_password(website)
            if password:
                print(f"Password for {website}: {password}")
            else:
                print("No password found.")

        elif choice == "3":
            website = input("Enter website to delete: ")
            safe.delete_password(website)
            print("Password deleted!")

        elif choice == "4":
            length = int(input("Enter password length: "))
            password = safe.generate_password(length)
            print(f"Generated Password: {password}")

        elif choice == "5":
            break

        else:
            print("Invalid option, try again.")


if __name__ == "__main__":
    main_cli()
