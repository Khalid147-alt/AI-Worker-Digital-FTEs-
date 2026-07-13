import xmlrpc.client
import os

url = "https://neuros.odoo.com"
db = "neuros"
username = "khalidunar103@gmail.com"
password = "0f7bf1b35af4c3064d84d8e3a1e28ad81efe5eac"

try:
    common = xmlrpc.client.ServerProxy('{}/xmlrpc/2/common'.format(url))
    uid = common.authenticate(db, username, password, {})
    if uid:
        print(f"Success! Authenticated with uid: {uid}")
    else:
        print("Authentication failed: Invalid credentials or database.")
except Exception as e:
    print(f"Error: {e}")
