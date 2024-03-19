import os
import csv

# Define the main folder path
main_folder = "all-discovered-subscriptions"
case_conversion_file = 'case_conversion.csv'

# Function to replace resource case in Microsoft Azure Enterprise
def update_resource_case(resource_case, case_conversion_file):
    # Read case_conversion_file
    with open(case_conversion_file, 'r') as csvfile:
        csvreader = csv.reader(csvfile)
        csv_data = {rows[0]: rows[1] for rows in csvreader}

    # Read resource_case file and update resource case
    with open(resource_case, 'r') as file:
        csvreader1 = csv.reader(file)
        resource_case_content = list(csvreader1)

    updated_content = []
    for line in resource_case_content:
        updated_line = line[:]
        for key, value in csv_data.items():
            updated_line = [cell.replace(key, value) for cell in updated_line]
        updated_content.append(updated_line)

    # Write updated content back to resource_case file
    with open(resource_case, 'w', newline='') as file:
        writer = csv.writer(file)
        writer.writerows(updated_content)

# Loop through subfolders in the main folder
for subfolder_name in os.listdir(main_folder):
    subfolder_path = os.path.join(main_folder, subfolder_name)
    
    # Check if the item in the main folder is a directory
    if os.path.isdir(subfolder_path):
        # Define the file paths for ms_to_tf and all_resources
        ms_to_tf_file_name = "ms_to_tf.csv"
        all_resources_file_name = os.path.join(subfolder_path, subfolder_name + ".csv")
        
        # Initialize mapping_dict
        mapping_dict = {}
        
        # Read data from "ms_to_tf" and store it in the dictionary
        with open(ms_to_tf_file_name, mode='r', newline='') as ms_to_tf_file:
            csv_reader = csv.reader(ms_to_tf_file)
            for row in csv_reader:
                if len(row) >= 2:
                    key = row[0]
                    value = row[1]
                    mapping_dict[key] = value
        
        # Update column 2 of "all_resources" using data from "ms_to_tf"
        updated_rows = []
        with open(all_resources_file_name, mode='r', newline='') as all_resources_file:
            csv_reader = csv.reader(all_resources_file)
            
            for row in csv_reader:
                if len(row) >= 2:
                    key = row[1]  # Assuming column 2 in "all_resources" file
                    if key in mapping_dict:
                        row[1] = mapping_dict[key]
                updated_rows.append(row)
        
        # Write the updated data back to "all_resources" file
        with open(all_resources_file_name, mode='w', newline='') as all_resources_file:
            csv_writer = csv.writer(all_resources_file)
            csv_writer.writerows(updated_rows)
        
        # Call update_resource_case function for each file
        update_resource_case(all_resources_file_name, case_conversion_file)
        print(f"Data in {all_resources_file_name} has been updated.")
        
