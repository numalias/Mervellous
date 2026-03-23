#!/usr/bin/env python3
"""
Sonarr Manager - Herramienta de gestión para Sonarr
Uso: python3 sonarr_manager.py [comando] [argumentos]
"""

import sys
import json
import argparse
import urllib.request
import urllib.parse
import urllib.error

SONARR_URL = "http://192.168.5.200:8989"
API_KEY = "4e0241f275944c83b775c024d5fa83c8"
BASE = f"{SONARR_URL}/api/v3"
HEADERS = {"X-Api-Key": API_KEY, "Content-Type": "application/json"}


def request(method, endpoint, data=None):
    url = f"{BASE}{endpoint}"
    body = json.dumps(data).encode() if data else None
    req = urllib.request.Request(url, data=body, headers=HEADERS, method=method)
    try:
        with urllib.request.urlopen(req, timeout=10) as r:
            return json.loads(r.read().decode())
    except urllib.error.HTTPError as e:
        print(f"Error {e.code}: {e.read().decode()}")
        sys.exit(1)


def get(endpoint):
    return request("GET", endpoint)


def post(endpoint, data):
    return request("POST", endpoint, data)


def delete(endpoint):
    return request("DELETE", endpoint)


# ─── SERIES ──────────────────────────────────────────────────────────────────

def buscar_serie(nombre):
    """Busca una serie en TVDB por nombre."""
    q = urllib.parse.quote(nombre)
    resultados = get(f"/series/lookup?term={q}")
    if not resultados:
        print("No se encontraron resultados.")
        return
    print(f"\n{'ID TVDB':<12} {'Título':<40} {'Año':<6} {'Estado'}")
    print("─" * 75)
    for s in resultados[:10]:
        tvdb = s.get("tvdbId", "N/A")
        titulo = s.get("title", "?")[:38]
        año = s.get("year", "?")
        estado = s.get("status", "?")
        print(f"{tvdb:<12} {titulo:<40} {año:<6} {estado}")


def añadir_serie(tvdb_id, ruta=None, perfil_calidad=1, monitoreada=True):
    """Añade una serie a Sonarr por su TVDB ID."""
    # Buscar info de la serie
    resultados = get(f"/series/lookup?term=tvdb:{tvdb_id}")
    if not resultados:
        print(f"No se encontró serie con TVDB ID {tvdb_id}")
        sys.exit(1)

    serie = resultados[0]
    titulo = serie.get("title", "Desconocida")

    # Obtener ruta raíz si no se especifica
    if not ruta:
        carpetas = get("/rootfolder")
        if not carpetas:
            print("No hay carpetas raíz configuradas en Sonarr.")
            sys.exit(1)
        ruta = carpetas[0]["path"]

    payload = {
        "title": serie["title"],
        "tvdbId": serie["tvdbId"],
        "qualityProfileId": perfil_calidad,
        "rootFolderPath": ruta,
        "monitored": monitoreada,
        "addOptions": {
            "searchForMissingEpisodes": True,
            "searchForCutoffUnmetEpisodes": False,
            "monitor": "all"
        },
        "seasons": serie.get("seasons", []),
        "images": serie.get("images", []),
        "titleSlug": serie.get("titleSlug", ""),
    }

    resultado = post("/series", payload)
    print(f"\n✓ Serie añadida: {titulo}")
    print(f"  ID interno: {resultado.get('id')}")
    print(f"  Ruta: {resultado.get('path')}")
    print(f"  Estado: {resultado.get('status')}")


def listar_series():
    """Lista todas las series monitoreadas."""
    series = get("/series")
    if not series:
        print("No hay series en Sonarr.")
        return
    print(f"\n{'ID':<6} {'Título':<45} {'Estado':<12} {'Temporadas':<12} {'Episodios'}")
    print("─" * 90)
    for s in sorted(series, key=lambda x: x.get("title", "")):
        sid = s.get("id", "?")
        titulo = s.get("title", "?")[:43]
        estado = s.get("status", "?")
        temporadas = s.get("seasonCount", "?")
        eps_total = s.get("episodeCount", 0)
        eps_file = s.get("episodeFileCount", 0)
        print(f"{sid:<6} {titulo:<45} {estado:<12} {temporadas:<12} {eps_file}/{eps_total}")


