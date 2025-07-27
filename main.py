import pandas as pd

part_df = pd.read_csv('cleaned_data/Part_clean.csv')
inventory_df = pd.read_csv('cleaned_data/PartInventory_clean.csv')
mapping_df = pd.read_csv('cleaned_data/PartMapping_clean.csv')
plant_df = pd.read_csv('cleaned_data/Plant_clean.csv')

targets_df = pd.DataFrame([{
    'plant_id': '9101',
    'low_target': 10,
    'high_target': 50
}])

if 'child_part_count' in mapping_df.columns:
    mapping_df['child_part_count'] = pd.to_numeric(mapping_df['child_part_count'], errors='coerce').fillna(0).astype(int)

inventory_df = inventory_df.set_index(['part_id', 'plant_id'])

def get_available_count(part_id, plant_id):
    key = (part_id, plant_id)
    return inventory_df.loc[key]['available_unit_count'] if key in inventory_df.index else 0

def get_buildable_count(assembly_id, plant_id):
    mapping = mapping_df[mapping_df['parent_part_id'] == assembly_id]
    if mapping.empty:
        return 0
    counts = []
    for _, row in mapping.iterrows():
        available = get_available_count(row['child_part_id'], plant_id)
        counts.append(available // row['child_part_count'] if row['child_part_count'] > 0 else 0)
    return min(counts) if counts else 0

readiness_rows = []
for _, plant in plant_df.iterrows():
    plant_id = str(plant['id']).strip()
    target_row = targets_df[targets_df['plant_id'] == plant_id]
    if target_row.empty:
        continue
    target_row = target_row.iloc[0]
    low_target = target_row['low_target']
    high_target = target_row['high_target']

    for _, part in part_df.iterrows():
        part_id = part['id']
        part_category = part['part_category']
        available = get_available_count(part_id, plant_id)
        buildable = get_buildable_count(part_id, plant_id) if part_category == 'Assembly' else None
        readiness_count = available + (buildable if buildable is not None else 0)
        if part_category == 'Assembly':
            if readiness_count >= high_target:
                status = 'At High Target'
            elif readiness_count >= low_target:
                status = 'At Low Target'
            else:
                status = 'Below Target'
        else:
            status = None
        readiness_rows.append({
            'plant_id': plant_id,
            'part_id': part_id,
            'part_category': part_category,
            'readiness_count': readiness_count,
            'available_unit_count': available,
            'buildable_unit_count': buildable,
            'readiness_status': status
        })

readiness_df = pd.DataFrame(readiness_rows)

assembly_part_df = part_df[part_df['part_category'] == 'Assembly'].copy()
component_part_df = part_df[part_df['part_category'] == 'Component'].copy()
part_readiness_df = readiness_df.copy()

assembly_part_df.to_csv('AssemblyPart.csv', index=False)
component_part_df.to_csv('ComponentPart.csv', index=False)
part_readiness_df.to_csv('PartReadiness.csv', index=False)