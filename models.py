from datetime import datetime
from flask_sqlalchemy import SQLAlchemy


db = SQLAlchemy()


class ObjectType(db.Model):
    __tablename__ = 'object_types'
    type = db.Column(db.String(20), primary_key=True, nullable=False)
    objects = db.relationship('Object', backref='object_types')

    def __repr__(self):
        return f'type {self.type}'


class Object(db.Model):
    __tablename__ = 'objects'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(20), nullable=False, unique=True)
    type = db.Column(db.String(20), db.ForeignKey('object_types.type'), nullable=False)
    time_create = db.Column(db.DateTime, default=datetime.utcnow)
    parent_id = db.Column(db.Integer, db.ForeignKey('objects.id'), nullable=True)

    def __repr__(self):
        return f'name {self.name}'

    def json(self):
        return {'id': self.id,
                'name': self.name,
                'type': self.type,
                'parent_id': self.parent_id
                }
