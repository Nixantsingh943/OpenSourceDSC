import uuid
import datetime
import threading
import random
import bcrypt  # For password hashing
import secrets  # For generating OTPs


class BankAccount:
    def __init__(self, account_holder, initial_balance=0, password=None):
        self.account_id = str(uuid.uuid4())
        self.account_holder = account_holder
        self._balance = initial_balance
        self.transaction_history = []
        self.is_active = True
        self._overdraft_limit = 500
        self._max_transaction_limit = 10000  # Example maximum transaction limit

        # Password handling
        if password:
            self._password_hash = bcrypt.hashpw(password.encode(), bcrypt.gensalt())
        else:
            raise ValueError("Password is required to create an account.")

        # Multi-Factor Authentication (MFA)
        self._otp = None

    def authenticate(self, password):
        """Authenticate the user by verifying the password."""
        if not bcrypt.checkpw(password.encode(), self._password_hash):
            raise PermissionError("Authentication failed: Incorrect password.")
        return True

    def generate_otp(self):
        """Generate a one-time password (OTP) for MFA."""
        self._otp = secrets.token_hex(3)  # Generate a 6-character OTP
        print(f"Your OTP is: {self._otp}")  # In a real system, send this via email/SMS
        return self._otp

    def verify_otp(self, otp):
        """Verify the provided OTP."""
        if self._otp == otp:
            self._otp = None  # Invalidate the OTP after use
            return True
        raise PermissionError("Authentication failed: Invalid OTP.")

    def deposit(self, amount, password):
        # Authenticate user
        self.authenticate(password)

        # Type and range validation
        if not isinstance(amount, (int, float)):
            raise TypeError("Deposit amount must be a number (int or float).")
        if amount <= 0:
            raise ValueError("Deposit amount must be greater than 0.")
        if amount > self._max_transaction_limit:
            raise ValueError(f"Deposit amount exceeds the maximum limit of {self._max_transaction_limit}.")

        self._balance += amount
        self._log_transaction("DEPOSIT", amount)
        return True

    def withdraw(self, amount, password, otp):
        # Authenticate user and verify OTP
        self.authenticate(password)
        self.verify_otp(otp)

        # Type and range validation
        if not isinstance(amount, (int, float)):
            raise TypeError("Withdrawal amount must be a number (int or float).")
        if amount <= 0:
            raise ValueError("Withdrawal amount must be greater than 0.")
        if amount > self._max_transaction_limit:
            raise ValueError(f"Withdrawal amount exceeds the maximum limit of {self._max_transaction_limit}.")

        # Check if withdrawal is within balance and overdraft limit
        if self._balance >= amount:
            self._balance -= amount
            self._log_transaction("WITHDRAWAL", amount)
            return True
        elif self._balance < amount <= (self._balance + self._overdraft_limit):
            overdraft_used = amount - self._balance
            self._balance = 0  # Deplete balance
            self._overdraft_limit -= overdraft_used  # Deduct from overdraft limit
            self._log_transaction("WITHDRAWAL (OVERDRAFT)", amount)
            return True

        raise ValueError("Insufficient funds, including overdraft limit.")

    def _log_transaction(self, transaction_type, amount):
        transaction = {
            'id': str(uuid.uuid4()),
            'type': transaction_type,
            'amount': amount,
            'timestamp': datetime.datetime.now(),
            'balance': self._balance
        }
        self.transaction_history.append(transaction)


class Bank:
    def __init__(self, name):
        self.name = name
        self.accounts = {}
        self._account_lock = threading.Lock()

    def create_account(self, account_holder, initial_balance, password):
        with self._account_lock:
            account = BankAccount(account_holder, initial_balance, password)
            self.accounts[account.account_id] = account
            return account.account_id

    def get_account(self, account_id):
        return self.accounts.get(account_id)

    def transfer_funds(self, from_account_id, to_account_id, amount, password, otp):
        try:
            with self._account_lock:
                from_account = self.get_account(from_account_id)
                to_account = self.get_account(to_account_id)

                if not from_account or not to_account:
                    print("Invalid account(s)")
                    return False

                # Authenticate and verify OTP for the sender
                from_account.authenticate(password)
                from_account.verify_otp(otp)

                if from_account.withdraw(amount, password, otp):
                    to_account.deposit(amount, password)
                    return True
                return False
        except Exception as e:
            print(f"Transfer failed: {e}")
            return False


class BankingSystem:
    def __init__(self):
        self.bank = Bank("Secure Bank")

    def simulate_transactions(self, num_transactions=100):
        accounts = []
        for i in range(5):
            account_id = self.bank.create_account(f"User {i}", 1000, f"password{i}")
            accounts.append(account_id)

        def random_transaction():
            from_account = random.choice(accounts)
            to_account = random.choice(accounts)
            amount = random.uniform(10, 500)
            password = f"password{accounts.index(from_account)}"
            otp = self.bank.get_account(from_account).generate_otp()
            self.bank.transfer_funds(from_account, to_account, amount, password, otp)

        threads = []
        for _ in range(num_transactions):
            thread = threading.Thread(target=random_transaction)
            thread.start()
            threads.append(thread)

        for thread in threads:
            thread.join()