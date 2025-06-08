import bcrypt

# Step 1: Define the plain password
password = "admin123"

# Step 2: Convert to bytes
password_bytes = password.encode("utf-8")

# Step 3: Generate salt
salt = bcrypt.gensalt()

# Step 4: Hash the password
hashed = bcrypt.hashpw(password_bytes, salt)
