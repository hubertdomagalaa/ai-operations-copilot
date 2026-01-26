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
from typing import Annotated

from pydantic import AfterValidator
from fastapi import FastAPI


app = FastAPI()

def validator(v):
    raise ValueError()

Ints = Annotated[list[int], AfterValidator(validator)]

@app.post("/")
def post(ints: Ints) -> None:
    return None
Description
If we run the code and send a request to the endpoint, e.g.

echo -n '[2,3,4]' | http POST http://localhost:8000
on version 0.115.9, we get a 422 but on 0.115.10 we get 200. Is this a bug?

Operating System
Linux

Operating System Details
No response

FastAPI Version
0.115.10

Pydantic Version
2.9.2, 2.10.6

Python Version
3.12

Additional Context
No response

@tiangolo writes:

This was introduced here: #13314

I'm currently investigating and a fix will be released shortly.

The problem is only when using Annotated directly in FastAPI parameters, when used inside of Pydantic models the validators work (raise) as expected:

from typing import Annotated

from fastapi import FastAPI
from pydantic import AfterValidator, BaseModel

app = FastAPI()


def validator(v):
    raise ValueError()


Ints = Annotated[list[int], AfterValidator(validator)]


class Model(BaseModel):
    ints: Ints


@app.post("/")
def post(ints: Model) -> None:
    return None