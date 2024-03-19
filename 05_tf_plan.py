import csv
import os
import subprocess
import shutil
import sys

# Read subscription name from command line as csv file
subscription = "Microsoft Azure Enterprise"
csv_file = subscription + ".csv"
main_folder = "all-discovered-subscriptions"
subfolder_path = os.path.join(main_folder, subscription)
csv_file_path = os.path.join(subfolder_path, csv_file)

# Function to create import files
def create_import_file(row):
    folder_path = row[3]
    if not os.path.exists(folder_path):
        os.makedirs(folder_path)

    file_path = os.path.join(folder_path, f"{row[0]}-tf-import.tf")
    with open(file_path, 'w') as file:
        file.write(
            f"""import {{
  id = "{row[2]}"

  to = {row[1]}.{row[0]}
}}"""
        )
    return folder_path
# Function to run terraform commands 
def run_terraform_command(command, folder_path):
    print(f"Running '{command}' in folder: {folder_path}")
    process = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, cwd=folder_path)
    out, err = process.communicate()
    if out:
        print(out.decode('utf-8'))
    if err:
        print(err.decode('utf-8'))
    return process.returncode

def terraform_plan(outfilename, folder_path):
    generate_cmd = f"terraform plan -generate-config-out={outfilename}.tf"
    print(generate_cmd)
    return_code_plan = run_terraform_command(generate_cmd, folder_path)
    if return_code_plan != 0:
        print(f"Failed to run 'terraform plan' for file '{outfilename}'.tf in folder '{folder_path}'. Skipping apply.")
        shutil.move(os.path.join(folder_path, f"{outfilename}.tf"), os.path.join(folder_path, "cfg-failures"))
    return return_code_plan

# Function to update terraform config file with the help of replace_config cfg file
def replace_in_tf_config(tf_config_file, azurerm_config):

    # Check if file exist
    if not os.path.exists(azurerm_config):
        print("Error: Append file does not exist.")
        return
    
    # Read terraform config tf file
    with open(tf_config_file, 'r') as file:
        terraform_content = file.readlines()
    # Read replace_config cfg file
    with open(azurerm_config, 'r') as cfgfile:
        csvreader = csv.reader(cfgfile)
        csv_data = {rows[0]: rows[1] for rows in csvreader}
    
    # Loop to replace values in terraform config file
    for key, value in csv_data.items():
        for i, line in enumerate(terraform_content):
            if key in line:
                terraform_content[i] = line.replace(line.split('=')[1].strip(), value.strip())

    # Write the updated content in the terraform config file
    with open(tf_config_file, 'w') as file:
        file.writelines(terraform_content)

# Function to run terraform plan without config out
def terraform_plan_wocfgout(folder_path):
    generate_cmd = "terraform plan"
    print(generate_cmd)
    return_code_plan = run_terraform_command(generate_cmd, folder_path)
    if return_code_plan != 0:
        print(f"Failed to run 'terraform plan' in folder '{folder_path}'. Skipping apply.")
        shutil.move(os.path.join(folder_path, "cfg-failures"), os.path.join(folder_path, "cfg-failures"))
    return return_code_plan

# Function to append the code block to tf config file from the append_config cfg file
def add_code_block(tf_config_file, append_file):

    # Check if file exist
    if not os.path.exists(append_file):
        print("Error: Append file does not exist.")
        return
    
    # Read terraform config tf file
    with open(tf_config_file, 'r') as f:
        tf_content = f.readlines()
    # Read append_config cfg file
    with open(append_file, 'r') as append:
        add_content = append.readlines()

    # Find the second last line's index, we will add the code block just after second last line which is"}"
    second_last_index = len(tf_content) - 1 if len(tf_content) > 1 else 0
    # Insert the content of add.txt into the .tf file after the second last line which is "}"
    tf_content = tf_content[:second_last_index] + add_content + tf_content[second_last_index:]

    # Write the updated content back to the terraform config tf file
    with open(tf_config_file, 'w') as f:
        f.writelines(tf_content)
    print("Code block added successfully.")

# Function to remove the code block from tf config file with the help of remove_config cfg file
def remove_matching_content(cfg_failure_path, remove_file):

    # Check if file exist
    if not os.path.exists(remove_file):
        print("Error: Append file does not exist.")
        return
    
    # Read terraform config tf file
    with open(cfg_failure_path, 'r') as file:
        file1_lines = file.readlines()
    # Read remove_config cfg file
    with open(remove_file, 'r') as file:
        file2_content = file.read().strip()
    
    # Loop to remove the remove_config cfg content from the terraform config tf file
    modified_content = []
    remove_next = False
    for line in file1_lines:
        if line.strip() == file2_content.split('\n')[0].strip():
            remove_next = True
            continue
        if remove_next and line.strip() == '}':
            remove_next = False
            continue
        if not remove_next:
            modified_content.append(line)

    # Write updated content back to terraform config tf file
    with open(cfg_failure_path, 'w') as file:
        file.writelines(modified_content)
        print("Content removed successfully.")

# Read the CSV file and process rows
with open(csv_file_path, newline='') as cfgfile:
    reader = csv.reader(cfgfile)
    for row in reader:
        fp = create_import_file(row)
        print(fp)
        outfilename = row[0]
        cfg_failure_path = os.path.join(fp, "cfg-failures", f"{outfilename}.tf")
        backup_file_path = os.path.join(fp, "cfg-failures", f"{outfilename}_bkp.tf")
        # path to move terraform config tf file to parent folder
        move_file_path = os.path.join(fp, f"{outfilename}.tf")
        print(cfg_failure_path)
        resource_check = row[1]
        azurerm_config = os.path.join("replace_config", f"{resource_check}.cfg")
        append_file = os.path.join("append_config", f"{resource_check}.cfg")
        remove_file = os.path.join("remove_config", f"{resource_check}.cfg")
        print(azurerm_config)
        print(resource_check)
        print(outfilename)

        if resource_check != "DONOTCREATE":
            rc = terraform_plan(outfilename, fp)
            print(f"return code of plan '{rc}'")
            if rc != 0:
                print("Plan has failed. Fixing the failure.")
                # Calling function to replace some values in the terraform config tf file
                replace_in_tf_config(cfg_failure_path, azurerm_config)
                # Calling function to append code block to the terraform config tf file 
                add_code_block(cfg_failure_path, append_file)
                # Calling function to remove code block from the terraform config tf file  
                remove_matching_content(cfg_failure_path, remove_file)
                # Back-up the terraform config tf file
                shutil.copy(cfg_failure_path, backup_file_path)
                # Move terraform config tf file to its parent folder
                shutil.move(cfg_failure_path, move_file_path)
                terraform_plan_wocfgout(fp)
                continue
            else:
                print(f"Plan Complete for {outfilename}")
        else:
            print("Encountered DONOTCREATE Resource Type. Skipping iteration.")
            print("Continue with next Resource Type")
            continue
