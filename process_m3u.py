import re
from imdb import IMDb
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
    meta, titulo = line.split(',', 1)
    titulo = titulo.strip()
    m = re.match(r"^(.+?)\s*(\d{4})$", titulo)
    query = m.group(1) if m else titulo

    results = ia.search_movie(query)
    if not results:
        return line
    movie = ia.get_movie(results[0].movieID)

    latam = titulo_latam_imdb(movie) or query
    nuevo_titulo = f"{latam} ({m.group(2)})" if m else latam

    genres = movie.get('genres') or []
    genero = genres[0] if genres else ''

    poster = movie.get('cover url') or ''

    new_meta = re.sub(r'tvg-logo=\"[^\"]*\"', f'tvg-logo=\"{poster}\"', meta)
    new_group = re.sub(r'group-title=\"[^\"]*\"', f'group-title=\"{genero}\"', new_meta)
    return f"{new_group},{nuevo_titulo}"

# Main
if __name__ == '__main__':
    in_file = os.getenv('INPUT_M3U_FILE', 'lista_original.m3u')
    out_file = os.getenv('INPUT_OUTPUT_FILE', 'lista_completa.m3u')
    if not os.path.exists(in_file):
        print(f"❌ Archivo de entrada no encontrado: {in_file}")
        sys.exit(1)
    with open(in_file, encoding='utf-8') as fin, open(out_file, 'w', encoding='utf-8') as fout:
        for line in fin:
            if line.startswith('#EXTINF'):
                fout.write(procesar_extinf(line.rstrip()) + '\n')
            else:
                fout.write(line)
    print(f"✅ Generado: {out_file}")
