#===== 1.- Cargar la info del archivo Histórico Curva Cetesi y nombrarla Factores =====
import pandas as pd
import numpy as np

archivo = "Insumos/Histórico Curva Cetesi.xls"
Factores = pd.read_excel(archivo, engine="xlrd")

#ver qué trae
print(Factores.shape)
print(Factores.head())
print(Factores.dtypes)

#checar que no falten datos
print(Factores.isnull().sum())
print(Factores["Factor"].unique())


#===== 2.- Transformar Factores a una matriz de 1501 x j (cada columna es un plazo) =====
#las fechas vienen como texto, hay que convertirlas antes de nada
Factores["Fecha"] = pd.to_datetime(Factores["Fecha"], format="%d/%m/%y")

#de tabla larga a matriz
Factores = Factores.pivot(index="Fecha", columns="Factor", values="Valor")
Factores = Factores.sort_index()
Factores = Factores.tail(1501)   #los 1501 días más recientes

print(Factores.head())

#validaciones rápidas
print(Factores.shape)
print(Factores.index.min())
print(Factores.index.max())


#===== 3.- Ordenar por fecha y plazo ascendente y exportar Resultado1.csv =====
#las fechas ya quedaron ordenadas en el paso 2, falta ordenar las columnas por plazo
#ojo: hay que ordenar por el número, si no CETESi-1092 se va antes que CETESi-14
orden_plazos = sorted(Factores.columns, key=lambda x: int(x.split("-")[1]))
Factores = Factores[orden_plazos]

print(Factores.head())

Factores.to_csv("Resultado1.csv")


#===== 4.- Interpolar lineal para el nodo 280 y exportar Resultado2.csv =====
#280 no existe, cae entre 273 y 364, así que interpolamos entre esos dos
x = 280
x1 = 273
x2 = 364

y1 = Factores["CETESi-273"]
y2 = Factores["CETESi-364"]
CETESi_280 = y1 + (y2 - y1) * (x - x1) / (x2 - x1)

#lo mismo pero con numpy para comparar que me dé igual
CETESi_280_np = Factores.apply(
    lambda fila: np.interp(x, [x1, x2], [fila["CETESi-273"], fila["CETESi-364"]]),
    axis=1
)

#si esto da todo cero la fórmula está bien
diferencia = (CETESi_280 - CETESi_280_np).abs()
print(diferencia.max())

Resultado2 = CETESi_280.to_frame(name="CETESi-280")
Resultado2.to_csv("Resultado2.csv")


#===== 5.- VaR al 99% de un portafolio de 250,000 CETES a 280 días, fecha 2026-06-25 =====
#parámetros del cete
VN = 10
plazo = 280
titulos = 250000

#la tasa de hoy es la última de la serie (la de 2026-06-25)
tasa_hoy = CETESi_280.iloc[-1]
precio_hoy = VN / (1 + tasa_hoy * plazo/360)
print("Precio hoy:", precio_hoy)

#variaciones diarias de la tasa
tasas = CETESi_280.values
var_historicas = np.diff(tasas)

#a la tasa de hoy le meto cada movimiento histórico y revalúo el cete
tasas_escenario = tasa_hoy + var_historicas
precios_escenario = VN / (1 + tasas_escenario * plazo/360)

#pérdidas y ganancias del portafolio en cada escenario
dist = (precios_escenario - precio_hoy) * titulos

#el VaR 99% es el percentil 1
VaR_99 = np.percentile(dist, 1)
print("VaR 99%:", VaR_99)
