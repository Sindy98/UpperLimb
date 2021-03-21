using System.Collections;
using System.Collections.Generic;
using UnityEngine;
using System.Net;
using System.Net.Sockets;
using System.Text;
using System.Threading;
using System;

///<summary>
///client get and send message;
///</summary>

public class TCP : MonoBehaviour
{
    public SocketPosture socketPosture;
    string editString = "hello wolrd";
    //编辑框文字     
    Socket serverSocket;
    //服务器端socket    
    IPAddress ip;
    //主机ip  
    IPEndPoint ipEnd;
    IPEndPoint a;
    string recvStr;
    //接收的字符串  
    string sendStr;
    //发送的字符串    
    byte[] recvData = new byte[1024];
    //接收的数据，必须为字节    
    byte[] sendData = new byte[1024];
    //发送的数据，必须为字节   
    int recvLen; //接收的数据长度 
    Thread connectThread; //连接线程   
                          //初始化   
    void InitSocket()
    {
        //定义服务器的IP和端口，端口与服务器对应 
        ip = IPAddress.Parse("192.168.1.105");
        //可以是局域网或互联网ip，此处是本机   
        ipEnd = new IPEndPoint(ip, 50041);
        // a = new IPEndPoint(ip, 50040);

        //开启一个线程连接，必须的，否则主线程卡死   
        connectThread = new Thread(new ThreadStart(SocketReceive));
        connectThread.Start();
    }
    void SocketConnet()
    {
        if (serverSocket != null)
            serverSocket.Close();
        //定义套接字类型,必须在子线程中定义   
        serverSocket = new Socket(AddressFamily.InterNetwork, SocketType.Stream, ProtocolType.Tcp);
        print("ready to connect");
        //连接       
        serverSocket.Connect(ipEnd);
        //输出初次连接收到的字符串      
        recvLen = serverSocket.Receive(recvData);
        Debug.Log(recvData);
        recvStr = Encoding.ASCII.GetString(recvData, 0, recvLen);
        print(recvStr);
    }
    void SocketSend(string sendStr)
    {        //清空发送缓存      
        sendData = new byte[1024];
        //数据类型转换     
        sendData = Encoding.ASCII.GetBytes(sendStr);
        //发送    
        serverSocket.Send(sendData, sendData.Length, SocketFlags.None);
    }
    void SocketReceive()
    {
        SocketConnet();
        //不断接收服务器发来的数据
        while (true)
        {
            recvData = new byte[1024];
          
            recvLen = serverSocket.Receive(recvData);

            ReadMessage(recvLen);
            
          //WriteVector();
        }
        while (false)
        {
            recvData = new byte[1024];

            recvLen = serverSocket.Receive(recvData);
            if (recvLen == 0)
            {
                SocketConnet();
                continue;
            }
            recvStr = Encoding.ASCII.GetString(recvData, 0, recvLen);
            Debug.Log(recvStr);


        }
    }
    void SocketQuit()
    {
        //关闭线程 
        if (connectThread != null)
        {
            connectThread.Interrupt();
            connectThread.Abort();
        }
        //最后关闭服务器   
        if (serverSocket != null)
            serverSocket.Close();
        print("diconnect");
    }
   public float[] position;
    // Use this for initialization    
  public  void StartSocket()
    {

        InitSocket();
        position = new float[12];
    }


    //程序退出则关闭连接   
    void OnApplicationQuit() { SocketQuit(); }
    string ReadMessage(int count)
    {
        // StringBuilder receiveStr;
        int byteCount;
        byteCount = count;
        int num = 4;
        int receiveCount;
        
        while (true)
        {
            
            //缓存区小于4个字节，表示连表头都无法解析
            if (byteCount <= num) return null;
            receiveCount = (BitConverter.ToInt32(recvData, 0))*4;
           
           
            //如果表头的数据小于48，不够12个float;
           if (receiveCount !=48)


            {
                return null;
            }
            

            
            for (int i = 0; i < position.Length; i++)
            {
                position[i] = BitConverter.ToSingle(recvData, num + i * 4);
                Debug.Log(position[i].ToString()+" "+i.ToString());
            }
            WriteVector();
          //  Debug.Log("1");
            return "1";
   
            //读取四个字节数据，代表这条数据的内容长度（不包括表头的4个数据）



            //int receiveCount = BitConverter(readBuff, 0);

            //缓存区中的数据，不够解析一条完整的数据

            //2、解析数据
            //从除去表头4个字节开始解析内容，解析的数据长度为（表头数据表示的长度）




            //把剩余的数据Copy到缓存区头部位置
         //   Array.Copy(recvData, 52, recvData, 0, byteCount - 52);
         //   byteCount = byteCount - 52;
            
            
        }

    }
    void WriteVector()
    {
        Debug.Log("a");
        float[] a = position;
        socketPosture.ElbowX = new Vector3(-a[0],-a[2],-a[1]);
        socketPosture.EndY = new Vector3(a[4],a[10],a[7]);
        socketPosture.EndZ = new Vector3(-a[5],-a[11],-a[8]);
    }
}


