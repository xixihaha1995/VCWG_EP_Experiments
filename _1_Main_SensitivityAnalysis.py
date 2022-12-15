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
        p = Process(target=ByPass.run_ep_api, args=([ini_file]))
        p.start()
        all_ini_process.append([p])
        # ByPass.run_ep_api(ini_file)

    for ini_processes in all_ini_process:
        for p in ini_processes:
            p.join()
def for_loop_all_ini():
    # selected_jobs = ["BUBBLE_Ue1.ini","BUBBLE_Ue2.ini",
    #                  "Vancouver_Rural.ini","Vancouver_TopForcing.ini",
    #                  "CAPITOUL_WithCooling.ini","CAPITOUL_WithoutCooling.ini",]
    selected_jobs = ["BUBBLE_Ue1.ini","BUBBLE_Ue2.ini"]
    nbr_job_for_one_batch = 6
    for i in range(0,len(selected_jobs),nbr_job_for_one_batch):
        print('Todo jobs',selected_jobs[i:i+nbr_job_for_one_batch])
        batch_run(selected_jobs[i:i+nbr_job_for_one_batch])


if __name__ == '__main__':
    for_loop_all_ini()