Adding this issue for completeness.

Solved by: #14301

Discussed in #14296
Originally posted by guldfisk November 5, 2025

First Check

I added a very descriptive title here.

I used the GitHub search to find a similar question and didn't find it.

I searched the FastAPI documentation, with the integrated search.

I already searched in Google "How to X in FastAPI" and didn't find any information.

I already read and followed all the tutorial in the docs and didn't find an answer.

I already checked if it is not related to FastAPI but to Pydantic.

I already checked if it is not related to FastAPI but to Swagger UI.

I already checked if it is not related to FastAPI but to ReDoc.
Commit to Help

I commit to help with one of those options 👆
Example Code
from types import NoneType
from typing import Iterator, Annotated

from fastapi import APIRouter
from fastapi import Depends
from fastapi import FastAPI


app = FastAPI()


class ApplicationError(Exception): ...


def dependency_with_cleanup_error() -> Iterator[None]:
    yield
    raise ApplicationError()


router = APIRouter(
    dependencies=[Depends(dependency_with_cleanup_error, scope="function")]
)


@router.get("/broken")
def broken():
    # Will return 200, and then fail in the cleanup.
    return {"status": "ok"}


@router.get("/works")
def endpoint(
    v: Annotated[NoneType, Depends(dependency_with_cleanup_error, scope="function")],
):
    # Will correctly return 500
    return {"status": "ok"}


app.include_router(router)
Description
When using the new "scope" feature for yield dependencies, function scope is still cleaned up after the response is sent, if the dependency is requested in the api router, instead of on the path function.

Maybe this is a feature, as in "function" should be interpreted as the scope of where the dependency is requested, and not always the path function, but I can't find any documentation mentioning this behavior, and in any case I'm not sure what the usecase for that would be.

Operating System
Linux

Operating System Details
No response

FastAPI Version
0.121.0

Pydantic Version
2.12.3

Python Version
3.11.12

Additional Context
No response