# goji/app/demand/services.py

from ..extensions import db
from .models import SalesOrder, SalesOrderLine, ForecastSet, ForecastLine
from .schemas import (
    SalesOrderSchema, SalesOrderLineSchema, 
    ForecastSetSchema, ForecastLineSchema
)
from marshmallow import ValidationError

class DemandService:
    """
    Encapsulates business logic for Demand Management 
    (Sales Orders, Forecasts).
    """

    def __init__(self):
        self.sales_order_schema = SalesOrderSchema()
        self.forecast_set_schema = ForecastSetSchema()

    # =========================================================
    # Sales Order Logic
    # =========================================================

    def get_all_sales_orders(self):
        """Retrieves all sales orders."""
        return SalesOrder.query.all()

    def get_sales_order_by_id(self, order_id):
        """Retrieves a single sales order by ID."""
        return SalesOrder.query.get_or_404(order_id)

    def create_sales_order(self, data: dict) -> SalesOrder:
        """
        Creates a new sales order.
        The Schema handles the creation of nested SalesOrderLines 
        if the payload contains 'lines'.
        """
        try:
            new_order = self.sales_order_schema.load(data)
            db.session.add(new_order)
            db.session.commit()
            return new_order
        except ValidationError as err:
            raise err
        except Exception as e:
            db.session.rollback()
            raise e

    def update_sales_order(self, order_id: int, data: dict) -> SalesOrder:
        """Updates an existing sales order."""
        order = self.get_sales_order_by_id(order_id)
        try:
            updated_order = self.sales_order_schema.load(data, instance=order, partial=True)
            db.session.commit()
            return updated_order
        except ValidationError as err:
            raise err
        except Exception as e:
            db.session.rollback()
            raise e

    def delete_sales_order(self, order_id: int):
        """Deletes a sales order."""
        order = self.get_sales_order_by_id(order_id)
        try:
            db.session.delete(order)
            db.session.commit()
        except Exception as e:
            db.session.rollback()
            raise e

    # =========================================================
    # Forecast Logic
    # =========================================================

    def get_all_forecast_sets(self):
        return ForecastSet.query.all()

    def create_forecast_set(self, data: dict) -> ForecastSet:
        try:
            new_forecast = self.forecast_set_schema.load(data)
            db.session.add(new_forecast)
            db.session.commit()
            return new_forecast
        except ValidationError as err:
            raise err
        except Exception as e:
            db.session.rollback()
            raise e

# Singleton instance
demand_service = DemandService()