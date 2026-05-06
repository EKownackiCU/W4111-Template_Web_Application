from pydantic import BaseModel, Field

from .AbstractBaseResource import AbstractBaseResource
from ..services.MySQLDataService import MySQLDataService


class Customer(BaseModel):
    customerNumber: int | None = None
    customerName: str = ""
    contactLastName: str | None = None
    contactFirstName: str | None = None
    phone: str | None = None
    addressLine1: str | None = None
    addressLine2: str | None = None
    city: str | None = None
    state: str | None = None
    postalCode: str | None = None
    country: str | None = None
    salesRepEmployeeNumber: int | None = None
    creditLimit: float | None = None


class CustomerCollection(BaseModel):
    items: list[Customer] = Field(default_factory=list)


class CustomerResource(AbstractBaseResource):
    def __init__(self, config: dict | None = None) -> None:
        cfg = dict(config or {})
        super().__init__(cfg)
        service_config = {
            "table": "customers",
            "primary_key_field": "customerNumber",
            **cfg,
        }
        self._service = MySQLDataService(service_config)

    def get(self, template: dict) -> CustomerCollection:
        rows = self._service.retrieveByTemplate(template or {})
        return CustomerCollection(
            items=[Customer.model_validate(r) for r in rows]
        )

    def get_by_id(self, id: str) -> Customer:
        row = self._service.retrieveByPrimaryKey(str(id))
        if not row:
            raise ValueError(f"No customer with id {id!r}")
        return Customer.model_validate(row)

    def post(self, new_data: Customer) -> str:
        data = new_data.model_dump(exclude_none=True)
        return self._service.create(data)

    def delete(self, id: str) -> int:
        return self._service.deleteByPrimaryKey(str(id))

    def put(self, character_id: str, new_data: Customer) -> int:
        data = new_data.model_dump(exclude_none=True)
        data.pop("customerNumber", None)
        return self._service.updateByPrimaryKey(str(character_id), data)