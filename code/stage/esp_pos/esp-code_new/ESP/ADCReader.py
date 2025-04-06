from machine import Timer, ADC, Pin
from ESP.tasks import LastingTask

class ADCReader(LastingTask):

    def __init__(self, name, adc_id, freq=1000, nsteps=1):

        super().__init__(name=name, mode=Timer.PERIODIC, freq=freq)

        self.adc_id = adc_id
        self.adc = ADC(adc_id)

        self.nsteps = nsteps
        if self.nsteps == 0:
            self.single_step = 0
        else:
            self.single_step = 1
        self.counter = 0        

    def callback(self, t):
        
        print(f"ESP_ADC_{self.adc_id}_{self.adc.read()}")
        self.counter += self.single_step
        if self.counter >= self.nsteps:
            self.finished = True
            print(f"ESP_ADC_{self.adc_id}_FIN")
