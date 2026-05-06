import os
import mysql.connector
from mysql.connector import Error

from .AbstractBaseDataService import AbstractBaseDataService


class MySQLDataService(AbstractBaseDataService):

    def __init__(self, config: dict) -> None:
        super().__init__(config)
        self._table = config["table"]
        pk = config.get("primary_key_field", "id")
        # Normalize primary key to a list of columns (supports composite keys).
        self._pk_cols = [pk] if isinstance(pk, str) else list(pk)

        self._db_config = {
            "host": os.getenv("DatabaseHost", "localhost"),
            "port": int(os.getenv("DatabasePort", "3306")),
            "user": os.getenv("DatabaseUser", "root"),
            "password": os.getenv("DatabasePassword", ""),
            "database": os.getenv("DatabaseName", "classicmodels"),
        }

    def _parse_key(self, primary_key: str) -> tuple[str, list]:
        """Build a WHERE clause for the primary key.

        Single-column PK: primary_key is the value itself.
        Composite PK: primary_key looks like "col1=val1&col2=val2".
        """
        if len(self._pk_cols) == 1:
            return f"`{self._pk_cols[0]}` = %s", [primary_key]

        kv = {}
        for part in str(primary_key).split("&"):
            if "=" in part:
                k, v = part.split("=", 1)
                kv[k] = v
        clauses = [f"`{c}` = %s" for c in self._pk_cols]
        values = [kv[c] for c in self._pk_cols]
        return " AND ".join(clauses), values

    def retrieveByPrimaryKey(self, primary_key: str) -> dict:
        where_sql, values = self._parse_key(primary_key)
        sql = f"SELECT * FROM `{self._table}` WHERE {where_sql} LIMIT 1"
        try:
            cnx = mysql.connector.connect(**self._db_config)
            cursor = cnx.cursor(dictionary=True)
            cursor.execute(sql, values)
            row = cursor.fetchone() or {}
            cursor.close()
            cnx.close()
            return row
        except Error as e:
            print(f"[MySQLDataService.retrieveByPrimaryKey] {e}")
            raise

    def retrieveByTemplate(self, template: dict) -> list[dict]:
        sql = f"SELECT * FROM `{self._table}`"
        values = []
        if template:
            clauses = [f"`{c}` = %s" for c in template.keys()]
            sql += " WHERE " + " AND ".join(clauses)
            values = list(template.values())
        try:
            cnx = mysql.connector.connect(**self._db_config)
            cursor = cnx.cursor(dictionary=True)
            cursor.execute(sql, values)
            rows = cursor.fetchall()
            cursor.close()
            cnx.close()
            return rows
        except Error as e:
            print(f"[MySQLDataService.retrieveByTemplate] {e}")
            raise

    def create(self, payload: dict) -> str:
        cols = list(payload.keys())
        placeholders = ", ".join(["%s"] * len(cols))
        col_sql = ", ".join(f"`{c}`" for c in cols)
        sql = f"INSERT INTO `{self._table}` ({col_sql}) VALUES ({placeholders})"
        try:
            cnx = mysql.connector.connect(**self._db_config)
            cursor = cnx.cursor()
            cursor.execute(sql, list(payload.values()))
            cnx.commit()
            cursor.close()
            cnx.close()
        except Error as e:
            print(f"[MySQLDataService.create] {e}")
            raise

        # Return the PK as a string. For composite keys, join with '&'.
        if len(self._pk_cols) == 1:
            return str(payload.get(self._pk_cols[0], ""))
        return "&".join(f"{c}={payload.get(c, '')}" for c in self._pk_cols)

    def updateByPrimaryKey(self, primary_key: str, payload: dict) -> int:
        update_data = {k: v for k, v in payload.items() if k not in self._pk_cols}
        if not update_data:
            return 0
        set_sql = ", ".join(f"`{c}` = %s" for c in update_data.keys())
        where_sql, where_values = self._parse_key(primary_key)
        sql = f"UPDATE `{self._table}` SET {set_sql} WHERE {where_sql}"
        values = list(update_data.values()) + where_values
        try:
            cnx = mysql.connector.connect(**self._db_config)
            cursor = cnx.cursor()
            cursor.execute(sql, values)
            cnx.commit()
            affected = cursor.rowcount
            cursor.close()
            cnx.close()
            return affected
        except Error as e:
            print(f"[MySQLDataService.updateByPrimaryKey] {e}")
            raise

    def deleteByPrimaryKey(self, primary_key: str) -> int:
        where_sql, values = self._parse_key(primary_key)
        sql = f"DELETE FROM `{self._table}` WHERE {where_sql}"
        try:
            cnx = mysql.connector.connect(**self._db_config)
            cursor = cnx.cursor()
            cursor.execute(sql, values)
            cnx.commit()
            affected = cursor.rowcount
            cursor.close()
            cnx.close()
            return affected
        except Error as e:
            print(f"[MySQLDataService.deleteByPrimaryKey] {e}")
            raise