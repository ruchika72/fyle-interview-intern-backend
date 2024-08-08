from flask import Blueprint
from core.apis import decorators
from core import db
from core.apis.responses import APIResponse
from core.models.assignments import Assignment, GradeEnum
from .schema import AssignmentSchema

principal_assignments_resources = Blueprint('principal_assignments_resources', __name__)

@principal_assignments_resources.route('/assignments', methods=['GET'], strict_slashes=False)
@decorators.authenticate_principal
def list_submitted_and_graded_assignments(p):
    """Returns list of submitted and graded assignments"""
    assignments = Assignment.get_submitted_and_graded_assignments()
    assignments_dump = AssignmentSchema().dump(assignments, many=True)
    return APIResponse.respond(data=assignments_dump)


@principal_assignments_resources.route('/assignments/grade', methods=['POST'], strict_slashes=False)
@decorators.accept_payload
@decorators.authenticate_principal
def grade_assignment(p, incoming_payload):
    """Grade or re-grade an assignment"""
    # incoming_payload = request.json
    assignment_id = incoming_payload.get('id')
    grade = incoming_payload.get('grade')
    # Validate the grade
    # if grade not in GradeEnum.__members__:
    #     return APIResponse.respond_error(f"Invalid grade value: {grade}", status_code=400)
    graded_assignment = Assignment.mark_grade(
        _id=assignment_id,
        teacher_id=p.user_id,  # Assuming user_id is used as teacher_id here
        grade=GradeEnum[grade],
        auth_principal=p  # Since we're not using AuthPrincipal, we pass None or remove this if not required
    )

    db.session.commit()

    graded_assignment_dump = AssignmentSchema().dump(graded_assignment)
    
    return APIResponse.respond(data=graded_assignment_dump)
