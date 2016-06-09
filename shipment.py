
from trytond.pool import PoolMeta
from trytond.model import fields

__all__ = ['ShipmentIn', 'ShipmentInReturn', 'ShipmentOut', 'ShipmentOutReturn']
__metaclass__ = PoolMeta

class ShipmentIn:
  __name__ = 'stock.shipment.in'

  serial_numbers = fields.Function(fields.One2Many('stock.move.serial_number', None, 
                                                   'Serial Numbers', readonly=True),
                                   'get_serial_numbers')

  def get_serial_numbers(self, name=None):
    serial_numbers = []
    for move in self.moves:
      for serial_number in move.input_serial_numbers:
        serial_numbers.append(serial_number)
    return [sn.id for sn in serial_numbers]

class ShipmentInReturn:
  __name__ = 'stock.shipment.in.return'

  serial_numbers = fields.Function(fields.One2Many('stock.move.serial_number', None, 
                                                   'Serial Numbers', readonly=True),
                                   'get_serial_numbers')

  def get_serial_numbers(self, name=None):
    serial_numbers = []
    for move in self.moves:
      for serial_number in move.input_serial_numbers:
        serial_numbers.append(serial_number)
    return [sn.id for sn in serial_numbers]

class ShipmentOut:
  __name__ = 'stock.shipment.out'

  serial_numbers = fields.Function(fields.One2Many('stock.move.serial_number', None, 
                                                   'Serial Numbers', readonly=True),
                                   'get_serial_numbers')

  def get_serial_numbers(self, name=None):
    serial_numbers = []
    for move in self.moves:
      for serial_number in move.output_serial_numbers:
        serial_numbers.append(serial_number)
    return [sn.id for sn in serial_numbers]

class ShipmentOutReturn:
  __name__ = 'stock.shipment.out.return'

  serial_numbers = fields.Function(fields.One2Many('stock.move.serial_number', None, 
                                                   'Serial Numbers', readonly=True),
                                   'get_serial_numbers')

  def get_serial_numbers(self, name=None):
    serial_numbers = []
    for move in self.moves:
      for serial_number in move.output_serial_numbers:
        serial_numbers.append(serial_number)
    return [sn.id for sn in serial_numbers]
