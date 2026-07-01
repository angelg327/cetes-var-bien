# VaR histórico · Curva CETESi (nodo 280 días)

Herramienta estática para reproducir toda la cadena de cálculo de riesgo sobre la curva CETESi:
pivoteo a matriz, orden por plazo, interpolación lineal del nodo y **VaR por simulación histórica**.

Incluye dos piezas:

- **`index.html`** — dashboard autocontenido. Se abre en el navegador, cargas tu `Histórico Curva Cetesi.xls`
  y calcula todo del lado del cliente (el archivo no sale del equipo). Gráficas de distribución de P&L con la
  cola sombreada, curva del último día, serie del nodo, y descarga de `Resultado1.csv` / `Resultado2.csv`.
- **`analisis_var_cetes.py`** — el script original en Python/pandas que genera los mismos resultados.

> La lógica del dashboard está validada contra el script de Python: reproduce tasa, precio, VaR y peor
> escenario **al décimo decimal** (incluida la interpolación lineal de `numpy.percentile`).

## Metodología (resumen)

- **Interpolación del nodo:** lineal entre los dos plazos que lo rodean (por defecto 273 y 364), fila por fecha.
- **Valuación:** descuento simple base 360 → `P = VN / (1 + tasa · plazo/360)`.
- **VaR:** simulación histórica a 1 día. Se aplican los cambios *absolutos* diarios de la tasa del nodo a la
  tasa de hoy, se revalúa cada escenario, y el VaR es el percentil `100 − confianza` de la distribución de
  P&L. Un VaR negativo indica pérdida.
- **Ventana:** últimas 1501 fechas disponibles.

El dashboard además permite ajustar en vivo el nodo, el número de títulos, el valor nominal y el nivel de
confianza, y agrega *Expected Shortfall*.

## Cómo correr el script de Python

```bash
pip install -r requirements.txt
# coloca el archivo en Insumos/Histórico Curva Cetesi.xls
python analisis_var_cetes.py
```

## Publicar el link con GitHub Pages

Pasos (el repositorio debe ser **público** en cuentas gratuitas, y `index.html` debe estar en la raíz):

**Opción A — desde la web (sin git):**
1. En GitHub, crea un repositorio nuevo y súbele estos archivos (botón *Add file → Upload files*, arrastra todo).
2. Entra a **Settings → Pages**.
3. En **Build and deployment → Source** elige **Deploy from a branch**.
4. En **Branch** selecciona `main` y carpeta `/(root)`. Guarda con **Save**.
5. Espera 1–3 min y recarga; aparecerá la URL: `https://<usuario>.github.io/<repo>/`.

**Opción B — desde la terminal:**
```bash
git init
git add .
git commit -m "Dashboard VaR curva CETESi"
git branch -M main
git remote add origin https://github.com/<usuario>/<repo>.git
git push -u origin main
```
Luego repite los pasos 2–5 de la Opción A.

## Notas

- No subas el histórico si contiene información sensible: el `.gitignore` ya excluye `*.xls`, `*.xlsx` y
  `Insumos/`. El dashboard funciona igual porque cada quien carga su archivo localmente.
- Es hosting estático: no hay servidor ni base de datos.
