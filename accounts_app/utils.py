from rest_framework import serializers
import random
from utls.response import ResponseMessage


def password_validate(passwords: str = None, pass2: str = None):
    if not passwords or not pass2:
        raise serializers.ValidationError(
            ResponseMessage.error("Passwords cannot be empty")
        )
    if passwords != pass2:
        raise serializers.ValidationError(
            ResponseMessage.error("Passwords do not match")
        )
    elif len(passwords) < 8:
        raise serializers.ValidationError(
            ResponseMessage.error("Password must be at least 8 characters long")
        )
    elif passwords.isnumeric():
        raise serializers.ValidationError(
            ResponseMessage.error("Password must contain at least one letter")
        )
    elif passwords.isdigit():
        raise serializers.ValidationError(
            ResponseMessage.error("Password must contain at least one number")
        )


def generate_code():
    code = random.randint(1000, 9999)
    return code
