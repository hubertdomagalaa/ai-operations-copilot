# Known Issues

This document catalogs known issues in the platform, derived from historical support tickets and engineering investigations. Each issue includes symptoms, affected versions, root cause, workarounds, and resolution status.

Use this document to:
- Quickly identify if a reported issue is known
- Provide workarounds to customers
- Avoid redundant escalations

---

## Issue Index

| ID | Category | Summary | Severity | Status |
|----|----------|---------|----------|--------|
| KI-001 | Validation | condecimal returns 500 instead of 422 | Medium | Open |
| KI-002 | Validation | allow_inf_nan not enforced on Query params | Medium | Open |
| KI-003 | Type Hints | JSONResponse type hint causes FastAPIError | Medium | Version-specific |
| KI-004 | Validation | AfterValidator silently ignored in 0.115.10 | High | Fixed upstream |
| KI-005 | Form Handling | Default values broken for form fields | High | Open |
| KI-006 | File Handling | UploadFile closed before StreamingResponse | High | Version-specific |
| KI-007 | Dependencies | Yield dependency cleanup errors after response | Low | By design |
| KI-008 | Tracebacks | Sync yield deps show incomplete tracebacks | Medium | Open |
| KI-009 | Client Disconnect | "No response returned" log spam | Low | By design |
| KI-010 | OpenAPI | Schema generation fails with extra='forbid' | High | Fixed upstream |
| KI-011 | OpenAPI | UnboundLocalError on non-integer status_code | High | Version-specific |
| KI-012 | Windows | Async subprocess raises NotImplementedError | Medium | Platform limitation |
| KI-013 | Middleware | GZipMiddleware ignores StreamingResponse | Low | By design |
| KI-014 | Middleware | BackgroundTasks blocks requests with middleware | Medium | Open |
| KI-015 | DELETE | 204 causes "Response content longer" log error | Low | By design |
| KI-016 | ASGI | GraphQL integration causes response timing error | Low | Integration issue |
| KI-017 | Performance | solve_dependencies overhead | Medium | Fixed upstream |
| KI-018 | TestClient | TypeError on 'extensions' argument | Medium | Version-specific |
| KI-019 | Validation | Empty body rejected when all fields optional | Low | By design |
| KI-020 | Serialization | jsonable_encoder fails on non-UTF8 bytes | Medium | Open |

---

## Detailed Issue Descriptions

### KI-001: condecimal Constraint Violations Return 500

**Status:** Open
**Severity:** Medium
**Category:** Validation

**Symptoms:**
- 500 Internal Server Error when condecimal constraint is violated
- TypeError in logs instead of ValidationError
- Customer expects 422 but receives 500

**Affected Versions:**
- FastAPI 0.44.0 and earlier
- Pydantic 1.x

**Root Cause:**
FastAPI's error handling does not properly catch and convert Pydantic condecimal validation errors to HTTP 422 responses.

**Workaround:**
Add explicit try/catch in endpoint or use custom exception handler:
```python
@app.exception_handler(TypeError)
async def type_error_handler(request, exc):
    # Check if this is a condecimal validation failure
    if "decimal" in str(exc).lower():
        return JSONResponse(status_code=422, content={"detail": str(exc)})
    raise exc
```

**Resolution:** None. Recommend upgrading to latest versions where behavior may differ.

---

### KI-002: allow_inf_nan Not Enforced on Query Parameters

**Status:** Open
**Severity:** Medium
**Category:** Validation

**Symptoms:**
- `allow_inf_nan=False` on Query parameter does not validate input
- inf and nan values pass through to route handler
- Handler receives invalid values, may cause assertion errors or 500

**Affected Versions:**
- FastAPI 0.111.0+
- Pydantic 2.7.x

**Root Cause:**
The `allow_inf_nan` parameter is not properly integrated into FastAPI's validation pipeline for Query parameters.

**Workaround:**
Validate manually in handler:
```python
@app.get("/endpoint")
async def handler(value: float = Query(...)):
    if not math.isfinite(value):
        raise HTTPException(status_code=422, detail="Infinite or NaN values not allowed")
    # continue
```

**Resolution:** None. Feature limitation.

---

### KI-003: JSONResponse Type Hint Causes FastAPIError

**Status:** Version-specific
**Severity:** Medium
**Category:** Type Hints

**Symptoms:**
- FastAPIError: Invalid args for response field
- Error occurs at module import/decoration time, not request time
- Error appears on Linux but may work on Windows

**Affected Versions:**
- FastAPI 0.89.0
- Fixed in later versions

