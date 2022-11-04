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

if __name__ == '__main__':
    info('main line')
    sensitivity_file = input("Please input the sensitivity file: "
                             "[SensitivityCAPITOUL_CanyonWidthToRoofWidth.ini]") or \
                       "SensitivityCAPITOUL_CanyonWidthToRoofWidth.ini"
    read_ini(sensitivity_file)
    uwgVariable = config['sensitivity']['uwgVariable']
    value_list = [float(i) for i in config['sensitivity']['value_list'].split(',')]
    for value in value_list:
        p = Process(target=ByPass.run_ep_api,
                    args=(config,uwgVariable, value))
        p.start()