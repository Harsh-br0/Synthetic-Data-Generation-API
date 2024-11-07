import csv
from io import BytesIO, StringIO, TextIOWrapper

from fastapi import UploadFile

from ..decorators import handle_errors
from ..exceptions.csv_exceptions import (
    CSVException,
    EmptyCSVException,
    InvalidCSVException,
)


def convert_to_actual_file(f):
    return BytesIO(f.read())


class CSVFile:
    @handle_errors({csv.Error: lambda _: CSVException("Error occured while opening csv file.")})
    def __init__(self, file: UploadFile, col: str = None) -> None:
        if file.filename is None or not file.filename.lower().endswith(".csv"):
            raise InvalidCSVException(f"Invalid csv file with name '{file.filename}'")

        f = TextIOWrapper(
            convert_to_actual_file(file.file)
        )  # its a binary file , so need to convert to text file
        self._csv = csv.DictReader(f)
        self.col = col
        self.is_empty = True

    @handle_errors({csv.Error: lambda _: CSVException("Error occured while reading csv file.")})
    def iterate(self):
        for row in self._csv:
            row.pop(None, None)

            if len(row) == 0:
                continue

            value = ""
            if self.col is None:
                if len(row) > 1:
                    raise CSVException("Multiple columns found, specify a column value.")

                self.col = self._csv.fieldnames[0]
                value = row[self.col].strip()

            elif self.col not in row:
                raise CSVException("Specified column value not found in csv.")

            else:
                value = row[self.col].strip()

            if value == "":
                continue

            yield value

            self.is_empty = False

        if self.is_empty:
            raise EmptyCSVException("CSV file is empty.")


class CSVOutFile:
    def __init__(self, cols: list[str]) -> None:
        self.cols = cols

        self._file = StringIO(newline="")
        self._csv = csv.DictWriter(self._file, cols)
        self._csv.writeheader()

    @handle_errors({csv.Error: lambda _: CSVException("Error occured while writing csv file.")})
    def write(self, content: list[str]):
        self._csv.writerow(dict(zip(self.cols, content)))

    def finish(self):
        return self._file
