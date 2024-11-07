import asyncio
from functools import partial
from io import BytesIO
from pathlib import Path

from fastapi import Response, UploadFile

from ..defaults import COOKIE_DURATION, MIN_DATA_LENGTH, S3_UPLOAD_FOLDER
from ..exceptions import BaseAppException
from ..exceptions.common import DataTooShort
from ..logging import logger
from ..mongo.db import Database
from ..mongo.model import GenerationStatus, SyntheticDataDoc
from ..mongo.utils import ensure_connection
from ..openai.synthetic_model import SyntheticDataModel
from ..s3.bucket import Bucket
from ..s3.utils import ensure_session
from ..utils import ensure_string_in_dict
from .csv_file import CSVFile, CSVOutFile
from .encrypted_cookie import EncryptedCookie
from .fetch_url import FetchWrapper
from .models import PostData

log = logger(__name__)


def set_cookie(res: Response, data: PostData):
    # check for creds first
    ensure_connection(data.mongo_url)
    ensure_session(data.s3_params)

    cookie = EncryptedCookie()
    session_data = cookie.encrypt(data.model_dump())
    res.set_cookie("sid", session_data, COOKIE_DURATION, httponly=True)
    return {"ok": True}


def delete_cookie(res: Response):
    res.delete_cookie("sid", httponly=True)  # delete it if present, otherwise no-op
    return {"ok": True}


def process_data(source: str, model: SyntheticDataModel):

    status = GenerationStatus(succeed=False, source=source)

    try:
        if FetchWrapper.is_url(source):
            source = FetchWrapper.fetch_url(source)

        elif FetchWrapper.is_url("http://" + source):  # re validating without http
            source = FetchWrapper.fetch_url("http://" + source)

        # here we have either url fetched data or src data
        if len(source) < MIN_DATA_LENGTH:
            raise DataTooShort("Source data is too short to generate interactions.")

        support_data = model.generate_customer_support_interactions(source)
        sales_data = model.generate_sales_agent_interactions(source)

    except BaseAppException as e:
        status.reason = str(e)

    except Exception:
        log.exception("Exception while processing data.")
        status.reason = "Some Internal error occurred."

    else:
        status.succeed = True
        status.set_data(support_data, sales_data)

    finally:
        return status


def upload_to_s3(bucket, key: str, data: str):
    file = BytesIO(data.encode("utf-8"))
    bucket.upload_file(key, file)
    file.close()


async def process_file(file: UploadFile, column, model: SyntheticDataModel, res: list, errs: list):
    succeed = False
    reason = None

    try:
        csv = CSVFile(file, column)

        statuses = await asyncio.gather(
            *[asyncio.to_thread(partial(process_data, source, model)) for source in csv.iterate()]
        )

    except BaseAppException as e:
        reason = str(e)

    except Exception:
        log.exception("Exception while processing file.")
        reason = "Some Internal error occurred."

    else:
        succeed = True

    finally:

        db = Database()

        doc = SyntheticDataDoc(
            file_name=file.filename,
            succeed=succeed,
            reason=reason,
        )

        csv_out = CSVOutFile(["customer_support", "sales_agent"])
        generation_errs = []

        if doc.succeed:
            doc.col_name = csv.col
            all_failed = True
            for status in statuses:
                if not status.succeed:
                    generation_errs.append(
                        ensure_string_in_dict(status.model_dump(include=["id", "reason"]))
                    )
                else:
                    all_failed = False
                    data = status.generated_data
                    csv_out.write([data.customer_support, data.sales_agent])

                doc.add_status(status)

            if all_failed:
                doc.succeed = False
                doc.reason = "All generation statuses failed."

        else:
            errs.append(doc.model_dump(include=["file_name", "reason"]))

        if len(generation_errs) > 0:
            errs.append({"file_name": doc.file_name, "errs": generation_errs})

        db.insert(doc)

        if doc.succeed:
            res.append(ensure_string_in_dict(doc.model_dump(include=["id", "file_name"])))
            bucket = Bucket()
            await asyncio.to_thread(
                partial(
                    upload_to_s3,
                    bucket,
                    Path(S3_UPLOAD_FOLDER, str(doc.id) + ".csv").as_posix(),
                    csv_out.finish().getvalue(),
                )
            )


async def process_files(files: list[UploadFile], column: str = None):
    if column is not None:
        column = column.strip()
        if len(column) == 0:
            column = None

    model = SyntheticDataModel()
    res, errs = [], []
    await asyncio.gather(*[process_file(file, column, model, res, errs) for file in files])
    return {"files": res, "errors": errs}
