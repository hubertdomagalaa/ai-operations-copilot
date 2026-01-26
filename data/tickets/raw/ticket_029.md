Describe the bug
got a 500 status with "TypeError: Object of type set is not JSON serializable" if I feed a invalid httpurl as Body

To Reproduce
Steps to reproduce the behavior with a minimum self-contained file.

Create a file with:
from fastapi import FastAPI
from pydantic import BaseModel, HttpUrl


class Image(BaseModel):
    url: HttpUrl
    name: str


app = FastAPI()


@app.put("/items/image")
async def update_image(image: Image):
    return image
Open the browser and call the endpoint PUT /items/image with body value: {"url":"htp://www.google.com","name":"something"}. here the schema of URL is invalid
It returns a 500 Internal Server Error.
But I expected it to return 422 with a hint of wrong URL format.
Expected behavior
the type validation should know the wrong URL and give a clear indication

Screenshots
If applicable, add screenshots to help explain your problem.

Environment
OS: [macOS]
Python Version 3.7.5
FastAPI Version 0.44.0
pydantic Version 1.2
starlette Version 0.12.9