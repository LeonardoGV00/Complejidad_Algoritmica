import matplotlib.pyplot as grafica

MAXIMO_NODOS_CICLO = 8
MAXIMO_NODOS_SECTOR = 64
MOSTRAR_COORDENADAS_GEOGRAFICAS = False
GUARDAR_IMAGENES = False

# Posiciones de los datos dentro de la lista que representa cada nodo
CODIGO = 0
DEMANDA_PARTICULAR = 1
DEMANDA_ALUMBRADO = 2
COORDENADA_X = 3
COORDENADA_Y = 4
LONGITUD = 5
LATITUD = 6
DEMANDA_SUMADA = 7

class Graph:
    def __init__(self):
        # Crea las listas de vertices y vecinos y relaciona cada codigo con su posicion
        self.Vertices = []
        self.label2v = dict()
        self.G = []

    def node(self, label):
        # Agrega un vertice y crea su lista de vecinos
        self.label2v[label] = len(self.Vertices)
        self.Vertices.append(label)
        self.G.append([])

    def nodes(self, labels):
        # Agrega al grafo todos los codigos de una lista
        for label in labels:
            self.node(label)

    def edge(self, u, v):
        # Agrega una conexion desde el vertice u hacia el vertice v
        origen = self.label2v[u]
        destino = self.label2v[v]
        self.G[origen].append(destino)

    def edges(self, u, vs):
        # Agrega las conexiones desde u hacia los vertices de la lista vs
        for v in vs:
            self.edge(u, v)

    def dibujar(self, eje, indices, nodos, titulo, demanda_minima,
            demanda_maxima, usar_puntos_pequenos=False):
        # Matplotlib conserva las ubicaciones geograficas y muestra la demanda
        # Representa graficamente el grafo o uno de sus subgrafos mediante Matplotlib
        return dibujar_grupo(eje, indices, nodos, self, titulo,
                             demanda_minima, demanda_maxima, usar_puntos_pequenos)


def leer_subestaciones():
    # El CSV revisado contiene las siete columnas completas en este orden:
    # COD, MAX_DEM_SP, MAX_DEM_AP, X, Y, LONGITUD y LATITUD
    # Lee las subestaciones y conserva sus coordenadas y demandas en listas
    nodos = []
    with open("SED_San_Juan_de_Lurigancho_1788.csv", "r") as archivo:
        archivo.readline()
        for linea in archivo:
            campos = linea.strip().split(",")
            nodo = [campos[CODIGO]]
            for posicion in range(1, 7):
                nodo.append(float(campos[posicion]))
            # Se suman los maximos registrados
            nodo.append(nodo[DEMANDA_PARTICULAR] + nodo[DEMANDA_ALUMBRADO])
            nodos.append(nodo)
    return nodos


def distancia_entre(nodos, origen, destino):
    # Calcula la distancia euclidiana entre dos subestaciones utilizando X e Y
    diferencia_x = nodos[origen][COORDENADA_X] - nodos[destino][COORDENADA_X]
    diferencia_y = nodos[origen][COORDENADA_Y] - nodos[destino][COORDENADA_Y]
    return (diferencia_x ** 2 + diferencia_y ** 2) ** 0.5


def ordenar_por_coordenada(indices, nodos, coordenada):
    # Se usa MergeSort
    # Ordena los nodos por el eje elegido mediante division y mezcla de listas
    if len(indices) <= 1:
        return indices[:]
    mitad = len(indices) // 2
    izquierda = ordenar_por_coordenada(indices[:mitad], nodos, coordenada)
    derecha = ordenar_por_coordenada(indices[mitad:], nodos, coordenada)
    ordenados = []
    posicion_izquierda = 0
    posicion_derecha = 0
    while posicion_izquierda < len(izquierda) and posicion_derecha < len(derecha):
        indice_izquierdo = izquierda[posicion_izquierda]
        indice_derecho = derecha[posicion_derecha]
        if nodos[indice_izquierdo][coordenada] <= nodos[indice_derecho][coordenada]:
            ordenados.append(indice_izquierdo)
            posicion_izquierda += 1
        else:
            ordenados.append(indice_derecho)
            posicion_derecha += 1
    while posicion_izquierda < len(izquierda):
        ordenados.append(izquierda[posicion_izquierda])
        posicion_izquierda += 1
    while posicion_derecha < len(derecha):
        ordenados.append(derecha[posicion_derecha])
        posicion_derecha += 1
    return ordenados


