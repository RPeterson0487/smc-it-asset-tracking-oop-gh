"""Configuration file for database manager class.
This is set up for the SMC IT Asset Tracking project."""

# Import object class to be used as a template for objects created by the
# database manager and assign the class to the template attribute below.
import asset

template = asset.Asset

mariadb_login = {
    "host": "REDACTED",
    "database": "REDACTED",
    "username": "REDACTED",
    "password": "REDACTED"
}

search_tables = (
    "IT_Assets_DT",
    "IT_Assets_FT",
    "IT_Assets_LT",
    "IT_Assets_PR",
    "IT_Assets_SG",
    "IT_Assets_SV",
    "IT_Assets_SW",
    "IT_Assets_TB",
    "IT_Assets_TC",
    "IT_Assets",
)

insert_tables = ("IT_Assets",)