import hub
import time
time.sleep(1)

def play(hub, freq, N=1, basetime=500):
    hub.sound.beep(freq, int(basetime*N), hub.sound.SOUND_SIN)
    time.sleep((basetime/1000)*N)

notes = {70:466,
         72:523,
         74:587,
         75:622,
         77:699,
         79:784,
         81:880,
         82:932,
        }

seq1 = [[79,1], [81,1.5], [82,0.5]]
seq2 = [[74,3], [74,1], [77,1.5], [74,0.5]]
seq3 = [[79,3], [79,1], [77,1.5], [75,0.5]]
seq4 = [[74,1], [74,1],[77,1.5], [74,0.5]]
seq5 = [[72,3], [74,0.5], [72,0.5],[70,1.5], [72,0.5], [74,1.5]]


seqs = [seq1, seq2, seq3, seq4, seq5]
motor = hub.port.A.motor
motor.run_at_speed(15)
hub.sound.volume(5)
i = 0
while True:    
    for item in seqs[i]:
        play(hub, notes[item[0]], item[1])
    i += 1
    if i >= len(seqs):
        i = 0
