
from trytond.pool import Pool, PoolMeta
from trytond.model import fields

__all__ = ["Product"]
__metaclass__ = PoolMeta

class Product:
  __name__ = 'product.product'

  completed_serial_numbers = fields.Function(fields.One2Many('stock.move.serial_number',
                                                             None, 'Completed Serial Numbers',
                                                             readonly=True),
                                             'get_completed_serial_numbers')
  pending_serial_numbers = fields.Function(fields.One2Many('stock.move.serial_number',
                                                           None, 'Pending Serial Numbers',
                                                           readonly=True),
                                           'get_pending_serial_numbers')

  def get_completed_serial_numbers(self, name=None):
    StockMoveSerialNumber = Pool().get('stock.move.serial_number')

    serial_numbers = StockMoveSerialNumber.search([('state', '=', 'completed'),
                                                   ('input_move.product', '=', self)])
    return [s.id for s in serial_numbers]

  def get_pending_serial_numbers(self, name=None):
    StockMoveSerialNumber = Pool().get('stock.move.serial_number')

    serial_numbers = StockMoveSerialNumber.search([('state', '!=', 'completed'),
                                                   ('input_move.product', '=', self)])
    return [s.id for s in serial_numbers]    