def limites_del_grupo(indices, nodos):
    # Obtiene los valores minimo y maximo de X e Y para un grupo de nodos
    primer_nodo = nodos[indices[0]]
    minimo_x = primer_nodo[COORDENADA_X]
    maximo_x = minimo_x
    minimo_y = primer_nodo[COORDENADA_Y]
    maximo_y = minimo_y
    for indice in indices:
        minimo_x = min(minimo_x, nodos[indice][COORDENADA_X])
        maximo_x = max(maximo_x, nodos[indice][COORDENADA_X])
        minimo_y = min(minimo_y, nodos[indice][COORDENADA_Y])
        maximo_y = max(maximo_y, nodos[indice][COORDENADA_Y])
    return [minimo_x, maximo_x, minimo_y, maximo_y]


def ciclo_por_backtracking(indices, nodos):
    # Se busca el ciclo mas corto que visita una vez cada nodo del grupo
    cantidad = len(indices)
    distancias = []
    for origen in indices:
        fila = []
        for destino in indices:
            fila.append(distancia_entre(nodos, origen, destino))
        distancias.append(fila)

    camino = [0]
    usados = [False] * cantidad
    usados[0] = True
    mejor_camino = []
    mejor_distancia = [float("inf")]
    explorar_ciclos(distancias, camino, usados, 0.0, mejor_camino,
                    mejor_distancia)
    aristas = []
    for posicion in range(cantidad):
        origen = indices[mejor_camino[posicion]]
        destino = indices[mejor_camino[(posicion + 1) % cantidad]]
        aristas.append([origen, destino, distancia_entre(nodos, origen, destino)])
    return aristas


def explorar_ciclos(distancias, camino, usados, longitud, mejor_camino,
                     mejor_distancia):
    # Backtracking: prueba recorridos y poda los que no pueden mejorar el ciclo encontrado
    if longitud >= mejor_distancia[0]:
        # Para la poda, toda continuacion sera al menos tan larga como esta rama
        return
    ultimo = camino[-1]
    cantidad = len(usados)
    if len(camino) == cantidad:
        # Fijar el inicio y descartar el recorrido inverso para evitar duplicados
        if camino[1] > camino[-1]:
            return
        longitud_cerrada = longitud + distancias[ultimo][0]
        if longitud_cerrada < mejor_distancia[0]:
            mejor_distancia[0] = longitud_cerrada
            mejor_camino.clear()
            for indice in camino:
                mejor_camino.append(indice)
        return

    candidatos = []
    for siguiente in range(1, cantidad):
        if not usados[siguiente]:
            posicion = 0
            while posicion < len(candidatos):
                vecino = candidatos[posicion]
                if distancias[ultimo][siguiente] < distancias[ultimo][vecino]:
                    break
                posicion += 1
            candidatos.insert(posicion, siguiente)
    for siguiente in candidatos:
        usados[siguiente] = True
        camino.append(siguiente)
        explorar_ciclos(distancias, camino, usados,
                        longitud + distancias[ultimo][siguiente],
                        mejor_camino, mejor_distancia)
        camino.pop()
        usados[siguiente] = False


def enlaces_entre_grupos(izquierda, derecha, nodos):
    # Se hace un enlace entre grupos, el mas corto entre los dos grupos
    # Elige dos conexiones cortas entre grupos usando extremos distintos
    primer_enlace = []
    menor_distancia = float("inf")
    for origen in izquierda:
        for destino in derecha:
            distancia = distancia_entre(nodos, origen, destino)
            if distancia < menor_distancia:
                menor_distancia = distancia
                primer_enlace = [origen, destino, distancia]

    # El segundo utiliza otro nodo en cada grupo para evitar un unico punto de union y asi tener un poco mas de redundancia en la red
    segundo_enlace = []
    menor_distancia = float("inf")
    for origen in izquierda:
        if origen == primer_enlace[0]:
            continue
        for destino in derecha:
            if destino == primer_enlace[1]:
                continue
            distancia = distancia_entre(nodos, origen, destino)
            if distancia < menor_distancia:
                menor_distancia = distancia
                segundo_enlace = [origen, destino, distancia]
    return [primer_enlace, segundo_enlace]


