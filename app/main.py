import os
from dotenv import load_dotenv

load_dotenv()

import sys
from pathlib import Path

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

# Allow running this file directly from PyCharm
if __package__ in (None, ""):
    sys.path.append(str(Path(__file__).resolve().parents[1]))
    from app.resources.HarryPotterResource import HarryPotterCharacter, HarryPotterCollection, HarryPotterResource
    from app.resources.CustomerResource import Customer, CustomerCollection, CustomerResource
    from app.resources.OrderResource import Order, OrderCollection, OrderResource
    from app.resources.OrderDetailsResource import OrderDetail, OrderDetailCollection, OrderDetailsResource, _composite_key
else:
    from .resources.HarryPotterResource import HarryPotterCharacter, HarryPotterCollection, HarryPotterResource
    from .resources.CustomerResource import Customer, CustomerCollection, CustomerResource
    from .resources.OrderResource import Order, OrderCollection, OrderResource
    from .resources.OrderDetailsResource import OrderDetail, OrderDetailCollection, OrderDetailsResource, _composite_key


app = FastAPI(title="W4111 HW4 API")

hp = HarryPotterResource()
customers = CustomerResource()
orders = OrderResource()
orderdetails = OrderDetailsResource()


class EchoRequest(BaseModel):
    message: str


@app.get("/")
def root():
    return {"message": "Hello from FastAPI"}


@app.get("/health")
def health():
    return {"status": "ok"}


@app.post("/echo")
def echo(payload: EchoRequest):
    return payload


# ------- Harry Potter (kept from starter) -------
@app.get("/harry-potter")
def get_hp(first_name=None, last_name=None, house_name=None):
    template = {}
    if first_name: template["first_name"] = first_name
    if last_name: template["last_name"] = last_name
    if house_name: template["house_name"] = house_name
    return hp.get(template)

@app.get("/harry-potter/{character_id}")
def get_hp_by_id(character_id: str):
    try:
        return hp.get_by_id(character_id)
    except ValueError as e:
        raise HTTPException(404, str(e))

@app.post("/harry-potter")
def create_hp(new_data: HarryPotterCharacter):
    return hp.post(new_data)

@app.put("/harry-potter/{character_id}")
def update_hp(character_id: str, new_data: HarryPotterCharacter):
    return {"updated": hp.put(character_id, new_data)}

@app.delete("/harry-potter/{character_id}")
def delete_hp(character_id: str):
    return {"deleted": hp.delete(character_id)}


# ------- Customers -------
@app.get("/customers")
def get_customers(customerName=None, city=None, state=None, country=None):
    template = {}
    if customerName: template["customerName"] = customerName
    if city: template["city"] = city
    if state: template["state"] = state
    if country: template["country"] = country
    return customers.get(template)

@app.get("/customers/{customerNumber}")
def get_customer(customerNumber: int):
    try:
        return customers.get_by_id(str(customerNumber))
    except ValueError as e:
        raise HTTPException(404, str(e))

@app.post("/customers")
def create_customer(new_data: Customer):
    return customers.post(new_data)

@app.put("/customers/{customerNumber}")
def update_customer(customerNumber: int, new_data: Customer):
    n = customers.put(str(customerNumber), new_data)
    if n == 0:
        raise HTTPException(404, "Customer not found")
    return {"updated": n}

@app.delete("/customers/{customerNumber}")
def delete_customer(customerNumber: int):
    n = customers.delete(str(customerNumber))
    if n == 0:
        raise HTTPException(404, "Customer not found")
    return {"deleted": n}


# ------- Orders -------
@app.get("/orders")
def get_orders(customerNumber: int | None = None, status=None):
    template = {}
    if customerNumber: template["customerNumber"] = customerNumber
    if status: template["status"] = status
    return orders.get(template)

@app.get("/orders/{orderNumber}")
def get_order(orderNumber: int):
    try:
        return orders.get_by_id(str(orderNumber))
    except ValueError as e:
        raise HTTPException(404, str(e))

@app.post("/orders")
def create_order(new_data: Order):
    return orders.post(new_data)

@app.put("/orders/{orderNumber}")
def update_order(orderNumber: int, new_data: Order):
    n = orders.put(str(orderNumber), new_data)
    if n == 0:
        raise HTTPException(404, "Order not found")
    return {"updated": n}

@app.delete("/orders/{orderNumber}")
def delete_order(orderNumber: int):
    n = orders.delete(str(orderNumber))
    if n == 0:
        raise HTTPException(404, "Order not found")
    return {"deleted": n}


# ------- Order Details (composite key: orderNumber + productCode) -------
@app.get("/orderdetails")
def get_orderdetails(orderNumber: int | None = None, productCode=None):
    template = {}
    if orderNumber: template["orderNumber"] = orderNumber
    if productCode: template["productCode"] = productCode
    return orderdetails.get(template)

@app.post("/orderdetails")
def create_orderdetail(new_data: OrderDetail):
    return orderdetails.post(new_data)

@app.get("/orders/{orderNumber}/orderdetails")
def get_orderdetails_for_order(orderNumber: int):
    return orderdetails.get({"orderNumber": orderNumber})

@app.get("/orders/{orderNumber}/orderdetails/{productCode}")
def get_orderdetail(orderNumber: int, productCode: str):
    try:
        return orderdetails.get_by_id(_composite_key(orderNumber, productCode))
    except ValueError as e:
        raise HTTPException(404, str(e))

@app.put("/orders/{orderNumber}/orderdetails/{productCode}")
def update_orderdetail(orderNumber: int, productCode: str, new_data: OrderDetail):
    n = orderdetails.put(_composite_key(orderNumber, productCode), new_data)
    if n == 0:
        raise HTTPException(404, "Not found")
    return {"updated": n}

@app.delete("/orders/{orderNumber}/orderdetails/{productCode}")
def delete_orderdetail(orderNumber: int, productCode: str):
    n = orderdetails.delete(_composite_key(orderNumber, productCode))
    if n == 0:
        raise HTTPException(404, "Not found")
    return {"deleted": n}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)