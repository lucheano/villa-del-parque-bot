import json
import os
import urllib.parse
import urllib.request
from datetime import datetime
from zoneinfo import ZoneInfo

CHAT_ID = "-1001243627353"

TIPOS = [
    ("oficial", "🏦 Oficial"),
    ("blue", "🔵 Blue"),
    ("bolsa", "📈 MEP"),
    ("contadoconliqui", "🌎 CCL"),
    ("tarjeta", "💳 Tarjeta"),
    ("mayorista", "🏢 Mayorista"),
    ("cripto", "₿ Cripto"),
]


def get_json(url):
    req = urllib.request.Request(
        url,
        headers={"User-Agent": "villa-del-parque-bot/1.0"}
    )
    with urllib.request.urlopen(req, timeout=30) as response:
        return json.loads(response.read().decode("utf-8"))


def formato_pesos(valor):
    if valor is None:
        return "—"

    return "$" + f"{valor:,.2f}".replace(
        ",", "X"
    ).replace(
        ".", ","
    ).replace(
        "X", "."
    )


def crear_mensaje(cotizaciones):
    por_tipo = {
        item.get("casa"): item
        for item in cotizaciones
    }

    lineas = [
        "💵 <b>COTIZACIÓN DEL DÓLAR</b>",
        "",
    ]

    for codigo, nombre in TIPOS:
        dolar = por_tipo.get(codigo)

        if not dolar:
            continue

        compra = formato_pesos(dolar.get("compra"))
        venta = formato_pesos(dolar.get("venta"))

        lineas.append(
            f"{nombre}: {compra} / {venta}"
        )

    ahora = datetime.now(
        ZoneInfo("America/Argentina/Buenos_Aires")
    )

    lineas.extend([
        "",
        f"🕐 Actualizado: <b>{ahora:%H:%M} hs</b>",
        "📍 Argentina",
        "",
        "<i>Compra / Venta</i>",
    ])

    return "\n".join(lineas)


def enviar_mensaje(token, texto):
    url = (
        f"https://api.telegram.org/"
        f"bot{token}/sendMessage"
    )

    datos = urllib.parse.urlencode({
        "chat_id": CHAT_ID,
        "text": texto,
        "parse_mode": "HTML",
    }).encode()

    req = urllib.request.Request(url, data=datos)

    with urllib.request.urlopen(req, timeout=30) as response:
        return json.loads(response.read().decode("utf-8"))


def main():
    token = os.environ["TELEGRAM_BOT_TOKEN"].strip()

    cotizaciones = get_json(
        "https://dolarapi.com/v1/dolares"
    )

    mensaje = crear_mensaje(cotizaciones)

    resultado = enviar_mensaje(token, mensaje)

    if not resultado.get("ok"):
        raise RuntimeError(resultado)


if __name__ == "__main__":
    main()
