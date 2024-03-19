import os
import subprocess
import csv
import sys

#ten_id=(sys.argv[1])
#print(ten_id)

# Set your Azure tenant ID
#tenant_id = '1d8dc9bc-5fad-4008-bbdb-132907d33f0d'

# Get a list of subscriptions using Azure CLI
az_command = f'az account list --query "[].{{subscriptionId:id, name:name}}" -o tsv'
subscriptions_info = subprocess.check_output(az_command, shell=True, text=True)

# Split the output by lines to get each subscription entry
subscription_entries = subscriptions_info.strip().split('\n')

# Create a master directory for all subscription folders
output_directory_parent = 'all-discovered-subscriptions'
os.makedirs(output_directory_parent, exist_ok=True)

# Iterate through each subscription
for entry in subscription_entries:
    subscription_id, subscription_name = entry.split('\t')
    ## 01_Start ##  Get All resources for the current subscription using Azure CLI ##
    az_command = f'az resource list --subscription {subscription_id} --query "[].{{name:name, type:type, id:id }}" -o tsv'
    subscription_resources = subprocess.check_output(az_command, shell=True, text=True) 
    rg_command = f'az group list --subscription {subscription_id} --query "[].{{name:name, type:type, id:id }}" -o tsv'
    subscription_rgs = subprocess.check_output(rg_command, shell=True, text=True)

    #if subscription is empty then do not create csv files and continue
    if not subscription_resources and not subscription_rgs:
        print(f"Subscription {subscription_name} is empty")   
    else:
        # Split the output by lines to get each resource entry
        resource_entries = subscription_resources.strip().split('\n')
        ## 01_End ##  Get All resources for the current subscription using Azure CLI ##

        ## 02_Start ##  Get All resource groups for the current subscription using Azure CLI ##
        # Split the output by lines to get each resource entry
        rg_entries = subscription_rgs.strip().split('\n')
        #print(rg_entries)
        ## 02_End ##  Get All resource groups for the current subscription using Azure CLI ##
        
        # 03_Create a directory to store the CSV file for particular subscriptions
        output_directory_child = f'{subscription_name}'
        path = os.path.join(output_directory_parent, output_directory_child)
        os.makedirs(path, exist_ok=True)

        # 04_Create a CSV file for the current subscription
        csv_file_path = os.path.join(path, f'{subscription_name}.csv')
        
        # 05_Write discovered resources in the CSV file for the current subscription
        with open(csv_file_path, 'w', newline='') as csvfile:
            csv_writer = csv.writer(csvfile)

            # # Write header
            # csv_writer.writerow(['Resource ID', 'Resource Name', 'Resource Type'])

            # 06_Write resource groups to the CSV file
            for resource in rg_entries:
                name, type, id = resource.split('\t')
                #csv_writer.writerow([id, name, type])
                csv_writer.writerow([name, type, id])
                
            # 07_Write all other resource to the CSV file  
            for resource_entry in resource_entries:  
                name, type, id = resource_entry.split('\t')
                #csv_writer.writerow([id, name, type])
                csv_writer.writerow([name, type, id])

        print(f"All Resources are discovered for subscription {subscription_name}")        
print("Script execution completed.")
