'''
simulate serve if delsys station is not available
sends random values (white noise)

run in extra process and connect to it by using
localhost
'''

import socket
import _thread
serverStatus = False
import PyQt5
from struct import pack
import numpy as np
import sys
from scipy import io
import time

def commandPort():
    global serverStatus
    
    port = 50040
    portData = 50041
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sData= socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sAcc= socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    
    s.bind(('', port))
    s.listen(1)
    print("ich warte")
    conn, _ = s.accept()
    
    sData.bind(('', portData))
    sData.listen(1)
    connData, _ = sData.accept()
    while True:
        data = conn.recv(1024)
        if not data: break
        if not serverStatus and data in bytes('START\r\n\r\n', encoding = 'ascii'):
            serverStatus = True
            conn.sendall(('accepted').encode())
            _thread.start_new_thread(sendData, (connData,))
        if serverStatus and data in bytes('STOP\r\n\r\n', encoding = 'ascii'):
            serverStatus = False
            break
    s.close()
    sData.close()
    sAcc.close()
def sendData(conn):
    i = 0
    # data = io.loadmat('/Users/lwre/Downloads/毕业设计/EMG数据分析/EmgData_FENGSUPING_20191023.mat',mat_dtype=True,squeeze_me = True)['EMG_DATA'][:-1,]
    # data = io.loadmat('/Users/lwre/Downloads/毕业设计/codes/2/fixed_data3.mat',mat_dtype=True,squeeze_me = True)['result_emg']
    # data = np.transpose(data)
    # sampleNum = data.shape[0]
    # chNum = data.shape[1]
    while serverStatus:
        package = b''
        ## simulation
        data = np.arange(16)
        for i in range(data.shape[0]): 
            package += pack('<'+'f', data[i])
        conn.sendall(package)
        # real data
        # for j in range(chNum):
        #     package += pack('<'+'f', data[i, j])
        # conn.sendall(package)
        time.sleep(0.0004)
        i += 1
if __name__ == '__main__':
    commandPort()