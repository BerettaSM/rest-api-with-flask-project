from flask import jsonify
from flask_jwt_extended import JWTManager
from http import HTTPStatus

from blocklist import BLOCKLIST


def register_jwt_manager(app):
    jwt = JWTManager(app)

    @jwt.token_in_blocklist_loader
    def is_token_in_blocklist(jwt_header, jwt_payload):
        return jwt_payload["jti"] in BLOCKLIST


    @jwt.revoked_token_loader
    def revoked_token_callback(jwt_header, jwt_payload):
        return jsonify({
            'message': 'The token has been revoked.',
            'error': 'token_revoked'
        }), HTTPStatus.UNAUTHORIZED


    @jwt.needs_fresh_token_loader
    def token_not_fresh_callback(jwt_header, jwt_payload):
        return jsonify({
            'message': 'The token is not fresh.',
            'error': 'fresh_token_required'
        }), HTTPStatus.UNAUTHORIZED


    @jwt.additional_claims_loader
    def add_claims_to_jwt(identity):
        return { 'is_admin': identity == 1 }


    @jwt.expired_token_loader
    def expired_token_callback(jwt_header, jwt_payload):
        return jsonify({
            'message': 'The token has expired',
            'error': 'token_expired'
        }), HTTPStatus.UNAUTHORIZED


    @jwt.invalid_token_loader
    def invalid_token_callback(error):
        return jsonify({
            'message': 'Signature verification failed.',
            'error': 'invalid_token'
        }), HTTPStatus.UNAUTHORIZED
    

    @jwt.unauthorized_loader
    def missing_token_callback(error):
        return jsonify({
            'message': 'Signature does not contain an access token.',
            'error': 'authorization_required'
        }), HTTPStatus.UNAUTHORIZED
