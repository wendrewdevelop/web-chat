from typing import Union, Callable
from typing import Dict
import typer
from calendar import monthrange
from datetime import datetime
import copy
import json
from werkzeug.datastructures import ImmutableMultiDict


class Validator:
    _base_errors_en = {
        'internal-server': {
            "type": "/errors/internal-error-exception",
            "message": "Internal server error",
            "code": 500
        },
        datetime: {
            "type": "/errors/bad-request-input-type-date",
            "message": "This field should be datetime value",
            "code": 400
        },
        str: {
            "type": "/errors/bad-request-input-type-string",
            "message": "This field should be string value",
            "code": 400
        },
        int: {
            "type": "/errors/bad-request-input-type-integer",
            "message": "This field should be integer value",
            "code": 400
        },
        float: {
            "type": "/errors/bad-request-input-type-float",
            "message": "This field should be float value",
            "code": 400
        },
        "input-entry-type": {
            "type": "/errors/bad-request-input-entry-type",
            "message": "Incorrect entry or invalid type",
            "code": 400
        },
        "input-required": {
            "type": "/errors/bad-request-input-required",
            "message": "This field is required",
            "code": 400
        },
        "auth-expiration": {
            "type": "/errors/auth-expired-code",
            "message": "Your token has expired",
            "code": 403
        },
        "auth-revoked": {
            "type": "/errors/auth-token-revoked",
            "message": "Access Token has been revoked",
            "code": 403
        },
        "auth-invalid-client-id": {
            "type": "/errors/auth-invalid-client-id",
            "message": "Invalid token client_id",
            "code": 403
        },
        "auth-invalid-client-iss": {
            "type": "/errors/auth-invalid-client-iss",
            "message": "Invalid token iss",
            "code": 403
        },
        "auth-invalid-token": {
            "type": "/errors/auth-invalid-token",
            "message": "Invalid token",
            "code": 403
        },
        "auth-invalid-scope": {
            "type": "/errors/auth-invalid-scope",
            "message": "Permission denied invalid scope access",
            "code": 403
        },
        "auth-unsupported-authorization": {
            "type": "/errors/auth-unsupported-authorization",
            "message": "Unsupported authorization type",
            "code": 401
        },
        "auth-token-missing": {
            "type": "/errors/auth-token-missing",
            "message": "Token missing",
            "code": 401
        },
        "auth-token-spaces": {
            "type": "/errors/auth-token-spaces",
            "message": "Token contains spaces",
            "code": 401
        },
        "bussines-roles-start-date": {
            "type": "/errors/bussines-roles-date",
            "message": "The start_date can't be greater than end_date",
            "code": 400,
            "field": "start_date"
        },
        "resource-not-found": {
            "type": "/errors/resource-not-found",
            "message": "The selected resource not exist",
            "code": 404
        },
        "bussines-roles-range-date": {
            "type": "/errors/bussines-roles-range-date",
            "message": "The limit is current date -366 days",
            "code": 400
        },
        "bussines-roles-range-limit": {
            "type": "/errors/bussines-roles-range-limit",
            "message": "The range bettween start_date and today can't be greater than one year",
            "code": 400
        }
    }

    def __init__(self, event=None, language='ptBR', bundles_errors=False):
        if event:
            self.event = event
            self.args = ImmutableMultiDict(event["queryStringParameters"])
        else:
            self.args = None
        self.arguments = []
        self.bundles_errors = bundles_errors
        if language == 'ptBR':
            self.base_errors = self._base_errors_en
        else:
            self.base_errors = self._base_errors_en

    """Apply a roles validation for params"""

    def add_argument(self, name: str, required: bool, location: str,
                     code: Union[Callable, str], function_lambda=None,
                     value_type=None, message=None):
        self.arguments.append({
            "function": function_lambda,
            "required": required,
            "location": location,
            "name": name,
            "message": message,
            "code": code,
            "value_type": value_type
        })

    def remove_argument(self, name: str):
        self.arguments = list(filter(lambda arg: arg['name'] != name, self.arguments))

    def parse_args(self):
        """
            It verifies all the roles and apply them to the arguments using the add_argument function
        """
        data = {}
        messages = {
            "errors": []
        }
        for args in self.arguments:
            request_params = getattr(self, args['location'])
            if not request_params and "args" in self.event:
                request_params = getattr(self, "args")
            if not request_params and "json" in self.event:
                request_params = getattr(self, "json")
            if request_params:
                data[args['name']] = request_params[args['name']] if args['name'] in request_params else ""

                # validation function lambda
                if data[args['name']] and args['function']:
                    try:
                        data[args['name']] = args['function'](data[args['name']])
                    except Exception as error:
                        message = copy.copy(self.base_errors[args['code']])
                        message['field'] = args['name']
                        message['message'] = args['message'] if args['message'] else message['message']
                        messages['errors'].append(message)

                # validation input required
                if args['required'] and data[args['name']] != 0 and not data[args['name']]:
                    message = copy.copy(self.base_errors['input-required'])
                    message['field'] = args['name']
                    message['message'] = args['message'] if args['message'] else message['message']
                    messages['errors'].append(message)

                # validate instance type
                try:
                    if args['value_type']:
                        data[args['name']] = args['value_type'](data[args['name']])
                except Exception as error:
                    message = copy.copy(self.base_errors[args['value_type']])
                    message['field'] = args['name']
                    messages['errors'].append(message)

                # Fechtone message per request if bundles_erro not true
                if not self.bundles_errors and messages['errors']:
                    fetchOne = {
                        "error": messages['errors'][0]
                    }
                    typer.echo(400, **fetchOne)
                    raise typer.Exit()
        if messages['errors']:
            typer.echo(400, **messages)
            raise typer.Exit()
        return data

    """Return code dictionaries response based on the code consult the documentation"""

    def get_message_error(self, code: str):
        return self.base_errors[code]

    """Validate ranges between start and end date, it can't be greater than 31 days or parameters can't be less than one year from current date """

    def validate_date_range(self, start_date: datetime, end_date: datetime):
        if end_date and start_date:
            dates_range = end_date - start_date
            if dates_range.days < 0:
                message = self.get_message_error("bussines-roles-start-date")
                response = self.define_response(message)
                raise ValueError(json.dumps(response))
            if dates_range.days > 31:
                message = self.get_message_error("bussines-roles-range-date")
                response = self.define_response(message)
                raise ValueError(json.dumps(response))
        if start_date and abs((datetime.now() - start_date).days) >= 366:
            message = self.get_message_error("bussines-roles-range-limit")
            response = self.define_response(message)
            raise ValueError(json.dumps(response))

    """Validate filters dictionares"""

    def validate_filters_dict(self, filters: dict, fields: list) -> Dict:
        q = []
        try:
            before = 0
            if "q" in filters and filters['q'] and "filter" in filters['q']:
                q = json.loads(filters["q"])['filter']
                before = len(q)
                q = [filters for filters in q if 'name' in filters and 'val' in filters and filters['name'] in fields]
            if before != len(q):
                # print(q, before)
                self.abort_with_message('input-entry-type', "q", message="Incorrect entry or invalid columns")
            return q
        except Exception as e:
            message = self.get_message_error("input-entry-type")
            message['field'] = 'q'
            response = self.define_response(message)
            typer.echo(message['code'], **response)
            typer.Exit()

    """Set default range date based on start or end date max range 31 days"""

    def valitade_default__range_date(self, data: dict) -> Dict:
        # set default value for initial and e final date
        if not data["end_date"] or not data["start_date"]:
            data["start_date"] = data["start_date"] if data["start_date"] else data["end_date"]
            data["start_date"] = data["start_date"] if data["start_date"] else datetime.now()
            last_day = monthrange(data["start_date"].year, data["start_date"].month)[1]
            data["start_date"] = datetime(data["start_date"].year, data["start_date"].month, 1, 0, 0, 0)
            data["end_date"] = datetime(data["start_date"].year, data["start_date"].month, last_day, 23, 59, 59)
        return data

    """Convert date"""

    def convert_date(self, date):
        try:
            return date.isoformat()
        except Exception as error:
            return None

    """Abort request and set response based on the {code} response"""

    def abort_with_message(self, code, field: str, message: str, raises=True):
        response = self.get_message_error(code)
        status = response["code"]
        if field:
            response['field'] = field
        response['message'] = message if message else response['message']
        response = self.define_response(response)
        if raises:
            raise ValueError(json.dumps(response))
        else:
            typer.echo(status, **response)
            typer.Exit()

    """If bundles_errors=true all roles will be verify before complete request and a list of errors will be send"""

    def define_response(self, message: Dict) -> Dict:
        if self.bundles_errors:
            response = {
                "errors": [message]
            }
        else:
            response = {
                "error": message
            }
        return response