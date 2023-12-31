# Server code
import socket
import os.path
import sys

def main():

    #Set the port number to what the user inputs
    serverPort = int(sys.argv[1])

    #Create a TCP Socket
    serverSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    #Bind the socket to the hostname and port
    hostName = socket.gethostname()
    serverSocket.bind(('', serverPort))

    #Start listening for incoming connections
    serverSocket.listen(1)
    
    print(f"Server started on {hostName}:{serverPort}")

    global servConnSocket
    servConnSocket, addr = serverSocket.accept()
    print("Connection established\n")

    while True :
        # Receive command from user
        try:
            command = servConnSocket.recv(40).decode()
        except IOError:
            print("Command has not been received properly. Connection has been closed. ")
            serverSocket.close()
            servConnSocket.close()
            break
        
        match command:
            case "get":
                put()
            case "put":
                get()
            case "ls":
                list()
            case "quit":
                print("Connection closed")
                serverSocket.close()
                servConnSocket.close()
                break 

def get_unique_filename(filename):
        # Validate filename uniqueness in the local directory
        dirContents = os.listdir()

        # File doesn't exist, return original filename
        if filename not in dirContents:
            return filename  

        i = 1
        while True:
            # Create a new filename by appending a numeric suffix
            new_filename = f"{os.path.splitext(filename)[0]}_{i}{os.path.splitext(filename)[1]}"
            if new_filename not in dirContents:
                return new_filename  # Return unique filename
            i += 1

# ************************************************
# Downloads file from client
# ************************************************
def get():
    # Create data channel 
    dataSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    # Bind the socket to port 0
    dataSocket.bind(('', 0))

    # Send ephemeral port number to client 
    servConnSocket.sendall(str(dataSocket.getsockname()[1]).encode())

    # Receive data channel connection from client
    dataSocket.listen(1) 
    connectionSocket, addr = dataSocket.accept()

    # Receive filename from client
    filename = connectionSocket.recv(40).decode()

    # Generate a unqiue filename
    new_filename = get_unique_filename(filename)   
    
    # Open file in append mode
    file = open(new_filename, "a")

    # Print this is the right function
    print("Receiving file from client...")
    # Get the data from the client and decode it
    while True:
        # Receive data
        data = connectionSocket.recv(40).decode()

        # If there is no data then close file 
        if not data:
            file.close()
            break
        else:
            file.write(data)

    # Success output
    print("SUCCESS")
    print(filename + " has been downloaded successfully")
    print("Number of bytes downloaded: " + str(os.stat(filename).st_size) + "\n")

    # Close data channel 
    file.close()
    dataSocket.close()
    connectionSocket.close()
    
# ************************************************
# Uploads file to client
# ************************************************
def put():
    # Create data channel 
    dataSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    # Bind the socket to hostname and port 
    dataSocket.bind(('', 0))

    # Send ephemeral port number to client 
    servConnSocket.sendall(str(dataSocket.getsockname()[1]).encode())

    # Receive data channel connection from client
    dataSocket.listen(1) 
    connectionSocket, addr = dataSocket.accept()
    
    # Receive filename from client
    filename = connectionSocket.recv(40).decode()

    # File is not found on server
    dirContents = os.listdir()
    if (filename not in dirContents):
        print("FILE NOT FOUND\n")
        connectionSocket.close()
        
    else:  
        # Upload file to client 
        print("Uploading file to client...")
        file = open(filename, "r")
        try:
            connectionSocket.sendall(file.read().encode())
        except IOError:
            print("Unable to upload contents to client")
            file.close()
            connectionSocket.close()

        # Success output
        print("SUCCESS")
        print(filename + " has been uploaded successfully")
        print("Number of bytes uploaded: " + str(os.stat(filename).st_size) + "\n")

        file.close()
        dataSocket.close()
        connectionSocket.close()
    
# ************************************************
# List files found on server
# ************************************************
def list():
    # Create data channel 
    dataSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    
    # Bind the socket to hostname and port
    dataSocket.bind(('', 0))

    # Send ephemeral port number to client 
    servConnSocket.sendall(str(dataSocket.getsockname()[1]).encode())

    # Receive data channel connection from client
    dataSocket.listen(1)
    connectionSocket, addr = dataSocket.accept()

    #Get list of files in directory 
    dirContents = os.listdir()
    dirList = ""
    for filename in dirContents:
        dirList = dirList + filename + "\n"

    print("Sending directory contents to client...")
    try:
        connectionSocket.sendall(dirList.encode())
    except IOError:
        print("Error sending directory contents to client")
        connectionSocket.close()

    # Success output
    print("SUCCESS")
    print("Directory contents been uploaded successfully\n")

    # Close connection
    dataSocket.close()
    connectionSocket.close()

if __name__ == '__main__':
    main()
