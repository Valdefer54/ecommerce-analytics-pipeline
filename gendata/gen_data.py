import pandas as pd
import random
from faker import Faker
import os
import sys

csv_productos ={
    'id_producto' : [],
    'nombre' : [],
    'categoria' : [],
    'precio' : [],
}

csv_clientes = {
    'id_cliente' : [],
    'nombre' : [],
    'email' : [],
    'ciudad' : []
}

csv_ventas = {
    'id_venta' : [],
    'fecha' : [],
    'id_cliente' : [],
    'id_producto' : [],
    'cantidad' : []
}

Productos = pd.DataFrame(csv_productos)
Clientes = pd.DataFrame(csv_clientes)
Ventas = pd.DataFrame(csv_ventas)

def generate_products(n=50, seed: int | None = None):
    """Genera `n` productos aleatorios y devuelve un DataFrame.

    - `n`: número de productos a generar.
    - `seed`: semilla opcional para reproducibilidad.
    """
    faker = Faker()
    if seed is not None:
        random.seed(seed)
        Faker.seed(seed)

    categorias = [
        'Electrónica', 'Hogar', 'Ropa', 'Alimentos', 'Deportes',
        'Juguetes', 'Belleza', 'Libros', 'Jardín', 'Automotriz'
    ]

    start_id = 1
    if not Productos.empty:
        try:
            start_id = int(Productos['id_producto'].max()) + 1
        except Exception:
            start_id = len(Productos) + 1

    rows = []
    next_id = start_id
    for _ in range(n):
        nombre = f"{faker.unique.word().capitalize()} {faker.word().capitalize()}"
        categoria = random.choice(categorias)
        precio = round(random.uniform(5.0, 999.99), 2)
        rows.append({
            'id_producto': next_id,
            'nombre': nombre,
            'categoria': categoria,
            'precio': precio,
        })
        next_id += 1

    return pd.DataFrame(rows)

