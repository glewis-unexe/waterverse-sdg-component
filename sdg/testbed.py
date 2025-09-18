import os
import datetime
import json


import sdg.sdg as sdg

import unexecore.testharness
import unexecore.time
import unexecore.debug

class sdg_Harness(unexecore.testharness.TestHarness):
    def __init__(self):
        super().__init__()

        start_date = unexecore.time.datetime_to_fiware(datetime.datetime.now(datetime.timezone.utc).replace(minute=0, hour=0, second=0, microsecond=0))

        datapath = 'sdg' + os.sep

        pilot = 'pwn-1'
        try:
            sdg.add_pilot(pilot)
            pwn_1_config = json.load(open(datapath + 'data/pwn_1.json'))
            sdg.add_sensor_to_pilot(pilot, 'test', pwn_1_config)
            sdg.reset_pilot(pilot, start_date)
            sdg.set_current_state(pilot, 'test', {"qOlst": "med"})

            sdg.reset_pilot(pilot, start_date)
            d = sdg.get_data(pilot, 'test', 3)

            print(json.dumps(d, indent=1))

        except Exception as e:
            self.log('SDG: Failed to start-up PWN-1' + unexecore.debug.exception_to_string(e))

        pilot = 'cy-1'
        try:

            sdg.add_pilot(pilot)

            sdg.add_sensor_to_pilot(pilot, 'test', json.load(open(datapath + 'data/cy_payload.json')))
            sdg.reset_pilot(pilot, start_date)

        except Exception as e:
            self.log('SDG: Failed to start-up ' + pilot + ' ' + unexecore.debug.exception_to_string(e))

        sdg.reset_pilot(pilot, start_date)
        d = sdg.get_data(pilot, 'test', 1)

        print(json.dumps(d, indent=1))

        pilot = 'etteln'
        try:

            sdg.add_pilot(pilot)

            sdg.add_sensor_to_pilot(pilot, 'test', json.load(open(datapath + 'data/etteln_payload.json')))
            sdg.reset_pilot(pilot, start_date)

            sdg.set_current_state(pilot, 'test', {"mode": "historic"})
            d = sdg.get_data(pilot, 'test', 1)

            print(json.dumps(d, indent=1))

        except Exception as e:
            self.log('SDG: Failed to start-up ' + pilot + ' ' + unexecore.debug.exception_to_string(e))

        option_id = 1
        self.options[str(option_id)] = {'label': 'dummy', 'function': self.dummy}
        option_id += 1

    def dummy(self):
        pass

    def log(self, text):
        print(text)

if __name__ == '__main__':
    harness = sdg_Harness()
    harness.run()