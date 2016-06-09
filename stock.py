
from trytond.pyson import Not, Bool, In, Or, Not, Eval
from trytond.model import ModelSQL, ModelView, fields
from trytond.pool import Pool, PoolMeta
from trytond.rpc import RPC

__all__ = ["StockMove", "StockMoveSerialNumber"]
__metaclass__ = PoolMeta

class StockMove:
  __name__ = 'stock.move'

  input_serial_numbers = fields.One2Many('stock.move.serial_number',
                                         'input_move', 'Input Serial Numbers',
                                         states={
                                           'readonly': Or(
                                                         In(Eval('state'), ['cancel', 'assigned', 'done']),
                                                         Not(Bool(Eval('product')))
                                                       ),
                                           'invisible' : Not(Bool(Eval('input_type_stock_move')))
                                         },
                                         depends=['input_type_stock_move', 'state'])
  output_serial_numbers = fields.One2Many('stock.move.serial_number',
                                          'output_move', 'Output Serial Numbers',
                                          states={
                                            'readonly': Or(
                                                          In(Eval('state'), ['cancel', 'assigned', 'done']),
                                                          Not(Bool(Eval('product')))
                                                        ),
                                            'invisible' : Not(Bool(Eval('output_type_stock_move')))
                                          },
                                          depends=['output_type_stock_move', 'state'],
                                          add_remove=[('state', '=', 'stored'),
                                                      ('output_move', '=', None),
                                                      ('input_move.product', '=', Eval('product'))])
  input_type_stock_move = fields.Function(fields.Boolean('Input Type Stock Move'),
                                          'on_change_with_input_type_stock_move')
  output_type_stock_move = fields.Function(fields.Boolean('Output Type Stock Move'),
                                           'on_change_with_output_type_stock_move')

  @classmethod
  def __setup__(cls):
    super(StockMove, cls).__setup__()

    cls._error_messages.update({
      'invalid_serial_number' : 'Serial number "%s" already stored'
    })

  @fields.depends('from_location', 'shipment')
  def on_change_with_input_type_stock_move(self, name=None):
    if self.from_location:
      location_type = self.from_location.type
      if location_type == 'production':
        return True

      if self.shipment:
        shipment_type = self.shipment.__name__
        if (shipment_type == 'stock.shipment.in') and (location_type == 'supplier'):
          return True
        if (shipment_type == 'stock.shipment.out.return') and (location_type == 'customer'):
          return True
    return False

  @fields.depends('to_location', 'shipment')
  def on_change_with_output_type_stock_move(self, name=None):
    if self.to_location and self.shipment:
      location_type = self.to_location.type
      shipment_type = self.shipment.__name__

      if (shipment_type == 'stock.shipment.out') and (location_type == 'customer'):
        return True
      if (shipment_type == 'stock.shipment.in.return') and (location_type == 'supplier'):
        return True
    return False

  @fields.depends('product', 'input_serial_numbers')
  def on_change_product(self):
    changes = super(StockMove, self).on_change_product()
    
    changes['output_serial_numbers'] = []
    if self.product:
      for record in self.input_serial_numbers:
        if not StockMoveSerialNumber.is_valid_serial_number(self, record.serial_number):
          self.raise_user_error('invalid_serial_number', record.serial_number)
    return changes

  @classmethod
  def search_rec_name(cls, name, clause):
    try:
      _, operator, value = clause

      return [('id', operator, int(value))]
    except ValueError:
      return super(StockMove, cls).search_rec_name(name, clause)

  @classmethod
  def do(cls, moves):
    super(StockMove, cls).do(moves)
    
    for move in moves:
      for serial_number in move.input_serial_numbers:
        serial_number.set_state()

      for serial_number in move.output_serial_numbers:
        serial_number.set_state()

