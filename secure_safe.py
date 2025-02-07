import os
import json
import base64
import hashlib
from Crypto.Cipher import AES

class SecureSafe:
    def __init__(self, master_password):
        """Initialize SecureSafe with a master password for encryption."""
        self.master_key = self._derive_key(master_password)
        self.data_file = "passwords.json"
        self.passwords = self._load_passwords()

    def _derive_key(self, password):
        """Derives a 32-byte key from the master password using SHA-256."""
        return hashlib.sha256(password.encode()).digest()

    def _encrypt(self, plaintext):
        """Encrypts a plaintext password using AES-GCM."""
        cipher = AES.new(self.master_key, AES.MODE_GCM)
        ciphertext, tag = cipher.encrypt_and_digest(plaintext.encode())
        return base64.b64encode(cipher.nonce + tag + ciphertext).decode()

    def _decrypt(self, encrypted_data):
        """Decrypts an AES-GCM encrypted password."""
        data = base64.b64decode(encrypted_data)
        nonce, tag, ciphertext = data[:16], data[16:32], data[32:]
        cipher = AES.new(self.master_key, AES.MODE_GCM, nonce=nonce)
        return cipher.decrypt_and_verify(ciphertext, tag).decode()

    def _load_passwords(self):
        """Loads stored passwords from the JSON file."""
        if os.path.exists(self.data_file):
            with open(self.data_file, "r") as file:
                return json.load(file)
        return {}

    def _save_passwords(self):
        """Saves encrypted passwords to the JSON file."""
        with open(self.data_file, "w") as file:
            json.dump(self.passwords, file, indent=4)

    def store_password(self, account, username, password):
        """Encrypts and stores a password for an account."""
        encrypted_password = self._encrypt(password)
        self.passwords[account] = {"username": username, "password": encrypted_password}
        self._save_passwords()
        print(f"🔐 Password for {account} stored securely!")

    def retrieve_password(self, account):
        """Retrieves and decrypts a stored password."""
        if account in self.passwords:
            encrypted_data = self.passwords[account]["password"]
            decrypted_password = self._decrypt(encrypted_data)
            print(f"🔓 Retrieved password for {account}: {decrypted_password}")
            return decrypted_password
        else:
            print(f"⚠️ No password found for {account}.")
            return None

    def delete_password(self, account):
        """Deletes a stored password securely."""
        if account in self.passwords:
            del self.passwords[account]
            self._save_passwords()
            print(f"🗑️ Password for {account} deleted successfully!")
        else:
            print(f"⚠️ No password found for {account} to delete.")


# CLI Interface
def main():
    master_password = input("🔑 Enter Master Password: ")
    safe = SecureSafe(master_password)

    while True:
        print("\n📌 SecureSafe Password Manager 📌")
        print("1️⃣ Store a Password")
        print("2️⃣ Retrieve a Password")
        print("3️⃣ Delete a Password")
        print("4️⃣ Exit")

        choice = input("👉 Choose an option: ")

        if choice == "1":
            account = input("Enter account/site name: ")
            username = input("Enter username: ")
            password = input("Enter password: ")
            safe.store_password(account, username, password)

        elif choice == "2":
            account = input("Enter account/site name: ")
            safe.retrieve_password(account)

        elif choice == "3":
            account = input("Enter account/site name: ")
            safe.delete_password(account)

        elif choice == "4":
            print("🔒 Exiting SecureSafe. Stay secure!")
            break

        else:
            print("⚠️ Invalid choice, please try again.")


if __name__ == "__main__":
    main()
