from trytond.pool import Pool
from .stock import *
from .product import *
from .shipment import *

def register():
  Pool.register(
    StockMove,
    StockMoveSerialNumber,
    Product,
    ShipmentIn,
    ShipmentInReturn,
    ShipmentOut,
    ShipmentOutReturn,
    module='stock_serializable', type_='model')
