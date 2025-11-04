import struct
import copy

precision = 0 
cant_caracteres_por_bloque = 0
#archivo de entrada original 
archivo = "beemovie.txt" 
potencia_maxima = 0

def crear_intervalos(frecuencias_actuales, total_simbolos_restantes):
    """
    Crea los rangos (intervalos) para cada símbolo basados en sus frecuencias
    actuales. Escala las probabilidades a un rango entero usando 'precision'.
    
    (Esta función debe ser IDÉNTICA a la del codificador)
    """
    intervalos = {}
    limite_inferior_acumulado = 0
    
    escala = 10 ** precision

    for simbolo, frecuencia in frecuencias_actuales.items():
        if frecuencia == 0:
            continue
        
        ancho_simbolo = (frecuencia / total_simbolos_restantes) * escala
        limite_superior = round(limite_inferior_acumulado + ancho_simbolo)
       
        intervalos[simbolo] = (limite_inferior_acumulado, limite_superior)
        limite_inferior_acumulado = limite_superior
        
    return intervalos

def decodificar(lista_codigos, frecuencias_iniciales, longitud_total):
    #Decodifica la lista de códigos para reconstruir el texto original,
    #usando el mismo modelo adaptativo que el codificador.

    
    # Crea una copia de las frecuencias para el modelo adaptativo
    frecuencias_actuales = copy.deepcopy(frecuencias_iniciales)
    simbolos_restantes = longitud_total 
    texto_decodificado = ""
    
    simbolos_decodificados = 0
   
    # procesa cada código (un bloque)
    for codigo_bloque in lista_codigos:
        
        # 1. Reinicia el Rango Principal
        # El rango [low, high] debe ser el mismo que al inicio de cada
        # bloque en el codificador.
        rango_superior = (1 << potencia_maxima) - 1
        rango_inferior = 0
        
        # 2. Recrea los Intervalos
        # Crea los intervalos con las frecuencias actuales (modelo adaptativo)
        intervalos = crear_intervalos(frecuencias_actuales, simbolos_restantes)
        # Calcula la suma total de los rangos escalados (ej. 10,000,000)
        suma_frecuencias_escaladas = sum(intervalos[s][1]-intervalos[s][0] for s in intervalos)
        
        for _ in range(cant_caracteres_por_bloque):
            
            # Si ya decodificamos todos los símbolos, salimos
            # (Importante para el último bloque, que puede ser más corto)
            if simbolos_decodificados > longitud_total:
                break
                
            # 3. "Traduce" el código al rango de frecuencias
            ancho_rango_actual = rango_superior - rango_inferior + 1 
           
            # Convierte el 'codigo_bloque' (que está en el rango [rango_inferior, rango_superior])
            # a un 'valor_escalado' (que está en el rango [0, suma_frecuencias_escaladas])
            valor_escalado = ((codigo_bloque - rango_inferior + 1) * suma_frecuencias_escaladas - 1) // ancho_rango_actual

            # 4. Encuentra el Símbolo
            # Busca en qué intervalo [low, high) de símbolo cae el valor escalado
            for simbolo, (simbolo_inf, simbolo_sup) in intervalos.items():
                
                if simbolo_inf <= valor_escalado < simbolo_sup:
                    # Se encontró el símbolo
                    texto_decodificado += simbolo
                    
                    # 5. Actualiza el Modelo Adaptativo (IDÉNTICO AL CODIFICADOR)
                    simbolos_restantes -= 1
                    frecuencias_actuales[simbolo] -= 1
            
                    # 6. Achica el rango [low, high] para que coincida con el
                    # sub-intervalo del símbolo que acabamos de encontrar.
                    rango_superior = rango_inferior + (ancho_rango_actual * simbolo_sup // suma_frecuencias_escaladas) - 1
                    rango_inferior = rango_inferior + (ancho_rango_actual * simbolo_inf // suma_frecuencias_escaladas)
                    
                    simbolos_decodificados += 1
                    
                    # Rompe el bucle de búsqueda de símbolo y pasa al siguiente
                    break 
                    
    return texto_decodificado

def leer_archivo():
    """
    Lee el archivo comprimido (.cmp), extrae el encabezado, la tabla
    de frecuencias y los códigos, y luego llama a decodificar.
    """
    
    with open("comprimido.cmp","rb") as file:
        
        # 1. Lectura del Encabezado 
        # Lee los 6 enteros (24 bytes)
        datos_globales = struct.unpack("iii",file.read(12)) # Lee los primeros 3 (precision, cantchar, potencia)
        longitud_total = struct.unpack("i",file.read(4))[0] # Lee el total
        cantidad_simbolos_alfabeto = struct.unpack("i",file.read(4))[0] # Lee la cantidad de símbolos
        cantidad_total_codigos = struct.unpack("i",file.read(4))[0] # Lee la cantidad de códigos

        # Lee los tamaños de bytes (determinados por sys.getsizeof en el encoder)
        bytes_por_frecuencia = int.from_bytes(file.read(1),"big")
        bytes_por_codigo = int.from_bytes(file.read(4),"big")
        
        # Guarda las variables globales
        global precision 
        global cant_caracteres_por_bloque
        global potencia_maxima
        
        precision = datos_globales[0]
        cant_caracteres_por_bloque = datos_globales[1]
        potencia_maxima = datos_globales[2]
        
        # 2. Lectura de la Tabla de Frecuencias 
        contador_simbolos = 0
        frecuencias_iniciales = {}
        buffer_bytes = b""
        seguir_leyendo = True
        
        while seguir_leyendo :
            try:
                # Lee un byte a la vez para formar el símbolo UTF-8
                byte_leido = file.read(1)

                byte_leido = buffer_bytes + byte_leido
                simbolo = byte_leido.decode()
                
                # Si la decodificación tiene éxito, limpia el buffer y lee la frecuencia
                buffer_bytes = b''
                contador_simbolos += 1
                frecuencia_simbolo = int.from_bytes(file.read(bytes_por_frecuencia))
                
                frecuencias_iniciales[simbolo] = frecuencia_simbolo
                
                # Si ya leímos todos los símbolos del alfabeto, paramos
                if contador_simbolos == cantidad_simbolos_alfabeto:
                    seguir_leyendo = False
            except UnicodeDecodeError:
                # El byte estaba incompleto, lo guarda para la próxima iteración
                buffer_bytes = byte_leido 
        
        # 3. Lectura de los Códigos 
        lista_codigos = []
        
        for _ in range(cantidad_total_codigos):
            bytes_leidos = file.read(bytes_por_codigo)
            codigo_bloque = int.from_bytes(bytes_leidos, "big")
            lista_codigos.append(codigo_bloque)
        
    # 4. Decodificación
    texto_decodificado = decodificar(lista_codigos, frecuencias_iniciales, longitud_total)

    # 5. Escritura del archivo final 
    with open("texto_decodificado.txt","w",encoding="utf-8",newline="") as f:
        f.write(texto_decodificado)


leer_archivo()