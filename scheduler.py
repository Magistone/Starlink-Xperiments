import importlib
import time, datetime
import db

class Scheduler:
    def __init__(self, module_name:str, start:str, config:dict|None, setup:dict|None, tags:list|None, is_one_off: bool) -> None:
        self.module_name = module_name
        self.start = start
        self.config = config
        self.setup = setup
        self.tags = tags
        self.is_one_off = is_one_off

    def save_data(self, data:None|dict|list[dict]):
        if not data:
            return
        if isinstance(data, list):
            ready_data = [self.inject_meta_data(d) for d in data]
        else:
            ready_data = self.inject_meta_data(data)

        #TODO MongoDB writer

        print(ready_data)

    def inject_meta_data(self, data:dict):
        if not data.get('metadata'):
            data['metadata'] = dict()
        
        #TODO Inject tags + name

        #Inject timestamp
        data['timestamp'] = datetime.datetime.now(datetime.timezone.utc)
        return data

    def delay(self):
        #delay starting scheduled tasks
        if self.start == None:
            return
        
        time_struct = time.strptime(self.start, "%a, %d %b %Y %H:%M:%S %Z") #RFC7231, "Sun, 06 Nov 1994 08:49:37 GMT"
        target_timestamp = round(time.mktime(time_struct))
        current_timestamp = round(time.mktime(time.gmtime())) # DO NOT GET TIME with time.time() - it's wrong value
        diff = target_timestamp - current_timestamp
        if diff <= 0:
            return
        time.sleep(diff)

    def create(self):
        mod = importlib.import_module('modules.' + self.module_name)
        mod.setup(self.setup)
        return mod

    def run(self):
        mod = self.create()
        task_stop_time = self.config.get('stop')
        forever = self.config.get('forever')
        while((not self.is_time_past_deadline(task_stop_time)) or forever):
            start_time = time.time_ns()
            # Intended to crash the subprocess if module raises an exception
            data = mod.collect(self.config.get('config'))
            self.save_data(data)
            stop_time = time.time_ns()
            time_diff = (stop_time - start_time)/1e9

            sleep_time = self.config['period'] - time_diff
            if self.is_one_off:
                break
            if sleep_time <= 0:
                continue
            time.sleep(sleep_time) # => starts spaced by 'period'

    def is_time_past_deadline(_self, deadline: str | None):
        if deadline == None:
            return True
        time_struct = time.strptime(deadline, "%a, %d %b %Y %H:%M:%S %Z") #RFC7231, "Sun, 06 Nov 1994 08:49:37 GMT"
        target_timestamp = round(time.mktime(time_struct))
        current_timestamp = round(time.mktime(time.gmtime())) # DO NOT GET TIME with time.time() - it's wrong value
        diff = target_timestamp - current_timestamp
        return diff < 0


def schedule(config: dict, is_one_off = False):
    scheduler = Scheduler(config['module'], config.get('start'), config, config.get('setup'), config.get('tags'), is_one_off)
    scheduler.delay()
    scheduler.run()