from flask import Flask, jsonify, request
import redis
import os

app = Flask(__name__)
items = []

cache = redis.Redis(
    host=os.environ.get('REDIS_HOST', 'localhost'),
    port=int(os.environ.get('REDIS_PORT', 6379)),
    decode_responses=True
)

@app.route('/health')
def health():
    return jsonify({"status": "healthy"})

@app.route('/ready')
def ready():
    try:
        cache.ping()
        return jsonify({"status": "ready", "cache": "connected"})
    except redis.ConnectionError:
        return jsonify({"status": "not ready", "cache": "disconnected"}), 503

@app.route('/items', methods=['GET'])
def get_items():
    return jsonify({"items": items, "count": len(items)})

@app.route('/items', methods=['POST'])
def add_item():
    data = request.get_json()
    if not data or 'name' not in data:
        return jsonify({"error": "Le champ 'name' est requis"}), 400

    item = {
        "id": len(items) + 1,
        "name": data['name'],
        "quantity": data.get('quantity', 0)
    }
    items.append(item)

    try:
        cache.incr('items_created')
    except redis.ConnectionError:
        pass

    return jsonify(item), 201

@app.route('/stats')
def stats():
    try:
        count = cache.get('items_created') or 0
        return jsonify({"items_created_total": int(count)})
    except redis.ConnectionError:
        return jsonify({"error": "Cache indisponible"}), 503

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
