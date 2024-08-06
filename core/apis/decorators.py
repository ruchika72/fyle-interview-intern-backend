import json
from flask import request, jsonify
from core.libs import assertions
from functools import wraps


class AuthPrincipal:
    def __init__(self, user_id, student_id=None, teacher_id=None, principal_id=None):
        self.user_id = user_id
        self.student_id = student_id
        self.teacher_id = teacher_id
        self.principal_id = principal_id


def accept_payload(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        incoming_payload = request.json
        return func(incoming_payload, *args, **kwargs)
    return wrapper

def validate_payload(required_properties):
    def decorator(func):
        @wraps(func)
        def wrapper(incoming_payload, *args, **kwargs):
            # Validate that all required properties are present and not None
            missing_properties = [prop for prop in required_properties if prop not in incoming_payload or incoming_payload[prop] is None]

            if missing_properties:
                return jsonify({
                    "error": "Bad request",
                    "message": f"Missing or None properties: {', '.join(missing_properties)}"
                }), 400

            return func(incoming_payload, *args, **kwargs)
        return wrapper
    return decorator

def authenticate_principal(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        p_str = request.headers.get('X-Principal')
        assertions.assert_auth(p_str is not None, 'principal not found')
        p_dict = json.loads(p_str)
        p = AuthPrincipal(
            user_id=p_dict['user_id'],
            student_id=p_dict.get('student_id'),
            teacher_id=p_dict.get('teacher_id'),
            principal_id=p_dict.get('principal_id')
        )

        if request.path.startswith('/student'):
            assertions.assert_true(p.student_id is not None, 'requester should be a student')
        elif request.path.startswith('/teacher'):
            assertions.assert_true(p.teacher_id is not None, 'requester should be a teacher')
        elif request.path.startswith('/principal'):
            assertions.assert_true(p.principal_id is not None, 'requester should be a principal')
        else:
            assertions.assert_found(None, 'No such api')

        return func(p, *args, **kwargs)
    return wrapper
