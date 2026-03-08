from app.services.auth_service import verify_google_token
try:
    verify_google_token("dummy_token")
    print("Success")
except Exception as e:
    import traceback
    traceback.print_exc()
