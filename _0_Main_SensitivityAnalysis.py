from multiprocessing import Process
import os, configparser, _1_Run_EP22_VCWG2 as ByPass

def read_ini(config_file_name):
    global config
    config = configparser.ConfigParser()
    project_path = os.path.dirname(os.path.abspath(__file__))
    if 'MedOffice' in config_file_name:
        config_path = os.path.join(project_path, 'A_prepost_processing','_configs','MedOffice',config_file_name)
    elif 'HighOffice' in config_file_name:
        config_path = os.path.join(project_path, 'A_prepost_processing','_configs','HighOffice',config_file_name)
    # config_path = os.path.join(project_path, 'A_prepost_processing','_configs','Only_VCWG',config_file_name)
    config.read(config_path)

def one_ini(sensitivity_file_name):
    read_ini(sensitivity_file_name)
    value_list = [i for i in config['Bypass']['value_list'].split(',')]
    this_ini_process = []
    nbr_of_parallel = 2
    batch_value_list = [value_list[i:i + nbr_of_parallel] for i in range(0, len(value_list), nbr_of_parallel)]
    for batch_nbr, batch_value in enumerate(batch_value_list):
        for value in batch_value:
            # ByPass.run_ep_api(sensitivity_file_name,config, value)
            this_ini_process.append(Process(target=ByPass.run_ep_api, args=(sensitivity_file_name,config, value)))
    for i in range(0, len(this_ini_process), nbr_of_parallel):
        for process in this_ini_process[i:i + nbr_of_parallel]:
            process.start()
        for process in this_ini_process[i:i + nbr_of_parallel]:
            process.join()


if __name__ == '__main__':

    jobs = [
        # "Chicago_HighOffice_Vector_Detailed.ini",
        "Chicago_HighOffice_Vector_Simplified.ini",
        # "Chicago_MedOffice_Vector_Detailed.ini",
    ]
    for job in jobs:
        one_ini(job)