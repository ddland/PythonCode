# temperature logger

import time
import machine

t1 = machine.ADC(0)
t2 = machine.ADC(1)

def to_temp(sensor, conversion = 3.3 / (2**16-1) ):
    volt = sensor.read_u16()*conversion
    return (volt - 0.5)*100


def percentile(sensors, function, percentile=0.5, delay=0.1, N=10):
    NS = len(sensors) 
    PS = int(N*percentile)
    data = []
    [data.append([]) for s in range(NS)]
    for i in range(N):
        for j in range(NS):
            data[j].append(function(sensors[j]))
        time.sleep(delay)
    return [sorted(data[j])[PS] for j in range(NS)]
    
    
        
    

while True:
    print(*percentile([t1,t2], to_temp,N=30))
    time.sleep(1)