def construir_por_division(indices, nodos, sectores,
                           guardar_sector=True):
    # Se divide el territorio, se resuelven los grupos y se combinan
    if guardar_sector and len(indices) <= MAXIMO_NODOS_SECTOR:
        sectores.append(indices[:])
        guardar_sector = False
    if len(indices) <= MAXIMO_NODOS_CICLO:
        return ciclo_por_backtracking(indices, nodos)

    # Se compara la extension X con la extension Y y se elige la mayor
    # Se ordenan los nodos por ese eje y se separan en dos mitades
    # La posicion central del ordenamiento corresponde al corte por mediana
    # Asi quedan cantidades equilibradas de nodos en cada lado del corte
    limites = limites_del_grupo(indices, nodos)
    extension_x = limites[1] - limites[0]
    extension_y = limites[3] - limites[2]
    coordenada = COORDENADA_X
    if extension_y > extension_x:
        coordenada = COORDENADA_Y
    ordenados = ordenar_por_coordenada(indices, nodos, coordenada)
    mitad = len(ordenados) // 2
    izquierda = ordenados[:mitad]
    derecha = ordenados[mitad:]
    # Resolver cada mitad repitiendo la division hasta grupos de 8 nodos
    aristas_izquierda = construir_por_division(izquierda, nodos, sectores,
                                             guardar_sector)
    aristas_derecha = construir_por_division(derecha, nodos, sectores,
                                           guardar_sector)
    # Combinar las soluciones con dos conexiones de extremos distintos
    enlaces = enlaces_entre_grupos(izquierda, derecha, nodos)
    return aristas_izquierda + aristas_derecha + enlaces


def crear_grafo(nodos, aristas):
    # Crea el grafo y registra cada conexion en ambos sentidos
    grafo = Graph()
    etiquetas = []
    for nodo in nodos:
        etiquetas.append(nodo[CODIGO])
    grafo.nodes(etiquetas)
    for arista in aristas:
        origen = nodos[arista[0]][CODIGO]
        destino = nodos[arista[1]][CODIGO]
        grafo.edge(origen, destino)
        grafo.edge(destino, origen)
    return grafo


def recorrer_bfs(grafo, origen, permitidos):
    # Se realiza busqueda en amplitud para verificar que toda la red este conectada entre si
    visitados = [False] * len(grafo.Vertices)
    cola = [origen]
    visitados[origen] = True
    posicion = 0
    while posicion < len(cola):
        actual = cola[posicion]
        posicion += 1
        for vecino in grafo.G[actual]:
            if permitidos[vecino] and not visitados[vecino]:
                visitados[vecino] = True
                cola.append(vecino)
    return visitados


def comprobar_grupo(indices, grafo):
    # Comprueba con BFS que todos los nodos del grupo sean alcanzables
    permitidos = [False] * len(grafo.Vertices)
    for indice in indices:
        permitidos[indice] = True
    visitados = recorrer_bfs(grafo, indices[0], permitidos)
    for indice in indices:
        if not visitados[indice]:
            return False
    return True


def sumar_demanda(indices, nodos):
    # Suma MAX_DEM_SP + MAX_DEM_AP de los nodos del grupo para comparar su demanda
    demanda = 0.0
    for indice in indices:
        demanda += nodos[indice][DEMANDA_SUMADA]
    return demanda


