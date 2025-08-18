# goji/app/demand/schemas.py
from ..extensions import ma
from .models import SalesOrder, SalesOrderLine, ForecastSet, ForecastLine

class SalesOrderLineSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = SalesOrderLine
        load_instance = True
        include_relationships = True

class SalesOrderSchema(ma.SQLAlchemyAutoSchema):
    lines = ma.Nested(SalesOrderLineSchema, many=True, dump_only=True)
    class Meta:
        model = SalesOrder
        load_instance = True
        include_relationships = True

class ForecastLineSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = ForecastLine
        load_instance = True
        include_relationships = True

class ForecastSetSchema(ma.SQLAlchemyAutoSchema):
    lines = ma.Nested(ForecastLineSchema, many=True, dump_only=True)
    class Meta:
        model = ForecastSet
        load_instance = True
        include_relationships = True
