def password_validating(password, password2):
    if not (password and password2):
        return False
    if password2 != password:
        return False
    return True
