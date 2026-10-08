""" Agente DETERMINISTA
"""

import random
from collections import deque

FILAS, COLS = 8, 10                      # tamaño del laberinto
S = (FILAS - 1, 0)                       # inicio: esquina inferior izquierda
G = (0, COLS - 1)                        # meta: esquina superior derecha

LIBRE, OBSTACULO, META = 0, 1, 2         # significado de cada número en el mapa

# Los 4 movimientos posibles: arriba, derecha, abajo, izquierda
VECINOS = [(-1, 0), (0, 1), (1, 0), (0, -1)]

RADIO_VISION = 2                         # el agente ve hasta 2 pasos a su alrededor

# creacion del laberinto
def generar_laberinto(prob=0.28):
    # cada celda tiene un 28% de probabilidad de ser obstáculo
    grid = [[OBSTACULO if random.random() < prob else LIBRE for _ in range(COLS)]
            for _ in range(FILAS)]
    grid[S[0]][S[1]] = LIBRE             # el inicio siempre queda libre
    grid[G[0]][G[1]] = META              # aquí se coloca la meta
    return grid                          # puede quedar sin solución


def percibir(grid, pos):
    # Devuelve solo las celdas cercanas al agente (a 2 pasos o segun el radio_vision).
    f0, c0 = pos
    vista = {}
    for f in range(f0 - RADIO_VISION, f0 + RADIO_VISION + 1):
        for c in range(c0 - RADIO_VISION, c0 + RADIO_VISION + 1):
            cerca = abs(f - f0) + abs(c - c0) <= RADIO_VISION
            if cerca and dentro((f, c)):
                vista[(f, c)] = grid[f][c]
    return vista


def dentro(celda):
    # la celda debe estar dentro del laberinto
    return 0 <= celda[0] < FILAS and 0 <= celda[1] < COLS



def bfs(mapa, inicio, es_objetivo):
    # Explora por capas: primero las celdas a 1 paso, luego a 2 pasos, etc.
    # Devuelve la ruta más corta (lista de celdas) hasta la primera celda
    # que cumpla 'es_objetivo', o None si no hay ninguna alcanzable.
    # Solo pasa por celdas que el agente ya conoce y que no son obstáculo.
    padres = {inicio: None}              # de dónde llegó a cada celda
    cola = deque([inicio])               # celdas pendientes de revisar
    while cola:
        celda = cola.popleft()           # saca la más antigua
        if es_objetivo(celda):
            ruta = []                    # reconstruye el camino hacia atrás
            while celda is not None:
                ruta.append(celda)
                celda = padres[celda]
            return ruta[::-1]            # lo invierte: de inicio a objetivo
        for df, dc in VECINOS:
            vecino = (celda[0] + df, celda[1] + dc)
            if vecino in mapa and mapa[vecino] != OBSTACULO and vecino not in padres:
                padres[vecino] = celda
                cola.append(vecino)
    return None


def es_frontera(celda, mapa):
    for df, dc in VECINOS:
        vecino = (celda[0] + df, celda[1] + dc)
        if dentro(vecino) and vecino not in mapa:
            return True
    return False


def navegar(grid):
    mapa = {}                # lo que el agente ha visto hasta ahora
    pos = S                  # posición actual
    recorrido = [S]          # todas las celdas por las que camina

    while True:
        # anota lo que ha visto en su mapa
        mapa.update(percibir(grid, pos))

        # si esta en la meta, terminó
        if mapa[pos] == META:
            return recorrido, mapa, True

        # logica de hacia donde ir
        ruta = None
        if META in mapa.values():        # ya vio la meta: ruta más corta hacia ella
            ruta = bfs(mapa, pos, lambda c: mapa[c] == META)
        if ruta is None:                 # no la ha visto: va a la frontera más cercana
            ruta = bfs(mapa, pos, lambda c: es_frontera(c, mapa))

        # si no hay meta alcanzable ni fronteras, ya exploró todo
        if ruta is None:
            return recorrido, mapa, False

        
        pos = ruta[1] # la nueva posicion es el siguiente paso en la ruta
        recorrido.append(pos)


def dibujar(grid, ruta=None):
    ruta = set(ruta or [])
    for f in range(FILAS):
        fila = ""
        for c in range(COLS):
            if (f, c) == S:
                simbolo = "S"
            elif grid[f][c] == META:
                simbolo = "G"
            elif (f, c) in ruta:
                simbolo = "*"
            elif grid[f][c] == OBSTACULO:
                simbolo = "#"
            else:
                simbolo = "."
            fila += f" {simbolo}"
        print(fila)



if __name__ == "__main__":
    grid = generar_laberinto()
    print("Laberinto generado (S=inicio, G=meta, #=obstáculo):\n")
    dibujar(grid)

    recorrido, mapa, llego = navegar(grid)

    print("\n=== Recorrido real del agente (*) ===\n")
    dibujar(grid, recorrido)
    print(f"\nMovimientos realizados: {len(recorrido) - 1} | "
          f"celdas conocidas por el agente: {len(mapa)} de {FILAS * COLS}")

    if llego:
        print("\nMeta alcanzada")
    else:
        print("\nSin salida: el agente exploró todo lo alcanzable y no encontró la meta.")