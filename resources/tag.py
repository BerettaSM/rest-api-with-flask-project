from flask.views import MethodView
from flask_smorest import Blueprint, abort
from http import HTTPStatus

from sqlalchemy.exc import SQLAlchemyError

from db import db
from models import StoreModel, TagModel, ItemModel
from schemas import TagSchema, TagAndItemSchema

blp = Blueprint('Tags', __name__, description='Operations on tags')

@blp.route('/store/<int:store_id>/tag')
class TagsInStore(MethodView):
    @blp.response(HTTPStatus.OK, TagSchema(many=True))
    def get(self, store_id):
        store = StoreModel.query.get_or_404(store_id)
        return store.tags.all(), HTTPStatus.OK
    
    
    @blp.arguments(TagSchema)
    @blp.response(HTTPStatus.CREATED, TagSchema)
    def post(self, tag_data, store_id):
        tag = TagModel(**tag_data, store_id=store_id)
        try:
            db.session.add(tag)
            db.session.commit()
        except SQLAlchemyError as e:
            abort(
                HTTPStatus.INTERNAL_SERVER_ERROR,
                message=str(e)
            )
        return tag, HTTPStatus.CREATED


@blp.route('/item/<int:item_id>/tag/<int:tag_id>')
class LinkTagsToItem(MethodView):
    @blp.response(HTTPStatus.OK, TagSchema)
    def post(self, item_id, tag_id):
        item = ItemModel.query.get_or_404(item_id)
        tag = TagModel.query.get_or_404(tag_id)
        item.tags.append(tag)
        try:
            db.session.add(item)
            db.session.commit()
        except SQLAlchemyError:
            abort(
                HTTPStatus.INTERNAL_SERVER_ERROR,
                message='An error occurred while inserting the tag.'
            )
        return tag, HTTPStatus.OK
    

    @blp.response(HTTPStatus.OK, TagAndItemSchema)
    def delete(self, item_id, tag_id):
        item = ItemModel.query.get_or_404(item_id)
        tag = TagModel.query.get_or_404(tag_id)
        item.tags.remove(tag)
        try:
            db.session.add(item)
            db.session.commit()
        except SQLAlchemyError:
            abort(
                HTTPStatus.INTERNAL_SERVER_ERROR,
                message='An error occurred while inserting the tag.'
            )
        return { 'message': 'Item removed from tag', 'item': item, 'tag': tag }, HTTPStatus.OK


@blp.route('/tag/<int:tag_id>')
class Tag(MethodView):
    @blp.response(HTTPStatus.OK, TagSchema)
    def get(self, tag_id):
        tag = TagModel.query.get_or_404(tag_id)
        return tag, HTTPStatus.OK


    @blp.response(
        HTTPStatus.ACCEPTED,
        description='Deletes a tag if no item is tagged with it.',
        example={ 'message': 'Tag deleted.' }
    )
    @blp.alt_response(
        HTTPStatus.NOT_FOUND,
        description='Tag not found.'
    )
    @blp.alt_response(
        HTTPStatus.BAD_REQUEST,
        description='Returned if the tag is assigned to one or more items. In this case, the tag is not deleted.'
    )
    def delete(self, tag_id):
        tag = TagModel.query.get_or_404(tag_id)
        if tag.items:
            abort(
                HTTPStatus.BAD_REQUEST,
                message='Could not delete tag. Make sure tag is not associated with any items, then try again.'
            )
        db.session.delete(tag)
        db.session.commit()
        return { 'message': 'Tag deleted.' }, HTTPStatus.ACCEPTED
