from models import User

def is_valid(field):
    if len(field) < 3 or len(field) > 21 or not field:
        return False
    if " " in field:
        return False
    return True

def validate(inputs, errors):
    if not is_valid(inputs['username']):
            errors['username']="That's not a valid username"
    if not is_valid(inputs['password']):
        errors["password"] = "That's not a valid password"
    if inputs['password'] != inputs['verify_pass'] or not inputs['verify_pass']:
        errors["match_password"] = "Passwords don't match"
    existing_user = User.query.filter_by(username=inputs['username']).first()
    if existing_user:
        errors["existing_user"] = "Sorry, that username is taken"