class StockMoveSerialNumber(ModelSQL, ModelView):
  'Stock Move Serial Number'
  __name__ = 'stock.move.serial_number'

  input_move = fields.Many2One('stock.move', 'Input Stock Move',
                               ondelete='CASCADE', select=True, required=True,
                               states={
                                 'readonly' : Eval('state') != 'draft',
                               })
  output_move = fields.Many2One('stock.move', 'Output Stock Move',
                                ondelete='SET NULL', select=True,
                                states={
                                  'readonly' : Eval('state') == 'completed',
                                })
  state = fields.Selection([('draft', 'Draft'),
                            ('stored', 'Stored'),
                            ('completed', 'Completed')], 
                           'State', readonly=True, required=True)
  serial_number = fields.Char('Serial Number', required=True)
  sequence = fields.Integer('Sequence')
  
  product = fields.Function(fields.Many2One('product.product', 'Product', readonly=True),
                            'get_product', searcher="search_product")
  input_date = fields.Function(fields.Date("Input Date", readonly=True),
                               'get_input_date', searcher="search_input_date")
  output_date = fields.Function(fields.Date("Output Date", readonly=True),
                               'get_output_date', searcher="search_output_date")

  @classmethod
  def __setup__(cls):
    super(StockMoveSerialNumber, cls).__setup__()

    cls._error_messages.update({
      'already_stored' : 'Serial number "%s" already stored',
      'duplicate_serial_numbers' : '"%s", Duplicate Serial Number'
    })

  def get_rec_name(self, name=None):
    return ("%s - %s" % (self.serial_number, self.product.rec_name))

  def get_product(self, name=None):
    return self.input_move.product.id

  def get_input_date(self, name=None):
    return self.input_move.effective_date

  def get_output_date(self, name=None):
    return (self.output_move.effective_date if self.output_move else None)

  @classmethod
  def search_product(cls, name, clause):
    field, operator, value = clause

    if (field == 'product') and (operator == 'ilike'):
      return ['OR',
                ('input_move.product.code', operator, value),
                ('input_move.product.template.name', operator, value)]
    else:
      return [(field.replace('product', 'input_move.product'), operator, value)]

  @classmethod
  def search_input_date(cls, name, clause):
    return [('input_move.effective_date',) + tuple(clause[1:])]

  @classmethod
  def search_output_date(cls, name, clause):
    return [('output_move.effective_date',) + tuple(clause[1:])]

  @classmethod
  def search_rec_name(cls, name, clause):
    _, operator, value = clause

    return ['OR',
             ('input_move.product.code', operator, value),
             ('input_move.product.template.name', operator, value),
             ('serial_number', operator, value)]

  @classmethod
  def default_state(cls):
    return 'draft'

  def __get_state(self):
    state = 'draft'

    if self.input_move.state == 'done':
      state = 'stored'

      if self.output_move and (self.output_move.state == 'done'):
        state = 'completed'
    return state

  def set_state(self):
    state = self.__get_state()
    if self.state != state:
      self.write([self], {'state' : state})

  @classmethod
  def is_valid_serial_number(cls, stock_move, serial_number):
    if type(stock_move) == int:
      stock_move = Pool().get('stock.move')(stock_move)

    result = cls.search([('serial_number', '=', serial_number),
                         ('product', '=', stock_move.product),
                         ('state', 'in', ('draft', 'stored'))])
    return (len(result) == 0)

  @classmethod
  def create(cls, vlist):
    serial_numbers = []
    for record in vlist:
      serial_number = record['serial_number']

      if serial_number in serial_numbers:
        cls.raise_user_error('duplicate_serial_numbers', serial_number)
      else:
        serial_numbers.append(serial_number)

      if not cls.is_valid_serial_number(record['input_move'], serial_number):
        cls.raise_user_error('already_stored', serial_number)
    
    return super(StockMoveSerialNumber, cls).create(vlist) or vlist

  @classmethod
  def write(cls, *args):
    serial_numbers = []

    current_record = args[0]
    for argument in args:
      if type(argument) == dict:
        if 'serial_number' in argument:
          serial_number = argument['serial_number']
          
          if serial_number in serial_numbers:
            cls.raise_user_error('duplicate_serial_numbers', serial_number)
          else:
            serial_numbers.append(serial_number)
          
          if not cls.is_valid_serial_number(current_record.input_move, serial_number):
            cls.raise_user_error('already_stored', serial_number)
      else:
        current_record = argument[0]
    super(StockMoveSerialNumber, cls).write(*args)

  #@classmethod
  #def import_data(cls, fields_names, data):
  #  print fields_names, data
  #  return super(StockMoveSerialNumber, cls).import_data(fields_names, data)
