import csv
import os
import subprocess
import pathlib

folders = ['infra', 'network', 'scaffold', 'shared-services', 'database']

# Create folders if they don't exist
for folder in folders:
    folder_path = os.path.join(os.getcwd(), folder)
    pathlib.Path(f"{folder}/cfg-failures").mkdir(parents=True, exist_ok=True)
    pathlib.Path(f"{folder}/importfiles").mkdir(parents=True, exist_ok=True)
    pathlib.Path(f"{folder}/cfg-success").mkdir(parents=True, exist_ok=True)
    
    # Create provider.tf file in each folder
    provider_file_path = os.path.join(folder_path, 'provider.tf')
    with open(provider_file_path, 'w') as provider_file:
        provider_file.write(
            f"""terraform {{
  required_version = "> 1.5"
  required_providers {{
    azurerm = {{
      source  = "hashicorp/azurerm"
      version = "=3.83.0"
    }}
  }}
}}

provider "azurerm" {{
  features {{}}
}}
"""
        )

print(" ")
print("Directory Structure has been created and provider file has been created inside all folders. Now terraform will be initialized ")
print(" ")

def run_terraform_command(command, folder_path):
    print(f"Running '{command}' in folder: {folder_path}")
    process = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, cwd=folder_path)
    out, err = process.communicate()
    if out:
        print(out.decode('utf-8'))
    if err:
        print(err.decode('utf-8'))
    return process.returncode

for folder in folders:
    folder_path = os.path.join(os.getcwd(), folder)
    if not os.path.exists(folder_path):
        print(f"Folder '{folder}' not found.")
        continue
    
    # Run terraform init
    return_code_init = run_terraform_command("terraform init -reconfigure", folder_path)
    if return_code_init != 0:
        print(f"Failed to initialize Terraform in folder '{folder}'. Skipping further operations.")
        continue
