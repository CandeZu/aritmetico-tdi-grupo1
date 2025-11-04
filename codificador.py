import sys
import os
import copy #Copias de estructuras profundas
from struct import * # para empaquetar y desempaquetar datos binarios

cantCaract=1400 #Cantidad de caracteres que se van a procesar por bloque
archivo="beemovie.txt" 
maxPotencia= (2**13) #Lim superior del rango de codificacion
prec=7 #precision (que redondea las probabilidades a enteros)


#Convierte las frecuencias de los símbolos en intervalos acumulativos proporcionales
def intervalos(frecInc,totalCarac): #diccionario de frecuencias y el total de caracteres contados
    limInf=0
    interv={}
    for symbol, frecuencia in frecInc.items(): #se recorre cada símbolo y su frecuencia
        if frecuencia==0:
            continue #para saltear los símbolos con frecuencia 0
        limSup=round(limInf+frecuencia/totalCarac * 10 ** prec) #calcula lim sup
        interv[symbol]=(limInf,limSup) #lo guarda en el diccionario
        limInf=limSup
    return interv #Devuelve el diccionario con los intervalos finales



def codificacion(frecInc, totalCarac): #frecuencias iniciales y el total de caracteres contados
    frecuenciasActuales = copy.deepcopy(frecInc) #Se crea una copia de las frecuencias para reducirlas sin modificar las actuales
    acumulado = totalCarac #se va a ir disminuyendo este
    rangoInfe = 0
    rangoSupe = (1 << maxPotencia) - 1 #establece el límite superior del intervalo de codificación, que sería de 8192 bits técnicamente
    #rangoSupe = (2 ** maxPotencia) - 1  
    
    #variables de control 
    bufferTexto = "" #bloque de texto actual
    sigueLeyendo = True 
    resultadosCodificados = [] #lista donde se guarda el código resultante de cada bloque
    bufferBytes = b'' #almacena bytes incompletos


    with open(archivo, 'rb') as archAcompr:     
        while sigueLeyendo:
            byteLeido = archAcompr.read(1)    
            if not byteLeido:
                sigueLeyendo = False
            byteLeido = bufferBytes  + byteLeido 
            #Lee el archivo byte a byte, si no llegara a haber más pum corta el bucle   
            try:
                bufferTexto += byteLeido.decode("utf-8")
                bufferBytes  = b'' 
                if len(bufferTexto) < cantCaract and sigueLeyendo:
                    continue
                tablaRangos = intervalos(frecuenciasActuales, acumulado)
                suma_rangos_escalados = sum(high - low for low, high in tablaRangos.values())
                for caracter in bufferTexto:
                    try:
                        frecuenciasActuales[caracter] -= 1
                        acumulado -= 1
                    except KeyError:
                        print(f"Error: Carácter no encontrado o agotado en el bloque: {bufferTexto}")
                    simbRangoBajo, simbRangoAlto = tablaRangos[caracter]
                    anchoRangoActual =rangoSupe-rangoInfe+1
                    rangoSupe= rangoInfe+(anchoRangoActual * simbRangoAlto // suma_rangos_escalados)-1 
                    rangoInfe= rangoInfe+(anchoRangoActual * simbRangoBajo // suma_rangos_escalados)           
                bufferTexto = ""
                resultadosCodificados.append(rangoInfe) #aca se guarda el comprimido
                rangoInfe  = 0
                rangoSupe = (1 << maxPotencia) - 1
            except UnicodeDecodeError:
                bufferBytes  = byteLeido
            #básicamente esta parte del try lee el bloque dps calcual los intervalos
            #y debería reducir el rango según cada símbolo, dps al final guarda el valor del rango inferior como el código comprimido del bloque
    return resultadosCodificados


def analizar_archivo():
    diccionario_frecuencias = {}
    total_caracteres = 0
    byte_buffer = b''
    
    # Abrimos el archivo en modo binario para leer byte a byte
    with open(archivo, 'rb') as input_stream:
        while True:
            # Leer un byte a la vez
            chunk = input_stream.read(1)
            
            if not chunk:
                break
            
            # Acumular bytes para manejar caracteres UTF-8 multi-byte
            chunk = byte_buffer + chunk
            
            try:
                caracter = chunk.decode("utf-8")
                byte_buffer = b''
                
                # Contar la frecuencia del carácter
                diccionario_frecuencias[caracter] = diccionario_frecuencias.get(caracter, 0) + 1
                total_caracteres += 1

            except UnicodeDecodeError:
                byte_buffer = chunk

    # Ordenamos por frecuencia descendente
    sorted_frequencies = sorted(diccionario_frecuencias.items(), key=lambda item: item[1], reverse=True)
    
    frecuencias_ordenadas = {}
    # Reconstruimos el diccionario ordenado
    for char, freq in sorted_frequencies:
        frecuencias_ordenadas[char] = freq
    
    return frecuencias_ordenadas, total_caracteres - 1

def guardar_archivo(encoded_list, tabla_frecuencias, total_count):
    with open("comprimido.cmp", "wb") as archivo_salida:
        # Escribir metadatos
        archivo_salida.write(pack("iiiiii", prec, cantCaract, maxPotencia, 
                              total_count, len(tabla_frecuencias), len(encoded_list)))
        
        # Calcular tamaños de datos
        freq_byte_size = sys.getsizeof(list(tabla_frecuencias.values())[0])
        code_byte_size = sys.getsizeof(encoded_list[0])
        
        # Escribir tamaños de datos
        archivo_salida.write(freq_byte_size.to_bytes(1, "big"))
        archivo_salida.write(code_byte_size.to_bytes(4, "big"))
        
        # Escribir tabla de frecuencias
        for simbolo, conteo in tabla_frecuencias.items():
            archivo_salida.write(simbolo.encode("utf-8"))
            archivo_salida.write(conteo.to_bytes(freq_byte_size, "big"))

        # Escribir códigos comprimidos
        for code_value in encoded_list:
            archivo_salida.write(code_value.to_bytes(code_byte_size, "big"))

def main():
    # Proceso principal
    frecuencias_acumuladas, total_caracteres = analizar_archivo()
    codigos_comprimidos = codificacion(frecuencias_acumuladas, total_caracteres)
    guardar_archivo(codigos_comprimidos, frecuencias_acumuladas, total_caracteres)

    print(f"Tamaño original: {os.path.getsize(archivo)} bytes")
    print(f"Tamaño comprimido: {os.path.getsize('comprimido.cmp')} bytes")
    print("Porcentaje compresión: "
          f"{(1 - os.path.getsize('comprimido.cmp') / os.path.getsize(archivo)) * 100:.2f}%")

if __name__ == "__main__":
    main()
