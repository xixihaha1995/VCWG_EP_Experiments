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
    config_path = os.path.join(project_path,'A_prepost_processing', 'configs',config_file_name)
    config.read(config_path)

def one_ini(sensitivity_file_name):
    info(f'main line{sensitivity_file_name}')
    read_ini(sensitivity_file_name)
    experiments_theme = config['Default']['experiments_theme']
    value_list = [i for i in config['Default']['value_list'].split(',')]
    this_ini_process = []
    for value in value_list:
        p = Process(target=ByPass.run_ep_api, args=(config,experiments_theme, value))
        p.start()
        this_ini_process.append(p)
        # ByPass.run_ep_api(config,experiments_theme, value)

    return this_ini_process

def batch_run(ini_files):
    all_ini_process = []
    for ini_file in ini_files:
        cur_ini_processes = one_ini(ini_file)
        all_ini_process.append(cur_ini_processes)

    for ini_processes in all_ini_process:
        for p in ini_processes:
            p.join()
def for_loop_all_ini():
    selected_jobs = ["IDFs_Size.ini"]
    nbr_job_for_one_batch = 1
    for i in range(0,len(selected_jobs),nbr_job_for_one_batch):
        print('Todo jobs',selected_jobs[i:i+nbr_job_for_one_batch])
        batch_run(selected_jobs[i:i+nbr_job_for_one_batch])


if __name__ == '__main__':
    for_loop_all_ini()