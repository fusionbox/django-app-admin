from setuptools import setup

def read(fname):
    import os
    return open(os.path.join(os.path.dirname(__file__), fname)).read()

setup(
        name="django-app-admin",
        version="0.0.1",
        packages=["app_admin"],
        author="Fusionbox Programmers",
        author_email="programmers@fusionbox.com",
        long_description=read("README.md"),
        url="https://github.com/fusionbox/django-app-admin",
        platforms="any",
        license="BSD",
        )
