#!/usr/bin/env python3
"""
Sonarr Agent - Relay entre GitHub Issues y Sonarr
Corre en la Raspberry Pi como servicio y ejecuta comandos enviados por Claude.

Configuración: edita las variables de la sección CONFIG o usa variables de entorno:
  GITHUB_TOKEN, GITHUB_REPO, SONARR_URL, SONARR_API_KEY
"""

import json
import os
import time
import urllib.request
import urllib.parse
import urllib.error

# ─── CONFIG ──────────────────────────────────────────────────────────────────

GITHUB_TOKEN   = os.getenv("GITHUB_TOKEN", "TU_GITHUB_TOKEN_AQUI")
GITHUB_REPO    = os.getenv("GITHUB_REPO", "numalias/Mervellous")
SONARR_URL     = os.getenv("SONARR_URL", "http://192.168.5.200:8989")
SONARR_API_KEY = os.getenv("SONARR_API_KEY", "4e0241f275944c83b775c024d5fa83c8")
POLL_INTERVAL  = int(os.getenv("POLL_INTERVAL", "20"))   # segundos entre comprobaciones
LABEL          = "sonarr-command"

# ─── GITHUB API ──────────────────────────────────────────────────────────────

GH_BASE = "https://api.github.com"

def gh_request(method, path, data=None):
    url = f"{GH_BASE}{path}"
    body = json.dumps(data).encode() if data else None
    headers = {
        "Authorization": f"token {GITHUB_TOKEN}",
        "Accept": "application/vnd.github+json",
        "Content-Type": "application/json",
        "User-Agent": "sonarr-agent/1.0",
    }
    req = urllib.request.Request(url, data=body, headers=headers, method=method)
    try:
        with urllib.request.urlopen(req, timeout=15) as r:
            return json.loads(r.read().decode())
    except urllib.error.HTTPError as e:
        print(f"[GitHub] Error {e.code}: {e.read().decode()[:200]}")
        return None

def get_pending_issues():
    issues = gh_request("GET", f"/repos/{GITHUB_REPO}/issues?labels={LABEL}&state=open&per_page=20")
    return issues or []

def comment_issue(number, body):
    gh_request("POST", f"/repos/{GITHUB_REPO}/issues/{number}/comments", {"body": body})

def close_issue(number, result_label="sonarr-done"):
    # Añadir label de resultado y cerrar
    gh_request("POST", f"/repos/{GITHUB_REPO}/issues/{number}/labels", {"labels": [result_label]})
    gh_request("PATCH", f"/repos/{GITHUB_REPO}/issues/{number}", {"state": "closed"})

def ensure_labels():
    """Crea los labels necesarios si no existen."""
    for label, color, desc in [
        (LABEL,         "0075ca", "Comando pendiente para Sonarr"),
        ("sonarr-done",  "0e8a16", "Comando ejecutado correctamente"),
        ("sonarr-error", "e4e669", "El comando falló"),
    ]:
        gh_request("POST", f"/repos/{GITHUB_REPO}/labels", {
            "name": label, "color": color, "description": desc
        })

# ─── SONARR API ──────────────────────────────────────────────────────────────

SONARR_HEADERS = {"X-Api-Key": SONARR_API_KEY, "Content-Type": "application/json"}

def sonarr_request(method, endpoint, data=None):
    url = f"{SONARR_URL}/api/v3{endpoint}"
    body = json.dumps(data).encode() if data else None
    req = urllib.request.Request(url, data=body, headers=SONARR_HEADERS, method=method)
    try:
        with urllib.request.urlopen(req, timeout=15) as r:
            return json.loads(r.read().decode())
    except urllib.error.HTTPError as e:
        raise RuntimeError(f"Sonarr {e.code}: {e.read().decode()[:300]}")

def sonarr_get(ep):    return sonarr_request("GET", ep)
def sonarr_post(ep, d): return sonarr_request("POST", ep, d)
def sonarr_delete(ep):  return sonarr_request("DELETE", ep)

# ─── COMANDOS ────────────────────────────────────────────────────────────────

