from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Iterable, Optional

import logging
import shutil
import pandas as pd
import os

logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# Helpers internos
# ---------------------------------------------------------------------------

@dataclass(frozen=True)
class FileTask:
    CREATE: int = 1
    WRITE: int = 2
    DELETE: int = 3


def _ensure_directory(path: Path) -> None:
    """
    Crea el directorio padre si no existe.
    No falla si ya existe.
    """
    try:
        path.parent.mkdir(parents=True, exist_ok=True)
    except Exception as exc:
        logger.error("No se pudo crear el directorio padre '%s': %s", path.parent, exc)
        raise


# ---------------------------------------------------------------------------
# API pública
# ---------------------------------------------------------------------------

def handleFile(
    tarea: int,
    directorio: str,
    archivo: str,
    texto: Optional[Iterable[str] | str] = None,
) -> None:
    """
    Create, write or delete a file in a directory.

    Parámetros
    ----------
    tarea : int
        1 = Crear, 2 = Escribir (append), 3 = Borrar.
    directorio : str
        Path del archivo (puede terminar o no en separador).
    archivo : str
        Nombre del archivo, por ejemplo: "test.txt".
    texto : Iterable[str] | str | None
        Texto a agregar (si tarea = 2). Puede ser string o iterable de líneas.

    Notas
    -----
    - Usa `pathlib.Path` para mayor robustez.
    - Crea el directorio padre si no existe cuando se crea/escribe.
    - Loguea errores en lugar de fallar silenciosamente.
    """
    task_label = {
        FileTask.CREATE: "Creando",
        FileTask.WRITE: "Escribiendo",
        FileTask.DELETE: "Borrando",
    }.get(tarea, "Tarea desconocida")

    path_file = Path(directorio) / archivo
    logger.info("Manejo de archivos - %s %s", task_label, path_file)

    try:
        if tarea == FileTask.CREATE:
            _ensure_directory(path_file)
            # Crear archivo vacío (sobrescribe si existe)
            path_file.touch(exist_ok=True)

        elif tarea == FileTask.WRITE:
            if texto is None:
                logger.warning(
                    "handleFile llamado con tarea=WRITE pero sin texto. Archivo: %s",
                    path_file,
                )
                return

            _ensure_directory(path_file)

            # Normalizar texto a iterable de líneas
            if isinstance(texto, str):
                data = [texto]
            else:
                data = list(texto)

            with path_file.open("a", encoding="utf8") as f:
                f.writelines(data)

        elif tarea == FileTask.DELETE:
            try:
                path_file.unlink(missing_ok=True)
            except TypeError:
                # Python < 3.8 no soporta missing_ok
                if path_file.exists():
                    path_file.unlink()

        else:
            logger.error("Tarea inválida en handleFile: %s", tarea)

    except Exception as exc:
        logger.error(
            "Error en handleFile (tarea=%s, archivo=%s): %s",
            tarea,
            path_file,
            exc,
        )
        raise


def copiarArchivo(
    sourcePath: str,
    sourceFile: str,
    targetPath: str,
    targetFile: str,
    overwrite: bool = True,
) -> None:
    """
    Copia un archivo desde un origen a un destino.

    Parámetros
    ----------
    sourcePath : str
        Directorio origen.
    sourceFile : str
        Nombre de archivo origen.
    targetPath : str
        Directorio destino.
    targetFile : str
        Nombre de archivo destino.
    overwrite : bool, default True
        Si es False y el archivo destino existe, no se copia.

    Notas
    -----
    - Usa `shutil.copy2` para preservar metadatos.
    - Crea el directorio destino si no existe.
    """
    src = Path(sourcePath) / sourceFile
    dst = Path(targetPath) / targetFile

    if not src.exists():
        logger.error("Archivo origen no existe: %s", src)
        return

    if dst.exists() and not overwrite:
        logger.info("Archivo destino ya existe y overwrite=False: %s", dst)
        return

    try:
        dst.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(src, dst)
        logger.info("Archivo copiado de '%s' a '%s'", src, dst)
    except Exception as exc:
        logger.error("Error al copiar archivo de '%s' a '%s': %s", src, dst, exc)
        raise


def leer_directorio(
    directorio: str,
    recorrer_subcarpetas: bool = False,
    extension: str = "*",
) -> pd.DataFrame:
    """
    Devuelve un DataFrame con dos columnas: 'Directory' y 'File_Name'.

    Parámetros
    ----------
    directorio : str
        Ruta del directorio que se quiere leer.
    recorrer_subcarpetas : bool, default False
        Si es True, recorre subcarpetas también.
    extension : str, default "*"
        Tipo de archivo a buscar (ej. 'csv', 'xls', 'txt'). Usa '*' para todos.

    Notas
    -----
    - Usa `Path.glob` / `Path.rglob` para mejor performance.
    - Ignora entradas que no sean archivos.
    """

    ruta = Path(directorio)

    if not ruta.exists() or not ruta.is_dir():
        logger.error("Directorio inválido en leer_directorio: %s", ruta)
        return pd.DataFrame(columns=["Directory", "File_Name"])

    patron = f"*.{extension}" if extension != "*" else "*"
    iterador = ruta.rglob(patron) if recorrer_subcarpetas else ruta.glob(patron)

    archivos: list[tuple[str, str]] = []

    for archivo in iterador:
        try:
            if archivo.is_file():
                archivos.append((str(archivo.parent), archivo.name))
        except OSError as exc:
            logger.warning("No se pudo acceder a '%s': %s", archivo, exc)

    df = pd.DataFrame(archivos, columns=["Directory", "File_Name"])
    return df


__all__ = [
    "handleFile",
    "copiarArchivo",
    "leer_directorio",
]