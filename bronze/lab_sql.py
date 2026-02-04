import duckdb

con = duckdb.connect("ecommerce_dw_.duckdb")

con.sql("SELECT month(fecha) FROM bronze_sales").show()