def elegir_sectores(sectores, nodos):
    # Compara los grupos guardados en sectores por construir_por_division
    # Estos grupos tienen hasta 64 nodos y se utilizan para las vistas A, B y C
    # Se elige los de mayor demanda, mayor concentracion y menor concentracion
    demandas = []
    concentraciones = []
    # Calcula la demanda acumulada y la concentracion de cada grupo
    for sector in sectores:
        demandas.append(sumar_demanda(sector, nodos))
        limites = limites_del_grupo(sector, nodos)
        area = (limites[1] - limites[0]) * (limites[3] - limites[2])
        if area == 0:
            concentraciones.append(float("inf"))
        else:
            concentraciones.append(len(sector) / area)
    seleccionados = []
    titulos = []
    # Criterio 0: mayor demanda, 1: mayor concentracion, 2: menor concentracion
    for criterio in range(3):
        elegido = -1
        for numero in range(len(sectores)):
            # Toma el primer grupo como candidato y lo reemplaza si encuentra uno mejor
            if elegido == -1:
                elegido = numero
            elif criterio == 0 and demandas[numero] > demandas[elegido]:
                elegido = numero
            elif criterio == 1 and concentraciones[numero] > concentraciones[elegido]:
                elegido = numero
            elif criterio == 2 and concentraciones[numero] < concentraciones[elegido]:
                elegido = numero
        # Guarda la posicion del grupo elegido y el titulo correspondiente
        if elegido != -1:
            seleccionados.append(elegido)
            if criterio == 0:
                titulos.append("Mayor demanda registrada")
            elif criterio == 1:
                titulos.append("Mayor concentracion de subestaciones")
            else:
                titulos.append("Mayor dispersion de subestaciones")
    return seleccionados, titulos


def posicion_para_dibujar(nodo):
    # Devuelve X e Y o longitud y latitud para ubicar el nodo en el grafico
    if MOSTRAR_COORDENADAS_GEOGRAFICAS:
        return [nodo[LONGITUD], nodo[LATITUD]]
    return [nodo[COORDENADA_X], nodo[COORDENADA_Y]]


def dibujar_areas_seleccionadas(eje, nodos, sectores, seleccionados):
    # Ubica en el grafo general las areas A, B y C correspondientes a los subgrafos
    letras = ["A", "B", "C"]
    colores = ["#d55e00", "#0072b2", "#882255"]
    for numero in range(len(seleccionados)):
        grupo = sectores[seleccionados[numero]]
        primera_posicion = posicion_para_dibujar(nodos[grupo[0]])
        minimo_x = primera_posicion[0]
        maximo_x = minimo_x
        minimo_y = primera_posicion[1]
        maximo_y = minimo_y
        for indice in grupo:
            posicion = posicion_para_dibujar(nodos[indice])
            minimo_x = min(minimo_x, posicion[0])
            maximo_x = max(maximo_x, posicion[0])
            minimo_y = min(minimo_y, posicion[1])
            maximo_y = max(maximo_y, posicion[1])
        eje.plot([minimo_x, maximo_x, maximo_x, minimo_x, minimo_x],
                 [minimo_y, minimo_y, maximo_y, maximo_y, minimo_y],
                 color=colores[numero])
        eje.text(minimo_x, maximo_y, letras[numero], color=colores[numero])


def dibujar_grupo(eje, indices, nodos, grafo, titulo, demanda_minima,
                  demanda_maxima, usar_puntos_pequenos=False):
    # Dibuja los nodos y conexiones internas, con color y tamano segun la demanda
    incluidos = [False] * len(nodos)
    for indice in indices:
        incluidos[indice] = True
    lineas_x = []
    lineas_y = []
    cantidad_aristas = 0
    for origen in indices:
        for destino in grafo.G[origen]:
            # Cada enlace se dibuja una sola vez, aunque se almacene en ambos sentidos
            if incluidos[destino] and origen < destino:
                posicion_origen = posicion_para_dibujar(nodos[origen])
                posicion_destino = posicion_para_dibujar(nodos[destino])
                lineas_x.extend([posicion_origen[0], posicion_destino[0], None])
                lineas_y.extend([posicion_origen[1], posicion_destino[1], None])
                cantidad_aristas += 1
    # Una llamada grafica dibuja todas las conexiones del grupo
    eje.plot(lineas_x, lineas_y, color="gray", linewidth=0.6, zorder=1)
    posiciones_x = []
    posiciones_y = []
    demandas = []
    tamanos = []
    for indice in indices:
        posicion = posicion_para_dibujar(nodos[indice])
        demanda = nodos[indice][DEMANDA_SUMADA]
        posiciones_x.append(posicion[0])
        posiciones_y.append(posicion[1])
        demandas.append(demanda)
        proporcion = 0.0
        if demanda_maxima > demanda_minima:
            proporcion = (demanda - demanda_minima) / (demanda_maxima - demanda_minima)
        if usar_puntos_pequenos:
            tamanos.append(9 + 85 * proporcion)
        else:
            tamanos.append(24 + 130 * proporcion)
    puntos = eje.scatter(posiciones_x, posiciones_y, c=demandas, s=tamanos,
                         cmap="viridis", vmin=demanda_minima, vmax=demanda_maxima,
                         zorder=2)
    resumen = str(len(indices)) + " subestaciones | " + str(cantidad_aristas) + " conexiones"
    if titulo != "":
        resumen = titulo + "\n" + resumen
    eje.set_title(resumen)
    if MOSTRAR_COORDENADAS_GEOGRAFICAS:
        eje.set_xlabel("Longitud (grados)")
        eje.set_ylabel("Latitud (grados)")
        # Se muestran grados pero las distancias se siguen calculando con X e Y
        eje.set_aspect("equal", adjustable="datalim")
    else:
        eje.set_xlabel("Coordenada X")
        eje.set_ylabel("Coordenada Y")
        eje.set_aspect("equal", adjustable="datalim")
    eje.ticklabel_format(style="plain", useOffset=False)
    eje.tick_params(axis="x", labelrotation=20)
    eje.grid(alpha=0.16)
    eje.margins(0.12)
    return puntos


