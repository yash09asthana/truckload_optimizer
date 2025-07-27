import pandas as pd
import numpy as np
from typing import Tuple, Dict

def generate_vbak(num_orders: int = 100) -> pd.DataFrame:
    """Generate synthetic VBAK (Sales Order Header) data."""
    orders = [f"SO{1000+i}" for i in range(num_orders)]
    order_types = np.random.choice(['OR', 'RE', 'ZOR'], num_orders)
    dates = pd.date_range('2023-01-01', periods=num_orders, freq='D')
    return pd.DataFrame({
        'VBELN': orders,
        'AUART': order_types,
        'ERDAT': dates
    })

def generate_vbap(vbak: pd.DataFrame, max_items_per_order: int = 5) -> pd.DataFrame:
    """Generate synthetic VBAP (Sales Order Items) data with weight, volume, pallets."""
    rows = []
    for order in vbak['VBELN']:
        num_items = np.random.randint(1, max_items_per_order+1)
        for item in range(1, num_items+1):
            material = f"MAT{np.random.randint(100,999)}"
            qty = np.random.randint(1, 20)
            weight = np.random.uniform(10, 200) * qty
            volume = np.random.uniform(0.5, 5) * qty
            pallets = np.random.randint(1, 4)
            rows.append({
                'VBELN': order,
                'POSNR': f"{item:04d}",
                'MATNR': material,
                'KWMENG': qty,
                'BRGEW': weight,
                'VOLUM': volume,
                'PALLET': pallets
            })
    return pd.DataFrame(rows)

def generate_vbpa(vbak: pd.DataFrame) -> pd.DataFrame:
    """Generate synthetic VBPA (Partner) data."""
    partners = []
    for order in vbak['VBELN']:
        for func, prefix in [('AG', 'CUST'), ('WE', 'SHIP')]:
            partners.append({
                'VBELN': order,
                'PARVW': func,
                'KUNNR': f"{prefix}{np.random.randint(100,999)}"
            })
    return pd.DataFrame(partners)

def generate_vbkd(vbak: pd.DataFrame) -> pd.DataFrame:
    """Generate synthetic VBKD (Business Data) data."""
    pricing = np.random.uniform(1000, 10000, len(vbak))
    delivery_dates = vbak['ERDAT'] + pd.to_timedelta(np.random.randint(1, 10, len(vbak)), unit='D')
    return pd.DataFrame({
        'VBELN': vbak['VBELN'],
        'NETWR': pricing,
        'LFDAT': delivery_dates
    })

def generate_vbfa(vbak: pd.DataFrame, num_trucks: int = 20) -> pd.DataFrame:
    """Generate synthetic VBFA (Document Flow) data linking POs (truckloads) to sales orders."""
    trucks = [f"PO{2000+i}" for i in range(num_trucks)]
    assignments = np.random.choice(trucks, len(vbak))
    return pd.DataFrame({
        'VBELV': assignments,  # PO number (truckload)
        'VBELN': vbak['VBELN']  # Sales order
    })

def generate_all_sap_data(num_orders: int = 100, num_trucks: int = 20) -> Dict[str, pd.DataFrame]:
    """Generate all synthetic SAP tables and return as a dict of DataFrames."""
    vbak = generate_vbak(num_orders)
    vbap = generate_vbap(vbak)
    vbpa = generate_vbpa(vbak)
    vbkd = generate_vbkd(vbak)
    vbfa = generate_vbfa(vbak, num_trucks)
    return {'VBAK': vbak, 'VBAP': vbap, 'VBPA': vbpa, 'VBKD': vbkd, 'VBFA': vbfa} 