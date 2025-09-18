import copy
import datetime
import random
import traceback
import os

def exception_to_string(exception):
    try:
        text = str(exception)
        text += '\n'
        stack = traceback.format_tb(tb=exception.__traceback__)
        stack.reverse()
        for entry in stack:
            terms = entry.split(',')
            head, filename = os.path.split(terms[0])
            text += filename.replace('"', '') + terms[1].replace('line ', ':').replace(' ', '')
            text += terms[2].replace('\n', '')
            text += '\n'

        return text

    except Exception as e:
        return 'Failed to process exception!'



def datetime_to_fiware(time_as_datetime:datetime) -> str:
    try:
        dt = time_as_datetime
        return str(dt.year) + '-' + str(dt.month).zfill(2) + '-' + str(dt.day).zfill(2) + 'T' + str(dt.hour).zfill(
            2) + ':' + str(dt.minute).zfill(2) + ':' + str(dt.second).zfill(2) + 'Z'
        return time_to_fiware(time_as_datetime.timestamp())
    except Exception as e:
        print('datetime_to_fiware()-' + str(e))

    return ''

def fiware_to_datetime(fiware_time)->datetime:
    try:
        if '.' in fiware_time:
            return datetime.datetime.strptime(fiware_time, '%Y-%m-%dT%H:%M:%S.%fZ')

        return datetime.datetime.strptime(fiware_time, '%Y-%m-%dT%H:%M:%SZ')
    except Exception as e:
        # no seconds?
        return datetime.datetime.strptime(fiware_time, '%Y-%m-%dT%H:%MZ')

    return ''


pilot_model = {}

def delete_pilot(name:str) -> bool:
    if name in pilot_model:
        pilot_model.pop(name)
        return True

    return False

def clear():
    pilot_model = {}

def add_pilot(name:str) ->bool:
    if name not in pilot_model:
        pilot_model[name] = {}

        return True

    return False

def add_sensor_to_pilot(pilot:str, sensor:str, configuration:dict) -> bool:
    if pilot not in pilot_model:
        if add_pilot(pilot) == False:
            return False

    if sensor not in pilot_model[pilot]:
        pilot_model[pilot][sensor] = {}
        pilot_model[pilot][sensor]['config'] = copy.deepcopy(configuration)
        #give the sensor a placeholder time
        pilot_model[pilot][sensor]['timestamp'] = datetime_to_fiware(datetime.datetime.utcnow())

        return True

    return False

def delete_sensor_from_pilot(pilot:str, sensor:str) -> bool:
    if pilot in pilot_model and sensor in pilot_model[pilot]:
        pilot_model[pilot].pop(sensor)
        return True

    return False

def reset_pilot(pilot:str, timestamp:str):

    if isinstance(timestamp, datetime.datetime):
        timestamp = datetime_to_fiware(timestamp)

    if timestamp != '' and isinstance(timestamp, str):
        if pilot in pilot_model:
            for sensor in pilot_model[pilot]:
                pilot_model[pilot][sensor]['timestamp'] = timestamp

            return True

    return False

def get_value(data:dict) -> float:
    return data['index']


def get_config(config:dict, current_attrib:str) -> dict:
    for entry in config['properties']:
        if 'name' in entry and entry['name'] == current_attrib:
            return entry

    return None


####################################################################################################################################
#
#   property processors
#
####################################################################################################################################
def process_base(timestamp:datetime.datetime,config:dict, current_attrib:str, current_results:dict) -> float:
    current_state = config['current_state'][current_attrib]
    attrib_config = get_config(config, current_attrib)

    raise Exception('Not processed')


def process_lookup_index(timestamp:datetime.datetime,config:dict, current_attrib:str, current_results:dict) -> float:

    try:
        current_mode = config['current_state']['mode']
        attrib_config = get_config(config, current_attrib)

        src_data = {}

        for mode in attrib_config['range']:
            if mode['name'] == current_mode:
                src_data = mode

        if src_data == {}:
            raise Exception('Can\'t find: ' + current_attrib +' in definition')

        date_to_index = (timestamp - fiware_to_datetime(attrib_config['start-date'])).days

        while date_to_index < 0:
            date_to_index += len(src_data['range'])

        while date_to_index >= len(src_data['range']):
            date_to_index -= len(src_data['range'])

        return src_data['range'][date_to_index]
    except Exception as e:
        print(exception_to_string(e))

    raise Exception('Not processed')

