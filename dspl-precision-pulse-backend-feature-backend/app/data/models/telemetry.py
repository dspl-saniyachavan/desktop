from ..models import db
from datetime import datetime

class Telemetry(db.Model):
    __tablename__ = "telemetry"

    id = db.Column(db.Integer, primary_key=True)
    value_int = db.Column(db.Integer)
    value_float = db.Column(db.Float)
    value_bool = db.Column(db.Boolean)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
