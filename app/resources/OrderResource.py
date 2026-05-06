from datetime import date
from pydantic import BaseModel, Field

from .AbstractBaseResource import AbstractBaseResource
from ..services.MySQLDataService import MySQLDataService


class Order(BaseModel):
    orderNumber: int | None = None
    orderDate: date | None = None
    requiredDate: date | None = None
    shippedDate: date | None = None
    status: str = ""
    comments: str | None = None
    customerNumber: int | None = None


class OrderCollection(BaseModel):
    items: list[Order] = Field(default_factory=list)


class OrderResource(AbstractBaseResource):
    def __init__(self, config: dict | None = None) -> None:
        cfg = dict(config or {})
        super().__init__(cfg)
        service_config = {
            "table": "orders",
            "primary_key_field": "orderNumber",
            **cfg,
        }
        self._service = MySQLDataService(service_config)

    def get(self, template: dict) -> OrderCollection:
        rows = self._service.retrieveByTemplate(template or {})
        return OrderCollection(
            items=[Order.model_validate(r) for r in rows]
        )

    def get_by_id(self, id: str) -> Order:
        row = self._service.retrieveByPrimaryKey(str(id))
        if not row:
            raise ValueError(f"No order with id {id!r}")
        return Order.model_validate(row)

    def post(self, new_data: Order) -> str:
        data = new_data.model_dump(exclude_none=True)
        return self._service.create(data)

    def delete(self, id: str) -> int:
        return self._service.deleteByPrimaryKey(str(id))

    def put(self, character_id: str, new_data: Order) -> int:
        data = new_data.model_dump(exclude_none=True)
        data.pop("orderNumber", None)
        return self._service.updateByPrimaryKey(str(character_id), data)