#!/usr/bin/env python3
from models import db, Restaurant, RestaurantPizza, Pizza
from flask_migrate import Migrate
from flask import Flask, request,jsonify
from flask_restful import Api, Resource
import os
from flask_cors import CORS


BASE_DIR = os.path.abspath(os.path.dirname(__file__))
DATABASE = os.environ.get("DB_URI", f"sqlite:///{os.path.join(BASE_DIR, 'app.db')}")

app = Flask(__name__)
CORS(app)

app.config["SQLALCHEMY_DATABASE_URI"] = DATABASE
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.json.compact = False

migrate = Migrate(app, db)

db.init_app(app)

api = Api(app)


@app.route("/")
def index():
    return "<h1>Code challenge</h1>"

# Route: GET /restaurants
@app.route("/restaurants", methods=["GET"])
def get_restaurants():
    restaurants = Restaurant.query.all()
    return jsonify([restaurant.to_dict(only=("id", "name", "address")) for restaurant in restaurants])

# Route: GET /pizzas
@app.route("/pizzas", methods=["GET"])
def get_pizzas():
    pizzas = Pizza.query.all()
    return jsonify([pizza.to_dict(only=("id", "name", "ingredients")) for pizza in pizzas]), 200


# Route: POST /restaurants
@app.route("/restaurants", methods=["POST"])
def create_restaurant():
    data = request.get_json()

    existing_restaurant = Restaurant.query.filter_by(name=data["name"], address=data["address"]).first()
    if existing_restaurant:
        return jsonify({"error": "Restaurant already exists."}), 400

    # Create and save the new restaurant
    new_restaurant = Restaurant(name=data["name"], address=data["address"])
    db.session.add(new_restaurant)
    db.session.commit()

    return jsonify({"success": "Restaurant added successfully."}), 201

# Route: GET /restaurants/<int:id>
@app.route("/restaurants/<int:id>",methods = ["GET"])
def get_restaurant_by_id(id):
    restaurant = Restaurant.query.get(id)
    if not restaurant:
        return jsonify({"error": "Restaurant not found"}),404
    return jsonify(restaurant.to_dict(only= ("id","name","address","restaurant_pizzas")))


# Route: DELETE /restaurants/<int:id>
@app.route("/restaurants/<int:id>", methods=["DELETE"])
def delete_restaurants(id):
    restaurant = Restaurant.query.get(id)
    if not restaurant:
        return jsonify({"error": "Restaurant not found"}), 404  

    db.session.delete(restaurant)
    db.session.commit()
    return "", 204  


# Route: POST /restaurant_pizzas
@app.route("/restaurant_pizzas", methods=["POST"])
def create_restaurant_pizza():
    data = request.get_json()

    # Validation of price
    if data.get("price") is None or not (1 <= data["price"] <= 30):
        return jsonify({"errors": ["validation errors"]}), 400  

    try:
        restaurant_pizza = RestaurantPizza(
            price=data["price"],
            pizza_id=data["pizza_id"],
            restaurant_id=data["restaurant_id"],
        )
        db.session.add(restaurant_pizza)
        db.session.commit()

        response_data = restaurant_pizza.to_dict(
            only=("id", "price", "pizza", "pizza_id", "restaurant", "restaurant_id")
        )
        return jsonify(response_data), 201

    except Exception as e:
        return jsonify({"errors": [str(e)]}), 400

if __name__ == "__main__":
    app.run(port=5555, debug=True)