def process_calculation(timestamp:datetime.datetime,config:dict, current_attrib:str, current_results:dict) -> float:

    attrib_config = get_config(config, current_attrib)

    input_value = current_results[attrib_config['input']]
    input_value = min(max(input_value, 50.0), 999.0)

    bucket = 0
    for i in range(0, len(attrib_config['steps'])):

        if input_value >= attrib_config['steps'][i][0]:
            bucket = i

    if bucket < len(attrib_config['steps']) - 1:
        return random.uniform(attrib_config['steps'][bucket][1], attrib_config['steps'][bucket + 1][1])

    return attrib_config['steps'][bucket][1]

    raise Exception('Not processed')

####################################################################################################################################

def process_lookup(timestamp:str, config:dict, current_attrib:str, current_results:dict) -> float:

    if current_attrib in config['current_state']:
        current_state = config['current_state'][current_attrib]
    else:
        current_state = config['current_state']['mode']

    attrib_config = get_config(config, current_attrib)

    if 'range' in attrib_config:
        for entry in attrib_config['range']:
            if entry['name'] == current_state:

                if 'range' in entry:
                    val = random.uniform(entry['range'][0], entry['range'][1])

                    if 'previous_result' not in attrib_config:
                        attrib_config['previous_result'] = val

                    magic_value = 1

                    if 'delta_limit' in attrib_config:
                        magic_value = attrib_config['delta_limit']

                    diff = abs(attrib_config['previous_result'] - val)
                    if diff > (attrib_config['previous_result'] * magic_value):
                        if val > attrib_config['previous_result']:
                            attrib_config['previous_result'] *= 1.0 + magic_value
                        else:
                            attrib_config['previous_result'] *= 1.0 - magic_value
                    else:
                        attrib_config['previous_result'] = val

                    return attrib_config['previous_result']

                if 'value' in entry:
                    attrib_config['previous_result'] = entry['value']

                    return attrib_config['previous_result']

    raise Exception('Not processed')

####################################################################################################################################
def process_24hrby3_lookup(timestamp:datetime.datetime, config:dict, current_attrib:str, current_results:dict) -> float:
    current_state = config['current_state'][current_attrib]
    attrib_config = get_config(config, current_attrib)

    range_list = []
    if isinstance(attrib_config['range'], str):
        range_list = config['reference_data'][attrib_config['range']]
    else:
        range_list = attrib_config['range']

    for entry in range_list:
        if entry['name'] == current_state:
            if len(entry['range']) != 8:
                raise Exception('Range must be 8 digits')
            index = int(timestamp.hour /3)
            next_index = int((index + 1) % 8)

            if 'previous_result' not in attrib_config:
                attrib_config['previous_result'] = 0

            attrib_config['previous_result'] += entry['range'][index]

            return attrib_config['previous_result']

    raise Exception('Not processed')

####################################################################################################################################
def process_pass_through(timestamp:datetime.datetime, config:dict, current_attrib:str, current_results:dict) -> float:

    attrib_config = get_config(config, current_attrib)

    return current_results[attrib_config['input']]

    raise Exception('Not processed')

####################################################################################################################################
def process_state_lookup(timestamp:datetime.datetime, config:dict, current_attrib:str, current_results:dict) -> float:

    attrib_config = get_config(config, current_attrib)

    source_state = config['current_state'][attrib_config['input']]

    state_list = []
    if isinstance(attrib_config['lookup'], str):
        state_list = config['reference_data'][attrib_config['lookup']]
    else:
        state_list = attrib_config['lookup']

    for entry in state_list:
        if entry['name'] == source_state:
            attrib_config['previous_result'] = entry['value']

            return attrib_config['previous_result']

    raise Exception('Not processed')


