from flask import Blueprint, request
from flask_restx import Api, Resource, fields

from project import db
from project.api.models import User

user_blueprint = Blueprint("users", __name__)
api = Api(user_blueprint)


user = api.model(
    "User",
    {
        "id": fields.Integer(readOnly=True),
        "username": fields.String(required=True),
        "email": fields.String(required=True),
        "created_date": fields.DateTime,
    },
)


class UserList(Resource):
    @api.expect(user, validate=True)
    def post(self):
        post_data = request.get_json()
        username = post_data.get("username")
        email = post_data.get("email")

        response = {"message": "Sorry. That email already exists."}
        status_code = 400

        user = User.query.filter_by(email=email).first()
        if not user:
            db.session.add(User(username=username, email=email))
            db.session.commit()

            status_code = 201
            response["message"] = f"{email} was added!"

        return response, status_code

    @api.marshal_with(user, as_list=True)
    def get(self):
        return User.query.all()


class Users(Resource):
    @api.marshal_with(user)
    def get(self, user_id):
        user = User.query.filter_by(id=user_id).first()
        status_code = 200

        if not user:
            api.abort(404, f"User {user_id} does not exist")

        return user, status_code


api.add_resource(UserList, "/users")
api.add_resource(Users, "/users/<int:user_id>")
