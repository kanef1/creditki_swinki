import pytest

@pytest.fixture(autouse=True)
def fast_test_passwords(settings):
    settings.PASSWORD_HASHERS = ['django.contrib.auth.hashers.MD5PasswordHasher']
