# 🧰 funciones_auxiliares  
Librería modular de funciones utilitarias para manejo de archivos, DataFrames, lectura de SAP, operaciones numéricas y utilidades varias.  
Diseñada para ser simple, robusta y fácil de integrar en proyectos Python.

---

## 📦 Instalación

Cloná el repositorio:

```bash
git clone https://github.com/<tu_usuario>/funciones_auxiliares.git
```

## Importá el paquete desde tu proyecto:
```Python
import funciones_auxiliares as fa
```
## 🧱Estructura del proyecto
```Código
funciones_auxiliares/
│
├── __init__.py
├── fn_archivos.py
├── fn_dataframe.py
├── fn_varios.py
└── func_auxiliares.py
```
**fn_archivos.py** → manejo de archivos y directorios <br>
**fn_dataframe.py** → limpieza, formateo y parsing de DataFrames <br>
**fn_varios.py** → utilidades generales (fechas, Excel, filesystem) <br>
**func_auxiliares.py** → interfaz legacy para compatibilidad <br>
**__init__.py** → fachada moderna del paquete <br>

## 🚀 Funcionalidades principales
### 📁 Manejo de archivos (fn_archivos)
**handleFile()** — crear, escribir o borrar archivos <br>
**copiarArchivo()** — copia robusta con manejo de errores <br>
**leer_directorio()** — listado de archivos en un directorio <br>

### 📊 DataFrames (fn_dataframe)
**formatearDF()** — limpieza de columnas de texto <br>
**formatear_columna_numerica()** — normalización numérica avanzada <br>
**leer_csv_sin_Pandas()** — parser robusto para archivos SAP LISTA (ALV) <br>

### 🧩 Utilidades varias (fn_varios)
**crear_serie()** — series numéricas o de fechas <br>
**buscar_carpeta()** — búsqueda recursiva en unidades Windows <br>
**obtener_data()** — lectura rápida de la primera columna de un Excel <br>

## 🧪 Ejemplos de uso
### Leer un directorio
```Python
import funciones_auxiliares as fa

df = fa.leer_directorio("C:/temp", recorrer_subcarpetas=True)
print(df)
```
### Limpiar un DataFrame
```Python
df = fa.formatearDF(df)
```
### Convertir una columna a numérica
```Python
df["importe"] = fa.formatear_columna_numerica(df["importe"])
```
### Leer archivo generado por SAP LISTA (ALV)
```Python
df = fa.leer_csv_sin_Pandas("export_sap.txt")
```
### Crear una serie de fechas
```Python
serie = fa.crear_serie(date(2024,1,1), date(2024,1,10))
```

## 🤝 Contribuciones
Las contribuciones son bienvenidas.
Abrí un issue o enviá un pull request.





