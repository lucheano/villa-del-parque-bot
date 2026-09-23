import json
import os
import urllib.parse
import urllib.request

CHAT_ID = "-1001243627353"
LAT = -34.603
LON = -58.494

WMO = {
    0: "Despejado", 1: "Mayormente despejado", 2: "Parcialmente nublado",
    3: "Nublado", 45: "Niebla", 48: "Niebla con escarcha",
    51: "Llovizna leve", 53: "Llovizna", 55: "Llovizna intensa",
    61: "Lluvia leve", 63: "Lluvia", 65: "Lluvia intensa",
    71: "Nieve leve", 73: "Nieve", 75: "Nieve intensa",
    80: "Chaparrones leves", 81: "Chaparrones", 82: "Chaparrones fuertes",
    95: "Tormentas", 96: "Tormentas con granizo", 99: "Tormentas fuertes con granizo",
}

def get_json(url, data=None):
    req = urllib.request.Request(url, data=data)
    with urllib.request.urlopen(req, timeout=30) as r:
        return json.loads(r.read().decode())

def main():
    token = os.environ["TELEGRAM_BOT_TOKEN"]
    params = urllib.parse.urlencode({
        "latitude": LAT, "longitude": LON,
        "current": "temperature_2m,apparent_temperature,weather_code,wind_speed_10m",
        "daily": "temperature_2m_max,temperature_2m_min,precipitation_probability_max,weather_code",
        "timezone": "America/Argentina/Buenos_Aires", "forecast_days": 2,
    })
    weather = get_json("https://api.open-meteo.com/v1/forecast?" + params)
    c, d = weather["current"], weather["daily"]
    estado = WMO.get(c["weather_code"], "Estado variable")
    manana = WMO.get(d["weather_code"][1], "Estado variable")
    text = (
        "🌤️ <b>CLIMA — VILLA DEL PARQUE</b>\n\n"
        f"🌡️ Ahora: <b>{round(c['temperature_2m'])} °C</b>\n"
        f"🤔 Sensación térmica: <b>{round(c['apparent_temperature'])} °C</b>\n"
        f"☁️ {estado}\n"
        f"🔺 Máxima: <b>{round(d['temperature_2m_max'][0])} °C</b> · "
        f"🔻 Mínima: <b>{round(d['temperature_2m_min'][0])} °C</b>\n"
        f"🌧️ Probabilidad máxima de lluvia: <b>{d['precipitation_probability_max'][0]}%</b>\n"
        f"💨 Viento: <b>{round(c['wind_speed_10m'])} km/h</b>\n\n"
        f"📅 <b>Mañana:</b> {manana} · "
        f"{round(d['temperature_2m_min'][1])} °C / {round(d['temperature_2m_max'][1])} °C"
    )
    payload = urllib.parse.urlencode({
        "chat_id": CHAT_ID, "text": text, "parse_mode": "HTML"
    }).encode()
    result = get_json(f"https://api.telegram.org/bot{token}/sendMessage", payload)
    if not result.get("ok"):
        raise RuntimeError(result)

if __name__ == "__main__":
    main()
