from flask_restful import Resource, reqparse

import datetime


getParser: reqparse.RequestParser = reqparse.RequestParser()

getParser.add_argument('start', type=int)
getParser.add_argument('end', type=int)

class Reqs(Resource):
    @staticmethod
    def get():
        args: dict = getParser.parse_agrs()


        return {
            'message': 'Failed'
        }