def cmd_buscar(query):
    q = urllib.parse.quote(query)
    resultados = sonarr_get(f"/series/lookup?term={q}")[:8]
    if not resultados:
        return f"No se encontraron resultados para **{query}**."
    lines = [f"Resultados para **{query}**:\n",
             "| TVDB ID | Título | Año | Estado |",
             "|---------|--------|-----|--------|"]
    for s in resultados:
        lines.append(f"| {s.get('tvdbId','?')} | {s.get('title','?')} | {s.get('year','?')} | {s.get('status','?')} |")
    return "\n".join(lines)

def cmd_añadir(tvdb_id, perfil_calidad=None, ruta=None):
    resultados = sonarr_get(f"/series/lookup?term=tvdb:{tvdb_id}")
    if not resultados:
        return f"No se encontró serie con TVDB ID {tvdb_id}."
    serie = resultados[0]
    titulo = serie.get("title", "Desconocida")

    # Comprobar si ya existe
    existentes = sonarr_get("/series")
    if any(s.get("tvdbId") == int(tvdb_id) for s in existentes):
        return f"⚠️ **{titulo}** ya está en Sonarr."

    if not ruta:
        carpetas = sonarr_get("/rootfolder")
        if not carpetas:
            return "No hay carpetas raíz configuradas en Sonarr."
        ruta = carpetas[0]["path"]

    if perfil_calidad is None:
        perfiles = sonarr_get("/qualityprofile")
        perfil_calidad = perfiles[0]["id"] if perfiles else 1

    payload = {
        "title": serie["title"],
        "tvdbId": serie["tvdbId"],
        "qualityProfileId": int(perfil_calidad),
        "rootFolderPath": ruta,
        "monitored": True,
        "addOptions": {
            "searchForMissingEpisodes": True,
            "searchForCutoffUnmetEpisodes": False,
            "monitor": "all"
        },
        "seasons": serie.get("seasons", []),
        "images": serie.get("images", []),
        "titleSlug": serie.get("titleSlug", ""),
    }

    resultado = sonarr_post("/series", payload)
    return (f"✅ **{titulo}** añadida correctamente.\n"
            f"- ID interno: {resultado.get('id')}\n"
            f"- Ruta: {resultado.get('path')}\n"
            f"- Estado: {resultado.get('status')}\n"
            f"- Temporadas: {len(resultado.get('seasons', []))}")

def cmd_listar():
    series = sonarr_get("/series")
    if not series:
        return "No hay series en Sonarr."
    lines = [f"**{len(series)} series en Sonarr:**\n",
             "| ID | Título | Estado | Eps |",
             "|----|--------|--------|-----|"]
    for s in sorted(series, key=lambda x: x.get("title", "")):
        ep_f = s.get("episodeFileCount", 0)
        ep_t = s.get("episodeCount", 0)
        lines.append(f"| {s['id']} | {s['title']} | {s.get('status','?')} | {ep_f}/{ep_t} |")
    return "\n".join(lines)

def cmd_eliminar(serie_id, borrar_archivos=False):
    series = sonarr_get("/series")
    serie = next((s for s in series if s["id"] == int(serie_id)), None)
    if not serie:
        return f"No se encontró serie con ID {serie_id}."
    params = f"?deleteFiles={'true' if borrar_archivos else 'false'}&addImportExclusion=false"
    sonarr_delete(f"/series/{serie_id}{params}")
    return f"🗑️ **{serie['title']}** eliminada de Sonarr."

def cmd_cola():
    cola = sonarr_get("/queue?includeUnknownSeriesItems=false")
    items = cola.get("records", [])
    if not items:
        return "La cola de descargas está vacía."
    lines = [f"**{len(items)} descarga(s) en cola:**\n",
             "| Serie | Episodio | Estado | Progreso |",
             "|-------|----------|--------|----------|"]
    for item in items:
        serie = item.get("series", {}).get("title", "?")
        ep = item.get("episode", {})
        episodio = f"S{ep.get('seasonNumber','?'):02}E{ep.get('episodeNumber','?'):02}" if ep else "?"
        estado = item.get("status", "?")
        size = item.get("size", 0)
        restante = item.get("sizeleft", 0)
        progreso = f"{((size - restante) / size * 100):.0f}%" if size > 0 else "?"
        lines.append(f"| {serie} | {episodio} | {estado} | {progreso} |")
    return "\n".join(lines)

