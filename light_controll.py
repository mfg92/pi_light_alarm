import threading
import wiringpi2 as IO
import datetime


class ControllEvent:

    def __init__(self, start_dtime, end_dtime, start_brightness=0.0, end_brightness=1.0, repeate_delay=None):
        self.start_time = start_dtime
        self.end_time = end_dtime
        self.start_brightness = start_brightness
        self.end_brightness = end_brightness
        self.repeate_delay = repeate_delay
        print(self.start_time, " to ", self.end_time)

    def calc_brightness(self):
        #    perc = (time.time()-self.start_time) / (self.end_time-self.start_time)
        perc = (datetime.datetime.now()-self.start_time) / (self.end_time-self.start_time)

        bri = self.start_brightness + (self.end_brightness - self.start_brightness)*perc
        return max(0.0, min(bri, 1.0))

    def on_finished(self, lightCtrl):
        if self.repeate_delay is None:
            return
        self.start_time += self.repeate_delay
        self.end_time += self.repeate_delay
        print("newTimes:", self.start_time, " to ", self.end_time)
        lightCtrl.add_controll_event(self)


class LightControll:

    def __init__(self):
        self.thrd_sleep_duration = 0.2  # sec
        self.light_pin = 18
        self.started = False
        self.exit_flag = threading.Event()
        self.brightness = 0.0  # 0.0 to 1.0
        self.ctrl_events = []

        IO.wiringPiSetupGpio()
        IO.pinMode(self.light_pin, IO.GPIO.PWM_OUTPUT)
        IO.pwmSetClock(1920)
        IO.pwmSetRange(100)
        # GPIO.setup(self.light_pin, GPIO.OUT)

    def __del__(self):
        self.exit_flag.set()

    def start(self):
        if self.started:
            return
        self.started = True
        thrd = threading.Thread(target=self.__run, name='LightControllThread')
        thrd.start()

    def add_controll_event(self, event):
        self.ctrl_events.append(event)
        self.ctrl_events.sort(key=lambda e: e.start_time)
        print("add", self.ctrl_events)

    def remove_controll_event(self, event):
        print("rem", self.ctrl_events)
        self.ctrl_events.remove(event)
        self.ctrl_events.sort(key=lambda e: e.start_time)

    def __run(self):
        print('start')
        while not self.exit_flag.is_set():
            if self.exit_flag.wait(self.thrd_sleep_duration):
                continue  # break if exit flag is set

            if not self.ctrl_events:
                continue

            now = datetime.datetime.now()

            event = self.ctrl_events[0]

            if event.end_time < now:
                self.remove_controll_event(event)
                event.on_finished(self)
                continue
            elif event.start_time > now:
                self._set_brightness(0.0)
                continue

            self._set_brightness(event.calc_brightness())

    def _set_brightness(self, brightness):
        self.brightness = brightness
        print("Brightness: {}".format(round(self.brightness, 2)))
        IO.pwmWrite(self.light_pin, brightness)
