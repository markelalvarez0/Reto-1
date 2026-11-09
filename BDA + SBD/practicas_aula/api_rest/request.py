import requests

url = "https://opendata.aemet.es/opendata/api/prediccion/especifica/municipio/diaria/todos"

parametros = {
    "api_key": "eyJhbGciOiJIUzI1NiJ9.eyJzdWIiOiJtYXJrZWxhYWx2YXJlekBnbWFpbC5jb20iLCJqdGkiOiIxNGEwMzRjMC04NmVhLTQ5MzAtOWU0MC1hODJlYjVhY2QzYzEiLCJleHAiOjE3OTc3NzY2ODUsImlzcyI6IkFFTUVUIiwiaWF0IjoxNzg5MTM2Njg1LCJ1c2VySWQiOiIxNGEwMzRjMC04NmVhLTQ5MzAtOWU0MC1hODJlYjVhY2QzYzEiLCJyb2xlIjoiIn0.ZfRk7hCoRr32v_wrvOQ3uRFAhBGRQetfvIJgqVYr0m4"
}

respuesta = requests.get(url, params=parametros)
datos = respuesta.json

campo_dato = datos

print("Status:", respuesta.status_code)
print(respuesta.text)