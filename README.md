# Truckload Optimizer (SAP Synthetic Data)

This Streamlit app generates synthetic SAP-like sales order data and optimizes truckload assignments to maximize utilization and minimize the number of trucks, subject to user-defined constraints.

## Features
- **Synthetic Data:** Generates data similar to SAP tables (VBAK, VBAP, VBPA, VBKD, VBFA).
- **Constraints:** Select and set values for max weight, volume, and pallets per truck via dropdowns.
- **Optimization:** Assigns sales orders to trucks (POs) using a mathematical optimizer (PuLP).
- **UI:** Preview data, define constraints, and view optimization results interactively.

## Setup

1. **Clone the repository or copy the files to your project directory.**

2. **Install dependencies:**
   ```sh
   pip install -r requirements.txt
   ```

## Running the App

Start the Streamlit app with:
```sh
streamlit run app.py
```

## How to Use
1. **Define Constraints:**
   - In the sidebar, select a constraint type (weight, volume, pallets) from the dropdown.
   - Enter a value and click "Add Constraint".
   - Repeat until all three constraints are set.
2. **Preview Data:**
   - Expand the data preview sections to see synthetic SAP data.
3. **Run Optimization:**
   - Click "Run Optimization" to assign sales orders to trucks based on your constraints.
   - View the number of trucks used and utilization details in the results section.

## File Structure
- `data_generation.py`: Synthetic SAP data generation functions.
- `optimizer.py`: Optimization logic using PuLP.
- `app.py`: Streamlit UI.
- `requirements.txt`: Python dependencies.

## Notes
- All data is synthetic and randomly generated for demonstration purposes.
- You must set all three constraints before running the optimizer.
- The app is modular—extend or modify constraints and data as needed.

## Example Constraints
- Max Weight per Truck (kg): e.g., 1000
- Max Volume per Truck (m3): e.g., 100
- Max Pallets per Truck: e.g., 30

---

For questions or improvements, feel free to update the code or reach out! 