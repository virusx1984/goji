# goji/app/demand/models.py
from ..extensions import db
from ..models import ModelBase
from datetime import datetime

class SalesOrder(ModelBase):
    """Master record for a sales order."""
    id = db.Column(db.Integer, primary_key=True)
    order_num = db.Column(db.String(50), nullable=False, unique=True)
    cust_id = db.Column(db.Integer, db.ForeignKey('gj_customers.id'), nullable=False)
    ship_to_loc_id = db.Column(db.Integer, db.ForeignKey('gj_customer_locations.id'), nullable=False)
    order_date = db.Column(db.Date, nullable=False)
    order_status = db.Column(db.String(50), nullable=False, default='Confirmed')

    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    created_by_id = db.Column(db.Integer, db.ForeignKey('gj_users.id'))
    updated_by_id = db.Column(db.Integer, db.ForeignKey('gj_users.id'))


class SalesOrderLine(ModelBase):
    """A single line item on a Sales Order."""
    id = db.Column(db.Integer, primary_key=True)
    order_id = db.Column(db.Integer, db.ForeignKey('gj_sales_orders.id'), nullable=False)
    line_num = db.Column(db.Integer)
    product_id = db.Column(db.Integer, db.ForeignKey('gj_products.id'), nullable=False)
    quantity = db.Column(db.Numeric(12, 4), nullable=False)
    unit_price = db.Column(db.Numeric(12, 6))
    req_ship_date = db.Column(db.Date)
    promised_ship_date = db.Column(db.Date)
    routing_id = db.Column(db.Integer, db.ForeignKey('gj_routings.id'))

    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    created_by_id = db.Column(db.Integer, db.ForeignKey('gj_users.id'))
    updated_by_id = db.Column(db.Integer, db.ForeignKey('gj_users.id'))


class ForecastSet(ModelBase):
    """A set of forecasts, typically from a customer."""
    id = db.Column(db.Integer, primary_key=True)
    cust_id = db.Column(db.Integer, db.ForeignKey('gj_customers.id'), nullable=True)
    set_name = db.Column(db.String(100), nullable=False)
    submission_date = db.Column(db.Date, nullable=False)
    period_type = db.Column(db.String(20), nullable=False) # e.g., 'Weekly', 'Monthly'
    set_status = db.Column(db.String(20), nullable=False, default='Active')

    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    created_by_id = db.Column(db.Integer, db.ForeignKey('gj_users.id'))
    updated_by_id = db.Column(db.Integer, db.ForeignKey('gj_users.id'))


class ForecastLine(ModelBase):
    """A single line item in a Forecast Set."""
    id = db.Column(db.Integer, primary_key=True)
    set_id = db.Column(db.Integer, db.ForeignKey('gj_forecast_sets.id'), nullable=False)
    product_id = db.Column(db.Integer, db.ForeignKey('gj_products.id'), nullable=False)
    period_start_date = db.Column(db.Date, nullable=False)
    quantity = db.Column(db.Numeric(12, 4), nullable=False)

    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    created_by_id = db.Column(db.Integer, db.ForeignKey('gj_users.id'))
    updated_by_id = db.Column(db.Integer, db.ForeignKey('gj_users.id'))

