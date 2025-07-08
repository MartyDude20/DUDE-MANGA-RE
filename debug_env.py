import os
from dotenv import load_dotenv

print("CWD:", os.getcwd())
load_dotenv()
print("MAIL_USERNAME:", os.getenv("MAIL_USERNAME"))
print("MAIL_PASSWORD:", os.getenv("MAIL_PASSWORD"))
print("MAIL_SERVER:", os.getenv("MAIL_SERVER"))
print("MAIL_DEFAULT_SENDER:", os.getenv("MAIL_DEFAULT_SENDER"))
print("TEST_ENV_CHECK:", os.getenv("TEST_ENV_CHECK")) 