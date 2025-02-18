# -*- coding: utf-8 -*-
"""Q-Learning.ipynb

Automatically generated by Colab.

Original file is located at
    https://colab.research.google.com/drive/1m-SMClIu8qa8zMwp__-X9IBWMlS6Lxhm

## Escenario - Robots en un almacén
Una empresa de comercio electrónico en crecimiento está construyendo un nuevo almacén y le gustaría que todas las operaciones de recolección en el nuevo almacén fueran realizadas por robots de almacén.
* En el contexto del almacenamiento de comercio electrónico, "recoger" es la tarea de reunir artículos individuales de varias ubicaciones en el almacén para cumplir con los pedidos de los clientes.

Después de recoger artículos de los estantes, los robots deben llevarlos a una ubicación específica dentro del almacén donde se pueden empaquetar para su envío.

Para garantizar la máxima eficiencia y productividad, los robots deberán aprender el camino más corto entre el área de empaque del artículo y todas las demás ubicaciones dentro del almacén donde los robots pueden viajar.
* ¡Usaremos Q-learning para realizar esta tarea!

#### Importar bibliotecas requeridas
"""

#importar librerias
import numpy as np

"""## Definir el entorno
El entorno consta de **estados**, **acciones** y **recompensas**. Los estados y las acciones son entradas para el agente de IA de Q-learning, mientras que las posibles acciones son las salidas del agente de IA.
#### Estados
Los estados del entorno son todas las ubicaciones posibles dentro del almacén. Algunas de estas ubicaciones son para almacenar artículos (**cuadrados negros**), mientras que otras ubicaciones son pasillos que el robot puede usar para viajar por el almacén (**cuadrados blancos**). El **cuadrado verde** indica el área de embalaje y envío del artículo.

Los cuadrados negros y verdes son **estados terminales**!

![warehouse map](https://www.danielsoper.com/teaching/img/08-warehouse-map.png)

El objetivo del agente de IA es aprender el camino más corto entre el área de empaque del artículo y todas las demás ubicaciones en el almacén donde el robot puede viajar.

Como se muestra en la imagen de arriba, hay 121 estados posibles (ubicaciones) dentro del almacén. Estos estados están dispuestos en una cuadrícula que contiene 11 filas y 11 columnas. Por lo tanto, cada ubicación puede identificarse por su índice de fila y columna.
"""

#definir la forma del ambiente (i.e., los estados)
environment_rows = 11
environment_columns = 11

#Cree una matriz numérica 3D para contener los valores Q actuales para cada par de estado y acción: Q(s, a)
#La matriz contiene 11 filas y 11 columnas (para que coincida con la forma del entorno), así como una
#tercera dimensión de "acción". La dimensión "acción" consta de 4 capas que nos permitirán realizar un
#seguimiento de los valores Q para cada acción posible en cada estado (consulte la siguiente celda para
#obtener una descripción de las posibles acciones).
#El valor de cada par (estado, acción) se inicializa en 0.

q_values = np.zeros((environment_rows, environment_columns, 4))

"""#### Acciones
Las acciones que están disponibles para el agente son moverse en una de cuatro direcciones:
* Arriba
* Derecha
* Abajo
* Izquierda

¡Obviamente, el agente debe aprender a evitar conducir a las ubicaciones de almacenamiento de artículos (por ejemplo, estantes)!
"""

#definir acciones
#codigo numérico de las acciones: 0 = Arriba, 1 = Derecha, 2 = Abajo, 3 = Izquierda
actions = ['up', 'right', 'down', 'left']

"""#### Recompensas
El último componente del entorno que necesitamos definir son las **recompensas**.

Para ayudar al agente de IA a aprender, a cada estado (ubicación) en el almacén se le asigna un valor de recompensa.

El agente puede comenzar en cualquier casilla blanca, pero su objetivo es siempre el mismo: ¡***maximizar sus recompensas totales***!

Las recompensas negativas (es decir, **castigos**) se utilizan para todos los estados excepto el objetivo.
* ¡Esto alienta a la IA a identificar el *camino más corto* hacia la meta al *minimizar sus castigos*!

![warehouse map](https://www.danielsoper.com/teaching/img/08-warehouse-map-rewards.png)

Para maximizar sus recompensas acumulativas (al minimizar sus castigos acumulativos), el agente de IA deberá encontrar los caminos más cortos entre el área de empaque del artículo (cuadrado verde) y todas las demás ubicaciones en el almacén donde el robot puede viajar (cuadrados blancos). ). ¡El agente también deberá aprender a evitar chocar contra cualquiera de las ubicaciones de almacenamiento de artículos (cuadrados negros)!
"""

