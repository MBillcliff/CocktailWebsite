from django.core.exceptions import ValidationError
import pint
from pint.errors import UndefinedUnitError
from ingredients.models import Ingredient

def validate_unit_of_measure(value):
	ureg = pint.UnitRegistry()
	try:
		single_unit = ureg[value]
		if not single_unit.check('[volume]') and not single_unit.check('[mass]'):
			raise UndefinedUnitError()
	except UndefinedUnitError:
		raise ValidationError(f"{value} is not a valid unit")


