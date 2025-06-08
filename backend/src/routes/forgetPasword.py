import random
import smtplib
from email.message import EmailMessage
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, EmailStr
from passlib.context import CryptContext
from backend.src.config import db


router = APIRouter()

# Password hashing setup
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# 📌 Function to send OTP via email
async def send_otp(email: str, otp: str):
    sender_email = "tenurastudy@gmail.com"  # Replace with your email
    sender_password = "awgv cnzj hzsz laos"  # Use App Password if using Gmail

    msg = EmailMessage()
    msg.set_content(f"Your OTP for password reset is: {otp}")
    msg["Subject"] = "Password Reset OTP"
    msg["From"] = sender_email
    msg["To"] = email

    try:
        with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
            server.login(sender_email, sender_password)
            server.send_message(msg)
        return True
    except Exception as e:
        return False


# 📌 Forgot Password Request Model
class ForgotPasswordRequest(BaseModel):
    email: EmailStr  

# 📌 Forgot Password Endpoint
@router.post("/forgot-password")
async def forgot_password(request: ForgotPasswordRequest):
    # Check if email exists in MongoDB
    user = await db.users.find_one({"email": request.email})
    if not user:
        raise HTTPException(status_code=404, detail="Email not found!")

    # Generate a random 6-digit OTP
    otp = str(random.randint(100000, 999999))

    # Store OTP in MongoDB
    await db.users.update_one({"email": request.email}, {"$set": {"reset_otp": otp}})

    # Send OTP via Email
    email_sent = await send_otp(request.email, otp)
    if email_sent:
        return {"message": "OTP sent to your email"}
    else:
        raise HTTPException(status_code=500, detail="Failed to send OTP")


# 📌 OTP Verification Model
class VerifyOTPRequest(BaseModel):
    email: EmailStr
    otp: str  

# 📌 OTP Verification Endpoint
@router.post("/verify-otp")
async def verify_otp(request: VerifyOTPRequest):
    user = await db.users.find_one({"email": request.email})
    if not user:
        raise HTTPException(status_code=404, detail="Email not found!")

    # Verify OTP
    if user.get("reset_otp") != request.otp:
        raise HTTPException(status_code=400, detail="Invalid or expired OTP!")

    # Remove OTP from database (security)
    await db.users.update_one({"email": request.email}, {"$unset": {"reset_otp": ""}})

    return {"message": "OTP verified successfully! You can now reset your password."}


# 📌 Change Password Model
class ChangePasswordRequest(BaseModel):
    email: EmailStr
    new_password: str

# 📌 Change Password Endpoint (AFTER OTP Verification)
@router.post("/change-password")
async def change_password(request: ChangePasswordRequest):
    # Check if email exists
    user = await db.users.find_one({"email": request.email})
    if not user:
        raise HTTPException(status_code=404, detail="Email not found!")

    # Hash the new password
    hashed_password = pwd_context.hash(request.new_password)

    # Update password in MongoDB
    await db.users.update_one(
        {"email": request.email},
        {"$set": {"password": hashed_password}}
    )

    return {"message": "Password updated successfully!"}
