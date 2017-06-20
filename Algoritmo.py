
# coding: utf-8

# ## Clasificación de documentos:

# # Calculo del género de una película a raíz de su sinopsis

# ## Parte I: Introducción

# Se requiere la implementación de un algoritmo que a partir de una sinopsis, y previamente entrenado, calcule el __género principal__ de una película en base al conocimiento adquirido.

# Los géneros que tendrá en cuenta el algoritmo son: ___acción___, ___comedia___, ___terror___, ___bélico___ y __western__.

# Los __archivos que contienen la sinopsis__ de las películas (o equivalente, pudiendo ser también un breve resumen de la primera parte de la película) estarán distribuídos de la siguiente forma: __1)__ Si forman parte del conjunto de pruebas estarán dentro de la carpeta del conjunto de prueba sin más, que será la carpeta en la que el algoritmo, una vez entrenado, buscará las sinopsis allí presentes para categorizarlas __2)__ Si forman parte del conjunto de entrenamiento estarán dentro de la carpeta del conjunto de entrenamiento y __a su vez__ dentro de una carpeta que indique su género.

# Inicialmente se planteó utilizar _html_ como __formato__ para almacenar los archivos con los que vamos a trabajar pero, dado que no ha sido posible encontrar una fuente común para extraer todas las sinopsis, finalmente se almacenarán como __texto plano__, trabajando de esta manera con archivos _.txt_.

# __Los conocimientos requeridos por parte del usuario__ que ejecutará el algoritmo __son mínimos__: tan sólo necesita __colocar__ los textos, en el formato adecuado, en la carpeta indicada y __ejecutar__ el algoritmo en sí. Únicamente se requiere mayor interacción por parte del usuario si desea cambiar si desea cambiar las palabras clave, puesto que entonces deberá modificar el fichero "_.csv_" indicado.

# ---

# ## Parte II: Puesta a punto y escaneo

# ### Parte II-A: Puesta a punto

# Empezamos símplemente indicando qué __carpeta__ contiene el __conjunto de entrenamiento__ y el de __prueba__, que por defecto se guardan en las carpetas "*conjunto_entrenamiento*" y "*conjunto_prueba*" respectivamente.

# In[1]:

ruta_conjunto_entrenamiento = "conjunto_entrenamiento"
ruta_conjunto_prueba = "conjunto_prueba"


# Además inicializaremos la ruta en la que se encuentra el __fichero con las palabras clave personalizadas__.

# In[2]:

localización_palabras_clave = "csv/palabras_clave.csv"


# E indicaremos __si queremos usar el auto-generado de palabras clave__ (para las categorías sin palabras clave) y los __umbrales a usar en dicho caso__ (se explican más adelante):

# In[3]:

usar_autogenerado_si_procede = True
umbral_repetición_autogenerado = 6
umbral_longitud_autogenerado = 5


# ### Parte II-B: Escaneo de las categorías

# A continuación, escaneamos la carpeta del conjunto de entrenamiento, que contendrá las __categorías__ en las que se podrán clasificar los nuevos documentos:

# In[4]:

import os # Nos ayudaremos de la librería "os" para leer ficheros y carpetas.

categorías = {elemento for elemento in os.listdir(ruta_conjunto_entrenamiento) if os.path.isdir(ruta_conjunto_entrenamiento + "/" + elemento)} # "os.listdir" devuelve las el contenido de un directorio dado, pero además queremos filtrar que sea un directorio, por eso lo procesamos y le aplicamos el filtro de que sea un directorio.

print("Categorías: %s" % (categorías))


# En la siguiente sección, vamos a recorrer nuestra estructura de carpetas para detectar cada uno de los textos a analizar.

# ### Parte II-C: Escaneo del conjunto de entrenamiento

# Procedemos a __encontrar__ todos los __archivos ya clasificados__ (conjunto de entrenamiento), según su __categoría__.

# Vamos a almacenar todos los archivos según su categoría en un __diccionario__ (llamado *archivos\_entrenamiento\_categoría*), que contrendrá como __clave la categoría y como valor el conjunto de archivos de la categoría__.

# Los valores del diccionario (es decir, en este caso los archivos que pertenecen a esa categoría) estarán contenidos en conjuntos (sets) ya que no nos interesa el orden y, además, no permite duplicados (no puede haber dos archivos con el mismo nombre).

# Además, aprovechamos y almacenamos en el set "*archivos_entrenamiento*" todos los archivos de entrenamiento independientemente de la categoría, para ahorrarnos procesar el diccionario cada vez que queramos acceder a todos los archivos de entrenamiento.

# In[5]:

archivos_entrenamiento = set()
archivos_entrenamiento_categoría = {}

for categoría in categorías:
    conjunto_auxiliar = set()
    
    for fichero in os.listdir(ruta_conjunto_entrenamiento + "/" + categoría):
        if fichero.endswith(".txt"):
            nombre_y_ruta_fichero = categoría + "/" + fichero
            conjunto_auxiliar.add(nombre_y_ruta_fichero)
    
    archivos_entrenamiento.update(conjunto_auxiliar) # Update nos permite añadir el contenido de un set a otro set
    archivos_entrenamiento_categoría[categoría] = conjunto_auxiliar


# Por tanto, para __acceder a todos los archivos__:

# In[6]:

print(archivos_entrenamiento)


# Y para obtener el __número total de archivos__ dentro __del conjunto de entrenamiento__ simplemente ejecutamos la siguiente instrucción:

# In[7]:

print(len(archivos_entrenamiento))


# Para __acceder a los archivos de una categoría__, por ejemplo _acción_, ejecutamos la siguiente orden:

# In[8]:

# Descomentar para comprobar. Por defecto estará comentado para que el algoritmo funcione sin la categoría usada en el ejemplo.
#archivos_entrenamiento_categoría["acción"]


# Para obtener el __número de archivos dentro de una categoría__, ejecutamos:

# In[9]:

# Descomentar para comprobar. Por defecto estará comentado para que el algoritmo funcione sin la categoría usada en el ejemplo.
#len(archivos_entrenamiento_categoría["acción"])


# ### Parte II-D: Escaneo del conjunto de prueba

# Y, por último, procedemos a __encontrar__ los __archivos que querríamos clasificar__ (conjunto de prueba).

# Esta vez no es necesario usar diccionario (no necesitamos separarlos por categorías porque precisamente es lo que queremos hallar), así que usaremos un set por la misma razón por la que lo usamos como valor en el diccionario de los archivos del conjunto de entrenamiento (no queremos repeticiones ni nos interesa el orden).

# In[10]:

archivos_prueba = set()
for fichero in os.listdir(ruta_conjunto_prueba):
    if fichero.endswith(".txt"):
        archivos_prueba.add(fichero)


# Por tanto, la variable "*archivos_prueba*" contendrá el conjunto con los archivos de prueba.

# In[11]:

print(archivos_prueba)


# El número de archivos que tendremos para prueba es de:

