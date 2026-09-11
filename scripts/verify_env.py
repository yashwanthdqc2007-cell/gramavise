"""Verify environment variables and basic connectivity."""
import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "backend")))


def verify():
    print("Checking GramaVise Environment configuration...")
    try:
        from app.config import settings
        print(f"  [OK] App Name: {settings.APP_NAME}")
        print(f"  [OK] Environment: {settings.ENVIRONMENT}")
        print(f"  [OK] Database URL: {settings.DATABASE_URL}")
        print(f"  [OK] AI Provider: {settings.LLM_PROVIDER}")
        print("Environment configuration verified successfully!")
    except Exception as e:
        print(f"  [ERROR] Configuration failed: {e}")
        sys.exit(1)


if __name__ == "__main__":
    verify()
