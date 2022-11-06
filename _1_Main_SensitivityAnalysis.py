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
    uwgVariable = config['sensitivity']['uwgVariable']
    value_list = [float(i) for i in config['sensitivity']['value_list'].split(',')]
    this_ini_process = []
    for value in value_list:
        p = Process(target=ByPass.run_ep_api, args=(config,uwgVariable, value))
        p.start()
        this_ini_process.append(p)
    return this_ini_process

def for_loop_all_ini():
    all_ini_process = []
    ini_files1 = ["SensitivityCAPITOUL_albedo.ini","SensitivityCAPITOUL_NoCooling_albedo.ini",
                 "SensitivityCAPITOUL_albedoNoIDF.ini","SensitivityCAPITOUL_NoCooling_albedoNoIDF.ini",
                 "SensitivityCAPITOUL_CanyonWidthToCanyonHeight.ini","SensitivityCAPITOUL_NoCooling_CanyonWidthToCanyonHeight.ini",]
    for ini_file in ini_files1:
        cur_ini_processes = one_ini(ini_file)
        all_ini_process.append(cur_ini_processes)

    print('all_ini_process',all_ini_process)
    for ini_processes in all_ini_process:
        print('ini_processes',ini_processes)
        for p in ini_processes:
            print('p',p)
            p.join()

    ini_files2 = ["SensitivityCAPITOUL_CanyonWidthToRoofWidth.ini","SensitivityCAPITOUL_NoCooling_CanyonWidthToRoofWidth.ini",
                 "SensitivityCAPITOUL_fveg_G.ini","SensitivityCAPITOUL_NoCooling_fveg_G.ini",
                 "SensitivityCAPITOUL_theta_canyon.ini","SensitivityCAPITOUL_NoCooling_theta_canyon.ini"]
    for ini_file in ini_files2:
        cur_ini_processes = one_ini(ini_file)
        all_ini_process.append(cur_ini_processes)

    for ini_processes in all_ini_process:
        for p in ini_processes:
            p.join()

if __name__ == '__main__':
    for_loop_all_ini()