import json
from pathlib import Path

from database import check_connection, fetch_parcels_by_land_use
from exchange import build_feature_collection, validate_feature_collection
from spatial import Parcel

OUTPUT_PATH = Path("output/residential_parcels.geojson")

def main():
    # 1. Confirm Python can reach PostgreSQL/PostGIS.
    if not check_connection():
        return

    # 2. Retrieve selected database rows.
    rows = fetch_parcels_by_land_use("Residential")
    print("Rows returned:", len(rows))

    if rows:
        print("First database row:", rows[0])

    # 3. Convert rows into domain objects.
    parcels = [
        Parcel.from_row(row)
        for row in rows
    ]
    print("Parcel objects created:", len(parcels))

    if parcels:
        first = parcels[0]
        print(
            "First Parcel object:",
            first.parcel_id,
            first.land_use
        )

    # 4. Build the exchange representation.
    collection = build_feature_collection(parcels)
    print("GeoJSON type:", collection["type"])
    print("Feature count:", len(collection["features"]))

    # 5. Validate the minimum contract.
    try:
        validate_feature_collection(collection)
        print("GeoJSON contract check: PASSED")
    except ValueError as error:
        print("GeoJSON contract check: FAILED")
        print(error)

    # 6. Write the final exchange file.
    OUTPUT_PATH.parent.mkdir(exist_ok=True)
    OUTPUT_PATH.write_text(
        json.dumps(collection, indent=2),
        encoding="utf-8"
    )

    print("Output written:", OUTPUT_PATH)
    print("File exists:", OUTPUT_PATH.exists())

if __name__ == "__main__":
    main()
