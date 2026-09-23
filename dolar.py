import json
import os
import urllib.parse
import urllib.request
from datetime import datetime
from zoneinfo import ZoneInfo

CHAT_ID = "-1001243627353"

def get_json(url):
    req = urllib.request.Request(url, headers={"User-Agent": "villa-del-parque-bot/1.0"})
    with urllib.request.urlopen(req, timeout=30) as r:
        return json.loads(r.read().decode())

def money(v):
    if v is None:
        return "—"
    return "$" + f"{v:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")

def main():
    token = os.environ["TELEGRAM_BOT_TOKEN"].strip()
    dolares = get_json("https://dolarapi.com/v1/dolares")

    wanted = ["oficial", "blue", "bolsa", "contadoconliqui", "tarjeta", "mayorista", "cripto"]
    by_casa = {d.get("casa"): d for d in dolares}
    labels = {
        "oficial": "🏦 Oficial",
        "blue": "🔵 Blue",
        "bolsa": "📈 MEP / Bolsa",
        "contadoconliqui": "🌎 CCL",
        "tarjeta": "💳 Tarjeta",
        "mayorista": "🏢 Mayorista",
        "cripto": "₿ Cripto",
    }

    lines = ["💵 <b>COTIZACIÓN DEL DÓLAR</b>", "", "<b>Tipo                 Compra        Venta</b>"]
    for key in wanted:
        d = by_casa.get(key)
        if not d:
            continue
        lines.append(f"{labels[key]}: <b>{money(d.get('compra'))}</b> / <b>{money(d.get('venta'))}</b>")

    now = datetime.now(ZoneInfo("America/Argentina/Buenos_Aires"))
    lines += ["", f"🕐 Actualizado: <b>{now:%H:%M} hs</b>", "📍 Argentina"]
    text = "\n".join(lines)

    payload = urllib.parse.urlencode({
        "chat_id": CHAT_ID,
        "text": text,
        "parse_mode": "HTML",
        "disable_web_page_preview": "true",
    }).encode()

    req = urllib.request.Request(
        f"https://api.telegram.org/bot{token}/sendMessage",
        data=payload,
        headers={"User-Agent": "villa-del-parque-bot/1.0"},
    )
    with urllib.request.urlopen(req, timeout=30) as r:
        result = json.loads(r.read().decode())
    if not result.get("ok"):
        raise RuntimeError(result)

if __name__ == "__main__":
    main()
