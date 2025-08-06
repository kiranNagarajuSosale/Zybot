import os
from dotenv import load_dotenv
import uvicorn

load_dotenv()

CERT_FILE = os.getenv("SSL_CERT_FILE")
KEY_FILE = os.getenv("SSL_KEY_FILE")
HOST = os.getenv("APP_HOST", "0.0.0.0")
PORT = int(os.getenv("APP_PORT", 9443))

if __name__ == "__main__":
    if not CERT_FILE or not KEY_FILE:
        raise ValueError("SSL_CERT_FILE or SSL_KEY_FILE not set in .env")
    if not os.path.exists(CERT_FILE) or not os.path.exists(KEY_FILE):
        raise FileNotFoundError("Certificate or Key file not found.")

    print(f"🔒 Serving app with HTTPS on https://{HOST}:{PORT}")
    uvicorn.run(
        "app:app",
        host=HOST,
        port=PORT,
        ssl_certfile=CERT_FILE,
        ssl_keyfile=KEY_FILE,
        reload=True
    )