#Crear un arreglo 2D de numpy para almacenar las recompensas de cada estado
rewards = np.full((environment_rows, environment_columns), -100.)
rewards[0, 5] = 100. #Recompensa para el area de embalaje (i.e., el objetivo) damos valor de 100

#Definir los estados por donde se puede transitar de acuerdo a la figura
aisles = {} #guardo las localizaciones de la zona transitable en un diccionario
aisles[1] = [i for i in range(1, 10)]
aisles[2] = [1, 7, 9]
aisles[3] = [i for i in range(1, 8)]
aisles[3].append(9)
aisles[4] = [3, 7]
aisles[5] = [i for i in range(11)]
aisles[6] = [5]
aisles[7] = [i for i in range(1, 10)]
aisles[8] = [3, 7]
aisles[9] = [i for i in range(11)]

#Recompensa de los pasillos (cuadros blancos) -1
for row_index in range(1, 10):
    for column_index in aisles[row_index]:
        rewards[row_index, column_index] = -1

#Imprimo la matriz de recompensas
for row in rewards:
    print(row)

"""## Entrenar al modelo
Nuestra próxima tarea es que nuestro agente de IA aprenda sobre su entorno mediante la implementación de un modelo Q-learning. El proceso de aprendizaje seguirá estos pasos:
1. Elija un estado no terminal aleatorio (cuadrado blanco) para que el agente comience este nuevo episodio.
2. Elija una acción (mover *arriba*, *derecha*, *abajo* o *izquierda*) para el estado actual. Las acciones se elegirán utilizando un *algoritmo voraz epsilon*. Este algoritmo generalmente elegirá la acción más prometedora para el agente de IA, pero ocasionalmente elegirá una opción menos prometedora para alentar al agente a explorar el entorno.
3. Realice la acción elegida y haga la transición al siguiente estado (es decir, muévase a la siguiente ubicación).
4. Reciba la recompensa por mudarse al nuevo estado y calcule la diferencia temporal.
5. Actualice el valor Q para el par de acción y estado anterior.
6. Si el nuevo estado (actual) es un estado terminal, vaya al #1. De lo contrario, vaya al #2.

Todo este proceso se repetirá a lo largo de 1000 episodios. Esto brindará al agente de IA la oportunidad suficiente para aprender los caminos más cortos entre el área de empaque del artículo y todas las demás ubicaciones en el almacén donde el robot puede viajar, ¡mientras que al mismo tiempo evita chocar contra cualquiera de las ubicaciones de almacenamiento de artículos!

#### Definir funciones auxiliares
"""

#función que determina si estoy en un estado terminal
def is_terminal_state(current_row_index, current_column_index):
  #Si la recompensa para esta localización es -1 no estoy en un estado terminal (i.e., es un 'cuadro blanco')
  if rewards[current_row_index, current_column_index] == -1.:
    return False
  else:
    return True

#definir la función que escoge una localización aleatoria no terminal inicial
def get_starting_location():
    #fila y columna aleatoria
    current_row_index = np.random.randint(environment_rows)
    current_column_index = np.random.randint(environment_columns)
    #continuar escogiendo aleatoriamente hasta encontrar un estado no temrinal
    while is_terminal_state(current_row_index, current_column_index):
        current_row_index = np.random.randint(environment_rows)
        current_column_index = np.random.randint(environment_columns)
    return current_row_index, current_column_index

#defino un algoritmo epsilon greedy para elegir la siguiente accion (i.e., donde moverme)
def get_next_action(current_row_index, current_column_index, epsilon):
    #Si un numero aleatorio es menor que epsilon, escoger el mejor valor de la tabla Q para este estado
    if np.random.random() < epsilon:
        return np.argmax(q_values[current_row_index, current_column_index])
    else: #de lo contrario escoja aleatoriamente
        return np.random.randint(4)

