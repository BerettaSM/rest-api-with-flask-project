from flask.views import MethodView
from flask_smorest import Blueprint, abort
from http import HTTPStatus

from sqlalchemy.exc import IntegrityError, SQLAlchemyError

from db import db
from models import StoreModel
from schemas import StoreSchema


blp = Blueprint('stores', __name__, description='Operations on stores')


@blp.route('/store/<int:store_id>')
class Store(MethodView):
    @blp.response(HTTPStatus.OK, StoreSchema)
    def get(self, store_id):
        store = StoreModel.query.get_or_404(store_id)
        return store, HTTPStatus.OK

    def delete(self, store_id):
        store = StoreModel.query.get_or_404(store_id)
        db.session.delete(store)
        db.session.commit()
        return { "message": "Store deleted." }, HTTPStatus.OK


@blp.route('/store')
class StoreList(MethodView):
    @blp.response(HTTPStatus.OK, StoreSchema(many=True))
    def get(self):
        return StoreModel.query.all(), HTTPStatus.OK


    @blp.arguments(StoreSchema)
    @blp.response(HTTPStatus.CREATED, StoreSchema)
    def post(self, store_data):
        store = StoreModel(**store_data)
        try:
            db.session.add(store)
            db.session.commit()
        except IntegrityError:
            abort(
                HTTPStatus.BAD_REQUEST,
                message='A store with that name already exists.'
            )
        except SQLAlchemyError:
            abort(
                HTTPStatus.INTERNAL_SERVER_ERROR,
                message="An error occurred creating the store."
            )
        return store, HTTPStatus.CREATED
