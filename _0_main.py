import os, configparser
import _1_parent_coordination as coordination
import _2_ep_timestep_handlers as time_step_handlers

def run_ep_api(_config_file_name):
    coordination.ini_all(_config_file_name)
    state = coordination.ep_api.state_manager.new_state()
    coordination.psychrometric=coordination.ep_api.functional.psychrometrics(state)
    coordination.ep_api.runtime.callback_begin_zone_timestep_before_set_current_weather(state,
                                                                                        time_step_handlers.overwrite_ep_weather)
    if 'Detailed_MedOffice' in coordination.bld_type or 'Detailed_MidRiseApartment' in coordination.bld_type:
        coordination.ep_api.runtime.callback_end_system_timestep_after_hvac_reporting(state,
                                                                                      time_step_handlers.medOff_midApart_get_ep_results)
    else:
        raise ValueError('ERROR: Building type not supported')


    coordination.ep_api.exchange.request_variable(state, "HVAC System Total Heat Rejection Energy", "SIMHVAC")
    coordination.ep_api.exchange.request_variable(state, "Site Outdoor Air Drybulb Temperature", "ENVIRONMENT")
    coordination.ep_api.exchange.request_variable(state, "Site Outdoor Air Humidity Ratio", "ENVIRONMENT")

    idfFileName = coordination.config['Bypass']['idfFileName']
    epwFileName = coordination.config['Bypass']['epwFileName']
    output_path = coordination.ep_trivial_path
    weather_file_path = os.path.join('.\\resources\\epw', epwFileName)
    idffolder = coordination.config['Bypass']['idfFolder']
    idfFilePath = os.path.join(f'.\\resources\\idf{idffolder}', idfFileName)
    sys_args = '-d', output_path, '-w', weather_file_path, idfFilePath
    coordination.ep_api.runtime.run_energyplus(state, sys_args)

if __name__ == '__main__':
    todo_jobs = [
        # 'Chicago_MedOffice.ini',
        'Chicago_MidRiseApartment.ini',
    ]
    for job in todo_jobs:
        run_ep_api(job)