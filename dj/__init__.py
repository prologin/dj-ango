from DJ_Ango.dj.player import MPDPlayer
import threading

player = MPDPlayer()
threading.Thread(target=(lambda: player.player_thread())).start()