**Root Cause:**
FastAPI 0.89.0 changed response field validation to check if return type hint is a valid Pydantic field type. JSONResponse is not recognized as valid.

**Workaround:**
Remove the type hint:
```python
# Instead of:
async def endpoint() -> JSONResponse:
    
# Use:
async def endpoint():
    return JSONResponse(...)
```

**Resolution:** Upgrade to FastAPI >0.89.0

---

### KI-004: AfterValidator Silently Ignored in 0.115.10

**Status:** Fixed upstream
**Severity:** High  
**Category:** Validation

**Symptoms:**
- Validator raising ValueError is ignored
- Returns HTTP 200 instead of expected 422
- Problem only when using Annotated directly in parameters
- Works correctly when used inside Pydantic models

**Affected Versions:**
- FastAPI 0.115.10 (broken)
- FastAPI 0.115.9 (working)
- Fixed in 0.115.11+

**Root Cause:**
Bug introduced in PR #13314 affecting Annotated validators in direct FastAPI parameters.

**Workaround:**
Move validation into Pydantic model:
```python
# Instead of:
async def endpoint(value: Annotated[str, AfterValidator(my_validator)]):

# Use:
class InputModel(BaseModel):
    value: Annotated[str, AfterValidator(my_validator)]

async def endpoint(input: InputModel):
```

**Resolution:** Upgrade to FastAPI 0.115.11+

---

### KI-005: Default Values Broken for Form Fields

**Status:** Open
**Severity:** High
**Category:** Form Handling

**Symptoms:**
- Empty string submitted in form returns '' instead of None default
- Default values ignored for Optional form fields
- Regression when migrating from v0.112.4 to v0.115.11

**Affected Versions:**
- FastAPI 0.115.11 (broken)
- FastAPI 0.112.4 (working)

**Root Cause:**
PRs #12134 and #12117 changed form field extraction logic, removing checks for empty fields and re-adding body fields blindly.

**Workaround:**
Explicit None coercion in handler:
```python
@app.post("/endpoint")
async def handler(field: Optional[str] = Form(None)):
    if field == "":
        field = None
    # continue
```

**Resolution:** Pin to FastAPI 0.112.4 or wait for upstream fix.

---

### KI-006: UploadFile Closed Before StreamingResponse Executes

**Status:** Version-specific
**Severity:** High
**Category:** File Handling

**Symptoms:**
- UploadFile file handle reports closed=true inside StreamingResponse generator
- Unable to read uploaded file content in streaming context
- Regression from v0.105.0 to v0.106.0

**Affected Versions:**
- FastAPI 0.106.0+ (broken)
- FastAPI 0.105.0 (working)

**Root Cause:**
FastAPI 0.106.0 introduced changes to file lifecycle management that close UploadFile handles before StreamingResponse generator executes.

**Workaround:**
Copy file contents before returning StreamingResponse:
```python
@app.post("/upload")
async def upload(file: UploadFile):
    contents = await file.read()  # Read before returning
    
    async def generate():
        yield contents  # Use copied contents
    
    return StreamingResponse(generate())
```

**Resolution:** Pin to FastAPI 0.105.0 if streaming uploads are critical.

---

### KI-007: Yield Dependency Cleanup Errors After Response

**Status:** By design
**Severity:** Low
**Category:** Dependencies

**Symptoms:**
- Dependency cleanup error occurs after HTTP 200 response is already sent
- Endpoint returns 200 instead of expected 500 when cleanup fails
- Different behavior when dependency is on router vs path function

**Affected Versions:**
- All versions

**Root Cause:**
The 'function' scope for yield dependencies is interpreted relative to where the dependency is requested (router level) rather than always being the path function.

**Workaround:**
Declare dependencies on path function, not router:
```python
# Instead of:
router = APIRouter(dependencies=[Depends(my_dep)])

# Use:
@router.get("/", dependencies=[Depends(my_dep)])
async def endpoint():
```

**Resolution:** By design. Consider if cleanup failure is acceptable for your use case.

---

### KI-008: Sync Yield Dependencies Show Incomplete Tracebacks

**Status:** Open
**Severity:** Medium
**Category:** Tracebacks

**Symptoms:**
- 500 Internal Server Error with incomplete traceback
- Traceback does not show line where exception was raised for sync yield dependencies
- Async yield dependencies show correct traceback with exception location

**Affected Versions:**
- FastAPI + Python 3.11

**Root Cause:**
Difference in how sync vs async yield dependencies handle exception context in Python 3.11, possibly related to contextmanager_in_threadpool implementation.

