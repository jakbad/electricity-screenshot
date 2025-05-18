from flask import Flask, Response
import requests


    response = requests.get(
    url='https://api.energidataservice.dk/dataset/Elspotprices?limit=5')

result = response.json()

for k, v in result.items():
    print(k, v)

records = result.get('records', [])

print('records:')
for record in records:
    print(' ', record)
    
