import duckdb

con = duckdb.connect("ecommerce_dw_.duckdb")


con.sql("CREATE TABLE bronze_clients AS SELECT *, now() AS ingest_ts FROM read_csv('clientes.csv')")
con.sql("CREATE TABLE bronze_products AS SELECT *, now() AS ingest_ts FROM read_csv('productos.csv')")
con.sql("CREATE TABLE bronze_sales AS SELECT *, now() AS ingest_ts FROM read_csv('ventas.csv')")


con.sql("SELECT 'bronze_clients' AS table_name, COUNT(*) AS rows FROM bronze_clients UNION ALL SELECT 'bronze_products', COUNT(*) FROM bronze_products UNION ALL SELECT 'bronze_sales', COUNT(*) FROM bronze_sales;").show()    
