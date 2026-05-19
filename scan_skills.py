import os
import json
import httpx

SKILLGUARD_API = "https://web-production-cf779.up.railway.app"
GITHUB_TOKEN = os.environ["GITHUB_TOKEN"]
PR_NUMBER = os.environ["PR_NUMBER"]
REPO = os.environ["REPO"]
FILES = os.environ["FILES"].split()

def scan_skill(file_path: str) -> dict:
    """Escanea un skill usando la API de SkillGuard."""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            contenido = f.read()

        response = httpx.post(
            f"{SKILLGUARD_API}/scan/content",
            json={"contenido": contenido, "nombre": file_path},
            timeout=60
        )
        return response.json()
    except Exception as e:
        return {"ok": False, "error": str(e), "veredicto": "ERROR", "score": 0}


def get_emoji(veredicto: str) -> str:
    emojis = {
        "LIMPIO": "✅",
        "BAJO RIESGO": "⚠️",
        "SOSPECHOSO": "🚨",
        "ALTO RIESGO": "☠️",
        "ERROR": "❌"
    }
    return emojis.get(veredicto, "❓")


def format_comment(resultados: list) -> str:
    lines = [
        "## 🛡️ SkillGuard — Análisis de Seguridad",
        "",
        "Se han analizado los siguientes skills modificados en este PR:",
        "",
    ]

    for r in resultados:
        emoji = get_emoji(r["veredicto"])
        lines.append(f"### {emoji} `{r['file']}`")
        lines.append(f"**Score:** {r['score']}/100 | **Veredicto:** {r['veredicto']}")
        lines.append("")

        if r.get("resumen"):
            lines.append(f"> {r['resumen']}")
            lines.append("")

        flags_estaticos = r.get("flags_estaticos", [])
        flags_semanticos = r.get("flags_semanticos", [])
        total_flags = len(flags_estaticos) + len(flags_semanticos)

        if total_flags > 0:
            lines.append(f"**{total_flags} flags detectados:**")
            lines.append("")

            for flag in flags_estaticos[:5]:
                sev = flag.get("severidad", "LOW")
                cat = flag.get("categoria", "")
                linea = flag.get("linea", "?")
                desc = flag.get("descripcion", "")
                lines.append(f"- `[{sev}]` **{cat}** (línea {linea}): {desc}")

            for flag in flags_semanticos[:5]:
                sev = flag.get("severidad", "LOW")
                cat = flag.get("categoria", "")
                linea = flag.get("linea", "?")
                exp = flag.get("explicacion", "")
                lines.append(f"- `[{sev}]` **{cat}** (línea {linea}): {exp}")

            if total_flags > 10:
                lines.append(f"- _... y {total_flags - 10} flags más_")
        else:
            lines.append("No se detectaron amenazas en este skill.")

        lines.append("")
        lines.append("---")
        lines.append("")

    lines.append("_Análisis realizado por [SkillGuard](https://skillguard-frontend.vercel.app) — Seguridad para la era de los agentes IA_")

    return "\n".join(lines)


def post_comment(comment: str):
    """Publica el comentario en el PR."""
    url = f"https://api.github.com/repos/{REPO}/issues/{PR_NUMBER}/comments"
    headers = {
        "Authorization": f"token {GITHUB_TOKEN}",
        "Accept": "application/vnd.github.v3+json"
    }
    response = httpx.post(url, json={"body": comment}, headers=headers, timeout=15)
    if response.status_code == 201:
        print("✅ Comentario publicado en el PR")
    else:
        print(f"❌ Error publicando comentario: {response.status_code}")


def main():
    if not FILES:
        print("No hay archivos SKILL.md modificados")
        return

    print(f"🔍 Escaneando {len(FILES)} skill(s)...")
    resultados = []

    for file_path in FILES:
        if not os.path.exists(file_path):
            print(f"⚠️ Archivo no encontrado: {file_path}")
            continue

        print(f"  Analizando {file_path}...")
        resultado = scan_skill(file_path)
        resultado["file"] = file_path
        resultados.append(resultado)

        emoji = get_emoji(resultado.get("veredicto", "ERROR"))
        print(f"  {emoji} Score: {resultado.get('score', 0)}/100 — {resultado.get('veredicto', 'ERROR')}")

    if resultados:
        comment = format_comment(resultados)
        post_comment(comment)


if __name__ == "__main__":
    main()