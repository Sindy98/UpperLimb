import pytrigno
import matplotlib.pyplot as plt
import _thread
import numpy as np
import socket
# from pdb import set_trace
import time
from EMGFeatures import EMGFeatures


channel_num = 5
fs = 2000
plot_time = 10
plot_data = np.zeros((channel_num, 0))
samples_per_read = 100
step_time = samples_per_read/fs
dev = pytrigno.TrignoEMG(channel_range = (0, 4), samples_per_read = samples_per_read, host = "", buffered = True)
try:
	dev.start()
except:
	print("something went wrong")
	raise socket.timeout("Could not connect to Delsys Station")
dev.recordFlag = True


_thread.start_new_thread(dev.read, ())
# _thread.start_new_thread(dev.getFeatures, ())

t = 0
ax = [0]*5
line = [0]*5
fig=plt.figure()
for i in range(5):
	ax[i] = fig.add_subplot(3,2,i+1)
	ax[i].set_xlabel('time/s')
	ax[i].set_title('channel'+str(i))
	line[i] = ax[i].plot(0,0)[0]
ax1 = fig.add_subplot(3,2,6)
# ax1.set_xlabel('Horizontal Position')
# ax1.set_ylabel('Vertical Position')
# ax1.set_title('Vessel trajectory')
line1 = ax1.plot(0,0)[0]

plt.ion()  #interactive mode on

dev.recordFlag = True #控制是否显示数据

while True:
# for t in range(10):
	print(t)
	t0 = time.time()
	while dev.buffer.shape[1]<fs*plot_time*(t+1):
		for i in range(5):
			line[i].set_ydata(dev.buffer[i])
			line[i].set_xdata(np.arange(dev.buffer.shape[1])/fs)
			ax[i].set_xlim((t*10,t*10+10))
			ax[i].set_ylim((-0.0005,0.0005))
		# line1.set_ydata(dev.buffer[0])
		# line1.set_xdata(np.arange(dev.buffer.shape[1])/fs)
		# ax1.set_xlim((t*10,t*10+10))
		# ax1.set_ylim((-0.01,0.01))
		# line1.set_ydata(dev.features[0])
		# line1.set_xdata(np.arange(dev.features.shape[1])*step_time)
		# ax1.set_xlim((t*10,t*10+10))
		# ax1.set_ylim((-0.0005,0.0005))

		plt.pause(0.001)
	t += 1
	print(time.time() - t0)	

plt.ioff()
plt.show()


