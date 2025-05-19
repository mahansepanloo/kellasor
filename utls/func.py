import random
import string


def generator():
    return random.randint(11111, 99999)


def generator_password(n):
    random_code = "".join(random.choices(string.ascii_letters + string.digits, k=n))
    return random_code
