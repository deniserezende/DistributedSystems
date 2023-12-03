# election.py
import time


class Election:
    def __init__(self, host_name, host_ports, broadcast_function, send_message_function):
        self.host_name = host_name
        self.host_ports = host_ports
        self.broadcast_function = broadcast_function
        self.election_in_progress = False
        self.send_message_function = send_message_function

    def start_election(self, online_nodes):
        if not self.election_in_progress:
            print("Starting Election...")
            if not self.election_in_progress:
                self.election_in_progress = True

                # Send election messages to all other online nodes
                for node in online_nodes:
                    if self.election_in_progress is False:
                        break

                    message = "ELECTION_REQUEST"
                    if self.host_name == node:
                        time.sleep(3)
                    else:
                        ip, port, _, _, _ = self.host_ports[node]
                        response = self.send_message_function(message, ip, port)

                        if response == "ACCEPTED":
                            print(f"Node {node} accepted the election.")
                            self.election_in_progress = False
                            message = f"ELECTION_RESULT/{node}"
                            # Broadcast the result to inform other nodes
                            self.broadcast_function(message)
                        else:
                            print(f"Node {node} did not respond to the election.")

                # Check if any node has accepted the election
                if self.election_in_progress:
                    # No one accepted, this node becomes the leader
                    print(f"No one accepted the election. Node {self.host_name} is the new leader.")
                    self.election_in_progress = False
                    message = f"ELECTION_RESULT/{self.host_name}"
                    # Broadcast the result to inform other nodes
                    self.broadcast_function(message)

    def abort_election(self):
        self.election_in_progress = True
