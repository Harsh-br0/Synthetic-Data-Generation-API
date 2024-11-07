from typing import Optional

from bson import ObjectId
from pydantic import BaseModel, Field

from .utils import make_id


class GeneratedData(BaseModel):
    customer_support: Optional[str] = None
    sales_agent: Optional[str] = None


class GenerationStatus(BaseModel):
    id: ObjectId = Field(alias="_id", default_factory=make_id)
    succeed: bool
    reason: Optional[str] = None
    source: str
    generated_data: GeneratedData = GeneratedData()

    class Config:
        arbitrary_types_allowed = True

    def set_data(self, support_data, sales_data):
        data = GeneratedData(customer_support=support_data, sales_agent=sales_data)
        self.generated_data = data


class SyntheticDataDoc(BaseModel):
    id: ObjectId = Field(alias="_id", default_factory=make_id)
    file_name: str
    succeed: bool
    col_name: Optional[str] = None
    reason: Optional[str] = None
    data: list[GenerationStatus] = []

    class Config:
        arbitrary_types_allowed = True

    def add_status(self, status: GenerationStatus):
        self.data.append(status)
