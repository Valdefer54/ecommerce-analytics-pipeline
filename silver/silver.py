import duckdb

con = duckdb.connect('../silver/ecommerce_dw_.duckdb')

con.sql("SHOW TABLES").show()
