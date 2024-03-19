import os
import csv

current_directory = os.getcwd()
convert_to_layer_file = os.path.join(current_directory, "convert_to_layer.csv")
main_directory = current_directory

def read_csv(file_path):
    data = {}
    with open(file_path, 'r') as csvfile:
        reader = csv.reader(csvfile)
        next(reader)  # Skip header
        for row in reader:
            data[row[0]] = row[1]
    return data

def update_target_files(main_folder, csv_data):
    target_folder = os.path.join(main_folder, "all-discovered-subscriptions")
    print("Updating CSV files in 'all-discovered-subscriptions' directory...")
    for root, _, files in os.walk(target_folder):
        for file in files:
            if file.endswith('.csv'):
                file_path = os.path.join(root, file)
                print(f"Processing file: {file_path}")

                rows = []
                with open(file_path, 'r') as csvfile:
                    reader = csv.reader(csvfile)
                    for row in reader:
                        row[0] = row[0].replace('/', "-").replace('\\', "-").replace('.', "-").replace('_', "-").replace(' ', "-")
                        if row[1] in csv_data:  # Match values from column 2 of target file
                            row.insert(3, csv_data[row[1]])  # Insert matching value at index 3 (column D)
                            if row[0].startswith('-'):
                                row[[0][0]] = row[[0][0]][0:].replace('-', "",1)
                            else:
                                pass
                        else:
                            row.insert(3, '')  # Insert empty string if no match found
                        rows.append(row)

                with open(file_path, 'w', newline='') as csvfile:
                    writer = csv.writer(csvfile)
                    writer.writerows(rows)
                print(f"Matching values added to column D in '{file_path}'")

    print("Layering completed.")

def rename_duplicates(main_folder):
    target_folder = os.path.join(main_folder, "all-discovered-subscriptions")
    print("Renaming duplicate resources in CSV files in 'all-discovered-subscriptions' directory...")
    for root, _, files in os.walk(target_folder):
        for file in files:
            if file.endswith('.csv'):
                file_path = os.path.join(root, file)
                print(f"Processing file: {file_path}")
                count_dict = {}
                renamed_count = 0
                rows = []
                with open(file_path, 'r') as file:
                    reader = csv.reader(file)
                    rows = list(reader)
                    for row in rows:
                        value = row[0]
                        if value in count_dict:
                            # Increment the count of occurrences
                            count_dict[value] += 1
                            # Rename the duplicate entry
                            row[0] = f"{value}_{count_dict[value]}"
                            renamed_count += 1
                        else:
                            # If it's the first occurrence, add it to the dictionary
                            count_dict[value] = 1
                with open(file_path, 'w', newline='') as file:
                    writer = csv.writer(file)
                    writer.writerows(rows)

                print(f"{renamed_count} duplicates renamed in {file_path}")

    print("Duplicate renaming completed.")

csv_data = read_csv(convert_to_layer_file)
# Calling function to update subscription csv file
update_target_files(main_directory, csv_data)
# Calling function to rename duplicate resources in subscription csv file
rename_duplicates(main_directory)