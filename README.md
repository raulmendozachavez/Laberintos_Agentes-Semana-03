# Agentes de navegación en un laberinto

Dos agentes que van de `S` a `G` con visión limitada. Ninguno conoce la posición de la meta: solo la reconocen cuando la ven.

## 1. Agente determinista: BFS con exploración de fronteras

**Funcionamiento**

1. Percibe las celdas cercanas y las anota en su propio mapa.
2. Si está sobre la meta, termina.
3. Aplica BFS sobre su mapa:
   - Si ya vio la meta, va por la ruta más corta hacia ella.
   - Si no, va hacia la **frontera** más cercana (una celda conocida con algún vecino aún desconocido).
4. Si no hay meta alcanzable ni fronteras, concluye que no hay salida.
5. Da un solo paso y repite desde el punto 1.

**Técnicas:** búsqueda por anchura (cola FIFO y diccionario de padres), exploración basada en fronteras, mapa incremental y replanificación en cada paso.

**Terminación:** en cada paso el agente se acerca a su frontera o su mapa crece. Como el laberinto es finito, el algoritmo termina siempre.

## 2. Agente no determinista: DFS con heurística y selección probabilística

**Funcionamiento**

1. Percibe las celdas cercanas.
2. Si está sobre la meta, termina.
3. Obtiene los candidatos: vecinos visibles que no son obstáculo y no fueron visitados.
4. Si ve la meta entre ellos, va directo hacia ella.
5. Calcula el peso de cada candidato:

```
   peso = (libertad + 1) × (1 + FUERZA_PISTA × bono_borde)
```

6. Sortea el siguiente paso con una ruleta ponderada (`random.choices`).
7. Si no hay candidatos, retrocede una celda (`pila.pop()`).
8. Si la pila se vacía, concluye que no hay salida.

**Heurísticas**

- **Libertad de movimiento:** cantidad de vecinos transitables y no visitados de un candidato. Favorece las zonas abiertas y evita los callejones.
- **Pista del borde:** el agente sabe que la meta está en el borde exterior, sin saber en cuál. El bono vale `1 / (1 + distancia_al_borde)`. Con `FUERZA_PISTA = 0` se desactiva.

**Técnicas:** búsqueda en profundidad con retroceso (pila explícita), heurística de libertad, pista estructural, selección probabilística ponderada y conjunto de celdas visitadas.

**Terminación:** el conjunto de visitados impide repetir celdas. Como el laberinto es finito, el algoritmo termina siempre.