def generate_clients(n=100, seed: int | None = None, id_min: int = 1, id_max: int = 1000):
    """
    Genera `n` clientes aleatorios y devuelve un DataFrame.
    - `n`: número de clientes a generar (máx. id_max-id_min+1).
    - `seed`: semilla opcional para reproducibilidad.
    - `id_min`, `id_max`: rango (inclusive) de ids posibles.
    Emails: algunos estarán vacíos; otros tendrán caracteres en mayúsculas
    o estarán corruptos (por ejemplo sin '@').
    """
    faker = Faker()
    if seed is not None:
        random.seed(seed)
        Faker.seed(seed)

    total_ids = id_max - id_min + 1
    if n > total_ids:
        raise ValueError(f"n ({n}) es mayor que el número de ids únicos disponibles ({total_ids}).")

    # ids únicos aleatorios sin repetición
    ids = random.sample(list(range(id_min, id_max + 1)), n)

    rows = []
    for uid in ids:
        nombre = faker.name()
        ciudad = faker.city()

        # generar email base
        email = faker.email()

        # introducir imperfecciones aleatorias
        r = random.random()
        if r < 0.12:
            # 12%: registro vacío (sin email)
            email = ''
        elif r < 0.30:
            # 18%: mayúsculas en posiciones aleatorias
            # convierto algunos caracteres a mayúsculas
            chars = list(email)
            # evitar vacíos
            if chars:
                for _ in range(random.randint(1, max(1, len(chars)//6))):
                    idx = random.randrange(len(chars))
                    chars[idx] = chars[idx].upper()
                email = ''.join(chars)
        elif r < 0.40:
            # 10%: correo corrupto (p. ej. sin '@' o con espacios)
            if '@' in email and random.random() < 0.7:
                email = email.replace('@', '')  # quitar '@'
            else:
                email = email.replace('@', '@ ')  # añadir espacio
        # else: email correcto (posible con mayúsculas por faker aleatorio)

        rows.append({
            'id_cliente': uid,
            'nombre': nombre,
            'email': email,
            'ciudad': ciudad
        })

    return pd.DataFrame(rows)

def generate_sales(n=100, seed: int | None = None, clientes_df: pd.DataFrame | None = None,
                   productos_df: pd.DataFrame | None = None, p_malformed: float = 0.2):
    """Genera `n` ventas aleatorias vinculadas a `clientes_df` y `productos_df`.

    - `clientes_df`: DataFrame con columna `id_cliente`. Si es None usa el global `Clientes`.
    - `productos_df`: DataFrame con columna `id_producto`. Si es None usa el global `Productos`.
    - `p_malformed`: probabilidad de que la fecha se devuelva como string en formato "descoordinado".

    Devuelve un DataFrame con columnas: `id_venta`, `fecha`, `id_cliente`, `id_producto`, `cantidad`.
    """
    faker = Faker()
    if seed is not None:
        random.seed(seed)
        Faker.seed(seed)

    if clientes_df is None:
        clientes_df = Clientes
    if productos_df is None:
        productos_df = Productos

    if clientes_df is None or 'id_cliente' not in clientes_df.columns or clientes_df.empty:
        raise ValueError("`clientes_df` debe proporcionarse y contener 'id_cliente' no vacío")
    if productos_df is None or 'id_producto' not in productos_df.columns or productos_df.empty:
        raise ValueError("`productos_df` debe proporcionarse y contener 'id_producto' no vacío")

    cliente_ids = clientes_df['id_cliente'].tolist()
    producto_ids = productos_df['id_producto'].tolist()

    from datetime import datetime, timedelta

    # formatos de fecha posibles (strings)
    date_formats = [
        lambda d: d.strftime('%Y-%m-%d'),
        lambda d: d.strftime('%d/%m/%Y'),
        lambda d: d.strftime('%m-%d-%Y'),
        lambda d: d.strftime('%b %d, %Y'),
        lambda d: d.strftime('%Y/%m/%d %H:%M'),
    ]

    rows = []
    next_id = 1
    for _ in range(n):
        id_cliente = random.choice(cliente_ids)
        id_producto = random.choice(producto_ids)
        cantidad = random.randint(1, 10)

        base_date = faker.date_between(start_date='-365d', end_date='today')
        dt = datetime.combine(base_date, datetime.min.time()) + timedelta(seconds=random.randint(0, 86400))

        if random.random() < p_malformed:
            fmt = random.choice(date_formats)
            fecha = fmt(dt)
            # introducir pequeñas imperfecciones
            if random.random() < 0.15:
                fecha = fecha.replace('  ', ' ')
            if random.random() < 0.10:
                fecha = fecha.replace('-', '/')
        else:
            fecha = dt

        rows.append({
            'id_venta': next_id,
            'fecha': fecha,
            'id_cliente': id_cliente,
            'id_producto': id_producto,
            'cantidad': cantidad,
        })
        next_id += 1

    return pd.DataFrame(rows)

if __name__ == '__main__':
    # --- Definir nombres de archivo ---
    PRODUCTOS_CSV = 'productos.csv'
    CLIENTES_CSV = 'clientes.csv'
    VENTAS_CSV = 'ventas.csv'

    # --- Verificación de existencia de archivos ---
    if os.path.exists(PRODUCTOS_CSV) or os.path.exists(CLIENTES_CSV) or os.path.exists(VENTAS_CSV):
        print("Error: Uno o más archivos CSV ya existen (productos.csv, clientes.csv, ventas.csv).")
        print("Por favor, elimínalos o cámbialos de nombre antes de generar nuevos datos.")
        sys.exit(1)
        
    # --- Generación de Datos ---
    NUM_CLIENTES = 500
    NUM_PRODUCTOS = 200
    NUM_VENTAS = 2500

    print(f"Generando {NUM_PRODUCTOS} productos...")
    df_prods = generate_products(n=NUM_PRODUCTOS, seed=42)
    
    print(f"Generando {NUM_CLIENTES} clientes...")
    df_clis = generate_clients(n=NUM_CLIENTES, seed=42, id_min=1, id_max=NUM_CLIENTES)

    print(f"Generando {NUM_VENTAS} ventas...")
    df_ventas = generate_sales(n=NUM_VENTAS, seed=42, clientes_df=df_clis, productos_df=df_prods, p_malformed=0.3)

    # --- Exportación a CSV ---
    try:
        print("\nExportando a archivos CSV...")
        df_prods.to_csv(PRODUCTOS_CSV, index=False, encoding='utf-8')
        print(f" -> {PRODUCTOS_CSV} ... OK")
        
        df_clis.to_csv(CLIENTES_CSV, index=False, encoding='utf-8')
        print(f" -> {CLIENTES_CSV} ... OK")

        df_ventas.to_csv(VENTAS_CSV, index=False, encoding='utf-8')
        print(f" -> {VENTAS_CSV} ... OK")
        
        print("\n¡Exportación completada!")

    except Exception as e:
        print(f"\nError durante la exportación a CSV: {e}")
