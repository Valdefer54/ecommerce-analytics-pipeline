import unittest
import sys
import os

# agregar la carpeta padre al path para importar gen_data
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from gen_data import generate_products, generate_clients, generate_sales


class TestGenerateProducts(unittest.TestCase):
    """Tests para la función generate_products."""

    def test_generate_products_basic_count(self):
        """Verifica que la función genera el número de productos solicitado."""
        df = generate_products(20, seed=42)
        self.assertEqual(len(df), 20)

    def test_generate_products_unique_ids(self):
        """Verifica que todos los ids de producto son únicos."""
        df = generate_products(15, seed=123)
        self.assertEqual(len(df['id_producto'].unique()), 15)

    def test_generate_products_required_columns(self):
        """Verifica que existan todas las columnas requeridas."""
        df = generate_products(10, seed=99)
        required_cols = {'id_producto', 'nombre', 'categoria', 'precio'}
        self.assertTrue(required_cols.issubset(df.columns))

    def test_generate_products_valid_prices(self):
        """Verifica que todos los precios están en rango válido."""
        df = generate_products(30, seed=456)
        self.assertTrue((df['precio'] >= 5.0).all())
        self.assertTrue((df['precio'] <= 999.99).all())

    def test_generate_products_valid_categories(self):
        """Verifica que las categorías son válidas."""
        df = generate_products(25, seed=789)
        valid_cats = {
            'Electrónica', 'Hogar', 'Ropa', 'Alimentos', 'Deportes',
            'Juguetes', 'Belleza', 'Libros', 'Jardín', 'Automotriz'
        }
        self.assertTrue(df['categoria'].isin(valid_cats).all())

    def test_generate_products_seed_reproducible(self):
        """Verifica que usar la misma seed genera los mismos datos."""
        df1 = generate_products(10, seed=111)
        df2 = generate_products(10, seed=111)
        self.assertTrue(df1.equals(df2))


class TestGenerateClients(unittest.TestCase):
    """Tests para la función generate_clients."""

    def test_generate_clients_basic_count(self):
        """Verifica que la función genera el número de clientes solicitado."""
        df = generate_clients(30, seed=42)
        self.assertEqual(len(df), 30)

    def test_generate_clients_unique_ids(self):
        """Verifica que todos los ids de cliente son únicos."""
        df = generate_clients(25, seed=321)
        self.assertEqual(len(df['id_cliente'].unique()), 25)

    def test_generate_clients_ids_in_range(self):
        """Verifica que los ids están en el rango especificado."""
        df = generate_clients(50, seed=555, id_min=1, id_max=1000)
        self.assertTrue((df['id_cliente'] >= 1).all())
        self.assertTrue((df['id_cliente'] <= 1000).all())

    def test_generate_clients_required_columns(self):
        """Verifica que existan todas las columnas requeridas."""
        df = generate_clients(15, seed=222)
        required_cols = {'id_cliente', 'nombre', 'email', 'ciudad'}
        self.assertTrue(required_cols.issubset(df.columns))

    def test_generate_clients_custom_range(self):
        """Verifica que se respeta el rango personalizado de ids."""
        df = generate_clients(20, seed=666, id_min=100, id_max=200)
        self.assertTrue((df['id_cliente'] >= 100).all())
        self.assertTrue((df['id_cliente'] <= 200).all())

    def test_generate_clients_email_imperfections(self):
        """Verifica que existan emails vacíos o imperfectos (en muestras grandes)."""
        df = generate_clients(100, seed=777)
        # contar emails vacíos o con problemas
        empty_emails = df[df['email'] == ''].shape[0]
        problematic_emails = df[~df['email'].str.contains('@', na=False)].shape[0]
        # esperamos al menos algunos emails problemáticos en 100 registros
        self.assertTrue(empty_emails + problematic_emails > 0)

    def test_generate_clients_n_exceeds_range_raises(self):
        """Verifica que se lanza excepción si n > número de ids disponibles."""
        with self.assertRaises(ValueError):
            generate_clients(n=2000, seed=888, id_min=1, id_max=1000)

    def test_generate_clients_seed_reproducible(self):
        """Verifica que usar la misma seed genera los mismos datos."""
        df1 = generate_clients(20, seed=999)
        df2 = generate_clients(20, seed=999)
        self.assertTrue(df1.equals(df2))


