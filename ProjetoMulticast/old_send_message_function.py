
# def _send_message_(message, host, address):
#     ip, port = address
#     await_time = host_ports[host][-1]*2
#     print(f"Timeout={host_ports[host][-1]}\tAwait time={await_time}")
#     try:
#         start_time = time.time()
#         print(f'Sending "{message}" to ({ip}, {port})')
#         sock.sendto(message.encode(), (ip, port))
#         sock.settimeout(await_time)
#         response, address = sock.recvfrom(1024)
#         decoded_response = response.decode()
#         parts = decoded_response.split('/')
#         if parts[0] == 'acknowledge':
#             # Verifica se é válido
#             received_time = float(parts[1])
#             time_difference = start_time - received_time
#             print(f"time_difference={time_difference}")
#             if time_difference < 0:
#                 # Válido, recebeu!
#                 print(f"Acknowledged {float(parts[2])-float(parts[1])}")
#                 change_timeout_host(host, time.time()-start_time)
#                 timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
#                 file_content.append(f'{timestamp} || Mensagem: "{message}" enviada para {ip}, {port}')
#             else:
#                 # Acknowledge atrasado
#                 print(f"acknowledge atrasado: {await_time * 2}")
#                 # preciso ver se a minha vai chegar no tempo certo #AQUIDE
#                 change_timeout_host(host, await_time * 2)
#         else:
#             # Manda a mensagem novamente caso não tiver sido recebida
#             _send_message_(message, host, address)
#     except socket.timeout:
#         change_timeout_host(host, await_time * 2)
#         print("deu time out")
#         # Manda a mensagem novamente caso tenha ocorrido timeout
#         global global_amount
#         global_amount += 1
#         if global_amount < 2:
#             _send_message_(message, host, address)
#         global_amount = 0
#         timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
#         file_content.append(f'{timestamp} || Mensagem: "{message}" não enviada para {ip}, {port}')
#     except Exception as e:
#         logging.warning(f"Error: {e}")
#         # pass
