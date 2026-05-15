from socket import *
import base64
import os
import ssl  # Necessary for secure encryption

# --- 1. CONFIGURATION ---
mailserver = ("mmtp.iitk.ac.in", 25) # Port 587 is standard for authenticated mail
username = "dakshdua22"      # Just the username, e.g., 'daksh'
password = "Tech@CCIITK123"
sender = f"{username}@iitk.ac.in"
to_recipient = "dakshdua22@iitk.ac.in"
cc_recipient = "dakshdua22@gmail.com"
subject = "Assignment 1: Authenticated Socket Mail"
filename = "file1.txt"

def send_cmd(sock, cmd, expected="250"):
    sock.send((cmd + "\r\n").encode())
    resp = sock.recv(1024).decode()
    print(f"C: {cmd[:20]}... | S: {resp.strip()}")
    return resp

# --- 2. CONNECT & UPGRADE TO SECURE (TLS) ---
clientSocket = socket(AF_INET, SOCK_STREAM)
clientSocket.connect(mailserver)
print(f"Server Greeting: {clientSocket.recv(1024).decode().strip()}")

send_cmd(clientSocket, "EHLO iitk.ac.in")
# Tell the server we want a secure connection
send_cmd(clientSocket, "STARTTLS", "220") 

# Wrap the existing socket in SSL
context = ssl.create_default_context()
secureSocket = context.wrap_socket(clientSocket, server_hostname=mailserver[0])
print("--- Connection Encrypted ---")

# --- 3. AUTHENTICATION ---
# Re-identify ourselves over the new secure tunnel
send_cmd(secureSocket, "EHLO iitk.ac.in")

# Encode credentials to Base64
user_b64 = base64.b64encode(username.encode()).decode()
pass_b64 = base64.b64encode(password.encode()).decode()

send_cmd(secureSocket, "AUTH LOGIN", "334")
send_cmd(secureSocket, user_b64, "334")
send_cmd(secureSocket, pass_b64, "235") # 235 = Success!

# --- 4. SET RECIPIENTS ---
send_cmd(secureSocket, f"MAIL FROM: <{sender}>")
send_cmd(secureSocket, f"RCPT TO: <{to_recipient}>")
send_cmd(secureSocket, f"RCPT TO: <{cc_recipient}>")

# --- 5. SEND DATA (Subject, Body, Attachment) ---
send_cmd(secureSocket, "DATA", "354")

boundary = "____NextPart____"
headers = f"From: {sender}\r\nTo: {to_recipient}\r\nCc: {cc_recipient}\r\nSubject: {subject}\r\nMIME-Version: 1.0\r\nContent-Type: multipart/mixed; boundary={boundary}\r\n\r\n"
body = f"--{boundary}\r\nContent-Type: text/plain\r\n\r\nSent via Python secure socket.\r\n"

# Add attachment logic
attachment = ""
if os.path.exists(filename):
    with open(filename, "rb") as f:
        encoded = base64.b64encode(f.read()).decode()
    attachment = f"--{boundary}\r\nContent-Type: application/octet-stream; name=\"{filename}\"\r\nContent-Transfer-Encoding: base64\r\n\r\n{encoded}\r\n"

footer = f"--{boundary}--\r\n.\r\n"

secureSocket.send((headers + body + attachment + footer).encode())
print(f"Final: {secureSocket.recv(1024).decode().strip()}")

# --- 6. QUIT ---
send_cmd(secureSocket, "QUIT", "221")
secureSocket.close()