# In[12]:

print(len(archivos_prueba))


# ---

# ## Parte III: Elección del conjunto de palabras clave

# Para ayudarnos en el estudio de las __palabras clave__ que debemos escoger para cada categoría vamos a realizar un pequeño estudio para determinar las palabras más frecuentes de cada categoría. La elección en sí, al menos en este caso concreto, vamos a realizarla a mano puesto que no podemos escoger directamente las más frecuentes puesto que con toda probabilidad (y a pesar de las barreras que pondremos, como se verá más adelante) entre las más frecuentes se nos colarán verbos, conectores, preposiciones, pronombres, artículos, nombres propios, etc. que en muchos casos no nos serán de utilidad a la hora de determinar la categoría de una película.

# Debemos definir __método que recibirá__ tanto __un conjunto de archivos__ como una __ruta__ donde se encuentran y __contará las palabras__ que aparecen en él __y el número de veces que dichas palabras aparecen__.

# Pero antes, definiremos un par de métodos que nos será útiles.

# El primero, convertido en método para aportar claridad al código, recibe una palabra y la procesa levemente (la convierte en minúsculas y elimina los carácteres no alfabéticos más típicos) para perder la menor cantidad de información posible (ya que más adelante el algoritmo descartará cualquier palabra que contenga carácteres que no sean alfabéticos).

# In[13]:

def procesa_palabra(palabra):
    palabra = palabra.lower() # Pasamos la palabra a minúscula.
    # Para perder la menor información posible, reemplazamos ':', ',', ':' y ';', que son los carácteres más típicos que nos podemos encontrar adyacentes a una palabra y que la invalidarían en el siguiente if del algoritmo.
    palabra = palabra.replace('.', '')
    palabra = palabra.replace(',', '')
    palabra = palabra.replace(':', '')
    palabra = palabra.replace(';', '')
    
    return palabra


# También definimos un método que reciba un solo archivo y cuente sus palabras. Este metodo será usado por el método que estamos buscando y los dividimos de esta forma porque debemos buscar en un solo archivo cuando apliquemos los algoritmos de Naive Bayes y kNN.

# In[14]:

def cuenta_palabras_desde_archivo(ruta, archivo):
    cuenta_palabras = {}
    
    fichero = open(ruta + "/" + archivo, "r", encoding="latin-1") # Elegimos latin-1 en vez de utf-8 por problemas con las tildes.

    for palabra in fichero.read().split(): # Recorremos el fichero, palabra a palabra.
        palabra = procesa_palabra(palabra)
        if palabra.isalpha() is True: # Será true cuando todos los caracteres son alfabéticos y hay al menos uno.
            if palabra in cuenta_palabras:
                cuenta_palabras[palabra] += 1 # Si la palabra ya existe, entonces incrementa en 1 el número de veces que hace aparición.
            else:
                cuenta_palabras[palabra] = 1 # Si la palabra no existe, la añade (con valor 1 al número de veces que aparece).

    cuenta_palabras
    return cuenta_palabras


# Ahora sí, definimos el método que estamos buscando en este momento y que se anunciaba antes:

# In[15]:

from collections import Counter # Lo usaremos para añadir un diccionario a otro.

def cuenta_palabras_desde_archivos(ruta, archivos):
    cuenta_palabras = {}
    
    for archivo in archivos:
        nuevo = cuenta_palabras_desde_archivo(ruta, archivo)
        cuenta_palabras = dict(Counter(cuenta_palabras)+Counter(nuevo))
    
    return cuenta_palabras


# Además, con propósito de limpiar la salida que obtendremos vamos a establecer un __umbral__ para desechar todas las palabras que se repitan por debajo del mismo:

# In[16]:

umbral_repetición = 4


# Y, con el mismo propósito, otro __umbral__ para desechar todas las palabras con una longitud menor a él:

# In[17]:

umbral_longitud = 4


# Y, por último, un método que use al anterior que, además, nos __ordene las palabras__ (de mayor a menor uso).

# Recordemos que almacenábamos las palabras en __sets__. Esto es un problema a la hora de ordenar, por tanto el método trabajará con una lista (y, a su vez, devolverá una lista).

# In[18]:

def cuenta_palabras_desde_archivos_ordenadas(ruta, archivos):
    cuenta_palabras = cuenta_palabras_desde_archivos(ruta, archivos)
    
    lista_ordenada = [] # Usamos una lista para poder ordenar las palabras.
    for palabra, contador in cuenta_palabras.items():
        lista_ordenada.append((contador, palabra)) # La lista ordenada almacenará una tupla.
    
    lista_ordenada = sorted(lista_ordenada, reverse = True) # Lo ordenamos y lo invertimos para que las palabras más frecuentes estén arriba.
    resultado = lista_ordenada.copy()
    
    for elemento in lista_ordenada:
        if (elemento[0] < umbral_repetición) or (len(elemento[1]) < umbral_longitud): # Si la palabra supera los umbrales indicados, se muestra.
            resultado.remove(elemento)
    
    return resultado


# ### Parte III-A: Elección específica de palabras clave

# Palabras más frecuentes por categoría (FILTRADAS):

# In[19]:

for categoría in categorías:
    print("----- Categoría [%s] -----" % (categoría))
    print(cuenta_palabras_desde_archivos_ordenadas(ruta_conjunto_entrenamiento, archivos_entrenamiento_categoría[categoría]))


# Una vez realizado el estudio, inicializamos manualmente las __palabras clave__ de cada __categoría__, usaremos unas 20 palabras para cada una de ellas (podrán repetirse entre categorías).

# Con __el objetivo__ de que __el usuario necesite entrar en el código lo menos posible__ (a ser posible, que no necesite entrar en el código) vamos a hacer que si quiere elegir sus palabras clave lo haga desde un archivo "_.csv_".

# El siguiente método, que además será utilizado más adelante, leerá un archivo _.csv_ y creará un diccionario a partir de él: la primera "columna" serán las claves y la segunda los valores de dichas claves.

# In[20]:

import csv # Librería que necesitaremos para leer y guardar en formato ".csv".

def lee_fichero(nombre_csv):
    with open(nombre_csv, 'rt', encoding="latin-1") as fichero:
        lector = csv.reader(fichero)
        diccionario = dict(lector)
    
    return diccionario


# El método que se muestra a continuación, se encargará de inicializar las palabras clave de cada categoría a partir de los datos subministrados por el archivo _".csv"_:

# In[21]:

def inicializa_palabras_clave_personalizadas_categoría():
    palabras_clave_categoría = {}
    
    fichero_leído = lee_fichero(localización_palabras_clave)
    
    for categoría in categorías:
        conjunto = set()
        
        cadena_palabras_clave = fichero_leído[categoría].replace(' ', '') # Si el usuario ha insertado espacios entre las comas, los eliminamos.
        cadena_palabras_clave = cadena_palabras_clave.lower()
        conjunto = cadena_palabras_clave.split(",") # Creamos un conjunto separando por coma.
        
        palabras_clave_categoría[categoría] = conjunto
    
    return palabras_clave_categoría


