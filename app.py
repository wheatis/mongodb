from flask import Flask, jsonify, request
import redis
import time
import os

app = Flask(__name__)

# Connexion à Redis (ajustez host/port/mot de passe si besoin)
redis_host = os.getenv("REDIS_HOST", "localhost")
redis_port = int(os.getenv("REDIS_PORT", 6379))
redis_pass = os.getenv("REDIS_PASS", None)

r = redis.Redis(host=redis_host, port=redis_port, password=redis_pass, decode_responses=True)

CACHE_TTL = 60  # durée de vie en secondes

def slow_database_fetch(key):
    """Simule une base de données lente (2 s de latence)"""
    time.sleep(2)
    # pour l’exemple, la "valeur" retournée est simplement key.upper()
    return key.upper()

@app.route("/data/<key>")
def get_data(key):
    # 1) Tentative de récupérer depuis Redis
    cached = r.get(key)
    if cached is not None:
        return jsonify({
            "key": key,
            "value": cached,
            "source": "cache"
        })

    # 2) Si absent, on simule un fetch lent
    value = slow_database_fetch(key)

    # 3) On stocke en cache avec TTL
    r.setex(key, CACHE_TTL, value)

    return jsonify({
        "key": key,
        "value": value,
        "source": "database (slow)"
    })

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
