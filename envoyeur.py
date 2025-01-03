import socket
import json
import threading
import time

# Constants
PORT = 3466
BUFFER_SIZE = 1024

# lock to secure the access to the shared variables
lock = threading.Lock()

# List of machines
with open('machines.txt', 'r') as file:
    machines = [line.strip() for line in file.readlines()]

# Input string to distribute
with open('input_strings.txt', 'r') as file:
    input_string = file.read().strip().replace('\n', ' ')

#verifying the input string
print("Input string: ", input_string)

#dictionnary to stock connexions
connexions = {}

# Status monitoring phases
phase1_status = {machine: False for machine in machines}
phase2_status = {machine: False for machine in machines}


#connect to the machines
# for machine in machines:
#     try:
#         # Créer un socket TCP/IP
#         client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        
#         # Se connecter à la machine
#         client_socket.connect((machine, PORT))
        
#         # Stocker la connexion
#         connexions[machine] = client_socket
#         print(f"Connexion établie avec {machine}")
#     except Exception as e:
#         print(f"Erreur lors de la connexion à {machine}: {e}")


def send_to_machine(machine, data, phase):
    """Send data to a machine."""
    try:
        # establish connexion
        client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        
        # connect to machine
        client_socket.connect((machine, PORT))
        
        # Stock the connexion
        with lock :
            connexions[machine] = client_socket

        # send data
        client_socket.sendall(json.dumps(data).encode('utf-8'))
    except Exception as e:
        print(f"[Phase {phase}] Error sending to {machine}: {e}")
        

def phase1(machine, data, phase):
    send_to_machine(machine, data, phase)
    response = connexions[machine].recv(BUFFER_SIZE).decode('utf-8')
    if response != None :
        message = json.loads(response)
        print("Response from machine: ", message['content'])
    else :
        print(f"[phase 1] No response from machine {machine}")
    with lock :
        if message['content'] == "finished phase 1":
            phase1_status[machine] = True
            
def phase2(machine, data, phase):
    send_to_machine(machine, data, phase)
    response = connexions[machine].recv(BUFFER_SIZE).decode('utf-8')
    if response != None :
        message = json.loads(response)
        print("Response from machine: ", message['content'])
    else :
        print(f"[phase 2] No response from machine {machine}")
    with lock :
        if message['content'] == "finished phase 2":
            phase2_status[machine] = True
    
    
def phase3(machine, data, phase):
    send_to_machine(machine, data, phase)
    response = connexions[machine].recv(BUFFER_SIZE).decode('utf-8')
    message = json.loads(response)
    print(f"count of words by {machine} : {message}\n")

def phase1_call():
    global phase1_status
    """Phase 1: Distribute machines list and string parts."""
    threads = []
    for idx, machine in enumerate(machines):
        # Divide the string equally for each machine
        string_part = input_string.split()[idx::len(machines)]
        data = {
            'phase': 1,
            'machines': machines,
            'string': " ".join(string_part)
        }
        thread = threading.Thread(target=phase1, args=(machine, data, 1))
        threads.append(thread)
        thread.start()

    for thread in threads:
        thread.join()
    print("Phase 1 completed.")
    print("status of phase 1: ", phase1_status)
    if all(phase1_status.values()):
        print("starting phase 2")
        phase2_call()
    

def phase2_call():
    global phase2_status
    print("started phase 2")
    threads = []
    # Send the phase 2 signal to all machines
    for  machine in machines :
        data = {
            'phase': 2,
            'content': "start phase 2"
        }
        thread = threading.Thread(target=phase2, args=(machine, data, 2))
        threads.append(thread)
        thread.start()
    for thread in threads:
        thread.join()
    print("sent signal to phase 2")
    if all(phase2_status.values()):
        print("sending signal to phase 3")
        phase3_call()

def phase3_call():
    print("started phase 3")
    threads = []
    # Send the phase 2 signal to all machines
    for  machine in machines :
        data = {
            'phase': 3,
            'content': "start phase 3"
        }
        thread = threading.Thread(target=phase3, args=(machine, data, 3))
        threads.append(thread)
        thread.start()
    for thread in threads:
        thread.join()
    # print("Phase 3 completed.")
    # print("All phases completed.")
    # print("Closing connections...")
    # for machine in machines:
    #     connexions[machine].close()
    # print("Connections closed.")
    

if __name__ == "__main__":
    print("Starting Phase 1...")
    phase1_call()


