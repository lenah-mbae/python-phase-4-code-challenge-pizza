#!/usr/bin/env python3
from models import db, Restaurant, RestaurantPizza, Pizza
from flask_migrate import Migrate
from flask import Flask, request
from flask_restful import Api, Resource
import os

# Setup database path
BASE_DIR = os.path.abspath(os.path.dirname(__file__))
DATABASE = os.environ.get("DB_URI", f"sqlite:///{os.path.join(BASE_DIR, 'app.db')}")

# Create app
app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = DATABASE
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.json.compact = False

# Initialize extensions
migrate = Migrate(app, db)
db.init_app(app)
api = Api(app)

# Root route
@app.route("/")
def index():
    return "<h1>Code challenge</h1>"

# ---------------- ROUTES ---------------- #

# GET /restaurants
class Restaurants(Resource):
    def get(self):
        restaurants = Restaurant.query.all()
        return [r.to_dict(rules=('-restaurant_pizzas',)) for r in restaurants], 200

# GET /restaurants/<int:id> & DELETE
class RestaurantByID(Resource):
    def get(self, id):
        restaurant = db.session.get(Restaurant, id)
        if not restaurant:
            return {"error": "Restaurant not found"}, 404
        return restaurant.to_dict(rules=("restaurant_pizzas", "restaurant_pizzas.pizza")), 200

    def delete(self, id):
        restaurant = db.session.get(Restaurant, id)
        if not restaurant:
            return {"error": "Restaurant not found"}, 404
        db.session.delete(restaurant)
        db.session.commit()
        return {}, 204

# GET /pizzas
class Pizzas(Resource):
    def get(self):
        pizzas = Pizza.query.all()
        return [p.to_dict(rules=('-restaurant_pizzas',)) for p in pizzas], 200

# POST /restaurant_pizzas
class RestaurantPizzas(Resource):
    def post(self):
        data = request.get_json()
        if not all(field in data for field in ("price", "pizza_id", "restaurant_id")):
            return {"errors": ["validation errors"]}, 400

        try:
            new_rp = RestaurantPizza(
                price=data["price"],
                pizza_id=data["pizza_id"],
                restaurant_id=data["restaurant_id"]
            )
            db.session.add(new_rp)
            db.session.commit()
            return new_rp.to_dict(rules=("pizza", "restaurant")), 201
        except Exception:
            return {"errors": ["validation errors"]}, 400

# Register API resources
api.add_resource(Restaurants, "/restaurants")
api.add_resource(RestaurantByID, "/restaurants/<int:id>")
api.add_resource(Pizzas, "/pizzas")
api.add_resource(RestaurantPizzas, "/restaurant_pizzas")

# Run the app
if __name__ == "__main__":
    app.run(port=5555, debug=True)
