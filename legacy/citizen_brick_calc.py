#!/usr/bin/env python3

import os
import csv
import re
import time
import math

import libbrick.path_utils
import libbrick.wrappers.bricklink_wrapper as BLW

# Define the bag sizes in mL
bag_sizes = {
    'quart': 946,
    'gallon': 3785,
    'two gallon': 7571,
    'half snack': 160,
    'snack': 320,
    'sandwich': 651,
}

def convert_bag_size_to_ml(bag_size):
    if bag_size.startswith('only') or bag_size.startswith('just'):
        return int(bag_size.split(' ')[1]) # Adjust this if necessary
    else:
        return bag_sizes.get(bag_size, 0)

# Initialize the BrickLink wrapper
blw = BLW.BrickLink()

output_dir = libbrick.path_utils.get_output_dir()
output_file_path = os.path.join(output_dir, 'citizen_brick_output.csv')

# Read the CSV file
with open('Citizen_Brick/Citizen_Brick_Draft-Minimal.csv', newline='', encoding='utf-8') as input_file:
    reader = csv.reader(input_file)
    header = next(reader)
    header = [re.sub(r'\s', '', field) for field in header] # Remove all whitespace characters

    # Prepare to write to a new CSV file
    with open(output_file_path, 'w', newline='', encoding='utf-8') as output_file:
        writer = csv.writer(output_file)

        # Write header
        new_headings = [
            'ElementID', 'PartID', 'ColorID', 'BL Color Name', 'Lego Color Name',
            'Part Name', 'Type', 'Category ID', 'Category Name', 'Weight',
            'Dim X', 'Dim Y', 'Dim Z', 'Year Released',
            'Item ID', 'New Median Sale Price', 'New Sale Quantity', 'New Median List Price', 'New List Quantity',
            'Volume', 'BagSize (mL)', 'Pieces'
        ]
        all_headings = header + new_headings
        writer.writerow(all_headings)

        i = 0
        # Iterate through the rows in the CSV
        for row in reader:
            i += 1
            row_data = dict(zip(header, row))
            element_id = row_data['ElementID']
            orig_part_id = row_data['BrickLinkID']
            bag_size_mL = convert_bag_size_to_ml(row_data['BagSize'])

            # Get Part ID and Color ID
            if element_id is None or element_id.lower() == 'none':
                continue
            part_id, color_id = blw.elementIDtoPartIDandColorID(element_id)
            if orig_part_id != part_id:
                print("PartID mismatch:", orig_part_id, part_id)
                time.sleep(1)

            # Get Part Data
            part_data = blw.getPartData(part_id)
            color_name = blw.getColorNameFromColorID(color_id)

            # Get Price Data
            price_data = blw.getPartPriceData(part_id, color_id)

            # Calculate Volume if dimensions are available
            dim_x = float(part_data['dim_x']) * 0.8
            dim_y = float(part_data['dim_y']) * 0.8
            dim_z = float(part_data['dim_z']) * 0.96
            part_volume = dim_x * dim_y * dim_z
            if part_volume > 0:
                pieces = math.floor(bag_size_mL / part_volume)
            else:
                pieces = -1

            part_data['category_name'] = blw.getCategoryName(part_data['category_id'])

            # Write data to the new CSV file
            output = [
                element_id,
                part_id,
                color_id,
                color_name,
                row_data['Color'],
                part_data['name'],
                part_data['type'],
                part_data['category_id'],
                part_data['category_name'],
                part_data['weight'],
                part_data['dim_x'],
                part_data['dim_y'],
                part_data['dim_z'],
                part_data['year_released'],
                price_data['item_id'],
                price_data['new_median_sale_price'],
                price_data['new_sale_qty'],
                price_data['new_median_list_price'],
                price_data['new_list_qty'],
                part_volume,
                bag_size_mL,
                pieces
            ]
            writer.writerow(row + output)
                    # Flush the data to disk every 10 entries
            if (i + 1) % 10 == 0:
                output_file.flush()