def eliminar_serie(serie_id, borrar_archivos=False):
    """Elimina una serie de Sonarr."""
    params = f"?deleteFiles={'true' if borrar_archivos else 'false'}&addImportExclusion=false"
    series = get("/series")
    serie = next((s for s in series if s["id"] == serie_id), None)
    if not serie:
        print(f"No se encontró serie con ID {serie_id}")
        sys.exit(1)
    delete(f"/series/{serie_id}{params}")
    print(f"✓ Serie eliminada: {serie.get('title')}")


# ─── CALIDAD ─────────────────────────────────────────────────────────────────

def listar_perfiles_calidad():
    """Lista perfiles de calidad disponibles."""
    perfiles = get("/qualityprofile")
    print(f"\n{'ID':<6} {'Nombre'}")
    print("─" * 30)
    for p in perfiles:
        print(f"{p['id']:<6} {p['name']}")


# ─── INDEXERS ────────────────────────────────────────────────────────────────

def listar_indexers():
    """Lista los indexers de torrent configurados."""
    indexers = get("/indexer")
    if not indexers:
        print("No hay indexers configurados.")
        return
    print(f"\n{'ID':<6} {'Nombre':<35} {'Habilitado':<12} {'Prioridad'}")
    print("─" * 65)
    for i in indexers:
        print(f"{i['id']:<6} {i['name'][:33]:<35} {'Sí' if i['enableRss'] else 'No':<12} {i.get('priority', '?')}")


def añadir_indexer_torznab(nombre, url_torznab, api_key_indexer, categorias="5000,5010,5020,5030,5040"):
    """
    Añade un indexer Torznab (compatible con Jackett/Prowlarr).
    url_torznab: URL del feed Torznab, ej: http://localhost:9117/api/v2.0/indexers/eztv/results/torznab/
    """
    payload = {
        "name": nombre,
        "implementation": "Torznab",
        "configContract": "TorznabSettings",
        "enableRss": True,
        "enableAutomaticSearch": True,
        "enableInteractiveSearch": True,
        "priority": 25,
        "fields": [
            {"name": "baseUrl", "value": url_torznab},
            {"name": "apiPath", "value": "/api"},
            {"name": "apiKey", "value": api_key_indexer},
            {"name": "categories", "value": [int(c) for c in categorias.split(",")]},
            {"name": "animeCategories", "value": []},
            {"name": "removeYear", "value": False},
        ],
        "protocol": "torrent",
        "supportsRss": True,
        "supportsSearch": True,
    }
    resultado = post("/indexer", payload)
    print(f"\n✓ Indexer añadido: {resultado.get('name')} (ID: {resultado.get('id')})")


def eliminar_indexer(indexer_id):
    """Elimina un indexer por ID."""
    delete(f"/indexer/{indexer_id}")
    print(f"✓ Indexer {indexer_id} eliminado.")


# ─── COLA / DESCARGAS ────────────────────────────────────────────────────────

def ver_cola():
    """Muestra la cola de descargas activa."""
    cola = get("/queue?includeUnknownSeriesItems=false")
    items = cola.get("records", [])
    if not items:
        print("La cola de descargas está vacía.")
        return
    print(f"\n{'ID':<8} {'Serie':<35} {'Episodio':<20} {'Estado':<15} {'Progreso'}")
    print("─" * 90)
    for item in items:
        iid = item.get("id", "?")
        serie = (item.get("series", {}).get("title", "?") or "?")[:33]
        ep = item.get("episode", {})
        episodio = f"S{ep.get('seasonNumber','?'):02}E{ep.get('episodeNumber','?'):02}" if ep else "?"
        estado = item.get("status", "?")
        size = item.get("size", 0)
        restante = item.get("sizeleft", 0)
        progreso = f"{((size - restante) / size * 100):.0f}%" if size > 0 else "?"
        print(f"{iid:<8} {serie:<35} {episodio:<20} {estado:<15} {progreso}")


def busqueda_manual(serie_id):
    """Lanza búsqueda manual de episodios que faltan para una serie."""
    post("/command", {"name": "SeriesSearch", "seriesId": serie_id})
    print(f"✓ Búsqueda lanzada para serie ID {serie_id}")


# ─── ESTADO ──────────────────────────────────────────────────────────────────