#función que nos lleva al siguiente estado basado en la accion tomada
def get_next_location(current_row_index, current_column_index, action_index):
    new_row_index = current_row_index
    new_column_index = current_column_index
    if actions[action_index] == 'up' and current_row_index > 0:
        new_row_index -= 1
    elif actions[action_index] == 'right' and current_column_index < environment_columns - 1:
        new_column_index += 1
    elif actions[action_index] == 'down' and current_row_index < environment_rows - 1:
        new_row_index += 1
    elif actions[action_index] == 'left' and current_column_index > 0:
        new_column_index -= 1
    return new_row_index, new_column_index

#Definir una función que obtendrá la ruta más corta entre cualquier ubicación dentro del almacén que
#el robot puede viajar y la ubicación del embalaje del artículo.
def get_shortest_path(start_row_index, start_column_index):
    #Si no es una posición valida retornar inmediatamente
    if is_terminal_state(start_row_index, start_column_index):
        return []
    else: #Si es una localización legal
        current_row_index, current_column_index = start_row_index, start_column_index
        shortest_path = []
        shortest_path.append([current_row_index, current_column_index])
        #continuar moviendose a lo largo del camino hasta llegar al objetivo (i.e., localización del empaquetador)
        while not is_terminal_state(current_row_index, current_column_index):
            #tomo la mejor accion
            action_index = get_next_action(current_row_index, current_column_index, 1.)
            #me muevo a la siguiente localización del camino más corto y agrego la nueva localizacion a la lista
            current_row_index, current_column_index = get_next_location(current_row_index, current_column_index, action_index)
            shortest_path.append([current_row_index, current_column_index])
    return shortest_path

"""#### Train the AI Agent using Q-Learning"""

#Parametros de entrenamiento
epsilon = 0.9 #del algoritmo epsilon greedy
discount_factor = 0.9 #factor de descuento de recompensa futura
learning_rate = 0.9 #tasa de aprendizaje

#1000 episodes de entrenamiento
for episode in range(1000):
    #localización de inicio
    row_index, column_index = get_starting_location()

    # continuar tomando acciones (es decir, moviéndose) hasta que lleguemos a un estado terminal
    # (es decir, hasta que lleguemos al área de empaque del artículo o nos estrellemos contra una
    # ubicación de almacenamiento del artículo)
    while not is_terminal_state(row_index, column_index):
        #elegir accion
        action_index = get_next_action(row_index, column_index, epsilon)

        #realizar la acción escogida y transitar al siguiente estado
        old_row_index, old_column_index = row_index, column_index #almaceno los indices viejos
        row_index, column_index = get_next_location(row_index, column_index, action_index)

        #recibo recompensa por moverme al siguiente estado y calculo los elementos de la funcion Q
        reward = rewards[row_index, column_index]
        old_q_value = q_values[old_row_index, old_column_index, action_index]
        temporal_difference = reward + (discount_factor * np.max(q_values[row_index, column_index])) - old_q_value

        #Actualizo el valor Q
        new_q_value = old_q_value + (learning_rate * temporal_difference)
        q_values[old_row_index, old_column_index, action_index] = new_q_value

print('Entrenamiento Completo!')

"""## Obtenga las rutas más cortas
Ahora que el agente de IA ha sido completamente capacitado, podemos ver lo que ha aprendido al mostrar la ruta más corta entre cualquier ubicación en el almacén donde el robot puede viajar y el área de empaque del artículo.

![warehouse map](https://www.danielsoper.com/teaching/img/08-warehouse-map.png)

"""

#Mostrar algunas rutas más cortas
print(get_shortest_path(3, 9)) #comenzando en fila 3, columna 9
print(get_shortest_path(5, 0)) # fila 5, columna 0
print(get_shortest_path(9, 5)) # fila 9, columna 5

"""#### Finalmente...
Es genial que nuestro robot pueda tomar automáticamente el camino más corto desde cualquier ubicación 'legal' en el almacén hasta el área de empaque del artículo. **Pero, ¿qué pasa con el escenario opuesto?**

Dicho de otra manera, nuestro robot actualmente puede entregar un artículo desde cualquier lugar del almacén ***a*** el área de embalaje, pero después de entregar el artículo, deberá viajar ***desde*** el área de embalaje a otra ubicación en el almacén para recoger el siguiente artículo!

No se preocupe, este problema se resuelve fácilmente ***invirtiendo el orden de la ruta más corta***.

Ejecute la siguiente celda de código para ver un ejemplo:
"""

#muestre el camino más corto al revés
path = get_shortest_path(5, 2) # fila 5, columna 2
path.reverse()
print(path)