import json
import os
import urllib.parse
import urllib.request
import xml.etree.ElementTree as ET
import html
import re

CHAT_ID = "-1001243627353"

FUENTES = [
    {
        "nombre": "La Comuna 11",
        "url": "https://lacomuna11.com.ar/feed/",
    },
    {
        "nombre": "VDP",
        "url": "https://vdp.com.ar/feed/",
    },
]

ARCHIVO_PUBLICADAS = "noticias_publicadas.json"

# Palabras que ayudan a confirmar que hablamos de Villa del Parque, CABA.
PALABRAS_VDP = [
    "villa del parque",
    "cuenca",
    "nogoyá",
    "nogoya",
    "nazca",
    "beiró",
    "beiro",
    "san martín",
    "san martin",
    "comuna 11",
]


def descargar(url):
    req = urllib.request.Request(
        url,
        headers={
            "User-Agent": "Mozilla/5.0 VillaDelParqueBot/1.0"
        },
    )

    with urllib.request.urlopen(req, timeout=30) as response:
        return response.read()


def limpiar_html(texto):
    if not texto:
        return ""

    texto = re.sub(r"<[^>]+>", " ", texto)
    texto = html.unescape(texto)
    texto = re.sub(r"\s+", " ", texto)

    return texto.strip()


def leer_feed(fuente):
    contenido = descargar(fuente["url"])
    root = ET.fromstring(contenido)

    noticias = []

    for item in root.findall(".//item"):

        titulo = limpiar_html(
            item.findtext("title", "")
        )

        enlace = item.findtext("link", "").strip()

        descripcion = limpiar_html(
            item.findtext("description", "")
        )

        noticias.append({
            "titulo": titulo,
            "enlace": enlace,
            "descripcion": descripcion,
            "fuente": fuente["nombre"],
        })

    return noticias


def es_villa_del_parque(noticia):

    texto = (
        noticia["titulo"]
        + " "
        + noticia["descripcion"]
    ).lower()

    return any(
        palabra in texto
        for palabra in PALABRAS_VDP
    )


def cargar_publicadas():

    if not os.path.exists(ARCHIVO_PUBLICADAS):
        return []

    try:
        with open(
            ARCHIVO_PUBLICADAS,
            "r",
            encoding="utf-8",
        ) as archivo:

            return json.load(archivo)

    except Exception:
        return []


def guardar_publicadas(publicadas):

    with open(
        ARCHIVO_PUBLICADAS,
        "w",
        encoding="utf-8",
    ) as archivo:

        json.dump(
            publicadas[-500:],
            archivo,
            ensure_ascii=False,
            indent=2,
        )


def enviar_telegram(token, noticia):

    descripcion = noticia["descripcion"]

    if len(descripcion) > 450:
        descripcion = descripcion[:447] + "..."

    texto = (
        "📰 <b>NOTICIAS DE VILLA DEL PARQUE</b>\n\n"
        f"<b>{html.escape(noticia['titulo'])}</b>\n\n"
    )

    if descripcion:
        texto += html.escape(descripcion) + "\n\n"

    texto += (
        f"🗞 <b>Fuente:</b> "
        f"{html.escape(noticia['fuente'])}\n"
        f'🔗 <a href="{html.escape(noticia["enlace"])}">'
        "Leer noticia completa</a>"
    )

    datos = urllib.parse.urlencode({
        "chat_id": CHAT_ID,
        "text": texto,
        "parse_mode": "HTML",
        "disable_web_page_preview": "false",
    }).encode()

    url = (
        "https://api.telegram.org/"
        f"bot{token}/sendMessage"
    )

    req = urllib.request.Request(
        url,
        data=datos,
    )

    with urllib.request.urlopen(
        req,
        timeout=30,
    ) as response:

        return json.loads(
            response.read().decode("utf-8")
        )


def main():

    token = os.environ[
        "TELEGRAM_BOT_TOKEN"
    ].strip()

    publicadas = cargar_publicadas()

    nuevas = []

    for fuente in FUENTES:

        try:
            noticias = leer_feed(fuente)

            for noticia in noticias:

                if not noticia["enlace"]:
                    continue

                if noticia["enlace"] in publicadas:
                    continue

                if not es_villa_del_parque(noticia):
                    continue

                nuevas.append(noticia)

        except Exception as error:
            print(
                f"Error leyendo "
                f"{fuente['nombre']}: {error}"
            )

    # En la primera ejecución NO inundamos
    # el grupo con noticias antiguas.
    if not publicadas:

        for noticia in nuevas:
            publicadas.append(
                noticia["enlace"]
            )

        guardar_publicadas(publicadas)

        print(
            "Primera ejecución: "
            "se registraron las noticias existentes."
        )

        return

    # Máximo 3 noticias nuevas por ejecución
    for noticia in nuevas[:3]:

        resultado = enviar_telegram(
            token,
            noticia,
        )

        if resultado.get("ok"):

            publicadas.append(
                noticia["enlace"]
            )

            print(
                "Publicada:",
                noticia["titulo"],
            )

    guardar_publicadas(publicadas)


if __name__ == "__main__":
    main()
