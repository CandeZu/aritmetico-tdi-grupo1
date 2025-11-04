Descripción general

Este proyecto implementa un sistema de compresión y descompresión de texto utilizando el algoritmo de Codificación Aritmética.
Consta de dos programas:
codificador.py en el cual se comprime el archivo de texto original.
decodificador.py en el cual se descomprime  el texto original a partir del archivo comprimido.

Bibliotecas utilizadas

sys: Permite obtener información del entorno del sistema, en este programa se usa lo principalmente para determinar el tamaño en bytes de ciertos objetos con sys.getsizeof() durante la creación del archivo comprimido.
os: Se lo usa específicamente para obtener e ltamaño de los archivos y calcular el porcentaje de compresión mostrado en consola.
copy: Permite realizar copias profundas de estructuras de datos complejas y se lo utiliza para poder preservar el original.
struct: Se lo utiliza para empaquetar y desempaquetar datos binarios al guardar y leer el archivo .cmp

Funcionamiento General

El codificador analiza el archivo original, calcula las frecuencias de los caracteres y divide el texto en bloques,
para cada bloque genera intervalos proporcionales a las frecuencias y reduce progresivamente un rango numérico hasta obtener
un valor único que representa todo el bloque, luego guarda en u narchivo binario (comprimido.cmp) los parámetros usados, la tabla
de frecuencias y los códigos resultantes, en consola debería salir "Tamaño original: Tamaño comprimido:" y el porcentaje de compresión.
Para el caso del decodificador, se realizaría el proceso inverso, lee ese archivo comprimido, reconstruye los intervalos y utilizando
los códigos numéricos recupera los caracteres originales bloque por bloque, generando así el rachivo "texto_decodifcado.txt" idéntico
al original. En este caso, el archivo original que se utilizó es un archivo .txt llamado "beemovie".


