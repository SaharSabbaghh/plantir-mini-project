import pandas as pd
import re

def to_snake_case(s):
    s = re.sub('(.)([A-Z][a-z]+)', r'\_\12', s)
    s = re.sub('([a-z0-9])([A-Z])', r'\1_\2', s)
    s = s.replace(" ", "_")
    return s.lower()

def clean_columns(df):
    df.columns = [to_snake_case(col.strip()) for col in df.columns]
    return df

part_df = pd.read_csv('Part.csv', dtype=str)
part_df = clean_columns(part_df)
part_df = part_df.applymap(lambda x: x.strip() if isinstance(x, str) else x)
part_df = part_df.drop_duplicates(subset=['id'])
part_df = part_df.dropna(subset=['id', 'part_category'])

inventory_df = pd.read_csv('PartInventory.csv', dtype={'PartID': str, 'PlantID': str, 'AvailableUnitCount': float})
inventory_df = clean_columns(inventory_df)
inventory_df['part_id'] = inventory_df['part_id'].str.strip()
inventory_df['plant_id'] = inventory_df['plant_id'].str.strip()
inventory_df['available_unit_count'] = pd.to_numeric(inventory_df['available_unit_count'], errors='coerce').fillna(0)
inventory_df = inventory_df.drop_duplicates(subset=['part_id', 'plant_id'])

mapping_df = pd.read_csv('PartMapping.csv', dtype=str)
mapping_df = clean_columns(mapping_df)
mapping_df = mapping_df.applymap(lambda x: x.strip() if isinstance(x, str) else x)
mapping_df['child_part_count'] = pd.to_numeric(mapping_df['child_part_count'], errors='coerce').fillna(0).astype(int)
mapping_df = mapping_df.drop_duplicates(subset=['parent_part_id', 'child_part_id'])

plant_df = pd.read_csv('Plant.csv', dtype=str)
plant_df = clean_columns(plant_df)
plant_df = plant_df.applymap(lambda x: x.strip() if isinstance(x, str) else x)
plant_df = plant_df.drop_duplicates(subset=['id'])
plant_df = plant_df.dropna(subset=['id'])

part_df.to_csv('Part_clean.csv', index=False)
inventory_df.to_csv('PartInventory_clean.csv', index=False)
mapping_df.to_csv('PartMapping_clean.csv', index=False)
plant_df.to_csv('Plant_clean.csv', index=False)

print("Data cleaning complete. Cleaned files saved with snake_case columns.")