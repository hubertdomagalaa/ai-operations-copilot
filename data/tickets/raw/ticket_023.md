First Check

I added a very descriptive title to this issue.

I used the GitHub search to find a similar issue and didn't find it.

I searched the FastAPI documentation, with the integrated search.

I already searched in Google "How to X in FastAPI" and didn't find any information.

I already read and followed all the tutorial in the docs and didn't find an answer.

I already checked if it is not related to FastAPI but to Pydantic.

I already checked if it is not related to FastAPI but to Swagger UI.

I already checked if it is not related to FastAPI but to ReDoc.
Commit to Help

I commit to help with one of those options 👆
Example Code
class RegistrationRequest(pydantic.BaseModel):
    order_id: str | None


@router.post("/registration")
async def registration(
    request: RegistrationRequest,
):
    if request.order_id:
        register_with_order(request.order_id)
    else:
        # This is only reached if body is '{}', if body is '' FastAPI throws 422.
        register_without_order()
Description
We are running an API endpoint which does not expect a request model.

We would like to repurpose the endpoint so that it optionally expects a JSON body. The existing logic should be available when there is no body present or the body hasn't got values for the fields.

Currently, declaring a request model class makes FastAPI return HTTP 422 errors if a user posts a request without a body.

Wanted Solution
We would like to be able to have the same behaviour with empty body and with {} as body.

Meaning that FastAPI would be configured to proceed with execution even if the body was not found, meaning that endpoint function would get to run if all request model fields were optional.

That way we could have an optional body with optional fields in our existing endpoint.

Wanted Code
class RegistrationRequest(pydantic.BaseModel):
    class Options:
        allow_empty = True

    order_id: str | None


@router.post("/registration")
async def registration(
    request: RegistrationRequest,
):
    if request.order_id:
        register_with_order(request.order_id)
    else:
        register_without_order()
Alternatives
No response

Operating System
macOS

Operating System Details
No response

FastAPI Version
0.85.1

Python Version
Python 3.10.2

Additional Context
No response