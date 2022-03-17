from flask import Flask
from flask_restful import Resource, reqparse, Api
from config import *
from datetime import datetime, timedelta
from urllib.parse import urlparse, parse_qs
import requests

app: Flask = Flask(__name__)
rest: Api = Api(app)

class Dnevnik:
    def __init__(self, login: str = None, password: str = None, token: str = None, group: int = None):
        self.session = requests.Session()
        self.host = BASE_URL
        self.token = token
        self.group = group
        if token is None:
            self.token = self.get_token(login, password)
            print(self.token)
        self.session.headers = {"Access-Token": self.token}

    def get_token(self, login, password):
        token = self.session.post(
            LOGIN_URL,
            params={
                "ReturnUrl": RETURN_URL,
                "login": login,
                "password": password,
            },
            allow_redirects=True,
        )
        parsed_url = urlparse(token.url)
        query = parse_qs(parsed_url.query)
        result = query.get("result")

        if result is None or result[0] != "success":
            token = self.session.post(RETURN_URL)
            parsed_url = urlparse(token.url)
            query = parse_qs(parsed_url.query)
            result = query.get("result")

            if result is None or result[0] != "success":
                raise DiaryError("Что то не так с авторизацией")

        if token.status_code != 200:
            raise DiaryError(
                "Сайт лежит или ведутся технические работы, использование api временно невозможно"
            )

        token = parsed_url.fragment[13:-7]
        return token

    @staticmethod
    def _check_response(response):
        if response.headers.get("Content-Type") == "text/html":
            error_html = response.content.decode()
            error_text = " ".join(
                word
                for word in error_html.split('<div class="error__description">')[-1]
                                .split("<p>")[1]
                                .strip()[:-4]
                                .split()
            )
            raise DiaryError(error_text)
        json_response = response.json()
        if isinstance(json_response, dict):
            if json_response.get("type") == "parameterInvalid":
                raise DiaryError(json_response["description"])
            if json_response.get("type") == "apiServerError":
                raise DiaryError(
                    "Неизвестная ошибка в API, проверьте правильность параметров"
                )
            if json_response.get("type") == "apiUnknownError":
                raise DiaryError(
                    "Неизвестная ошибка в API, проверьте правильность параметров"
                )
            if json_response.get("type") == "authorizationFailed":
                raise DiaryError("Ошибка авторизации")

    def get(self, method: str, params=None, **kwargs):
        if params is None:
            params = {}
        response = self.session.get(self.host + method, params=params, **kwargs)
        self._check_response(response)
        return response.json()

    def post(self, method: str, data=None, **kwargs):
        if data is None:
            data = {}
        response = self.session.post(self.host + method, data=data, **kwargs)
        self._check_response(response)
        return response.json()

    def delete(self, method: str, params=None, **kwargs):
        if params is None:
            params = {}
        response = self.session.delete(self.host + method, params=params, **kwargs)
        self._check_response(response)
        return response.json()

    def put(self, method: str, params=None, **kwargs):
        if params is None:
            params = {}
        response = self.session.put(self.host + method, data=params, **kwargs)
        self._check_response(response)
        return response.json()

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.session.close()

    def get_timetable(self, start, end):
        return self.get(f"edu-groups/{self.group}/lessons/{start}/{end}")

dnevnik: Dnevnik = Dnevnik(LOGIN, PASSWORD, group=GROUP)

getParser: reqparse.RequestParser = reqparse.RequestParser()

getParser.add_argument('start', type=int)
getParser.add_argument('end', type=int)

class Timetable(Resource):
    @staticmethod
    def get():
        args: dict = getParser.parse_args()

        if args['start'] is not None and args['end'] is not None:
            lessons = dnevnik.get_timetable(args['start'], args['end'])
        else:
            lessons = dnevnik.get_timetable(datetime.now() - timedelta(days=2),
                                            datetime.now() + timedelta(days=2))
        last_date = None
        dates: list = []
        date: list = []

        for lesson in lessons:
            current_date: str = lesson['date']
            if last_date is None or current_date == last_date:
                last_date = lesson['date']
                date.append({'date': last_date, 'number': lesson['number'], 'lesson': lesson['subject']['name']})
            else:
                dates.append(date)
                date = []
                date.append({'date': last_date, 'number': lesson['number'], 'lesson': lesson['subject']['name']})
                last_date = current_date
        return dates

rest.add_resource(Timetable, '/')

if __name__ == '__main__':
    app.run()