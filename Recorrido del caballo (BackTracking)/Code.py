# -*- coding: utf-8 -*-
"""Recorrido del Caballo personalizado.ipynb

Automatically generated by Colab.

Original file is located at
    https://colab.research.google.com/drive/1OiGmh1DYi3d1flTi_yc-eiKmS7cbKYMh
"""

def intentar(i,x,y,q):
  k = 0
  global q1
  while not(q1) and (k < 8):
    u = x + mov[k][0]
    v = y + mov[k][1]
    if u in s and v in s:
      if h[u,v] == 0:
        h[u,v] = i
        if i < ncasillas:
          intentar(i+1,u,v,q1)
          if not(q1):
            h[u,v] = 0
        else:
          q1 = True
    k += 1
  return q1

import numpy as np
n = 5 # Tamaño del tablero
# Valores iniciales
x_0=4
y_0=0


ncasillas = n**2
q=True
mov=[(2, 1), (1, 2), (-1, 2), (-2, 1), (-2, -1), (-1, -2), (1, -2), (2, -1)] # Movimientos
s=list(np.arange(n))
h = np.zeros((n,n),dtype=int)
q1=False
h[x_0,y_0] = 1
if intentar(2,x_0,y_0,q):
  print(h) # Mostrar solución.
else:
  print('No hay solución')