**Workaround:**
Use async yield dependencies for better debugging:
```python
# Instead of:
def get_db():
    db = create_db()
    try:
        yield db
    finally:
        db.close()

# Use:
async def get_db():
    db = create_db()
    try:
        yield db
    finally:
        db.close()
```

**Resolution:** None. Python/async library interaction.

---

### KI-009: "No response returned" Log Spam

**Status:** By design
**Severity:** Low
**Category:** Client Disconnect

**Symptoms:**
- "No response returned" RuntimeError spam in logs
- AnyIO EndOfStream error propagated as RuntimeError
- Occurs when client disconnects mid-request

**Affected Versions:**
- All versions with db session middleware + exception handler middleware combo

**Root Cause:**
Middleware chain does not properly handle client disconnection, causing EndOfStream to propagate as unhandled RuntimeError.

**Workaround:**
Add exception filter in logging config to suppress these specific errors.

**Resolution:** By design. Client disconnects are normal behavior.

---

### KI-010: OpenAPI Schema Generation Fails with extra='forbid'

**Status:** Fixed upstream
**Severity:** High
**Category:** OpenAPI

**Symptoms:**
- pydantic.error_wrappers.ValidationError on openapi() call
- "additionalProperties value is not a valid dict" error
- "$ref field required" error
- Breaking change when using extra='forbid' in Pydantic models

**Affected Versions:**
- FastAPI 0.99.0 (broken)
- FastAPI 0.98.0 (working)
- Pydantic 1.10.10

**Root Cause:**
JSON Schema 2020-12 upgrade removed bool as valid type for additionalProperties; it can be false to mean no additional properties allowed.

**Workaround:**
Remove `extra='forbid'` from models or upgrade.

**Resolution:** Upgrade to FastAPI 0.99.1+

---

### KI-011: UnboundLocalError on Non-Integer status_code

**Status:** Version-specific
**Severity:** High
**Category:** OpenAPI

**Symptoms:**
- UnboundLocalError: local variable 'status_code' referenced before assignment
- GET /openapi.json returns 500 Internal Server Error
- /docs page fails to load

**Affected Versions:**
- FastAPI 0.76.0

**Root Cause:**
Code path in openapi/utils.py line 261-265 does not set status_code variable when status_code_param.default is not an int.

**Workaround:**
Ensure all status_code parameters have integer defaults.

**Resolution:** Upgrade FastAPI.

---

### KI-012: Async Subprocess NotImplementedError on Windows

**Status:** Platform limitation
**Severity:** Medium
**Category:** Windows

**Symptoms:**
- NotImplementedError when calling asyncio.create_subprocess_exec
- 500 Internal Server Error on endpoint
- Works when run directly with asyncio.run but fails under uvicorn

**Affected Versions:**
- All FastAPI versions on Windows

**Root Cause:**
Windows default event loop (SelectorEventLoop) does not support subprocess operations; ProactorEventLoop is required but uvicorn does not support custom event loop configuration.

**Workaround:**
Use synchronous subprocess or run async subprocess in thread:
```python
import asyncio
import concurrent.futures

executor = concurrent.futures.ThreadPoolExecutor()

async def run_subprocess():
    loop = asyncio.get_event_loop()
    result = await loop.run_in_executor(
        executor, 
        lambda: subprocess.run(["cmd"], capture_output=True)
    )
    return result
```

**Resolution:** Platform limitation. Use Linux for production.

---

### KI-013: GZipMiddleware Does Not Compress StreamingResponse

**Status:** By design
**Severity:** Low
**Category:** Middleware

**Symptoms:**
- StreamingResponse not compressed with GZipMiddleware
- FileResponse works correctly with compression
- Inconsistent middleware behavior between response types

**Affected Versions:**
- All versions

**Root Cause:**
GZipMiddleware may not properly handle streaming response iterators or lacks Content-Length header needed for compression decision.

**Workaround:**
Compress content before streaming or use FileResponse for static content.

**Resolution:** By design. Streaming and compression have conflicting requirements.

---

### KI-014: BackgroundTasks Blocks Requests with Middleware

**Status:** Open
**Severity:** Medium
**Category:** Middleware

**Symptoms:**
- Second request to endpoint hangs pending
- Works fine without middleware
- Background task with async sleep blocks subsequent requests

**Affected Versions:**
- FastAPI 0.66.1+

**Root Cause:**
Middleware interaction with BackgroundTasks and async sleep causes request processing to block.

**Workaround:**
Use synchronous background tasks or dedicated task queue (Celery, etc.):
```python
# Instead of:
background_tasks.add_task(long_running_async_task)

# Use:
background_tasks.add_task(sync_wrapper, args)
```

