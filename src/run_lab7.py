from database import fetch_parcels_by_land_use

from spatial import Parcel

rows = fetch_parcels_by_land_use("Residential")

print("Rows returned:", len(rows))

if rows:
    print("First database row:", rows[0])

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