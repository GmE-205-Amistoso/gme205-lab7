# Laboratory 7: Python–PostGIS to Interoperable GeoJSON

## Contents
- [Required Dependencies](#required-dependencies)
- [Database Setup](#database-setup)
- [Set up the Virtual Environment](#set-up-the-virtual-environment)
    - [Create a Python Virtual Environment](#create-a-python-virtual-environment)
    - [Install dependencies](#install-dependencies)

- [Configure Environment Variables](#configure-environment-variables)
- [Executing the Python Scripts](#executing-the-python-scripts)
- [Directory Structure](#directory-structure)
- [Data Path](#data-path)
- [Author](#author)

## Required Dependencies
Before starting, make sure that you have installed the following dependencies:

- **[Python](https://www.python.org/downloads/) >= 3.14**
- **[pip](https://pip.pypa.io/en/stable/installation/) >= 26.2.1**
- **[PostgreSQL 18](https://www.postgresql.org/download/macosx/)** with **PostGIS** enabled
- `psql` (included with PostgreSQL) and [pgAdmin 4](https://www.pgadmin.org/)
- *(Optional)* **[VSCode](https://code.visualstudio.com/)**

## Database Setup
Run these as a PostgreSQL superuser (on Homebrew/macOS this is usually your OS username). Add `-U <superuser>` to each command if you connect as a different role.

```bash
createdb gisdb
psql -d gisdb -c "CREATE EXTENSION IF NOT EXISTS postgis;"
psql -d gisdb -v ON_ERROR_STOP=1 -f <YOUR_PATH_TO>/GmE205_Lab6_Database_With_Inserts.sql
```

If the application will connect as a different role, grant it access (replace `app_user`):

```bash
psql -d gisdb -c "GRANT USAGE ON SCHEMA lab6 TO app_user;"
psql -d gisdb -c "GRANT SELECT ON ALL TABLES IN SCHEMA lab6 TO app_user;"
```

Verify the load:
```bash
psql -d gisdb \
  -c "SELECT current_database();" \
  -c "SELECT PostGIS_Version();" \
  -c "SELECT parcel_id, land_use, ST_Area(geom) AS area_sqm FROM lab6.parcels ORDER BY parcel_id;"
```

## Set up the Virtual Environment

### Create a Python Virtual Environment
From the project root, create and activate a virtual environment:

```bash
python3 -m venv .venv
source .venv/bin/activate
```

### Install Dependencies
Upgrade pip, then install the required packages:

```bash
pip install --upgrade pip
pip install -r requirements.txt
```

## Configure Environment Variables
In your root directory, run the following command:
```bash
cp .env.example .env
```
Then open `.env` and set the values for your PostgreSQL/PostGIS database.

> **Note:** `.env` contains credentials and is listed in `.gitignore`. **Never commit it.**

## Executing the Python Scripts
Make sure PostgreSQL is running and the virtual environment is active, then run the entry-point script from the project root:

```bash
python3 src/run_lab7.py
```
The script writes the result to `output/residential_parcels.geojson`.


## Directory Structure
```text
├── output                          # Generated artifacts
│   └── residential_parcels.geojson     # Exported residential parcels
├── src                             # Application source code
│   ├── database.py                     # PostgreSQL/PostGIS connection and queries
│   ├── exchange.py                     # Converts database rows/objects to GeoJSON
│   ├── run_lab7.py                     # Entry point: wires everything together and writes output/
│   └── spatial.py                      # Domain entities (e.g. Parcel, geometry primitives)
├── .env                            # Local database credentials (not included in commit)
├── .env.example                    # Template for .env
├── .gitignore                      # Files excluded from version control
├── README.md                       # Project overview, setup, and usage instructions
└── requirements.txt                # Pinned/declared third-party dependencies
```


## Data Path

### *1. What responsibility belongs to PostgreSQL/PostGIS in this workflow?*

In this workflow, PostgreSQL/PostGIS stores the parcel data and answers the question "which parcels?" through SQL. It selects the rows by `land_use`, orders them, and performs the spatial work. For instance, `ST_Transform` converts the geometry to EPSG:4326 and `ST_AsGeoJSON` returns it as GeoJSON text. Python does not compute any of this.

### *2. Why is land_use passed as a query parameter instead of inserted into the SQL string?*
Passing `land_use` separately means the database receives the SQL text and the value as two distinct things, so the value is always treated as data and never executed as SQL. This prevents **SQL injection** and lets psycopg handle quoting and types correctly. It also lets the same query be reused for other values, but I think safety is the main reason.

### *3. What changes when a database row becomes a Parcel object?*
The row is only a positional tuple (`row[0]`, `row[1]`, `row[2]`) with a geometry stored as a JSON string. `Parcel.from_row()` gives each value a meaningful name (`parcel_id`, `land_use`, `geometry`), parses the geometry into a Python dictionary, and wraps everything in an object that can have its own behavior, such as `to_feature()`.

### *4. What changes when a Parcel object becomes a GeoJSON Feature?*
When a Parcel object becomes a GeoJSON Feature, the object becomes a plain, standard structure with `type`, `id`, `geometry` and `properties`, which any GeoJSON-aware tool can read without knowing the `Parcel` class. Only the data is carried over, and `parcel_id` and `land_use` move into `properties`. The class's behavior is not part of the exchange.

### *5. Why is ST_Transform(..., 4326) placed at the exchange boundary?*
The parcels are stored in EPSG:32651, a projected CRS in metres that suits measurement. GeoJSON expects WGS 84 longitude/latitude, so the geometry must be converted before it leaves the system. Doing it in the query transforms only the exported copy, leaves the stored data unchanged, and means the file is correct for web maps, QGIS and other consumers.

### *6. Why is producing a valid GeoJSON file an interoperability exercise even though you did not build an API?*
Interoperability means different systems can exchange data without knowing each other's internals. The GeoJSON file follows an open standard, uses the CRS that standard expects, and passes a contract check, so QGIS, another script or a future web service can use it without access to the database or the Python code. The file is the exchange boundary, which is the same idea an API would implement over a network.

## 👤 Author
**ALLAN FRITZGERALD N. AMISTOSO** <br>
*2014-73618* <br>
MS Geomatics Engineering - Geoinformatics <br>
University of the Philippines Diliman