# A continuación, leemos del archivo y extraemos todas las palabras claves de las categorías que tengamos:

# In[22]:

palabras_clave_categoría = inicializa_palabras_clave_personalizadas_categoría()


# Para acceder a las palabras claves de una categoría en concreto, ejecutamos:

# In[23]:

# Descomentar para comprobar. Por defecto estará comentado para que el algoritmo funcione sin la categoría usada en el ejemplo.
#palabras_clave_categoría["acción"]


# ### Parte III-B: Elección automática de palabras clave en base a su frecuencia

# Si para una categoría __no se han añadido palabras clave__, vamos a generarlas automáticamente en base a su frecuencia. Para ello, necesitamos el siguiente método. __NOTA:__ Esto es una medida "de emergencia" ya que está lejos de ser lo más recomendable.

# In[24]:

def genera_palabras_clave(categoría):
    lista_ordenada = cuenta_palabras_desde_archivos_ordenadas(ruta_conjunto_entrenamiento, archivos_entrenamiento_categoría[categoría])
    
    candidatos = lista_ordenada[:20] # Elegimos los 20 primeros elementos de la lista (no olvidemos que obtenemos una tupla).
    
    resultado = [elemento[1] for elemento in candidatos] # De la tupla, nos quedamos con el elemento "1", que contiene la cadena de texto que repesenta la palabra.
    
    return resultado


# Antes de ejecutar el algoritmo para auto-generar las palabras claves, puesto que el resultado carecerá de revisión, vamos a __endurecer los umbrales__ para así asegurarnos, en la medida de lo posible, que las palabras resultantes serán de mayor calidad:

# In[25]:

umbral_repetición = umbral_repetición_autogenerado
umbral_longitud = umbral_longitud_autogenerado


# Ahora es el momento de ejecutar el pequeño algoritmo para auto-generar las palabras clave __si faltan__, para cada categoría:

# In[26]:

contador_categorías_generadas = 0

if usar_autogenerado_si_procede:
    for categoría in categorías:
        if (categoría not in palabras_clave_categoría) or (len(palabras_clave_categoría[categoría]) == 0):
            palabras_clave_categoría[categoría] = genera_palabras_clave(categoría)
            contador_categorías_generadas += 1

print("Se han generado palabras clave de %d categorías automáticamente." % (contador_categorías_generadas))


# ### Parte III-C: Resumen, procesado y estudio de las palabras clave

# Comprobamos las palabras clave de cada categoría:

# In[27]:

print("Palabras clave por categoría:")

for categoría in categorías:
    print("----- Palabras clave de [%s] -----" % (categoría))
    print(palabras_clave_categoría[categoría])


# Y, a continuación, añadimos todas las palabras clave de cada categoría a un nuevo conjunto que contenga __todas las palabras clave__.

# In[28]:

palabras_clave = set()

for categoría in categorías:
    palabras_clave.update(palabras_clave_categoría[categoría]) # Update nos permite añadir el contenido de un set a otro set

print("Las palabras clave son:\n%s" % (palabras_clave))


# Y, antes de acabar, realizaremos un pequeño estudio relacionado con las palabras clave seleccionadas:

# In[29]:

print("Número total de palabras clave: \t %s" % (len(palabras_clave)))
print("Media de palabras clave por categoría (%d categorías): \t %s" % (len(categorías), len(palabras_clave)/len(categorías)))


# ---

# ## Parte IV: Procesamiento

# En esta parte se va a llevar a cabo la generación de los datos pertinentes para posteriormente utilizarlos en los algoritmos de __Naive Bayes__ y __kNN__.

# Puesto que se deben realizar cálculos distintos para cada algoritmo, dividiremos esta sección en dos subsecciones: __Procesamiento de Naive Bayes__ y __Procesamiento de kNN__.

# ### Parte IV-A: Procesamiento de Naive Bayes

# Para aplicar el algoritmo Naive Bayes primero debemos calcular todos los __P(c)__ ___(probabilidad de "c")___ y los __P(t|c)__ ___(probabilidad de "t" condicionada a "c")___.

# En este caso __"c"__ sería nuestra categoría y __"t"__ cada palabra clave.

# Primero, vamos a calcular los __P(c)__. Para ello, tenemos que contar el número de documentos de la categoría en cuestión existentes en nuestro conjunto de entrenamiento y dividirlo entre el número total de documentos de nuestro conjunto de entrenamiento. Así pues, por ejemplo, la probabilidad de acción (__P(acción)__) sería el número resultante de dividir el total de documentos catalogados como "acción" de nuestro conjunto de entrenamiento entre el número total de documentos del conjunto de entrenamiento.

# Como tenemos un conjunto con todos los archivos de entrenamiento y un conjunto específico por cada categoría, realizamos un bucle y por cada categoría generamos su probabilidad:

# In[30]:

probabilidad_categoría = {}

for categoría in categorías:
    probabilidad_categoría[categoría] = len(archivos_entrenamiento_categoría[categoría]) / len(archivos_entrenamiento)
    print("P(%s) = \t %f" % (categoría, probabilidad_categoría[categoría]))


# Sólo para asegurarnos, todas las probabilidades deben sumar __~1__ en este apartado:

# In[31]:

print("Suma de probabilidades (debe ser ~1): \t %f" % (sum([probabilidad_categoría[categoría] for categoría in categorías])))


# Ahora, para calcular los __P(t|c)__ será un poco más complejo. Para llevar a cabo esta tarea haremos uso de __un diccionario por cada categoría__ que a su vez __contendrá otro diccionario dentro__ que __relacionará palabras clave con su probabilidad condicionada a la categoría del diccionario__. De nuevo, tomaremos la categoría "acción" como ejemplo: en "probabilidad_palabraclave['acción']" recogerá, por cada palabra clave, su probabilidad condiccionada a la categoría acción, es decir, su __P(t|acción__), siendo "t" cada entrada del diccionario.

# Pero antes de empezar, definiremos un método, que utilizaremos en los siguientes pasos, que genere cada diccionario deseado como salida y, además, le __aplique un suavizado de LaPlace__:

# In[32]:

def crea_diccionario_probabilidades_condicionadas(archivos_entrenamiento_categoría):
    probabilidades_condicionadas = {}
    cuenta_palabras_categoría = cuenta_palabras_desde_archivos(ruta_conjunto_entrenamiento, archivos_entrenamiento_categoría) # Almacena las palabras clave de la categoría y el número de veces que se repiten.
    
    número_palabras_clave_totales = len(palabras_clave) # Número de palabras clave que poseemos en total.
    número_palabras_clave_categoría = sum(cuenta_palabras_categoría.values())
    
    for palabra_clave in palabras_clave:
        if palabra_clave in cuenta_palabras_categoría:
            número_veces_aparece_palabra_en_categoría = cuenta_palabras_categoría[palabra_clave] # Número de veces que la palabra clave se repite en esta categoría.
        else:
            número_veces_aparece_palabra_en_categoría = 0
        resultado = ((número_veces_aparece_palabra_en_categoría + 1) / (número_palabras_clave_categoría + número_palabras_clave_totales)) # Añadimos 1 en el numerador y el número de palabras claves totales en el denominador para aplicar el suavizado.
        probabilidades_condicionadas[palabra_clave] = resultado
    
    return probabilidades_condicionadas


