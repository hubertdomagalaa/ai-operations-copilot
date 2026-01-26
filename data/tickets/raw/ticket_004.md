Discussed in #10856
Originally posted by adrwz December 28, 2023

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
async def upload_file_event(files: List[UploadFile]):
    print("2", files[0].filename, files[0].file._file.closed)

    # ... more code ...


@router.post("/upload_session_file")
async def upload_file(files: List[UploadFile] = File(...)):
    print("1", files[0].filename, files[0].file._file.closed)

    try:
        return StreamingResponse(
            upload_file_event(files),
            media_type="text/event-stream",
        )
    except Exception as error:
        logging.error(error)
        raise HTTPException(status_code=500, detail="Internal Server Error")
Description
Hitting this endpoint with an uploaded file on v0.105.0 will print:

1 filename false
2 filename false
Hitting this endpoint with an uploaded file on v0.106.0 will print:

1 filename false
2 filename true
Unfortunately this means I'm unable to upload files in a StreamingResponse with fastapi>=0.106.0

Operating System
macOS

Operating System Details
No response

FastAPI Version
0.105.0

Pydantic Version
2.5.3

Python Version
3.11.4

Additional Context
No response