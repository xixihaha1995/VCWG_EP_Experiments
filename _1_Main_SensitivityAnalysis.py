from multiprocessing import Process
import os, configparser, _1_Run_EP22_VCWG2 as ByPass


def info(title):
    print(title)
    print('module name:', __name__)
    print('parent process:', os.getppid())
    print('process id:', os.getpid())


def batch_run(ini_files):
    all_ini_process = []
    for ini_file in ini_files:
        # p = Process(target=ByPass.run_vcwg, args=([ini_file]))
        p = Process(target=ByPass.run_ep_api, args=([ini_file]))
        p.start()
        all_ini_process.append([p])
        # ByPass.run_ep_api(ini_file)

    for ini_processes in all_ini_process:
        for p in ini_processes:
            p.join()
def for_loop_all_ini():
    selected_jobs = ["BUBBLE_Ue1.ini","BUBBLE_Ue2.ini",
                     "Vancouver_Rural.ini","Vancouver_TopForcing.ini",
                     "CAPITOUL_WithCooling.ini","CAPITOUL_WithoutCooling.ini",]
    # selected_jobs = ["BUBBLE_Ue1.ini","BUBBLE_Ue2.ini"]
    # selected_jobs = ["CAPITOUL_WithCooling.ini"]
    selected_jobs = ["BUBBLE_Ue1.ini", "BUBBLE_Ue2.ini" ]
    selected_jobs = ['Chicago_MedOffice_Detailed.ini', 'Chicago_MedOffice_ShoeBox.ini']
    nbr_job_for_one_batch = 6
    for i in range(0,len(selected_jobs),nbr_job_for_one_batch):
        print('Todo jobs',selected_jobs[i:i+nbr_job_for_one_batch])
        batch_run(selected_jobs[i:i+nbr_job_for_one_batch])

def read_ini(config_file_name):
    global config
    config = configparser.ConfigParser()
    project_path = os.path.dirname(os.path.abspath(__file__))
    config_path = os.path.join(project_path, 'A_prepost_processing','configs','MedOffice_Sensitivity',config_file_name)
    config.read(config_path)
def one_ini(sensitivity_file_name):
    read_ini(sensitivity_file_name)
    ctl_viriable_1 = config['Bypass']['control_variable_1']
    ctl_values_1 = [i for i in config['Bypass']['control_values_1'].split(',')]
    this_ini_process = []
    nbr_of_parallel = 4
    batch_value_list = [ctl_values_1[i:i + nbr_of_parallel] for i in range(0, len(ctl_values_1), nbr_of_parallel)]
    for batch_nbr, batch_value in enumerate(batch_value_list):
        for value in batch_value:
            # ByPass.run_ep_api(sensitivity_file_name,config, ctl_viriable_1, value)
            this_ini_process.append(Process(target=ByPass.run_ep_api, args=(sensitivity_file_name,config, ctl_viriable_1, value)))
        for process in this_ini_process:
            process.start()
        for process in this_ini_process:
            process.join()
        this_ini_process = []


if __name__ == '__main__':
    # for_loop_all_ini()
    one_ini('Chicago_MedOffice_Density.ini')