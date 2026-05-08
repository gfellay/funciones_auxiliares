from __future__ import annotations

import pandas as pd
from pandas.api.types import is_string_dtype, is_numeric_dtype
from pathlib import Path
import logging
import re

logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# formatearDF
# ---------------------------------------------------------------------------

def formatearDF(df: pd.DataFrame) -> pd.DataFrame:
    """
    Limpia columnas de texto eliminando caracteres especiales y espacios.
    Solo aplica a columnas de tipo string.

    Mejoras:
    - Regex compilada una sola vez.
    - Evita conversiones innecesarias.
    - No modifica el DataFrame original (devuelve copia).
    """
    caracteres = re.compile(r"[,\uFF0C\n\t'\"€£*$%&#|;]+")

    df = df.copy()

    for col in df.columns:
        if is_string_dtype(df[col]):
            df[col] = (
                df[col]
                .astype(str)
                .str.strip()
                .str.replace(caracteres, "", regex=True)
            )

    return df


# ---------------------------------------------------------------------------
# formatear_columna_numerica
# ---------------------------------------------------------------------------

def formatear_columna_numerica(serie: pd.Series) -> pd.Series:
    """
    Convierte una columna a formato numérico robusto.

    Mejoras:
    - Manejo de negativos al final (ej: '123-').
    - Limpieza de comas y símbolos.
    - No falla si la serie ya es numérica.
    - Devuelve siempre una serie numérica sin NaN.
    """
    if is_numeric_dtype(serie):
        return serie.fillna(0)

    serie = serie.astype(str)

    # Normalizar negativos al final
    serie = serie.str.replace(r"^(\d+[.,]?\d*)-$", r"-\1", regex=True)

    # Eliminar comas y símbolos
    serie = serie.str.replace(r"[^\d\.-]", "", regex=True)

    serie = pd.to_numeric(serie, errors="coerce")

    return serie.fillna(0)


# ---------------------------------------------------------------------------
# leer_csv_sin_Pandas
# ---------------------------------------------------------------------------

def leer_csv_sin_Pandas(
    filepath: str,
    sep: str | None = None,
    strip: bool = True,
    grabar: bool = False,
) -> pd.DataFrame:
    """
    Parser robusto para archivos LISTA (ALV) exportados desde SAP.

    Mejoras:
    - Lectura binaria con autodetección de encoding.
    - Limpieza de líneas más eficiente.
    - Detección de cabecera más robusta.
    - Normalización de filas más rápida.
    - Uso de formatearDF al final.
    """

    # -------------------------
    # Leer archivo como texto
    # -------------------------
    def _read_text_sap(path: str) -> list[str]:
        raw = Path(path).read_bytes()

        if raw.startswith(b"\xff\xfe") or raw.startswith(b"\xfe\xff"):
            text = raw.decode("utf-16")
        elif raw.startswith(b"\xef\xbb\xbf"):
            text = raw.decode("utf-8-sig")
        else:
            text = raw.decode("cp1252", errors="replace")

        return text.splitlines()

    raw_lines = _read_text_sap(filepath)

    # -------------------------
    # Limpieza de líneas
    # -------------------------
    def _clean(line: str) -> str:
        line = line.replace("\u00A0", " ").strip()
        if line == "\\":
            return ""
        if line.startswith("\\"):
            line = line[1:].lstrip()
        if line.endswith("\\"):
            line = line[:-1].rstrip()
        return line

    lines = [_clean(l) for l in raw_lines]

    # -------------------------
    # Detectar cabecera
    # -------------------------
    header_idx = None
    data_start_idx = None

    for i in range(len(lines) - 2):
        l1, l2, l3 = lines[i].strip(), lines[i+1].strip(), lines[i+2].strip()

        if (
            re.fullmatch(r"-{5,}", l1)
            and l2
            and not re.fullmatch(r"-{5,}", l2)
            and re.fullmatch(r"-{5,}", l3)
        ):
            header_idx = i + 1
            data_start_idx = i + 3
            break

    if header_idx is None:
        raise ValueError("No se encontró cabecera válida (guiones → texto → guiones).")

    header_line = lines[header_idx]

    # -------------------------
    # Autodetectar separador
    # -------------------------
    if sep is None:
        candidates = ["|", "\t", ";", ","]
        sep = max(candidates, key=lambda c: header_line.count(c))

    headers = [h.strip() for h in header_line.strip(sep).split(sep)]

    # -------------------------
    # Parsear datos
    # -------------------------
    data = []
    for l in lines[data_start_idx:]:
        if not l.strip() or re.fullmatch(r"-{5,}", l.strip()):
            continue

        row = [v.strip() for v in l.strip(sep).split(sep)]

        # Normalizar longitud
        if len(row) < len(headers):
            row += [""] * (len(headers) - len(row))
        else:
            row = row[:len(headers)]

        data.append(row)

    df = pd.DataFrame(data, columns=headers)

    # -------------------------
    # Formateo final
    # -------------------------
    df = formatearDF(df)

    if grabar:
        df.to_csv(filepath, sep=sep, index=False, encoding="utf-8-sig")

    return df


__all__ = [
    "formatearDF",
    "formatear_columna_numerica",
    "leer_csv_sin_Pandas",
]