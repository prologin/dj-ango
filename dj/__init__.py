from DJ_Ango.dj.player import MPDPlayer
import threading

print("Init")
player = MPDPlayer()
threading.Thread(target=(lambda: player.player_thread())).start()
print("Thread started")