# También vamos a crear un pequeño método que nos ayude a visualizar las probabilidades condicionadas:

# In[33]:

def mostrar_diccionario_probabilidades_condicionadas(diccionario, categoría):
    for entrada in diccionario:
        print("P(%s|%s) = \t %f" % (entrada, categoría, diccionario[entrada]))


# Ahora, empezamos con el cálculo en sí:

# In[34]:

probabilidad_palabraclave = {}

for categoría in categorías:
    probabilidad_palabraclave[categoría] = crea_diccionario_probabilidades_condicionadas(archivos_entrenamiento_categoría[categoría])
    
    print("----- Categoría: %s -----" % (categoría))
    mostrar_diccionario_probabilidades_condicionadas(probabilidad_palabraclave[categoría], categoría)


# Una vez calculadas todas las probabilidades condicionadas de todas las categorías ya hemos finalizado con este subapartado, pero antes vamos a recordar un par de cosas:

# Para acceder a una probabilidad específica símplemente ejecutamos lo siguiente (para el ejemplo obtendremos la __probabilidad de coche__ condicionada a la categoría __acción__, es decir, __P(coche|acción)__):

# In[35]:

# Descomentar para comprobar. Por defecto estará comentado para que el algoritmo funcione sin la categoría usada en el ejemplo.
#print("P(coche|acción) = %f" % (probabilidad_palabraclave["acción"]["coche"]))


# Si hubiese una __palabra clave que no apareciese en acción, la probabilidad no sería 0__ ya que estamos usando suavizado. Por ejemplo, podemos comprobarlo con la probabilidad de soldado (que no forma parte de las palabras clave de acción) condicionada a acción (__P(gags|acción)__):

# In[36]:

# Descomentar para comprobar. Por defecto estará comentado para que el algoritmo funcione sin la categoría usada en el ejemplo.
#print("P(gags|acción) = %f" % (probabilidad_palabraclave["acción"]["gags"]))


# ### Parte IV-B: Procesamiento de kNN

# Como en este escenario __el orden de las palabras clave sí nos importa__, vamos a asegurarnos y a definir una lista con las palabras clave (creada a partir del conjunto de palabras clave que ya teníamos):

# In[37]:

lista_palabras_clave = list(palabras_clave)

print(lista_palabras_clave)


# También vamos a __crear__ un __diccionario__ que tenga como __clave cada palabras clave__ y como __valor el número de veces que se repiten en documentos distintos__, ya que nos va a ser necesario en el método que definiremos a continuación.

# In[38]:

palabras_clave_frecuencias_documentales = {}

for archivo in archivos_entrenamiento:
    cuenta_palabras = cuenta_palabras_desde_archivo(ruta_conjunto_entrenamiento, archivo)
    
    for palabra in cuenta_palabras:
        if palabra in palabras_clave:
            if palabra in palabras_clave_frecuencias_documentales:
                palabras_clave_frecuencias_documentales[palabra] += 1
            else:
                palabras_clave_frecuencias_documentales[palabra] = 1

print(palabras_clave_frecuencias_documentales)


# Ahora, vamos a definir un __método__ que tenga como entrada una palabra clave y un archivo (y su ruta) y __calcule el peso para esa palabra clave y ese documento__.

# In[39]:

def calculo_peso(palabra_clave, ruta, archivo):
    #print("Peso para la palabra clave: %s y el archivo: %s" % (palabra_clave, archivo))
    frecuencia_en_documento = 0
    frecuencia_documental = 0
    frecuencia_documental_inversa = 0
    peso = 0
    
    cuenta_palabras = cuenta_palabras_desde_archivo(ruta, archivo)
    if palabra_clave in cuenta_palabras:
        frecuencia_en_documento = cuenta_palabras[palabra_clave]
    
    frecuencia_documental = palabras_clave_frecuencias_documentales[palabra_clave]
    
    frecuencia_documental_inversa = math.log((len(archivos_entrenamiento) / frecuencia_documental), 10)
    
    peso = frecuencia_en_documento * frecuencia_documental_inversa
    
    #print("Frecuencia en documento: %s" % (frecuencia_en_documento))
    #print("Frecuencia documental: %s" % (frecuencia_documental))
    #print("Frecuencia documental inversa: %s" % (frecuencia_documental_inversa))
    #print("Peso: %s" % (peso))
    
    return peso


# A continuación, un __método__ que reciba __como entrada un conjunto de archivos__ y __calcule sus pesos__ (devolverá una lista).

# In[40]:

def calculo_pesos(ruta, archivo):
    lista_pesos = []
    
    for palabra_clave in lista_palabras_clave:
        lista_pesos.append(calculo_peso(palabra_clave, ruta, archivo))
    
    return lista_pesos


# Ahora es momento de usar lo que hemos definido anteriormente, vamos a crear un __diccionario__ ("*diccionario_palabraclave_pesos*") que __por cada archivo del conjunto de entrenamiento__ (clave del diccionario) contenga __una lista de pesos__ de cada palabra (valor de la clave del diccionario).

# In[41]:

import math

diccionario_palabraclave_pesos = {}

for archivo in archivos_entrenamiento:
    lista_pesos_archivo = calculo_pesos(ruta_conjunto_entrenamiento, archivo)
    
    diccionario_palabraclave_pesos[archivo.replace(".txt", "")] = lista_pesos_archivo

#print(diccionario_palabraclave_pesos)


# ---

# ## Parte V: Salvado del procesamiento en fichero

# Dado que el enunciado de la práctica requiere que guardemos el procesado que acabamos que realizar (en la parte IV) para después utilizarlo en la ejecución de los algoritmos, procedemos a ello.

# ### Parte V-A: Salvado del procesamiento de Naive Bayes

# El objetivo aquí es que el usuario pueda abrir el archivo "*.csv*" y lo entienda, por ello vamos a guardar en la primera columna de dicho "*.csv*" (es decir, en el primer valor) cada probabilidad, y lo haremos como "***P(categoría)***" o "***P(palabra|categoría)***" y en la segunda columna, su valor.

# Para ello, como tenemos cada probabilidad en un diccionario distinto, vamos a crear un nuevo diccionario que contenga todas las probabilidades:

# In[42]:

diccionario_probabilidades_a_guardar = {}