def cmd_estado():
    info = sonarr_get("/system/status")
    disco = sonarr_get("/diskspace")
    lines = [
        "**Estado de Sonarr:**",
        f"- Versión: {info.get('version')}",
        f"- OS: {info.get('osName')} {info.get('osVersion')}",
        f"- URL: {SONARR_URL}",
        "",
        "**Espacio en disco:**",
    ]
    for d in disco:
        libre = d.get("freeSpace", 0) / 1e9
        total = d.get("totalSpace", 0) / 1e9
        lines.append(f"- {d.get('path')}: {libre:.1f} GB libres / {total:.1f} GB total")
    return "\n".join(lines)

def cmd_buscar_ep(serie_id):
    sonarr_post("/command", {"name": "SeriesSearch", "seriesId": int(serie_id)})
    series = sonarr_get("/series")
    serie = next((s for s in series if s["id"] == int(serie_id)), None)
    nombre = serie["title"] if serie else f"ID {serie_id}"
    return f"🔍 Búsqueda lanzada para **{nombre}**."

# ─── DISPATCHER ──────────────────────────────────────────────────────────────

def ejecutar_comando(cmd_data):
    """
    cmd_data es un dict con al menos {"action": "..."}
    Acciones: buscar, añadir, listar, eliminar, cola, estado, buscar_ep
    """
    action = cmd_data.get("action", "").lower()

    if action == "buscar":
        return cmd_buscar(cmd_data["query"])
    elif action in ("añadir", "add"):
        return cmd_añadir(
            cmd_data["tvdb_id"],
            perfil_calidad=cmd_data.get("quality_profile_id"),
            ruta=cmd_data.get("root_folder")
        )
    elif action == "listar":
        return cmd_listar()
    elif action == "eliminar":
        return cmd_eliminar(cmd_data["serie_id"], cmd_data.get("delete_files", False))
    elif action == "cola":
        return cmd_cola()
    elif action == "estado":
        return cmd_estado()
    elif action == "buscar_ep":
        return cmd_buscar_ep(cmd_data["serie_id"])
    else:
        return f"Acción desconocida: `{action}`"

def parse_command(issue_body):
    """Extrae el bloque JSON del cuerpo del issue."""
    # Busca un bloque ```json ... ```
    import re
    match = re.search(r"```(?:json)?\s*(\{.*?\})\s*```", issue_body, re.DOTALL)
    if match:
        return json.loads(match.group(1))
    # Intenta parsear el cuerpo completo como JSON
    return json.loads(issue_body.strip())

# ─── MAIN LOOP ───────────────────────────────────────────────────────────────

def process_issue(issue):
    number = issue["number"]
    title = issue["title"]
    body = issue.get("body", "")
    print(f"[Issue #{number}] {title}")

    try:
        cmd_data = parse_command(body)
        result = ejecutar_comando(cmd_data)
        comment_issue(number, f"### ✅ Resultado\n\n{result}")
        close_issue(number, "sonarr-done")
        print(f"  -> OK")
    except json.JSONDecodeError as e:
        msg = f"No se pudo parsear el comando JSON: {e}\n\nCuerpo recibido:\n```\n{body[:500]}\n```"
        comment_issue(number, f"### ❌ Error\n\n{msg}")
        close_issue(number, "sonarr-error")
        print(f"  -> JSON error: {e}")
    except Exception as e:
        comment_issue(number, f"### ❌ Error\n\n{e}")
        close_issue(number, "sonarr-error")
        print(f"  -> Error: {e}")

def main():
    print(f"Sonarr Agent iniciado")
    print(f"  Repo:    {GITHUB_REPO}")
    print(f"  Sonarr:  {SONARR_URL}")
    print(f"  Polling: cada {POLL_INTERVAL}s")

    ensure_labels()

    processed = set()
    while True:
        try:
            issues = get_pending_issues()
            for issue in issues:
                n = issue["number"]
                if n not in processed:
                    processed.add(n)
                    process_issue(issue)
        except Exception as e:
            print(f"[Loop] Error: {e}")
        time.sleep(POLL_INTERVAL)

if __name__ == "__main__":
    main()
