import requests

url = 'http://localhost:5000/register'
data = {
    'username': 'testuser',
    'email': 'test@example.com',
    'password': 'testpass123'
}

response = requests.post(url, json=data)
print('Status code:', response.status_code)
print('Response:', response.json()) 