for categoría in categorías:
    diccionario_probabilidades_a_guardar["P(" + categoría + ")"] = probabilidad_categoría[categoría]
    
    for entrada in probabilidad_palabraclave[categoría]:
        diccionario_probabilidades_a_guardar["P(" + entrada + "|" + categoría + ")"] = probabilidad_palabraclave[categoría][entrada]


# Y a continuación procedemos al guardado:

# In[43]:

fichero_csv = "csv/naive-bayes.csv"
datos_a_guardar = diccionario_probabilidades_a_guardar

with open(fichero_csv, "w") as output:
    writer = csv.writer(output, lineterminator='\n')
    for dato in datos_a_guardar:
        writer.writerow([dato] + [datos_a_guardar[dato]])


# ### Parte V-B: Salvado del procesamiento de kNN

# El salvado de kNN es mucho más fácil, sólo tenemos que guardar el diccionario que generamos en la parte anterior: El primer valor del "*.csv*" sería la clave del diccionario (el __nombre del documento__) y el segundo su valor (la __lista de pesos para cada palabra__).

# In[44]:

fichero_csv = "csv/knn.csv"
datos_a_guardar = diccionario_palabraclave_pesos

with open(fichero_csv, "w") as output:
    writer = csv.writer(output, lineterminator='\n')
    for dato in datos_a_guardar:
        writer.writerow([dato] + [datos_a_guardar[dato]])


# ---

# ## Parte VI: Ejecución de los algoritmos

# En la parte II ya encontramos los ficheros del conjunto de test, que están en su respectiva carpeta, ahora tenemos que procesaros igual que hicimos en la parte III con los ficheros del conjunto de pruebas.

# ### Parte VI-A: Ejecución de Naive Bayes

# El método naive_bayes recibe un archivo y los datos procesados (probabilidades) como parámetros y determina la categoría del archivo pasado como parámetro.

# In[45]:

def naive_bayes(archivo, csv):
    cuenta_palabras = cuenta_palabras_desde_archivo(ruta_conjunto_prueba, archivo)
    
    palabras_coincidentes_con_palabras_clave = cuenta_palabras.copy()
    
    # De las palabras que contiene el fichero, desechamos todas las que no coinciden con las palabras clave.
    for palabra in cuenta_palabras:
        if palabra not in palabras_clave:
            del palabras_coincidentes_con_palabras_clave[palabra]
    
    # Abrimos el fichero ".csv" generado para consultar datos en el siguiente paso.
    datos = lee_fichero(csv)
    
    # Ejecutamos el algoritmo en sí.
    candidatos = {} # "candidatos" será un diccionario que contendrá la categoría y la "puntuación" otorgada por el algoritmo a esa categoría (para posteriormente elegir la categoría con el máximo valor).
    
    for categoría in categorías:
        probabilidades_condicionadas_a_multiplicar = []
        for palabra_clave in palabras_coincidentes_con_palabras_clave:
            cadena_a_buscar = "P(" + palabra_clave + "|" + categoría + ")" # Define la cadena que se debe buscar en el archivo. En este caso la probabilidad condicionada a la categoría.
            probabilidades_condicionadas_a_multiplicar.append(float(datos[cadena_a_buscar]) ** palabras_coincidentes_con_palabras_clave[palabra_clave]) # Busca el valor de la probabilidad condicionada requerida (lo transforma en float), lo eleva al número de veces que se repite y añade el valor de la probabilidad condicionada hallada a una lista que se pasará a multiplicar después.
        
        cadena_a_buscar = "P(" + categoría + ")" # Define la cadena que se debe buscar en el archivo. En este caso la probabilidad de la categoría.
        probabilidad_categoría = float(datos[cadena_a_buscar])
        
        # Multiplicamos los elementos de la lista de probabilidades condicionadas
        probabilidades_condicionadas_multiplicadas = 1.0
        for elemento in probabilidades_condicionadas_a_multiplicar:
            probabilidades_condicionadas_multiplicadas = probabilidades_condicionadas_multiplicadas * elemento
        
        candidatos[categoría] = probabilidades_condicionadas_multiplicadas * probabilidad_categoría # Calcula el coeficiente
        # Descomentar para obtener más detalles de la puntuación da cada categoría:
        #print("Para la categoría %s obtenemos una puntuación de: %f" % (categoría, resultados[categoría]))
    
    resultado = max(candidatos, key=candidatos.get) # Devuleve el resultado del algoritmo. En este caso el elemento del diccionario con mayor coeficiente.
    
    return resultado, candidatos


# __Ejecutamos el algoritmo__ e __imprimimos__ los __resultados__ obtenidos:

# In[46]:

def aplicar_naive_bayes_archivos_prueba():
    print("El resultado de aplicar el algoritmo [Naive-Bayes] al conjunto de pruebas es...")
    for archivo in archivos_prueba:
        algoritmo = naive_bayes(archivo, "csv/naive-bayes.csv")
        print("[%s] \t [%s]" % (archivo.replace(".txt", ""), algoritmo[0]))
        print("Puntuaciones: %s" % (algoritmo[1]))
        print("-------------------------")


# In[47]:

aplicar_naive_bayes_archivos_prueba()


# ### Parte VI-B: Ejecución de kNN

# El siguiente método, "*calcula_distancia*", recibe como parámetros dos listas de pesos, comprueba si tienen el mismo tamaño y aplica la fórmula de similitud a ambas listas. Cada elemento de la lista está relacionado con una palabra clave (y las palabras clave mantienen posición entre las listas, es decir, el elemento 1 de la lista 1 es el peso de la misma palabra que el elemento 1 de la lista 2).

# In[48]:

def calcula_distancia(v, w):
    # Comprueba que las listas de pesos son del mismo tamaño, por seguridad.
    if(len(v) == len(w)):
        numerador = sum([elemento_v * elemento_w for elemento_v, elemento_w in zip(v,w)])
        
        denominador = (math.sqrt(sum([elemento_v ** 2 for elemento_v in v]))) * (math.sqrt(sum([elemento_w ** 2 for elemento_w in w])))
        
        return numerador / denominador


# A continuación, creamos un método utilidad para calcular los __k__ elementos con mayor valor de un diccionario.

# In[49]:

def k_maximos(diccionario, k):
    resultado = {}
    
    for i in range(k):
        maximo = max(diccionario, key=diccionario.get)
        resultado[maximo] = diccionario[maximo]
        del diccionario[maximo]
    
    return resultado


# El siguiente método es el algoritmo __kNN__ en sí. Recibe un documento, los datos procesados de la parte IV y un valor de __k__ y determina a qué categoría pertenece un documento.

# In[50]:

def knn(archivo, csv, k):
    v = calculo_pesos(ruta_conjunto_prueba, archivo)
    #print(v)
    
    # Abrimos el fichero ".csv" generado para consultar datos en el siguiente paso.
    datos = lee_fichero(csv)
    
    # Ejecutamos el algoritmo en sí.
    documento_similitud = {} # documento_similitud será un diccionario que contendrá el archivo y la "puntuación" (similitud) otorgada por el algoritmo a esa categoría (para posteriormente elegir la categoría del archivo con la similitud más cercana a uno, que será el mayor valor).
    
    # Ahora que tenemos el peso del archivo a clasificar mediante el algoritmo y los pesos de los archivos del conjunto de entrenamiento (extraídos del ".csv" y guardados en forma de diccionario) tenemos que calcular, una por una, la distancia a cada elemento del conjunto de entrenamiento y quedarnos con la menor.
    for dato in datos:
        # Como lo que guardamos es una cadena, es necesario un pequeño procesamiento para transformarlo de nuevo en una lista.
        w = datos[dato].replace('[', '') # Primero eliminamos "[".
        w = w.replace(']', '') # Hacemos lo mismo con "]".
        w = w.split(",") # Aplicamos ".split()" para volver a "trocear" la cadena y convertirla de nuevo en una lista.
        w = [float(elemento) for elemento in w]
        documento_similitud[dato] = calcula_distancia(v, w) # "v" son los pesos del archivo a clasificar y "w" los del archivo del conjunto de entrenamiento que está siendo procesado.
    
    k_documentos_similitud = k_maximos(documento_similitud, k)
    #print(k_documentos_similitud)
    
    # Para hallar la categoría más repetida y gestionar los desempates haremos lo siguiente:
    # La clave del diccionario será un string: la categoría.
    # El valor un entero: el número de veces que se repite la categoría (para elegir la mayor, si no hay empate).
    
    candidatos_repetición = {}
    
    for elemento in k_documentos_similitud:
        género_documento = elemento.split("/") # "género_documento" guarda "género/nombre_documento", por ejemplo "acción/El caso bourne".
        género = género_documento[0]
        if género not in candidatos_repetición:
            #candidatos[género] = (1, k_documentos_similitud[elemento])
            candidatos_repetición[género] = 1
        else:
            #candidatos[género] = (candidatos[género][0] + 1, k_documentos_similitud[elemento] + candidatos[género][1])
            candidatos_repetición[género] = candidatos_repetición[género] + 1
    
    #print(candidatos_repetición)
    
    # Hallamos el máximo número de veces que una categoría se repite
    elemento_máxima_repetición = max(candidatos_repetición, key=candidatos_repetición.get)
    #print(elemento_máxima_repetición)
    máxima_repetición = candidatos_repetición[elemento_máxima_repetición]
    #print(máxima_repetición)
    
    # Ahora toca repetir un bucle similar. Esta vez vamos a excluir todos los elementos que no tengan la máxima repetición.
    # Entre los elementos con máxima repetición, nos quedamos con la categoría cuyos elementos sumen más similitud.
    # La clave del diccionario volverá a ser un string, y de nuevo almacenará la categoría.
    # Esta vez el value será un decimal (float): la suma de las similitudes (para elegir la mayor si hay empate).
    
    candidatos_suma_similitudes = {}
    
    for elemento in k_documentos_similitud:
        género_documento = elemento.split("/") # "género_documento" guarda "género/nombre_documento", por ejemplo "acción/El caso bourne".
        género = género_documento[0]
        if candidatos_repetición[género]== máxima_repetición:
            if género not in candidatos_suma_similitudes:
                candidatos_suma_similitudes[género] = k_documentos_similitud[elemento]
            else:
                candidatos_suma_similitudes[género] = candidatos_suma_similitudes[género] + k_documentos_similitud[elemento]
    
    #print(candidatos_suma_similitudes)
    
    # Hallamos la(s) categoría(s) que más se repiten
    resultado = max(candidatos_suma_similitudes, key=candidatos_suma_similitudes.get)
    
    # Para una mayor exactitud, saber en qué categoría se enmarcará la muestra y a qué película se debe devolvemos ambos datos (el elemento 0 contendrá la categoría y el 1 la película de dónde procede).
    return resultado, k_documentos_similitud


# Elegimos un valor para __k__ (podemos hacerlo en la llamada a la función, pero para hacerlos más visual):

# In[51]:

k = 5 # Importante, "k" no puede ser mayor que el conjunto de prueba.


# Y __ejecutamos el algoritmo__ e __imprimimos__ los __resultados__ obtenidos:

# In[52]:

def aplicar_knn_archivos_prueba():
    print("El resultado de aplicar el algoritmo [kNN] con [k=%d] (%dNN) al conjunto de pruebas es..." % (k, k))
    for archivo in archivos_prueba:
        algoritmo = knn(archivo, "csv/knn.csv", k)
        print("[%s] \t [%s]" % (archivo.replace(".txt", ""), algoritmo[0]))
        print("Similitudes: %s" % (algoritmo[1]))
        print("-------------------------")


# In[53]:

aplicar_knn_archivos_prueba()


# ---

# ## Parte VII: Análisis de los resultados

# La siguiente tabla muestra la relación entre el __documento a clasificar__ del conjunto de pruebas, su __género real__ y los __géneros en los que ha sido clasificado__ mediante __Naive Bayes__ y un __valor bajo de kNN__ (1) y __un valor un poco más elevado__ (5) y, finalmente, con uno __mucho más elevado__ (12).

# \begin{array}{|r|c|c|c|c|c|} \hline
# \textbf{Nombre del documento}&\textbf{Género REAL}&\textbf{Género Naive Bayes}&\textbf{Género 1NN}&\textbf{Género 5NN}&\textbf{Género 12NN}\\ \hline
# A \: todo \: gas - Tokyo \: race&\textbf{Acción}&Acción&Acción&Acción&Acción\\ \hline
# Apocalipsis \: now&\textbf{Bélico}&Bélico&Western&Bélico&Bélico\\ \hline
# Django \: desencadenado&\textbf{Western}&Western&Western&Western&Western\\ \hline
# El \: gran \: dictador&\textbf{Comedia / Bélico}&Comedia&Bélico&Comedia&Comedia\\ \hline
# El \: jinete \: pálido&\textbf{Western}&Western&Acción&Acción&Terror\\ \hline
# El \: padrino&\textbf{Drama}&Western&Acción&Terror&Western\\ \hline
# El \: tirador&\textbf{Acción}&Acción&Acción&Acción&Acción\\ \hline
# El \: ultimátum \: de \: Bourne&\textbf{Acción}&Acción&Acción&Acción&Acción\\ \hline
# Fast \: and \: Furious \: 5&\textbf{Acción}&Acción&Acción&Acción&Acción\\ \hline
# Insidious&\textbf{Terror}&Terror&Terror&Terror&Terror\\ \hline
# It&\textbf{Terror}&Western&Bélico&Western&Western\\ \hline
# Jungla \: de \: cristal&\textbf{Acción}&Acción&Terror&Acción&Acción\\ \hline
# La \: caza \: del \: Octubre \: Rojo&\textbf{Acción / Bélico}&Western&Western&Bélico&Bélico\\ \hline
# La \: chaqueta \: metálica&\textbf{Bélico}&Bélico&Bélico&Bélico&Bélico\\ \hline
# La \: máscara&\textbf{Comedia}&Comedia&Comedia&Comedia&Comedia\\ \hline
# La \: matanza \: de \: Texas&\textbf{Terror}&Terror&Comedia&Terror&Terror\\ \hline
# La \: noche \: de \: los \: muertos \: vivientes&\textbf{Terror}&Western&Terror&Terror&Western\\ \hline
# Le \: llamaban \: Trinidad&\textbf{Western / Comedia}&Western&Western&Western&Western\\ \hline
# Los \: otros&\textbf{Terror}&Bélico&Terror&Bélico&Bélico\\ \hline
# Misión \: imposible - Protocolo \: fantasma&\textbf{Acción}&Acción&Acción&Acción&Acción\\ \hline
# Monstruos\: S.A.&\textbf{Comedia}&Comedia&Comedia&Comedia&Comedia\\ \hline
# Resacón \: en \: las \: Vegas&\textbf{Comedia}&Comedia&Terror&Terror&Terror\\ \hline
# Salvar \: al \: soldado \: Ryan&\textbf{Bélico}&Bélico&Bélico&Bélico&Bélico\\ \hline
# Shrek \: 3&\textbf{Comedia}&Comedia&Comedia&Comedia&Comedia\\ \hline
# Sin \: perdón&\textbf{Western}&Western&Western&Western&Western\\ \hline
# Solo \: ante \: el \: peligro&\textbf{Western}&Western&Western&Western&Western\\ \hline
# Teléfono \: rojo - Volamos \: hacia \: Moscú&\textbf{Bélico / Comedia}&Bélico&Bélico&Bélico&Bélico\\ \hline
# \end{array}

