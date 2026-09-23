import json
import os
import urllib.parse
import urllib.request

CHAT_ID = "-1001243627353"


def main():
    token = os.environ["TELEGRAM_BOT_TOKEN"].strip()

    texto = (
        "📸 <b>¡Seguinos en Instagram!</b>\n\n"
        "👉 <b>@envilladelparque</b>"
    )

    datos = urllib.parse.urlencode({
        "chat_id": CHAT_ID,
        "text": texto,
        "parse_mode": "HTML",
    }).encode()

    url = f"https://api.telegram.org/bot{token}/sendMessage"

    req = urllib.request.Request(url, data=datos)

    with urllib.request.urlopen(req, timeout=30) as response:
        resultado = json.loads(
            response.read().decode("utf-8")
        )

    if not resultado.get("ok"):
        raise RuntimeError(resultado)


if __name__ == "__main__":
    main()
