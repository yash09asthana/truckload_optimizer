import streamlit as st
import pandas as pd
from data_generation import generate_all_sap_data
from optimizer import optimize_truckloads

# --- UI Functions ---
def constraint_dropdown():
    """Show dropdown for constraint type and input for value."""
    constraint_options = {
        'Max Weight per Truck (kg)': 'max_weight',
        'Max Volume per Truck (m3)': 'max_volume',
        'Max Pallets per Truck': 'max_pallets'
    }
    constraint_label = st.selectbox('Select constraint type', list(constraint_options.keys()))
    constraint_key = constraint_options[constraint_label]
    value = st.number_input(f"Enter value for {constraint_label}", min_value=1.0, value=1000.0 if 'weight' in constraint_key else 100.0)
    return constraint_key, value

def show_utilization(assignments, sap_data, constraints, stage_label):
    """Show truck utilization table with percentages for weight, volume, and pallet."""
    vbap = sap_data['VBAP']
    merged = assignments.merge(vbap.groupby('VBELN').agg({'BRGEW':'sum','VOLUM':'sum','PALLET':'sum'}).reset_index(), on='VBELN')
    util = merged.groupby('PO').agg({'BRGEW':'sum','VOLUM':'sum','PALLET':'sum'}).reset_index()
    util['Weight Util %'] = 100 * util['BRGEW'] / constraints['max_weight']
    util['Volume Util %'] = 100 * util['VOLUM'] / constraints['max_volume']
    util['Pallet Util %'] = 100 * util['PALLET'] / constraints['max_pallets']
    st.write(f'{stage_label} Truck Utilization (% of constraint):')
    st.dataframe(util[['PO','BRGEW','Weight Util %','VOLUM','Volume Util %','PALLET','Pallet Util %']])
    avg = util[['Weight Util %','Volume Util %','Pallet Util %']].mean()
    maxv = util[['Weight Util %','Volume Util %','Pallet Util %']].max()
    st.write(f"Average {stage_label} Utilization: Weight {avg['Weight Util %']:.1f}%, Volume {avg['Volume Util %']:.1f}%, Pallet {avg['Pallet Util %']:.1f}%")
    st.write(f"Max {stage_label} Utilization: Weight {maxv['Weight Util %']:.1f}%, Volume {maxv['Volume Util %']:.1f}%, Pallet {maxv['Pallet Util %']:.1f}%")
    return avg, maxv

# --- Main App ---
st.title('Truckload Optimizer (SAP Synthetic Data)')

# Sidebar: constraint selection
st.sidebar.header('Define Constraints')
if 'constraints' not in st.session_state:
    st.session_state['constraints'] = {}

constraint_key, value = constraint_dropdown()
if st.sidebar.button('Add Constraint'):
    st.session_state['constraints'][constraint_key] = value

st.sidebar.write('Active Constraints:')
for k, v in st.session_state['constraints'].items():
    st.sidebar.write(f"{k}: {v}")

# Data generation
sap_data = generate_all_sap_data(num_orders=100, num_trucks=20)

# Data preview
st.subheader('Synthetic SAP Data Preview')
with st.expander('VBAK (Order Header)'):
    st.dataframe(sap_data['VBAK'].head())
with st.expander('VBAP (Order Items)'):
    st.dataframe(sap_data['VBAP'].head())
with st.expander('VBPA (Partners)'):
    st.dataframe(sap_data['VBPA'].head())
with st.expander('VBKD (Business Data)'):
    st.dataframe(sap_data['VBKD'].head())
with st.expander('VBFA (Document Flow)'):
    st.dataframe(sap_data['VBFA'].head())

# Show mapping between sales orders and purchase orders
st.subheader('Sales Order to Purchase Order Mapping (VBFA)')
mapping_df = sap_data['VBFA'][['VBELN', 'VBELV']]
st.dataframe(mapping_df)
st.write(f"Total sales orders: {mapping_df['VBELN'].nunique()}")
st.write(f"Total purchase orders: {mapping_df['VBELV'].nunique()}")
st.download_button(
    label="Download Mapping as CSV",
    data=mapping_df.to_csv(index=False),
    file_name="sales_order_to_po_mapping.csv",
    mime="text/csv"
)

# Initial allocation (Initial Stage)
st.subheader('Initial Stage: Allocation of Sales Orders to Trucks (POs)')
initial_assignments = mapping_df.rename(columns={'VBELV': 'PO'})
st.dataframe(initial_assignments)

# Show initial truck utilization by pallets
if 'max_pallets' in st.session_state['constraints']:
    po_group = initial_assignments.groupby('PO')['VBELN'].apply(list).reset_index()
    po_pallets = initial_assignments.merge(sap_data['VBAP'].groupby('VBELN').agg({'PALLET':'sum'}).reset_index(), on='VBELN')
    po_pallets_sum = po_pallets.groupby('PO')['PALLET'].sum().reset_index()
    initial_util = po_group.merge(po_pallets_sum, on='PO')
    initial_util['Pallet Utilization (%)'] = 100 * initial_util['PALLET'] / st.session_state['constraints']['max_pallets']
    initial_util['Sales Orders'] = initial_util['VBELN'].apply(lambda x: ', '.join(x))
    st.write('Initial Truck Utilization by Pallets (%):')
    st.dataframe(initial_util[['PO', 'Sales Orders', 'PALLET', 'Pallet Utilization (%)']])
else:
    st.write('Set max pallets constraint to see initial truck utilization by pallets.')

# Utilization summary for initial allocation
if all(k in st.session_state['constraints'] for k in ['max_weight','max_volume','max_pallets']):
    avg_init, max_init = show_utilization(initial_assignments, sap_data, st.session_state['constraints'], 'Initial')
else:
    st.write('Set all constraints to see utilization percentages.')

# Run optimizer
if st.button('Run Optimization'):
    if not all(k in st.session_state['constraints'] for k in ['max_weight','max_volume','max_pallets']):
        st.error('Please add all three constraints (weight, volume, pallets) before running optimization.')
    else:
        st.info('The optimizer will only shuffle and move sales orders between the initial trucks (POs) to maximize utilization, subject to constraints. All sales orders in a PO will always stay together.')
        assignments = optimize_truckloads(sap_data, st.session_state['constraints'])
        avg_opt, max_opt = show_utilization(assignments, sap_data, st.session_state['constraints'], 'Optimized')
        # Show improvement
        st.write('---')
        st.write('**Utilization Improvement (Optimized - Initial):**')
        st.write(f"Average Weight: {avg_opt['Weight Util %']-avg_init['Weight Util %']:.1f}% | Volume: {avg_opt['Volume Util %']-avg_init['Volume Util %']:.1f}% | Pallet: {avg_opt['Pallet Util %']-avg_init['Pallet Util %']:.1f}%")
        st.write(f"Max Weight: {max_opt['Weight Util %']-max_init['Weight Util %']:.1f}% | Volume: {max_opt['Volume Util %']-max_init['Volume Util %']:.1f}% | Pallet: {max_opt['Pallet Util %']-max_init['Pallet Util %']:.1f}%") 