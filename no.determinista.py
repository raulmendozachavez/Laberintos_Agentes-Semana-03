"""
Agente NO determinista
"""

import random

FILAS, COLS = 8, 10                      # tamaño del laberinto
S = (FILAS - 1, 0)                       # inicio: esquina inferior izquierda
G = (0, COLS - 1)                        # meta: esquina superior derecha

LIBRE, OBSTACULO, META = 0, 1, 2         # significado de cada número en el mapa

# Los 4 movimientos posibles: arriba, derecha, abajo, izquierda
VECINOS = [(-1, 0), (0, 1), (1, 0), (0, -1)]

RADIO_VISION = 2                         # el agente ve hasta 2 pasos a su alrededor
FUERZA_PISTA = 1.0                       # cuánto pesa la pista (0 = sin pista)
CORRIDAS = 3                             # cuántas veces se repite en el mismo laberinto


# creacion del laberinto
def generar_laberinto(prob=0.28):
    # Cada celda tiene un 28% de probabilidad de ser obstáculo
    grid = [[OBSTACULO if random.random() < prob else LIBRE for _ in range(COLS)]
            for _ in range(FILAS)]
    grid[S[0]][S[1]] = LIBRE             # el inicio siempre queda libre
    grid[G[0]][G[1]] = META              # la meta siempre está en el borde
    return grid                          # puede quedar sin solución



def percibir(grid, pos):
    # Devuelve solo las celdas cercanas al agente (a 2 pasos o segun el radio_vision).
    # el resto del mapa es desconocido para el agente
    f0, c0 = pos
    vista = {}
    for f in range(f0 - RADIO_VISION, f0 + RADIO_VISION + 1):
        for c in range(c0 - RADIO_VISION, c0 + RADIO_VISION + 1):
            cerca = abs(f - f0) + abs(c - c0) <= RADIO_VISION
            dentro = 0 <= f < FILAS and 0 <= c < COLS
            if cerca and dentro:
                vista[(f, c)] = grid[f][c]
    return vista


def libertad(celda, vista, visitados):
    # Cuenta cuántas salidas tiene una celda: sus vecinos que no son
    # obstáculo y que el agente todavía no visitó.
    # Más salidas = zona más abierta = menos riesgo de quedar atrapado.
    cuenta = 0
    for df, dc in VECINOS:
        vecino = (celda[0] + df, celda[1] + dc)
        if vecino in vista and vista[vecino] != OBSTACULO and vecino not in visitados:
            cuenta += 1
    return cuenta


# LA PISTA (la meta está en el borde exterior)
def bono_borde(celda):
    # Mide qué tan cerca del borde está una celda:
    #   en el borde            -> bono 1.0
    #   a 1 paso del borde     -> bono 0.5
    #   a 2 pasos del borde    -> bono 0.33  ... y así, cada vez menos.
    # No dice hacia cuál borde ir: cualquier borde sirve.
    f, c = celda
    distancia_al_borde = min(f, FILAS - 1 - f, c, COLS - 1 - c)
    return 1 / (1 + distancia_al_borde)


def navegar(grid):
    visitados = {S}      # celdas donde ya estuvo (evita repetir y dar vueltas sin fin)
    pila = [S]           # camino actual; la última celda es donde está el agente
    retrocesos = 0       # cuántas veces tuvo que volver atrás

    while pila:          # sigue mientras le queden opciones
        actual = pila[-1]                  # posición actual del agente
        vista = percibir(grid, actual)     # mira a su alrededor

        # si esta en la meta, terminó
        if vista[actual] == META:
            return pila, visitados, retrocesos

        # busqueda de candidatos para el siguiente paso
        # Un candidato es un vecino que está dentro del mapa, que no es obstáculo y que todavía no visitó.
        candidatos = []
        for df, dc in VECINOS:
            vecino = (actual[0] + df, actual[1] + dc)
            if vecino in vista and vista[vecino] != OBSTACULO and vecino not in visitados:
                candidatos.append(vecino)

        if candidatos:
            # Si ve la meta al lado, va directo hacia ella.
            metas = [v for v in candidatos if vista[v] == META]
            if metas:
                siguiente = metas[0]
            else:
                # Sistema de pesos para elegir el siguiente paso:
                #   (libertad + 1)            -> favorece las zonas abiertas
                #   (1 + FUERZA_PISTA * bono) -> favorece las celdas cercanas al borde
                # Se suma 1 a la libertad para que ninguno tenga probabilidad cero.
                pesos = [(libertad(v, vista, visitados) + 1) * (1 + FUERZA_PISTA * bono_borde(v))
                         for v in candidatos]

                # Sorteo con ruleta. Los candidatos con más peso tienen más probabilidad, pero cualquiera puede salir.
                siguiente = random.choices(candidatos, weights=pesos)[0]

            visitados.add(siguiente)       # anota que ya pasó por ahí
            pila.append(siguiente)         # avanza a esa celda
        else:
            # Callejón sin salida: no hay candidatos
            # Retrocede a la celda anterior
            pila.pop()
            retrocesos += 1

    # Si la pila se vacía, probó todo y no hay forma de llegar a la meta.
    return None, visitados, retrocesos


# MOSTRAR EL LABERINTO EN CONSOLA
def dibujar(grid, ruta=None, explorados=None):
    # Símbolos: S inicio | G meta | * ruta final | o explorada y descartada
    #           # obstáculo | . celda libre
    ruta = set(ruta or [])
    explorados = explorados or set()
    for f in range(FILAS):
        fila = ""
        for c in range(COLS):
            if (f, c) == S:
                simbolo = "S"
            elif grid[f][c] == META:
                simbolo = "G"
            elif (f, c) in ruta:
                simbolo = "*"
            elif (f, c) in explorados:
                simbolo = "o"
            elif grid[f][c] == OBSTACULO:
                simbolo = "#"
            else:
                simbolo = "."
            fila += f" {simbolo}"
        print(fila)



if __name__ == "__main__":
    grid = generar_laberinto()
    print("Pista del agente: la meta está en el borde exterior del laberinto.")
    print(f"Fuerza de la pista: {FUERZA_PISTA}\n")
    print("Laberinto generado (S=inicio, G=meta, #=obstáculo):\n")
    dibujar(grid)

    rutas = []
    # Se repite varias veces en el MISMO laberinto para comparar resultados
    for n in range(1, CORRIDAS + 1):
        ruta, explorados, retrocesos = navegar(grid)

        print(f"\n=== Corrida {n} (*=ruta final, o=explorada y descartada) ===\n")
        dibujar(grid, ruta, explorados)

        if ruta:
            print(f"\nMeta alcanzada | movimientos de la ruta: {len(ruta) - 1} | "
                  f"celdas exploradas: {len(explorados)} | retrocesos: {retrocesos}")
        else:
            print(f"\nSin salida | celdas exploradas: {len(explorados)} | retrocesos: {retrocesos}")

        rutas.append(tuple(ruta) if ruta else None)

    print(f"\nRutas distintas en {CORRIDAS} corridas sobre el mismo laberinto: {len(set(rutas))}")