#!/usr/bin/env python3
import secrets

def generate_secret_key(length: int = 32) -> str:
    return secrets.token_urlsafe(length)

if __name__ == "__main__":
    print("-" * 60)
    print("SECRET GENERATION TOOL")
    print("-" * 60)
    print(f"JWT Secret Key: {generate_secret_key(32)}")
    print(f"API Key: {secrets.token_hex(20)}")
    print("-" * 60)