def estado_sistema():
    """Muestra el estado general del sistema Sonarr."""
    info = get("/system/status")
    disco = get("/diskspace")
    print("\n── Estado de Sonarr ──────────────────────────────")
    print(f"  Versión:    {info.get('version')}")
    print(f"  OS:         {info.get('osName')} {info.get('osVersion')}")
    print(f"  Plataforma: {info.get('runtimeVersion')}")
    print(f"  URL:        {SONARR_URL}")
    print("\n── Espacio en disco ──────────────────────────────")
    for d in disco:
        total = d.get("totalSpace", 0) / 1e9
        libre = d.get("freeSpace", 0) / 1e9
        print(f"  {d.get('path'):<30} Libre: {libre:.1f} GB / {total:.1f} GB")


# ─── MAIN ─────────────────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(
        description="Sonarr Manager - Gestión de series y torrents",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Ejemplos:
  python3 sonarr_manager.py estado
  python3 sonarr_manager.py series
  python3 sonarr_manager.py buscar "Breaking Bad"
  python3 sonarr_manager.py añadir 81189
  python3 sonarr_manager.py añadir 81189 --perfil 1
  python3 sonarr_manager.py eliminar 5
  python3 sonarr_manager.py calidades
  python3 sonarr_manager.py indexers
  python3 sonarr_manager.py add-indexer "EZTV" "http://jackett:9117/api/..." "mi_api_key"
  python3 sonarr_manager.py del-indexer 3
  python3 sonarr_manager.py cola
  python3 sonarr_manager.py buscar-ep 5
        """
    )

    sub = parser.add_subparsers(dest="cmd")

    sub.add_parser("estado", help="Estado del sistema Sonarr")
    sub.add_parser("series", help="Listar todas las series")
    sub.add_parser("calidades", help="Listar perfiles de calidad")
    sub.add_parser("indexers", help="Listar indexers de torrent")
    sub.add_parser("cola", help="Ver cola de descargas")

    p_buscar = sub.add_parser("buscar", help="Buscar serie por nombre")
    p_buscar.add_argument("nombre", help="Nombre de la serie")

    p_add = sub.add_parser("añadir", help="Añadir serie por TVDB ID")
    p_add.add_argument("tvdb_id", type=int, help="ID de TVDB")
    p_add.add_argument("--perfil", type=int, default=1, help="ID perfil de calidad (default: 1)")
    p_add.add_argument("--ruta", help="Ruta raíz (opcional, usa la primera por defecto)")

    p_del = sub.add_parser("eliminar", help="Eliminar serie por ID interno")
    p_del.add_argument("id", type=int, help="ID interno de la serie en Sonarr")
    p_del.add_argument("--borrar-archivos", action="store_true", help="Eliminar también los archivos")

    p_idx = sub.add_parser("add-indexer", help="Añadir indexer Torznab (Jackett/Prowlarr)")
    p_idx.add_argument("nombre", help="Nombre del indexer")
    p_idx.add_argument("url", help="URL Torznab")
    p_idx.add_argument("apikey", help="API Key del indexer")
    p_idx.add_argument("--cats", default="5000,5010,5020,5030,5040", help="Categorías (default: 5000,5010,5020,5030,5040)")

    p_delidx = sub.add_parser("del-indexer", help="Eliminar indexer por ID")
    p_delidx.add_argument("id", type=int, help="ID del indexer")

    p_busep = sub.add_parser("buscar-ep", help="Lanzar búsqueda manual para una serie")
    p_busep.add_argument("id", type=int, help="ID interno de la serie")

    args = parser.parse_args()

    if not args.cmd:
        parser.print_help()
        return

    if args.cmd == "estado":
        estado_sistema()
    elif args.cmd == "series":
        listar_series()
    elif args.cmd == "calidades":
        listar_perfiles_calidad()
    elif args.cmd == "indexers":
        listar_indexers()
    elif args.cmd == "cola":
        ver_cola()
    elif args.cmd == "buscar":
        buscar_serie(args.nombre)
    elif args.cmd == "añadir":
        añadir_serie(args.tvdb_id, ruta=args.ruta, perfil_calidad=args.perfil)
    elif args.cmd == "eliminar":
        eliminar_serie(args.id, borrar_archivos=args.borrar_archivos)
    elif args.cmd == "add-indexer":
        añadir_indexer_torznab(args.nombre, args.url, args.apikey, args.cats)
    elif args.cmd == "del-indexer":
        eliminar_indexer(args.id)
    elif args.cmd == "buscar-ep":
        busqueda_manual(args.id)


if __name__ == "__main__":
    main()
