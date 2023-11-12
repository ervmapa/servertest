from flask import Flask, jsonify, request
from flask_restful import Resource, Api

app = Flask(__name__)
api = Api(app)

# Sample data (you can replace this with your data source)
data = {
    '1': {'name': 'Item 1', 'description': 'Description of Item 1'},
    '2': {'name': 'Item 2', 'description': 'Description of Item 2'},
}

class ItemList(Resource):
    def get(self):
        return jsonify(data)

class Item(Resource):
    def get(self, item_id):
        if item_id in data:
            return jsonify(data[item_id])
        else:
            return {'error': 'Item not found'}, 404

api.add_resource(ItemList, '/items')
api.add_resource(Item, '/items/<string:item_id>')

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
