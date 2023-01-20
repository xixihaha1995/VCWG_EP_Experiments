from multiprocessing import Process
import os, configparser, _1_Run_EP22_VCWG2 as ByPass


def info(title):
    print(title)
    print('module name:', __name__)
    print('parent process:', os.getppid())
    print('process id:', os.getpid())

def read_ini(config_file_name):
    global config
    config = configparser.ConfigParser()
    project_path = os.path.dirname(os.path.abspath(__file__))
    config_path = os.path.join(project_path, 'A_prepost_processing','configs','bypass','AllCases',config_file_name)
    config.read(config_path)


def batch_run(ini_files):
    all_ini_process = []
    for ini_file in ini_files:
        read_ini(ini_file)
        if config['Bypass']['framework'] == 'OnlyVCWG':
            p = Process(target=ByPass.run_vcwg, args=([ini_file]))
        else:
            p = Process(target=ByPass.run_ep_api, args=([ini_file]))
        p.start()
        all_ini_process.append([p])
        # ByPass.run_ep_api(ini_file)

    for ini_processes in all_ini_process:
        for p in ini_processes:
            p.join()
def for_loop_all_ini():
    selected_jobs = ["BUBBLE_Ue1_WithoutShading.ini","BUBBLE_Ue2_WithoutShading.ini",
                     "Vancouver_Rural_WithoutShading.ini","Vancouver_TopForcing_WithShading.ini",
                     "CAPITOUL_WithoutCooling_WithoutShading.ini", "CAPITOUL_WithCooling_WithoutShading.ini",
                     "BUBBLE_Ue1_WithShading.ini","BUBBLE_Ue2_WithShading.ini",
                     "Vancouver_Rural_WithShading.ini","Vancouver_TopForcing_WithoutShading.ini",
                     "CAPITOUL_WithoutCooling_WithShading.ini", "CAPITOUL_WithCooling_WithShading.ini",
                     "BUBBLE_Ue1_OnlyVCWG.ini","BUBBLE_Ue2_OnlyVCWG.ini",
                     "Vancouver_Rural_OnlyVCWG.ini","Vancouver_TopForcing_OnlyVCWG.ini",
                     "CAPITOUL_WithoutCooling_OnlyVCWG.ini", "CAPITOUL_WithCooling_OnlyVCWG.ini"]
    selected_jobs = ["BUBBLE_Ue1_OnlyVCWG.ini", "BUBBLE_Ue2_OnlyVCWG.ini",
                     "Vancouver_Rural_OnlyVCWG.ini", "Vancouver_TopForcing_OnlyVCWG.ini",
                     "CAPITOUL_WithoutCooling_OnlyVCWG.ini", "CAPITOUL_WithCooling_OnlyVCWG.ini"]
    nbr_job_for_one_batch = 3
    for i in range(0,len(selected_jobs),nbr_job_for_one_batch):
        print('Todo jobs',selected_jobs[i:i+nbr_job_for_one_batch])
        batch_run(selected_jobs[i:i+nbr_job_for_one_batch])


if __name__ == '__main__':
    for_loop_all_ini()