class TestGenerateSales(unittest.TestCase):
    """Tests para la función generate_sales."""

    def test_generate_sales_basic_count(self):
        """Verifica que la función genera el número de ventas solicitado."""
        clientes = generate_clients(20, seed=100)
        productos = generate_products(15, seed=101)
        ventas = generate_sales(50, seed=102, clientes_df=clientes, productos_df=productos)
        self.assertEqual(len(ventas), 50)

    def test_generate_sales_required_columns(self):
        """Verifica que existan todas las columnas requeridas."""
        clientes = generate_clients(10, seed=200)
        productos = generate_products(10, seed=201)
        ventas = generate_sales(20, seed=202, clientes_df=clientes, productos_df=productos)
        required_cols = {'id_venta', 'fecha', 'id_cliente', 'id_producto', 'cantidad'}
        self.assertTrue(required_cols.issubset(ventas.columns))

    def test_generate_sales_valid_client_ids(self):
        """Verifica que todos los ids de cliente en ventas existen en clientes."""
        clientes = generate_clients(15, seed=300)
        productos = generate_products(10, seed=301)
        ventas = generate_sales(40, seed=302, clientes_df=clientes, productos_df=productos)
        
        cliente_ids_validos = set(clientes['id_cliente'].tolist())
        ventas_cliente_ids = set(ventas['id_cliente'].tolist())
        
        # todos los ids de cliente en ventas deben estar en clientes
        self.assertTrue(ventas_cliente_ids.issubset(cliente_ids_validos))

    def test_generate_sales_valid_product_ids(self):
        """Verifica que todos los ids de producto en ventas existen en productos."""
        clientes = generate_clients(15, seed=400)
        productos = generate_products(12, seed=401)
        ventas = generate_sales(35, seed=402, clientes_df=clientes, productos_df=productos)
        
        producto_ids_validos = set(productos['id_producto'].tolist())
        ventas_producto_ids = set(ventas['id_producto'].tolist())
        
        # todos los ids de producto en ventas deben estar en productos
        self.assertTrue(ventas_producto_ids.issubset(producto_ids_validos))

    def test_generate_sales_valid_quantities(self):
        """Verifica que las cantidades están en rango válido."""
        clientes = generate_clients(10, seed=500)
        productos = generate_products(10, seed=501)
        ventas = generate_sales(30, seed=502, clientes_df=clientes, productos_df=productos)
        
        self.assertTrue((ventas['cantidad'] >= 1).all())
        self.assertTrue((ventas['cantidad'] <= 10).all())

    def test_generate_sales_unique_ids(self):
        """Verifica que todos los ids de venta son únicos."""
        clientes = generate_clients(12, seed=600)
        productos = generate_products(10, seed=601)
        ventas = generate_sales(25, seed=602, clientes_df=clientes, productos_df=productos)
        
        self.assertEqual(len(ventas['id_venta'].unique()), len(ventas))

    def test_generate_sales_mixed_date_formats(self):
        """Verifica que existan diferentes formatos de fecha."""
        clientes = generate_clients(20, seed=700)
        productos = generate_products(15, seed=701)
        ventas = generate_sales(100, seed=702, clientes_df=clientes, productos_df=productos, p_malformed=0.5)
        
        # contar fechas que son strings (formatos descoordinados)
        string_dates = sum(isinstance(fecha, str) for fecha in ventas['fecha'])
        # con p_malformed=0.5 esperamos aprox. 50 strings en 100 registros
        self.assertTrue(string_dates > 30)  # al menos 30% deberían ser strings

    def test_generate_sales_with_empty_dataframes_raises(self):
        """Verifica que se lanza excepción si clientes o productos están vacíos."""
        import pandas as pd
        
        clientes_vacios = pd.DataFrame({'id_cliente': []})
        productos = generate_products(10, seed=800)
        
        with self.assertRaises(ValueError):
            generate_sales(20, seed=801, clientes_df=clientes_vacios, productos_df=productos)

    def test_generate_sales_synchronization(self):
        """Verifica que las ventas se sincronizan correctamente con clientes y productos."""
        clientes = generate_clients(25, seed=900)
        productos = generate_products(20, seed=901)
        ventas = generate_sales(100, seed=902, clientes_df=clientes, productos_df=productos)
        
        # verificar que cada venta tenga un cliente válido
        for idx, venta in ventas.iterrows():
            cliente_id = venta['id_cliente']
            producto_id = venta['id_producto']
            
            # debe haber al menos un cliente con este id
            self.assertTrue((clientes['id_cliente'] == cliente_id).any())
            # debe haber al menos un producto con este id
            self.assertTrue((productos['id_producto'] == producto_id).any())


if __name__ == '__main__':
    unittest.main()
