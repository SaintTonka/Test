import hashlib
import json
from app.config import SECRET_KEY 

def generate_signature(data):
    sorted_data = ''.join(f"{k}{v}" for k, v in sorted(data.items()))  
    raw_string = sorted_data + SECRET_KEY  
    return hashlib.sha256(raw_string.encode()).hexdigest()  

#Example data
data = {
    "transaction_id": "transaction_123",
    "amount": 50.0,
    "account_id": 2,
    "user_id": 2,
}

print(generate_signature(data)) # non comstant decision)