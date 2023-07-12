import secrets
from contextlib import contextmanager
from logging import getLogger as get_logger
from logging.config import fileConfig as logger_file_config
from pathlib import Path
from typing import Dict, Optional, Annotated

from fastapi import Depends, HTTPException
from fastapi.security import HTTPBasicCredentials, HTTPBasic
from starlette import status

security = HTTPBasic()


@contextmanager
def catch(*exceptions):
    if not exceptions:
        exceptions = (Exception,)

    err_container = lambda: None
    err_container.err = None

    try:
        yield err_container
    except exceptions as e:
        err_container.err = e


@contextmanager
def cry():
    try:
        yield
    except Exception as err:
        import pdb
        pdb.post_mortem()


def problemjson(
        title: str,
        detail: Optional[str] = None,
        type_uri: Optional[str] = None,
        instance: Optional[str] = None,
        **kwargs: Dict[str, str]
) -> Dict[str, Dict[str, str]]:
    """
    Return a JSON representation of a HTTP Problem Details response.

    :param title: A short, human-readable summary of the problem.
    :param detail: A human-readable explanation specific to this occurrence of the problem.
    :param type_uri: A URI reference that identifies the problem type.
    :param instance: A URI reference that identifies the specific occurrence of the problem.
    :param kwargs: Any additional properties to include in the response.
    :return: A dictionary representation of the HTTP Problem Details response.
    """
    response = {
        "title": title,
        **{
            k: v
            for k, v in {
                "detail": detail,
                "type": type_uri,
                "instance": instance,
                **kwargs
            }.items()
            if v is not None
        }
    }
    return {"problem": response}


def generate_basic_auth(u: str, pw: str):
    def inner(
            credentials: Annotated[HTTPBasicCredentials, Depends(security)]
    ):
        current_username_bytes = credentials.username.encode("utf8")
        is_correct_username = secrets.compare_digest(
            current_username_bytes, u.encode("utf-8")
        )

        current_password_bytes = credentials.password.encode("utf8")
        is_correct_password = secrets.compare_digest(
            current_password_bytes, pw.encode("utf-8")
        )
        if not (is_correct_username and is_correct_password):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Incorrect email or password",
                headers={"WWW-Authenticate": "Basic"},
            )
        return credentials.username

    return inner


def flatten(l):
    return [item for sublist in l for item in sublist]


logger_file_config(str(Path(__file__).parent / 'logging.conf'), disable_existing_loggers=False)
L = get_logger(__name__)