# Nótese que el __género real__ en algunos casos es un poco __ambiguo__ (esto ha sido forzado, eligiendo el conjunto de prueba, puesto que nos parece correcto ver el comportamiento del algoritmo en ese tipo de casos), por lo que si acierta cualquiera de los dos daremos el resultado por correcto.

# Además, si nos fijamos en la tabla, lo primero que nos llama la atención es que la película __"_El padrino_" no pertenece a ninguna de las categorías para las que se realiza el estudio__. Esto es porque se ha insertado en el conjunto de prueba a modo de "trampa" para ver cómo se comportar el algoritmo en estos casos: __Naive Bayes__ y __12NN__ lo categorizan como _Western_, __1NN__ como _Acción_ y __5NN__ como _Terror_. Por lo tanto __apreciamos un comportamiento errático__.

# Teniendo en cuenta esto (descontando 1 al total de categorías por la "trampa" de "_El padrino_") y a partir de la tabla anterior, vamos a realizar un estudio del porcentaje de acierto según el algoritmo aplicado. Para ello, utilizaremos la siguiente fórmula:

# \begin{equation*}
# Porcentaje \: de \: aciertos \: (Algoritmo) = \frac{muestras \: coincidentes \: con \: la \: categoría \: real}{muestras \: totales} * 100
# \end{equation*}

# Porcentaje aciertos algoritmo __Naive Bayes__:

# \begin{equation*}
# Porcentaje \: de \: aciertos \: (Naive \: Bayes) = \frac{22}{26} * 100 = 84.61\%
# \end{equation*}

# Porcentaje aciertos algoritmo __kNN__ con _k=1_ (__1NN__):

# \begin{equation*}
# Porcentaje \: de \: aciertos \: (1NN) = \frac{19}{26} * 100 = 73.07\%
# \end{equation*}

# Porcentaje aciertos algoritmo __kNN__ con _k=5_ (__5NN__):

# \begin{equation*}
# Porcentaje \: de \: aciertos \: (5NN) = \frac{22}{26} * 100 = 84.61\%
# \end{equation*}

# Porcentaje aciertos algoritmo __kNN__ con _k=12_ (__12NN__):

# \begin{equation*}
# Porcentaje \: de \: aciertos \: (12NN) = \frac{21}{26} * 100 = 80.76\%
# \end{equation*}

# Ahora, mirando de nuevo la tabla, vamos a centrarnos en calcular el porcentaje de acierto por categoría. Consideraremos los resultados de 1NN, 5NN y 12NN independientes para el cálculo. Usaremos la siguiente fórmula en este caso:

# \begin{equation*}
# Porcentaje \: de \: aciertos \: (Categoría) = \frac{muestras \: de \: la \: categoría \: coincidentes \: con \: la \: categoría \: real}{muestras \: totales \: que \: deberían \: clasificarse \: en \: la \: categoría} * 100
# \end{equation*}

# Porcentaje aciertos algoritmo __Acción__:

# \begin{equation*}
# Porcentaje \: de \: aciertos \: (Acción) = \frac{23}{24} * 100 = 95.83\%
# \end{equation*}

# Porcentaje aciertos algoritmo __Comedia__:

# \begin{equation*}
# Porcentaje \: de \: aciertos \: (Comedia) = \frac{17}{20} * 100 = 85\%
# \end{equation*}

# Porcentaje aciertos algoritmo __Bélico__:

# \begin{equation*}
# Porcentaje \: de \: aciertos \: (Bélico) = \frac{15}{16} * 100 = 93.75\%
# \end{equation*}

# Porcentaje aciertos algoritmo __Terror__:

# \begin{equation*}
# Porcentaje \: de \: aciertos \: (Terror) = \frac{10}{20} * 100 = 50\%
# \end{equation*}

# Porcentaje aciertos algoritmo __Western__:

# \begin{equation*}
# Porcentaje \: de \: aciertos \: (Western) = \frac{17}{20} * 100 = 85\%
# \end{equation*}

# ---

# ## Parte VIII: Conclusiones

# ### Parte VIII-A: Reseñas del aprendizaje automático

# Recordemos que los algoritmos de __aprendizaje automático__ (o _Machine learning_) intentan categorizar nuevos elementos en base a su experiencia previa con un conjunto de aprendizaje, con el que entrenan, pero __en ningún caso ofrecen una garantía a la hora de clasificar nuevos elementos__: se basan en su experiencia y en base al conjunto de entrenamiento y las palabras claves que hayan sido elegidas el resultado final puede verse alterado drásticamente.

# En cualquier caso, incluso con el mejor escenario (elegido el mejor conjunto de entrenamiento, tanto en tamaño como en contenido, y las palabras clave más correctas) __no ofrecen un acierto del 100%__, puesto que "no" es lo que se pretende con esta clase de algoritmos.

# ### Parte VIII-B: Resultados por clasificador

# Ciñéndonos ahora a los resultados obtenidos en la parte anterior, tanto con __Naive Bayes__ como con __kNN__ con k igual a 1, 5 y 12 __en el peor de los casos nos quedamos cerca del 75% de acierto__, y __en el mejor estamos justo a las puertas del 85%__.

