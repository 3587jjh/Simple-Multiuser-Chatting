import sys 
import socket 
import threading

try:
  # 로컬에서 보낸 메시지들을 지속적으로 서버로 보냄
  def send():
    global client_socket
    while True:
      msg = input()
      client_socket.send(msg.encode())

  # 서버가 보낸 메시지를 지속적으로 받아 출력함
  def receive():
    global client_socket
    while True:
      msg = client_socket.recv(1024).decode()
      print(msg)

  HOST = sys.argv[1] # server측의 ip주소 전달받기 
  PORT = int(sys.argv[2]) # server측의 port번호 전달받기
  # (HOST, PORT)정보를 가지는 server의 socket과 연결하기
  client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM) 
  client_socket.connect((HOST, PORT)) 

  # send 스레드 시작
  thread_send = threading.Thread(target=send, args=())
  thread_send.daemon = True
  thread_send.start()

  # receive 스레드 시작
  thread_receive = threading.Thread(target=receive, args=())
  thread_receive.daemon = True
  thread_receive.start()

  # keyboardinterrupt로 인해 프로그램이 종료되기 전까지 두 스레드는 계속 실행됨
  thread_send.join()
  thread_receive.join()

# ctrl+c를 입력했을 때 프로그램이 종료됨
except KeyboardInterrupt: 
  print("\nexit")
  client_socket.close()

