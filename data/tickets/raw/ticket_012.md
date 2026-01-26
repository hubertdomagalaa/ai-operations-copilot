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
import pytest
from fastapi.testclient import TestClient

@pytest.mark.parametrize(
    ["token", "data", "status_code_returned"],
    [
        pytest.param(USER_ID_CORRECT_TOKEN, UPDATE_DATA, 200, id="update user info success"),
        pytest.param(USER_ID_FAILED_TOKEN, UPDATE_DATA, 404, id="update user info failed"),
    ],
)

def test_update_user_info(client: TestClient, token, data, status_code_returned: int):
    headers = {"Authorization": f"Bearer {token}"}
    response = client.put("/admin/user", json=data, headers=headers)
    assert response.status_code == status_code_returned
    if token == USER_ID_CORRECT_TOKEN:
        assert "success" in response.text
    elif token == USER_ID_FAILED_TOKEN:
        assert "UserNotFoundException" in response.text
Description
Hello! My test worked correctly until I wasn't updated fast api version after commit f92f87d. Commit message in Fast API repo was "Update references to Requests for tests to HTTPX, and add HTTPX to extras". After it, it was always occured an error:

 TypeError: Client.put() got an unexpected keyword argument 'extensions'

If we check fastapi TestClient.put() method, we will see that we have an "extensions" here. Also we see that super().put(..) method called

def put(  
        self,
        url: httpx._types.URLTypes,
        *,
        content: httpx._types.RequestContent = None,
        data: httpx._types.RequestData = None,
        files: httpx._types.RequestFiles = None,
        json: typing.Any = None,
        params: httpx._types.QueryParamTypes = None,
        headers: httpx._types.HeaderTypes = None,
        cookies: httpx._types.CookieTypes = None,
        auth: typing.Union[
            httpx._types.AuthTypes, httpx._client.UseClientDefault
        ] = httpx._client.USE_CLIENT_DEFAULT,
        follow_redirects: bool = None,
        allow_redirects: bool = None,
        timeout: typing.Union[
            httpx._client.TimeoutTypes, httpx._client.UseClientDefault
        ] = httpx._client.USE_CLIENT_DEFAULT,
        extensions: dict = None,
    ) -> httpx.Response:
        redirect = self._choose_redirect_arg(follow_redirects, allow_redirects)
        return super().put(
            url,
            content=content,
            data=data,
            files=files,
            json=json,
            params=params,
            headers=headers,
            cookies=cookies,
            auth=auth,
            follow_redirects=redirect,
            timeout=timeout,
            extensions=extensions,
        )
BUT! super().put(..) method its a httpx.put() method and its dont have extensions param, let's see source code of httpx

def put(self,
        url: URLTypes,
        *,
        content: RequestContent = None,
        data: RequestData = None,
        files: RequestFiles = None,
        json: typing.Any = None,
        params: QueryParamTypes = None,
        headers: HeaderTypes = None,
        cookies: CookieTypes = None,
        auth: typing.Union[AuthTypes, UseClientDefault] = USE_CLIENT_DEFAULT,
        follow_redirects: typing.Union[bool, UseClientDefault] = USE_CLIENT_DEFAULT,
        timeout: typing.Union[TimeoutTypes, UseClientDefault] = USE_CLIENT_DEFAULT,
    ) -> Response:
I'm not totally sure, but it's looks like a bug.
Thank was answering!

Operating System
Linux

Operating System Details
No response

FastAPI Version
0.87.0

Python Version
3.10

Additional Context
No response