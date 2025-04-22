import os, json, uuid, shutil
import zipfile, datetime

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))

def zip_folder_except_script(arg_folder_path, arg_script_name):
    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M")
    zip_name = os.path.join(arg_folder_path, f"{arg_script_name}_backup_{timestamp}.zip")

    with zipfile.ZipFile(zip_name, 'w', zipfile.ZIP_DEFLATED) as zipf:
        for root, _, files in os.walk(arg_folder_path):
            for file in files:
                if file == arg_script_name:
                    continue  # Skip the current script
                full_path = os.path.join(root, file)
                relative_path = os.path.relpath(full_path, arg_folder_path)
                zipf.write(full_path, arcname=relative_path)

    print(f"Backup created: {zip_name}")

# -----------------------------------------------------------

#0. searching for the main project file
lst_files = []
for each_file in os.listdir(SCRIPT_DIR):
    if each_file.endswith(".kicad_pro"):
        str_original_project_filename = each_file
        print(f"Main project file is: {each_file}")
        
        #1. Requesting the desired project name
        str_new_project_name = input("Input desired project name:\n")
        
        #quitting the tool if canceled by the empty string providing
        if str_new_project_name == "":
            print("Canceled. Quitting...")
            exit()
        else:
            # 2. Preliminary backup of the project
            zip_folder_except_script(SCRIPT_DIR, str_original_project_filename)


        #3. getting the required information about the project from the main project file
        with open(SCRIPT_DIR + "/" + str_original_project_filename, 'r') as file_kicad_pro:
            dict_kicad_pro = json.load(file_kicad_pro)
        
            #2. getting the original project name
            try:
                tmp_string = dict_kicad_pro["meta"]["filename"]
                print(f"Original project name is: {tmp_string}")

                if str_original_project_filename == tmp_string:
                    print("The kicad project filename matches with the original project name")
                else:
                    print("The kicad project filename DOES NOT match the original project name")
                
                str_original_project_name = str_original_project_filename.replace(".kicad_pro","")


                #4. project sheets processing
                try:
                    print("Sheets detected:")
                    new_sheets = []

                    #checking just for the case
                    if len(dict_kicad_pro["sheets"]) > 0:
                        str_root_sheet_name = dict_kicad_pro["sheets"][0][1]
                        str_root_sheet_uuid = dict_kicad_pro["sheets"][0][0]

                        with open(SCRIPT_DIR + "/" + str_original_project_name + '.kicad_sch', 'r') as file_kicad_sch:
                            str_kicad_sch = file_kicad_sch.read()

                            #updating project_name
                            str_kicad_sch.replace(f'(project "{str_original_project_name}"',
                                                f'(project "{str_new_project_name}"')

                            for each_sheet in dict_kicad_pro["sheets"]:
                                print(f"Sheet {each_sheet[1]} with the UIN: {each_sheet[0]}")
                                
                                new_sheet_uuid = str(uuid.uuid4())
                                temp_sheet = [new_sheet_uuid, each_sheet[1]]
                                new_sheets.append(temp_sheet)

                                # --------------
                                #replacing the uuids
                                str_kicad_sch.replace(f'(uuid "{each_sheet[0]}"',
                                                    f'(uuid "{new_sheet_uuid}"')
                            
                            print("Updating the UINs of the sheets")
                            dict_kicad_pro["sheets"] = new_sheets
                    
                    else:
                        print("Error: Unable to determine project sheets for some reason")



                    #5. Replacing kicad_pro content
                    dict_kicad_pro["meta"]["filename"] = str_new_project_name + '.kicad_pro'

                    
                    #6. Saving the updated kicad_pro file
                    with open(SCRIPT_DIR + "/" + str_new_project_name + '.kicad_pro', 'w') as file_kicad_pro:
                        json.dump(dict_kicad_pro, file_kicad_pro, indent=4)
                    
                    print(f"Removing the {str_original_project_name + '.kicad_pro'} file")
                    os.remove(SCRIPT_DIR + "/" + str_original_project_name + '.kicad_pro')

                    # ------------------

                    #7. Saving the updated kicad_pro file
                    with open(SCRIPT_DIR + "/" + str_new_project_name + '.kicad_sch', 'w') as file_kicad_sch:
                        file_kicad_sch.write(str_kicad_sch)

                    print(f"Removing the {str_original_project_name + '.kicad_sch'} file")
                    os.remove(SCRIPT_DIR + "/" + str_original_project_name + '.kicad_sch')

                    # ------------------

                    #8. Updating the PRL-file
                    with open(SCRIPT_DIR + "/" + str_original_project_name + '.kicad_prl', 'r') as file_kicad_prl:
                        dict_kicad_prl = json.load(file_kicad_prl)

                        dict_kicad_prl["meta"]["filename"] = str_new_project_name + '.kicad_prl'
                    
                    with open(SCRIPT_DIR + "/" + str_new_project_name + '.kicad_prl', 'w') as file_kicad_prl:
                        json.dump(dict_kicad_prl, file_kicad_prl, indent=4)

                    print(f"Removing the {str_original_project_name + '.kicad_prl'} file")
                    os.remove(SCRIPT_DIR + "/" + str_original_project_name + '.kicad_prl')

                    # ------------------

                    #9. Renaming the PCB-file
                    lst_pcb_files = []
                    for each_pcb_file in os.listdir(SCRIPT_DIR):
                        if each_pcb_file.endswith(".kicad_pcb"):
                            lst_pcb_files.append(each_pcb_file)
                    
                    if len(lst_pcb_files) == 1:
                        shutil.copy(SCRIPT_DIR + "/" + lst_pcb_files[0],
                                    SCRIPT_DIR + "/" + str_new_project_name + '.kicad_pcb')
                        print("the only one PCB-file was found, renaming...")
                    elif len(lst_pcb_files) == 0:
                        print("no PCB-files has been found, nothing to rename...")
                    else:
                        print("a couple of PCB-files has been found, skipping the renaming...")

                    
                    print(f"Removing the {str_original_project_name + '.kicad_pcb'} file")
                    os.remove(SCRIPT_DIR + "/" + str_original_project_name + '.kicad_pcb')



                except Exception as e2:
                    print("Error: Unable to determine project sheets:")
                    print(e2)


            except Exception as e1:
                print("Error: Unable to get original project name:")
                print(e1)


        #processing the main kicad project file only
        break
    

