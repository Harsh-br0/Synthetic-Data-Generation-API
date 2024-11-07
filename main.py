from typing import Annotated, Optional

from fastapi import Depends, FastAPI, Query, Response, UploadFile, status
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from mangum import Mangum

from src.exceptions import BaseAppException
from src.exceptions.cookie_exceptions import CookieException
from src.handlers import (
    PostData,
    cookie_dependency,
    delete_cookie,
    openai_params_dependency,
    process_files,
    set_cookie,
)
from src.logging import logger

log = logger(__name__)


app = FastAPI(title="Synthetic Data Generation API")


@app.get("/", include_in_schema=False)
def home_route():
    "Testing route."
    return "OK"


@app.post("/login", tags=["Auth"])
def login_route(res: Response, data: PostData):
    "Sets the cookie with mongo and s3 creds in encrypted form."

    return set_cookie(res, data)


@app.get("/logout", tags=["Auth"])
def logout_route(res: Response):
    "Deletes the login cookie."

    return delete_cookie(res)


@app.post(
    "/process",
    tags=["Main"],
    dependencies=[Depends(cookie_dependency), Depends(openai_params_dependency)],
)
async def process_route(files: list[UploadFile], column: Annotated[Optional[str], Query()] = None):
    """
    Process route that takes a list of csv files of data with
    optional column name to pick column if multiple columns are there."""

    return await process_files(files, column)


@app.exception_handler(CookieException)
async def cookie_exception_handler(_, exc: CookieException):
    res = JSONResponse(
        status_code=status.HTTP_400_BAD_REQUEST,
        content={"message": str(exc)},
    )
    res.delete_cookie("sid", httponly=True)
    return res


@app.exception_handler(RequestValidationError)
async def pydantic_validation_exception_handler(_, exc: RequestValidationError):
    msg = ""
    for err in exc.errors():
        msg += f"{err['loc'][-1]}: {err['msg']}\n"

    return JSONResponse(
        status_code=status.HTTP_406_NOT_ACCEPTABLE,
        content={"message": msg.rstrip()},
    )


@app.exception_handler(BaseAppException)
async def base_app_exception_handler(_, exc: BaseAppException):
    return JSONResponse(
        status_code=status.HTTP_406_NOT_ACCEPTABLE,
        content={"message": str(exc)},
    )


@app.exception_handler(Exception)
async def base_exception_handler(_, exc: Exception):
    log.exception("FastAPI Base Exception Handler.")
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={"message": "Some internal server error occured."},
    )


handler = Mangum(app)
