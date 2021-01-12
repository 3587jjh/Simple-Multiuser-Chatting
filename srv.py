import sys
import socket 
import threading

try:
	# addr0의 주소를 가진 client의 활동이 기록된 메시지를 모든 client들에게 전파함
	def broadcast(addr0, msg_type, msg=""):
		global client_sockets
		msg_you = "" # addr0 주소를 갖는 client에게 보낼 전체 메시지
		msg_other = "" # addr0 이외의 주소를 갖는 client들에게 보낼 전체 메시지
		ip_port = str(addr0[0])+":"+str(addr0[1])
		
		if msg_type == "Chat":
			# addr0는 채팅 메시지를 보낸 client 주소, msg는 메시지 내용
			msg_you = "[You] "+msg
			msg_other = "["+ip_port+"] "+msg

		else:
			if msg_type == "Enter":
				# addr0는 채팅방에 들어온 client 주소, msg는 비어있음
				msg_you = "> Connected to the chat server "
				msg_other = "> New user "+ip_port+" entered "
			else: # msg_type == "Left"
				# addr0는 채팅방에서 나간 client 주소, msg는 비어있음
				msg_other = "< The user "+ip_port+" left "

			# 전체 메시지에 남은 유저 수 정보 추가하기
			totuser = len(client_sockets)
			addmsg = "("+str(totuser)
			addmsg += " user online)" if totuser <= 1 else " users online)"
			msg_you += addmsg
			msg_other += addmsg

		print(msg_other) # 서버 측에서도 client들의 활동을 기록
		# 모든 client에게 전체 메시지 보내기
		for client_socket, addr in client_sockets:
			try:
				if addr == addr0:
					client_socket.send(msg_you.encode())
				else:
					client_socket.send(msg_other.encode())

			# 멀티 스레드로 인해 메시지를 보내려는 client와의 연결이 이미 끊긴 경우 고려
			except ConnectionResetError:
				continue

	# addr의 주소를 가진 client가 보내는 메시지를 지속적으로 받음
	def receive(client_socket, addr):
		global client_sockets
		while True:
			msg = client_socket.recv(1024).decode()
			if not msg: # 해당 client와의 연결이 끊김
				break
			# client가 보낸 채팅 메시지를 broadcasting하기
			broadcast(addr, "Chat", msg)

		# 해당 client와의 연결이 끊겼으므로 client_socket을 정리하기
		client_sockets.remove((client_socket, addr))
		client_socket.close()
		# client가 채팅방에서 나갔다는 활동을 broadcasting하기
		broadcast(addr, "Left")

	# 새로운 client가 보내는 connection 요청을 지속적으로 받음
	def accept():
		global client_sockets
		while True:
			client_socket, addr = server_socket.accept()
			client_sockets.append((client_socket, addr))
			# 해당 client가 보내는 메시지를 받는 역할을 하는 스레드 생성
			thread_receive = threading.Thread(target=receive, args=(client_socket, addr))
			thread_receive.daemon = True
			thread_receive.start()
			# client가 채팅방에 들어왔다는 활동을 broadcasting하기
			broadcast(addr, "Enter")

	HOST = sys.argv[1] # server측의 ip주소 전달받기
	PORT = int(sys.argv[2]) # server측의 port번호 전달받기

	# HOST, PORT 정보를 가지는 server의 socket을 listening 상태로 만들기 
	server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM) 
	server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
	server_socket.bind((HOST, PORT)) 
	server_socket.listen()
	print("Chat Server started on port "+str(PORT)+".")

	client_sockets = [] # 현재 채팅방에 있는 client의 (socket, address) 모음
	# keyboardinterrupt로 인해 프로그램이 종료되기 전까지 accept 스레드가 계속 실행됨
	thread_accept = threading.Thread(target=accept, args=())
	thread_accept.daemon = True
	thread_accept.start()
	thread_accept.join()

# ctrl+c를 입력했을 때 프로그램이 종료됨
except KeyboardInterrupt:
	print("\nexit")
	server_socket.close()