def mostrar_graficos(nodos, grafo, sectores, seleccionados, titulos):
    # Muestra el grafo general y los tres subgrafos con la misma escala de demanda
    demanda_minima = nodos[0][DEMANDA_SUMADA]
    demanda_maxima = demanda_minima
    indices = []
    for indice in range(len(nodos)):
        indices.append(indice)
        demanda_minima = min(demanda_minima, nodos[indice][DEMANDA_SUMADA])
        demanda_maxima = max(demanda_maxima, nodos[indice][DEMANDA_SUMADA])
    figura_general, eje_general = grafica.subplots(figsize=(11, 10), layout="constrained")
    puntos = grafo.dibujar(eje_general, indices, nodos,
                           "",
                           demanda_minima, demanda_maxima, True)
    barra = figura_general.colorbar(puntos, ax=eje_general)
    barra.set_label("MAX_DEM_SP + MAX_DEM_AP")
    figura_general.suptitle("Propuesta de subestaciones de San Juan de Lurigancho")
    dibujar_areas_seleccionadas(eje_general, nodos, sectores, seleccionados)

    figura_sectores = grafica.figure(figsize=(18, 7), layout="constrained")
    ejes = []
    for posicion in range(len(seleccionados)):
        eje = figura_sectores.add_subplot(1, len(seleccionados), posicion + 1)
        ejes.append(eje)
        sector = sectores[seleccionados[posicion]]
        titulo = ['A ', 'B ', 'C '][posicion] + titulos[posicion]
        puntos = grafo.dibujar(eje, sector, nodos,
                               titulo, demanda_minima, demanda_maxima)
    barra = figura_sectores.colorbar(puntos, ax=ejes)
    barra.set_label("MAX_DEM_SP + MAX_DEM_AP")
    if GUARDAR_IMAGENES:
        figura_general.savefig("grafo_general_sjl.png", dpi=180)
        figura_sectores.savefig("subgrafos_sjl.png", dpi=180)
    grafica.show()


def principal():
    # Coordina la lectura, la construccion del grafo, BFS y la presentacion de las figuras
    nodos = leer_subestaciones()
    indices = []
    for indice in range(len(nodos)):
        indices.append(indice)
    sectores = []
    aristas = construir_por_division(indices, nodos, sectores)
    grafo = crear_grafo(nodos, aristas)
    conectividad_general = comprobar_grupo(indices, grafo)
    sectores_conexos = 0
    for sector in sectores:
        if comprobar_grupo(sector, grafo):
            sectores_conexos += 1
    seleccionados, titulos = elegir_sectores(sectores, nodos)
    print("Subestaciones leidas:", len(nodos))
    print("Enlaces propuestos:", len(aristas))
    print("Sectores geograficos:", len(sectores))
    print("Grafo general conectado:", conectividad_general)
    print("Sectores conectados:", sectores_conexos, "de", len(sectores))
    print("Demanda registrada acumulada:", sumar_demanda(indices, nodos))
    mostrar_graficos(nodos, grafo, sectores, seleccionados, titulos)


principal()
