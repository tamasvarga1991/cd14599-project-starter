from flask import Flask, request, jsonify, send_from_directory
from werkzeug.exceptions import BadRequest, UnsupportedMediaType
from backend.order_tracker import OrderTracker
from backend.in_memory_storage import InMemoryStorage

app = Flask(__name__, static_folder='../frontend')
in_memory_storage = InMemoryStorage()
order_tracker = OrderTracker(in_memory_storage)

@app.route('/')
def serve_index():
    return send_from_directory(app.static_folder, 'index.html')

@app.route('/<path:filename>')
def serve_static(filename):
    return send_from_directory(app.static_folder, filename)

@app.route('/api/orders', methods=['POST'])
def add_order_api():
    try:
        data = request.get_json()
        required_fields = ('order_id', 'item_name', 'quantity', 'customer_id')
        if not isinstance(data, dict) or any(field not in data for field in required_fields):
            return jsonify({"error": "A JSON object with order_id, item_name, quantity, and customer_id is required."}), 400
        order_tracker.add_order(
            data['order_id'], data['item_name'], data['quantity'],
            data['customer_id'], status=data.get('status', 'pending'),
        )
        return jsonify(order_tracker.get_order_by_id(data['order_id'])), 201
    except (BadRequest, UnsupportedMediaType) as error:
        return jsonify({"error": error.description}), error.code
    except ValueError as error:
        return jsonify({"error": str(error)}), 400

@app.route('/api/orders/<string:order_id>', methods=['GET'])
def get_order_api(order_id):
    order = order_tracker.get_order_by_id(order_id)
    if order is None:
        return jsonify({"error": f"Order with ID '{order_id}' does not exist."}), 404
    return jsonify(order), 200

@app.route('/api/orders/<string:order_id>/status', methods=['PUT'])
def update_order_status_api(order_id):
    try:
        data = request.get_json()
        if not isinstance(data, dict) or 'new_status' not in data:
            return jsonify({"error": "A JSON object with new_status is required."}), 400
        order_tracker.update_order_status(order_id, data['new_status'])
        return jsonify(order_tracker.get_order_by_id(order_id)), 200
    except (BadRequest, UnsupportedMediaType) as error:
        return jsonify({"error": error.description}), error.code
    except ValueError as error:
        return jsonify({"error": str(error)}), 400

@app.route('/api/orders', methods=['GET'])
def list_orders_api():
    try:
        if 'status' in request.args:
            orders = order_tracker.list_orders_by_status(request.args['status'])
        else:
            orders = order_tracker.list_all_orders()
        return jsonify(orders), 200
    except ValueError as error:
        return jsonify({"error": str(error)}), 400

if __name__ == '__main__':
    app.run(host="0.0.0.0", debug=True)