# Teniendo en cuenta lo descrito en los párrafos anteriores, un __~75%__ nos parece un resultado dentro de lo aceptable (aunque mejorable, pero normal si tenemos en cuenta que proviene de 1NN), y un __~85%__ un resultado bastante bueno.

# De entre todos los algoritmos (entendiendo por algoritmos tanto Naive Bayes como kNN con distintos valores), __el que peor se ha comportado con este conjunto de entrenamiento / pruebas / palabras clave ha sido 1NN__ (kNN con k=1) con un __73.07%__ y, por otra parte, __los que mejor se han comportado__, respecto a lo mismo, __han sido Naive Bayes y 5NN__ (kNN con k=5), con un __84.61%__ de aciertos. __12NN__ (kNN con k=12) se queda un poco detrás con un __80.76%__ de aciertos.

# Debemos destacar también que __el algoritmo kNN__, en nuestro caso, se comporta mejor con un __"k" medio__, en este caso con k=5, ya que se obtiene __73.07% con k=1__, __84.61% con k=5__ y un __80.76% con k=12__, por lo que __en mitad de los valores de "k" testeados se aprecia una mejora__, quedando el mejor porcentaje de acierto, como decíamos, en el k intermedio de los que se han probado.

# Aunque no aparece en la tabla, con __valores de "k" muy altos el algoritmo empieza a fallar demasiado__ (con k=70, por ejemplo) incluso categorizando películas en las que antes no tenía problemas.

# Todo lo anterior nos hace pensar que __el valor de "k" idóneo__ en este caso está en la franja de 5 a 12, pero es necesario un estudio más en detalle para comprobar esto de una forma veraz, puesto que puede ser fruto de la casualidad.

# ### Parte VIII-C: Resultados por categoría

# Además, podemos distinguir que algunas categorías se clasifican mejor que otras.

# Cuando el género del documento a categorizar es __Acción__, aplicando Naive Bayes, 1NN, 5NN y 12NN, en un amplio porcentaje (__95.83%__) se categoriza bien. En concreto, de los elementos del conjunto de prueba que sólo están categorizados como _Acción_, únicamente _Jungla de cristal_ con 1NN falla y se categoriza como _Terror_.

# En el género __Terror__ es dónde se presentan las mayores dificultades, ya que en este caso sólo en un __50%__ de las veces se categoriza bien. Esto es un tanto relativo, ya que estamos contando los resultados de 1NN que a priori, según las conclusiones anteriores, es peor que 5NN y 12NN, pero sin dudas es la categoría que sufre más problemas para categorizarse correctamente.

# Los documentos a clasificar de los géneros __Western__ y __Comedia__ el __85%__ de las veces son categorizados correctamente. Lo cuál entra dentro de lo que podríamos considerar un buen resultado.

# Y, por último, los documentos a de __Bélico__ ofrecen un __93.75%__ de acierto. Es algo que se esperaba puesto que pudimos apreciar durante el estudio de las palabras clave por categoría que _Bélico_ es una categoría muy fácil de clasificar, ya que los documentos (sinopsis) de esta categoría tienen unas palabras clave tremendamente específicas, por ejemplo: soldado, general, almirante, etc.

# ### Parte VIII-D: Conclusiones finales

# En general __los algoritmos implementados categorizan correctamente en un porcentaje asumible__, y si no contamos 1NN aún más (ya que es esperable que con 1NN el algoritmo kNN arroje peores resultados que con un valor de k mayor), __superando el 80% de clasificaciones satisfactorias como media__.

# Además, respecto a las __categorización por géneros__, nos encontramos que __todos los documentos a categorizar se categorizan bien__, __exceptuando el género de Terror__ que se queda claramente por debajo. Esto puede deberse a una mala elección de las palabras clave, que el género sea por naturaleza más difícil de clasificar que otros, que haya que ampliar el conjunto de entrenamiento de _Terror_ o una combinación de estas circustancias.

# ---

# ## Parte IX: Referencias

# Para la elaboración del trabajo se ha usado principalmente el material y el conocimiento adquirido en la asignatura y en sus prácticas.

# Además de ello, se han realizado consultas a la documentación de Python y a páginas como _StackOverflow_, para dudas puntuales.

# Las principales consultas son sobre el uso de Python (ya que es la primera asignatura en la carrera donde se nos enseña este lenguaje).

# Una de las pocas excepciones en las que hemos consultado para algo menos básico este tipo de páginas ha podido ser para el recuento de palabras de un fichero o la lectura y escritura de ficheros ".csv", puesto que no sabíamos cómo realizarlos y sí tuvimos que, específicamente, buscar información para ello.

# A continuación, ofrecemos una lista de dichas consultas:

# <ul>
#     <li>Contar palabras desde fichero: https://stackoverflow.com/q/21107505</li>
#     <li>Leer y guardar csv: http://ccm.net/faq/2091-python-read-and-write-csv-files y https://stackoverflow.com/a/21780875</li>
#     <li>Leer csv: https://stackoverflow.com/a/24662707</li>
#     <li>Guardar csv: https://stackoverflow.com/a/41233907</li>
# </ul>

# Y también una lista de consultas que hemos podido realizar para pequeñas consultas __muy__ específicas, que creemos que no tienen la menor importancia pero las indicamos igualmente:

# <ul>
#     <li>Añadir un diccionario a otro: https://stackoverflow.com/a/11012181 (para obtener un resultado similar al método update que existe con conjuntos)</li>
#     <li>Listar elementos de un directorio: https://stackoverflow.com/a/120676</li>
#     <li>Comprobar que un elemento de un directorio es una carpeta: https://stackoverflow.com/a/40347279</li>
#     <li>Borrar elementos de un diccionario: https://stackoverflow.com/a/5844692</li>
#     <li>Buscar clave en diccionario: https://stackoverflow.com/a/1602945</li>
#     <li>Crear tabla LaTeX en Jupyter Notebook: https://redd.it/4lxy1l</li>
#     <li>Máximo valor de un diccionario: https://stackoverflow.com/a/42044202</li>
#     <li>Reemplazar y eliminar elementos de una cadena: https://stackoverflow.com/a/3559600</li>
# </ul>

# Y para acabar, para la recopilación de __sinopsis__ o argumentos se han usado, principalmente, las siguientes fuentes:

# <ul>
#     <li>https://www.filmaffinity.com/</li>
#     <li>https://www.blogdecine.com/</li>
#     <li>http://www.sensacine.com/</li>
#     <li>http://www.labutaca.net/</li>
#     <li>http://www.lahiguera.net/</li>
#     <li>http://www.ecartelera.com/</li>
#     <li>https://es.wikipedia.org/</li>
# </ul>

# Remarcar que, como expresamos al inicio del documento, en bastantes ocasiones ha sido complicado (o directamente imposible) encontrar una sinopsis que contuviese de 200 a 300 palabras, por lo que en algunas ocasiones hemos tenido que utilizar la primera parte del argumento de una película que ofrecen fuentes como _wikipedia_.

input('Presiona INTRO para salir')