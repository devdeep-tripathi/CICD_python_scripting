import os
import subprocess
import shutil
import glob
import sys

#Read subcription name from command line as csv file
subscription = "Microsoft Azure Enterprise"
csv_file = (subscription)+".csv"
main_folder = "all-discovered-subscriptions"
subfolder_path = os.path.join(main_folder, (subscription))
csv_file_path = os.path.join(subfolder_path,csv_file)

def run_terraform_command(command, folder_path):
    print(f"Running '{command}' in folder: {folder_path}")
    process = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, cwd=folder_path)
    out, err = process.communicate()
    if out:
        print(out.decode('utf-8'))
    if err:
        print(err.decode('utf-8'))
    return process.returncode

def terraform_apply(folder_path):
    apply_cmd = f"terraform apply -auto-approve"
    return_code_apply = run_terraform_command(apply_cmd, folder_path)
    if return_code_apply != 0:
        print(f"Failed to run 'terraform apply' in folder '{folder_path}'")    
    return return_code_apply

# Funtion to move terraform importfiles to importfiles folder
def importfiles_move(src_folder):
    dst_folder = (f"{src_folder}\importfiles")
    pattern = "\*-import.tf"
    files = glob.glob(src_folder + pattern)
    for file in files:
        shutil.move(file, dst_folder)
    print("Import files moved to importfiles folder")

# Funtion to move terraform config tf files to cfg-success folder
def cfgfiles_move(src_folder):
    dst_folder = (f"{src_folder}\cfg-success")
    pattern = "\*.tf"
    files = glob.glob(src_folder + pattern)
    for file in files:
        if file != (f"{src_folder}\provider.tf"):
            shutil.move(file, dst_folder)
    print("cfg files moved to cfg-success folder")    

folders = ['infra', 'network', 'scaffold', 'shared-services', 'database']
for folder in folders:
    fp = os.path.join(os.getcwd(), folder)
    rc = terraform_apply(fp)
    print (f"return code of plan '{rc}'")
    if rc !=0:
        print ("Apply has failed. Continue to next iteration")
        continue
    else:
        print (f"'terraform apply' complete for folder {fp}")
        # Calling funtion to move terraform importfiles to importfiles folder
        importfiles_move(fp)
        # Calling funtion to move terraform config tf files to cfg-success folder
        cfgfiles_move(fp)
