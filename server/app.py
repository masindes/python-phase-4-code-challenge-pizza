#!/usr/bin/env python3
from models import db, Restaurant, RestaurantPizza, Pizza
from flask_migrate import Migrate
from flask import Flask, request, jsonify, make_response
from flask_restful import Api
import os

BASE_DIR = os.path.abspath(os.path.dirname(__file__))
DATABASE = os.environ.get("DB_URI", f"sqlite:///{os.path.join(BASE_DIR, 'app.db')}")

app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = DATABASE
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.json.compact = False

migrate = Migrate(app, db)
db.init_app(app)

api = Api(app)

@app.route("/")
def index():
    return "<h1>Code challenge</h1>"

@app.route("/restaurants", methods=["GET"])
def get_restaurants():
    restaurants = [restaurant.to_dict() for restaurant in Restaurant.query.all()]
    return jsonify(restaurants), 200

@app.route("/restaurants/<int:id>", methods=["GET"])
def get_restaurant_by_id(id):
    restaurant = Restaurant.query.get(id)
    if restaurant:
        return jsonify(restaurant.to_dict(only=("id", "name", "address", "restaurant_pizzas"))), 200
    else:
        return jsonify({"error": "Restaurant not found"}), 404

@app.route("/restaurants/<int:id>", methods=["DELETE"])
def delete_restaurant(id):
    restaurant = Restaurant.query.get(id)
    if restaurant:
        db.session.delete(restaurant)
        db.session.commit()
        return make_response("Deleted successfully", 204)
    else:
        return jsonify({"error": "Restaurant not found"}), 404

@app.route("/pizzas", methods=["GET"])
def get_pizzas():
    pizzas = [pizza.to_dict() for pizza in Pizza.query.all()]
    return jsonify(pizzas), 200

@app.route("/restaurant_pizzas", methods=["POST"])
def create_restaurant_pizza():
    data = request.get_json()
    try:
        price = data.get("price")
        pizza_id = data.get("pizza_id")
        restaurant_id = data.get("restaurant_id")

        if not (1 <= price <= 30):
            raise ValueError("validation errors")

        restaurant_pizza = RestaurantPizza(price=price, pizza_id=pizza_id, restaurant_id=restaurant_id)
        db.session.add(restaurant_pizza)
        db.session.commit()

        response = restaurant_pizza.to_dict(only=("id", "price", "pizza_id", "restaurant_id"))
        response['pizza'] = restaurant_pizza.pizza.to_dict(only=("id", "name", "ingredients"))
        response['restaurant'] = restaurant_pizza.restaurant.to_dict(only=("id", "name", "address"))
        return jsonify(response), 201

    except ValueError as e:
        return jsonify({"errors": [str(e)]}), 400

if __name__ == "__main__":
    app.run(port=5555, debug=True)