from contextlib import contextmanager

from typing import Dict, Optional


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
