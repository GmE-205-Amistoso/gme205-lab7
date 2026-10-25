import json

class Parcel:
    def __init__(self, parcel_id, land_use, geometry):
        self._parcel_id = parcel_id
        self._land_use = land_use
        self._geometry = geometry

    @classmethod
    def from_row(cls, row):
        return cls(
            parcel_id = row[0],
            land_use = row[1],
            geometry = json.loads(row[2])
        )

    def to_feature(self):
        return {
            "type": "Feature",
            "id": self._parcel_id,
            "geometry": self._geometry,
            "properties": {
                "parcel_id": self._parcel_id,
                "land_use": self._land_use
            }
        }

    @property
    def parcel_id(self) -> str:
        return self._parcel_id

    @property
    def land_use(self) -> str:
        return self._land_use