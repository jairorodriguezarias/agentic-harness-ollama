import re

def es_palindromo(texto):
    texto = re.sub(r'[\W_]', '', texto).lower()
    return texto == texto[::-1]