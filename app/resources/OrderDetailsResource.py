from pydantic import BaseModel, Field

from .AbstractBaseResource import AbstractBaseResource
from ..services.MySQLDataService import MySQLDataService


class OrderDetail(BaseModel):
    orderNumber: int | None = None
    productCode: str = ""
    quantityOrdered: int = 0
    priceEach: float = 0.0
    orderLineNumber: int = 0


class OrderDetailCollection(BaseModel):
    items: list[OrderDetail] = Field(default_factory=list)


def _composite_key(order_number: int | str, product_code: str) -> str:
    """Build a string that identifies one orderdetails row."""
    return f"orderNumber={order_number}&productCode={product_code}"


class OrderDetailsResource(AbstractBaseResource):
    def __init__(self, config: dict | None = None) -> None:
        cfg = dict(config or {})
        super().__init__(cfg)
        service_config = {
            "table": "orderdetails",
            "primary_key_field": ["orderNumber", "productCode"],
            **cfg,
        }
        self._service = MySQLDataService(service_config)

    def get(self, template: dict) -> OrderDetailCollection:
        rows = self._service.retrieveByTemplate(template or {})
        return OrderDetailCollection(
            items=[OrderDetail.model_validate(r) for r in rows]
        )

    def get_by_id(self, id: str) -> OrderDetail:
        row = self._service.retrieveByPrimaryKey(str(id))
        if not row:
            raise ValueError(f"No orderdetail with id {id!r}")
        return OrderDetail.model_validate(row)

    def post(self, new_data: OrderDetail) -> str:
        data = new_data.model_dump(exclude_none=True)
        return self._service.create(data)

    def delete(self, id: str) -> int:
        return self._service.deleteByPrimaryKey(str(id))

    def put(self, character_id: str, new_data: OrderDetail) -> int:
        data = new_data.model_dump(exclude_none=True)
        data.pop("orderNumber", None)
        data.pop("productCode", None)
        return self._service.updateByPrimaryKey(str(character_id), data)