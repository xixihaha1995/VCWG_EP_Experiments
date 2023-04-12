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

def one_control_variable(sensitivity_file_name):
    ctl_viriable_1 = config['Bypass']['control_variable_1']
    ctl_values_1 = [i for i in config['Bypass']['control_values_1'].split(',')]
    framework = config['Bypass']['framework']
    this_ini_process = []
    nbr_of_parallel = 3
    batch_value_list = [ctl_values_1[i:i + nbr_of_parallel] for i in range(0, len(ctl_values_1), nbr_of_parallel)]
    for batch_nbr, batch_value in enumerate(batch_value_list):
        for value in batch_value:
            if 'OnlyVCWG' in framework:
                this_ini_process.append(
                    Process(target=ByPass.run_vcwg, args=(sensitivity_file_name, config, ctl_viriable_1, value)))
            else:
                # ByPass.run_ep_api(sensitivity_file_name,config, ctl_viriable_1, value)
                this_ini_process.append(
                    Process(target=ByPass.run_ep_api, args=(sensitivity_file_name, config, ctl_viriable_1, value)))
    for p in this_ini_process:
        p.start()
    for p in this_ini_process:
        p.join()

def one_ini(sensitivity_file_name):
    read_ini(sensitivity_file_name)
    one_control_variable(sensitivity_file_name)


if __name__ == '__main__':
    # one_ini('Chicago_MedOffice_MixedVariable.ini')
    # one_ini('Chicago_MedOffice_MixedVariable_OnlyVCWG.ini')
    # one_ini('Chicago_MedOffice_IDFComplexity.ini')
    # one_ini('Chicago_MedOffice_IDFComplexity_OnlyVCWG.ini')
    todo_jobs = [
        # 'Chicago_MedOffice_IDFComplexity.ini',
        # 'Chicago_MedOffice_IDFComplexity_OnlyVCWG.ini',
        'Chicago_HighOffice_IDFComplexity.ini',
        # 'Chicago_HighOffice_IDFComplexity_OnlyVCWG.ini',
        # 'upperLimits_Chicago_HighOffice_IDFComplexity.ini',
    ]
    for job in todo_jobs:
        one_ini(job)