else:
    print("No .kicad_pro file found! Aborting...")


# -----------------------
#10. Dependent files' renaming
for each_sch_file in os.listdir(SCRIPT_DIR): #listing all the files in the directory
    if each_sch_file.endswith(".kicad_sch"): #processing only SCH-files
        
        #if this is not the main SCH-file
        if not each_sch_file == str_new_project_name + '.kicad_sch':
            
            #asking if needs to rename the SCH-file
            str_rename_answer = input(f"Do you want to rename the {each_sch_file}? (Y/n):\n")
            if str_rename_answer in ["Y", "y"]:
                str_new_sch_filename = input(f"Input new name for the the {each_sch_file} without extension:\n")
                if not str_new_sch_filename == "":

                    with open(SCRIPT_DIR + "/" + str_new_project_name + '.kicad_sch', 'r') as file_kicad_sch:
                        str_kicad_sch = file_kicad_sch.read()

                    replacement_result = str_kicad_sch.replace(each_sch_file, str_new_sch_filename + '.kicad_sch')
                    #print(replacement_result)
                    #print(f"replaced the {each_sch_file} to the {str_new_sch_filename}.kicad_sch")

                    with open(SCRIPT_DIR + "/" + str_new_project_name + '.kicad_sch', 'w') as file_kicad_sch_w:
                        file_kicad_sch_w.write(replacement_result)

                    os.rename(SCRIPT_DIR + "/" + each_sch_file,
                            SCRIPT_DIR + "/" + str_new_sch_filename + '.kicad_sch')