**Resolution:** None. Consider using proper task queue for long-running tasks.

---

### KI-015: DELETE 204 Causes Log Error

**Status:** By design
**Severity:** Low
**Category:** DELETE

**Symptoms:**
- RuntimeError: Response content longer than Content-Length
- ERROR: Exception in ASGI application in logs
- Client receives correct 204 response despite error

**Affected Versions:**
- FastAPI 0.78.0+

**Root Cause:**
Returning None from endpoint with 204 status creates a response body mismatch with Content-Length header in Starlette/uvicorn.

**Workaround:**
Return explicit Response:
```python
from fastapi import Response

@app.delete("/resource/{id}", status_code=204)
async def delete_resource(id: str):
    # do deletion
    return Response(status_code=204)
```

**Resolution:** By design. Use explicit Response for 204.

---

### KI-016: GraphQL Integration Causes Response Timing Error

**Status:** Integration issue
**Severity:** Low
**Category:** ASGI

**Symptoms:**
- RuntimeError: Unexpected ASGI message 'http.response.start' sent, after response already completed
- ERROR: Exception in ASGI application in logs
- No erroneous client behavior

**Affected Versions:**
- FastAPI + starlette-graphene3

**Root Cause:**
GraphQL app wrapper sends response after FastAPI/Starlette has already completed the response cycle, possibly due to background tasks or async gather operations.

**Workaround:**
Filter this error in logging. Does not affect functionality.

**Resolution:** Integration limitation. Consider alternative GraphQL libraries.

---

### KI-017: solve_dependencies Performance Overhead

**Status:** Fixed upstream
**Severity:** Medium
**Category:** Performance

**Symptoms:**
- Performance overhead with Depends type dependencies
- Slow non-path parameter resolution

**Affected Versions:**
- FastAPI main branch (historical)

**Root Cause:**
Inefficient implementation in solve_dependencies function.

**Resolution:** Fixed in upstream FastAPI. Upgrade to latest.

---

### KI-018: TestClient TypeError on 'extensions'

**Status:** Version-specific
**Severity:** Medium
**Category:** TestClient

**Symptoms:**
- TypeError: Client.put() got an unexpected keyword argument 'extensions'
- Tests fail after FastAPI version update

**Affected Versions:**
- FastAPI 0.87.0 + httpx

**Root Cause:**
FastAPI TestClient passes 'extensions' parameter to httpx.Client.put() but httpx does not support this parameter.

**Workaround:**
Check httpx version compatibility or use requests-based TestClient.

**Resolution:** Check FastAPI release notes for compatible httpx version.

---

### KI-019: Empty Body Rejected When All Fields Optional

**Status:** By design
**Severity:** Low
**Category:** Validation

**Symptoms:**
- HTTP 422 returned when body is empty string
- Works with {} but not with empty body
- Inconsistent behavior between empty body and empty JSON object

**Affected Versions:**
- All versions

**Root Cause:**
FastAPI validates that JSON body must be present even when all model fields are optional.

**Workaround:**
Send `{}` instead of empty body, or make body parameter optional:
```python
from typing import Optional

@app.post("/endpoint")
async def handler(body: Optional[Model] = None):
    if body is None:
        body = Model()  # defaults
```

**Resolution:** By design. JSON body must be valid JSON.

---

### KI-020: jsonable_encoder Fails on Non-UTF8 Bytes

**Status:** Open
**Severity:** Medium
**Category:** Serialization

**Symptoms:**
- UnicodeDecodeError: 'utf-8' codec can't decode byte 0xff
- Exception in ASGI application
- Occurs when caching responses with binary data

**Affected Versions:**
- FastAPI 0.70.0
- With fastapi_cache

**Root Cause:**
Pydantic's default bytes encoder uses `lambda o: o.decode()` which assumes UTF-8 encoding, failing on binary data.

**Workaround:**
Base64 encode binary data before serialization:
```python
import base64

def encode_bytes(data: bytes) -> str:
    return base64.b64encode(data).decode('ascii')
```

**Resolution:** None. Handle binary data explicitly.

---

## Reporting New Known Issues

When you identify a new recurring issue:

1. Confirm it affects multiple customers or is reproducible
2. Check if existing issue covers it
3. Create new entry with:
   - Unique ID (KI-XXX)
   - Clear symptoms
   - Affected versions
   - Root cause (if known)
   - Workaround (if available)
   - Resolution status

4. Add to index table
5. Notify #support channel of new known issue
