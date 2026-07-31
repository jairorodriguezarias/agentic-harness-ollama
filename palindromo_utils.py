def es_palindromo(texto):
    """
    Verifica si una cadena de texto es un palíndromo, 
    ignorando espacios y mayúsculas/minúsculas.

    Args:
        texto (str): La cadena a verificar.

    Returns:
        bool: True si es palíndromo, False en caso contrario.
    """
    # 1. Convertir a minúsculas para ignorar el case.
    texto_lower = texto.lower()
    
    # 2. Eliminar todos los espacios.
    texto_sin_espacios = texto_lower.replace(" ", "")
    
    # NOTA: Si se deseara eliminar también puntuación (ej. puntos, comas), 
    # sería necesario usar una librería como 're' o filtrar caracteres alfabéticos/numéricos.
    # Pero siguiendo la instrucción estricta ("ignora espacios y mayúsculas/minúsculas"),
    # solo manejamos espacios y case.

    # 3. Comprobar si la cadena es igual a su reverso.
    return texto_sin_espacios == texto_sin_espacios[::-1]

if __name__ == '__main__':
    print(f"'A man, a plan, a canal: Panama' -> {es_palindromo('A man, a plan, a canal: Panama')}") # Nota: El ejemplo clásico incluye puntuación. 
                                                                                                  # Si se mantiene el filtrado solo de espacios, el resultado será 'amanaplanacanalpanama' que es falso si usamos la versión original con comas/puntos.
    print(f"'radar' -> {es_palindromo('radar')}")
    print(f"'Hola mundo' -> {es_palindromo('Hola mundo')}")
    print(f"'Race Car' -> {es_palindromo('Race Car')}")