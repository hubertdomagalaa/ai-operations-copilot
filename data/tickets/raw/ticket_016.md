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
# does not apply
Description
Debugging a FastAPI application and the overhead introduced by adding Depends type dependencies to endpoints led me to discover problems in the way dependencies are solved. Please see PR #5554 for information.
That PR removes a performance bug in solve_dependencies as well as speeding up non-path parameters for endpoints.
I'm adding this defect for visibilty

Operating System
Windows

Operating System Details
No response

FastAPI Version
"main" branch

Python Version
3.10

Additional Context
No response