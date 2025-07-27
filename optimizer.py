import pandas as pd
from typing import Dict, Any, List
import pulp

def optimize_truckloads(sap_data: Dict[str, pd.DataFrame], constraints: Dict[str, float]) -> pd.DataFrame:
    """
    Shuffle initial PO-to-sales order assignments among the same set of trucks (POs) to maximize utilization.
    A truck is considered used if any of its constraints (weight, volume, or pallet) is met first.
    All sales orders in a PO must stay together.
    Returns a DataFrame with order assignments.
    """
    vbap = sap_data['VBAP']
    vbfa = sap_data['VBFA']
    orders = vbap['VBELN'].unique()
    trucks = vbfa['VBELV'].unique()

    # Aggregate order-level totals
    order_totals = vbap.groupby('VBELN').agg({
        'BRGEW': 'sum',
        'VOLUM': 'sum',
        'PALLET': 'sum'
    }).reset_index()
    order_totals = order_totals.set_index('VBELN')

    # Map each PO to its sales orders
    po_to_orders = vbfa.groupby('VBELV')['VBELN'].apply(list).to_dict()
    po_list = list(po_to_orders.keys())

    # Model
    prob = pulp.LpProblem("TruckloadOptimization", pulp.LpMinimize)
    # z[t] = 1 if truck t is used
    z = pulp.LpVariable.dicts('used', (t for t in trucks), cat='Binary')
    # assign[(po, t)] = 1 if PO po is assigned to truck t
    assign = pulp.LpVariable.dicts('assign', ((po, t) for po in po_list for t in trucks), cat='Binary')

    # Each PO assigned to exactly one truck
    for po in po_list:
        prob += pulp.lpSum([assign[(po, t)] for t in trucks]) == 1

    # If a PO is assigned to a truck, that truck is used
    for po in po_list:
        for t in trucks:
            prob += assign[(po, t)] <= z[t]

    # Truck constraints: sum over all orders in POs assigned to truck t
    for t in trucks:
        prob += pulp.lpSum([
            sum(order_totals.loc[o, 'BRGEW'] for o in po_to_orders[po]) * assign[(po, t)]
            for po in po_list
        ]) <= constraints['max_weight'] * z[t]
        prob += pulp.lpSum([
            sum(order_totals.loc[o, 'VOLUM'] for o in po_to_orders[po]) * assign[(po, t)]
            for po in po_list
        ]) <= constraints['max_volume'] * z[t]
        prob += pulp.lpSum([
            sum(order_totals.loc[o, 'PALLET'] for o in po_to_orders[po]) * assign[(po, t)]
            for po in po_list
        ]) <= constraints['max_pallets'] * z[t]

    # Objective: minimize number of trucks used
    prob += pulp.lpSum([z[t] for t in trucks])

    prob.solve()

    assignments = []
    for po in po_list:
        for t in trucks:
            if pulp.value(assign[(po, t)]) == 1:
                for o in po_to_orders[po]:
                    assignments.append({'VBELN': o, 'PO': t})
    return pd.DataFrame(assignments) 