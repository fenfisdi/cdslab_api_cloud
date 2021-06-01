from mongoengine import DateTimeField, Document

from src.utils.date_time import DateTime


class BaseDocument(Document):
    inserted_at = DateTimeField()
    updated_at = DateTimeField()

    meta = {'allow_inheritance': True, 'abstract': True}

    def clean(self):
        if not self.inserted_at:
            self.inserted_at = DateTime.current_datetime()
        self.updated_at = DateTime.current_datetime()
