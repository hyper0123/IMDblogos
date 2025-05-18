import re
from imdb import IMDb
from imdb._exceptions import IMDbDataAccessError
import os
import sys

# Inicializar cliente IMDbPY
ia = IMDb()
LATAM_CODES = {
    'Argentina', 'Mexico', 'Colombia', 'Chile', 'Peru', 'Venezuela', 'Uruguay',
    'Ecuador', 'Guatemala', 'Costa Rica', 'Panama', 'Paraguay', 'El Salvador',
    'Honduras', 'Nicaragua', 'Dominican Republic', 'Bolivia', 'Puerto Rico'
}

# Obtener título LATAM vía AKA
def titulo_latam_imdb(movie):
    akas = movie.get('akas') or []
    for aka in akas:
        m = re.match(r"^(.+?)\s*(.+?)$", aka)
        if m and m.group(2) in LATAM_CODES:
            return m.group(1)
    return None

# Procesar línea EXTINF
def procesar_extinf(line):
    try:
        meta, titulo = line.split(',', 1)
        titulo = titulo.strip()
        m = re.match(r"^(.+?)\s*(\d{4})$", titulo)
        query = m.group(1) if m else titulo

        # Búsqueda IMDb
        results = ia.search_movie(query)
        if not results:
            raise IMDbDataAccessError({'errmsg': 'No results'})
        movie = ia.get_movie(results[0].movieID)

        # Título en LATAM
        latam = titulo_latam_imdb(movie) or query
        nuevo_titulo = f"{latam} ({m.group(2)})" if m else latam

        # Género y póster
        genres = movie.get('genres') or []
        genero = genres[0] if genres else ''
        poster = movie.get('cover url') or ''

        # Reemplazar en metadata
        new_meta = re.sub(r'tvg-logo=\"[^\"]*\"', f'tvg-logo=\"{poster}\"', meta)
        new_group = re.sub(r'group-title=\"[^\"]*\"', f'group-title=\"{genero}\"', new_meta)
        return f"{new_group},{nuevo_titulo}"

    except (IMDbDataAccessError, Exception) as e:
        # Log de warning y fallback al original
        sys.stderr.write(f"⚠️ Warning procesando '{line}': {e}\n")
        return line

# Main
if __name__ == '__main__':
    in_file = os.getenv('INPUT_M3U_FILE', 'lista_original.m3u')
    out_file = os.getenv('INPUT_OUTPUT_FILE', 'lista_completa.m3u')
    if not os.path.exists(in_file):
        sys.stderr.write(f"❌ Archivo de entrada no encontrado: {in_file}\n")
        sys.exit(1)

    with open(in_file, encoding='utf-8') as fin, open(out_file, 'w', encoding='utf-8') as fout:
        for line in fin:
            if line.startswith('#EXTINF'):
                # Procesar con robustez ante errores
                processed = procesar_extinf(line.rstrip())
                fout.write(processed + '\n')
            else:
                fout.write(line)
    print(f"✅ Generado: {out_file}")
