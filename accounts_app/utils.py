from rest_framework import serializers
import random


def password_validate(passwords: str = None, pass2: str = None):
    if not passwords or not pass2 :
        raise serializers.ValidationError("Passwords cannot be empty")
    if passwords != pass2:
        raise serializers.ValidationError("Passwords do not match")
    elif len(passwords) < 8:
        raise serializers.ValidationError("Password must be at least 8 characters long")
    elif passwords.isnumeric():
        raise serializers.ValidationError("Password must contain at least one letter")
    elif passwords.isdigit():
        raise serializers.ValidationError("Password must contain at least one number")



def generate_code():
    code = random.randint(1000, 9999)
    print(code)
    return code
