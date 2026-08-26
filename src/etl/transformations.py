from datetime import date

from src.etl.helpers import Reader, Writer, TripDataType

class TransformationsEtl:
    def __init__(self, _date: date, year: int, month: int):
        self.reader = Reader(_date,(year, month)) if year and month else Reader(_date,None)
        self.writer = Writer(_date)

    def read_input_lookup(self):
        return self.reader.read_lookup_data()

    def read_input_trip(self):
        return self.reader.read_trip_data_raw(TripDataType.yellow)