####################################################################################################################################
def process_attrib(timestamp:datetime.datetime, config:dict, current_attrib:str, current_results:dict) -> float:

    attrib_config = get_config(config, current_attrib)

    if 'type' in attrib_config:
        if attrib_config['type'] == 'lookup-index':
            return process_lookup_index(timestamp,config,current_attrib,current_results)

        if attrib_config['type'] == 'lookup':
            return process_lookup(timestamp,config,current_attrib,current_results)

        if attrib_config['type'] == 'calculation':
            return process_calculation(timestamp,config,current_attrib,current_results)

        if attrib_config['type'] == '24hr-by3-lookup':
            return process_24hrby3_lookup(timestamp,config,current_attrib,current_results)

        if attrib_config['type'] == 'pass-through':
            return process_pass_through(timestamp,config,current_attrib,current_results)

        if attrib_config['type'] == 'state_lookup':
            return process_state_lookup(timestamp,config,current_attrib,current_results)


    raise Exception('Not processed:' + attrib_config['type'])

def get_data(pilot:str, sensor:str, count:int) -> list:
    payload = []

    if pilot in pilot_model and sensor in pilot_model[pilot]:

        for i in range(0,count):

            if 'config' in pilot_model[pilot][sensor]:
                results = {}

                timestamp = fiware_to_datetime(pilot_model[pilot][sensor]['timestamp'])

                attrib_results = {}
                if 'order' in pilot_model[pilot][sensor]['config'] and pilot_model[pilot][sensor]['config'] != None:
                    for attrib in pilot_model[pilot][sensor]['config']['order']:

                        attrib_results[attrib] = process_attrib(timestamp, pilot_model[pilot][sensor]['config'], attrib, attrib_results)

                        print_name = get_config(pilot_model[pilot][sensor]['config'], attrib)['output-name']

                        results[print_name] = round(attrib_results[attrib],2)
                else:
                    config = pilot_model[pilot][sensor]['config']
                    for prop in config['properties']:

                        attrib = prop['name']

                        attrib_results[attrib] = process_attrib(timestamp, config, attrib, attrib_results)

                        print_name = attrib

                        if 'output-name' in config:
                            print_name = get_config(config, attrib)['output-name']

                        if isinstance(attrib_results[attrib], float):
                            results[print_name] = round(attrib_results[attrib], 2)
                        else:
                            if isinstance(attrib_results[attrib], int):
                                results[print_name] = round(attrib_results[attrib], 2)
                            else:
                                results[print_name] = attrib_results[attrib]

                results['dateObserved'] = datetime_to_fiware(timestamp)

                payload.append(results)

                timestamp += datetime.timedelta(seconds=pilot_model[pilot][sensor]['config']['step'])
                pilot_model[pilot][sensor]['timestamp'] = datetime_to_fiware(timestamp)

    return payload

def set_current_state(pilot:str, sensor:str, current_state:dict) ->bool:
    try:
        pilot_model[pilot][sensor]['config']['current_state'] = copy.deepcopy(current_state)
        return True

    except Exception as e:
        print(str(e))

    return False


def get_smart_data_post(pilot:str, sensor:str, count:int) -> list:
    payload = []

    if pilot in pilot_model and sensor in pilot_model[pilot]:

        property = pilot_model[pilot][sensor]['property_name']

        for i in range(0,count):

            payload.append({property : copy.deepcopy(pilot_model[pilot][sensor]['smart_model'][property])})

            t = fiware_to_datetime(pilot_model[pilot][sensor]['timestamp'])
            t += datetime.timedelta(minutes=pilot_model[pilot][sensor]['timestep'])
            pilot_model[pilot][sensor]['timestamp'] = datetime_to_fiware(t)
            pilot_model[pilot][sensor]['index'] += 1

            pilot_model[pilot][sensor]['smart_model'][property]['value'] = pilot_model[pilot][sensor]['index']
            pilot_model[pilot][sensor]['smart_model'][property]['observedAt'] = pilot_model[pilot][sensor]['timestamp']

    return payload

def get_datapath() -> str:
    return os.path.join(os.path.dirname(__file__), 'data')