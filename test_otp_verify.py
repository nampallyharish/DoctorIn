import sqlite3, hmac, hashlib, json, urllib.request, time

email = f"testavatar_{int(time.time())}@example.com"
name = "Avatar Sync User"

# 1. Register user
reg_payload = json.dumps({
    "role": "user",
    "full_name": name,
    "email": email,
    "password": "Password123!"
}).encode('utf-8')

req = urllib.request.Request(
    'http://127.0.0.1:8000/api/v1/auth/register',
    data=reg_payload,
    headers={'Content-Type': 'application/json'}
)
with urllib.request.urlopen(req) as resp:
    print("Register Response:", resp.status)

# 2. Extract OTP from db
conn = sqlite3.connect('backend/doctorin_dev.db')
c = conn.cursor()
row = c.execute("SELECT identifier, otp_hash FROM otp_verifications WHERE identifier=? ORDER BY created_at DESC LIMIT 1", (email,)).fetchone()
stored_hash = row[1]
pepper = b'doctorin-dev-secret-key-minimum-32-chars-long'
found_otp = None
for num in range(100000, 1000000):
    code = str(num)
    if hmac.new(pepper, code.encode('utf-8'), hashlib.sha256).hexdigest() == stored_hash:
        found_otp = code
        break

print(f"Discovered OTP: {found_otp}")

# 3. Verify OTP via API
v_payload = json.dumps({
    "identifier": email,
    "otp": found_otp,
    "purpose": "registration"
}).encode('utf-8')

v_req = urllib.request.Request(
    'http://127.0.0.1:8000/api/v1/auth/verify-otp',
    data=v_payload,
    headers={'Content-Type': 'application/json'}
)
with urllib.request.urlopen(v_req) as resp:
    v_data = json.loads(resp.read().decode())
    print("Verify OTP Response:", json.dumps(v_data, indent=2))

access_token = v_data["data"]["access_token"]

# 4. Call /auth/me
me_req = urllib.request.Request(
    'http://127.0.0.1:8000/api/v1/auth/me',
    headers={'Authorization': f'Bearer {access_token}'}
)
with urllib.request.urlopen(me_req) as resp:
    me_data = json.loads(resp.read().decode())
    print("/auth/me Response:", json.dumps(me_data, indent=2))
