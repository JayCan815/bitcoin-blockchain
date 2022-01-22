from socket import *
import hashlib
import os
from sys import getsizeof

turn = 1  # init to 1 per instructions - used to mine odd blocks
balance = 0  # full node balance


# takes data and hases it in a 32 byte form
def forMerkleHashing(data):
    hashHandler = hashlib.sha256()
    hashHandler.update(data.encode("utf-8"))
    hashValue = hashHandler.hexdigest()
    return (hashValue)


# function for creting block
# params: LastBlockHash=header of last block(, and tx1-tx4= the last 4 transactions(12byte each)
def makeBlock(lastBlockHash, tx1, tx2, tx3, tx4):
    tx1HashValue = forMerkleHashing(tx1)
    tx2HashValue = forMerkleHashing(tx2)
    tx3HashValue = forMerkleHashing(tx3)
    tx4HashValue = forMerkleHashing(tx4)
    tx12HashValue = forMerkleHashing(tx1HashValue + tx2HashValue)
    tx34HashValue = forMerkleHashing(tx3HashValue + tx4HashValue)
    merkleRoot = forMerkleHashing(tx12HashValue + tx34HashValue)
    # print("t1: "+tx1HashValue)
    # print("ml: "+len(merkleRoot))
    hashHandler = hashlib.sha256()
    nonce = 0  # block hash digits 0-7
    while True:
        block_header = str(nonce) + lastBlockHash + merkleRoot
        hashHandler.update(block_header.encode("utf-8"))
        hashValue = hashHandler.hexdigest()
        # print('nonce:{0}, hash:{1}'.format(nonce, hashValue))
        nounceFound = True
        for i in range(4):
            if hashValue[i] != '0':
                nounceFound = False
        if nounceFound:
            # print('nonce:{0}, hash:{1}'.format(nonce, hashValue))
            # print(hex(nonce))
            break
        else:
            nonce = nonce + 1

        # end of header of block, now onto body/data section of block
    # newBlock=hashValue+tx1+tx2+tx3+tx4
    # print(str(hex(nonce))+lastBlockHash+merkleRoot)
    nonce = str(hex(nonce))
    nonce = nonce[2:].zfill(8)
    newBlock = nonce + lastBlockHash + merkleRoot + tx1 + tx2 + tx3 + tx4
    return (newBlock)


# Returns number of Tx in Temp_Tx.txt
def getNumberOfTx():
    with open("Temp_T.txt") as tx:
        count = sum(1 for _ in tx)
    return count


# Writes to Temp_Tx.txt
def writeToTx(message):
    tx = open("Temp_T.txt", "a+")
    tx.write(message + '\n')
    tx.close()


def removeTx():
    a_file = open("Temp_T.txt", "r")
    lines = a_file.readlines()
    a_file.close()
    del lines[0:4]
    revised_file = open("Temp_T.txt", "w+")
    for line in lines:
        revised_file.write(line)
    revised_file.close()


# Removes 4 Tx from Temp_T -> add mining fee and total tx fee ( 30BC + 8BC) to full node balance) -> send Tx to client
# actual mining still needs to be implemented
def mine():
    global balance
    clientPort = 10001  # client to send confirmed Tx to, change depending on which full node this is // CHANGE DEPENDING ON IF THIS IS F1 OR F2
    fullNodePort = 20000  # F2 full node, used to send the blocks // CHANGE DEPENDING ON IF THIS IS F1 OR F2
    serverName = '127.0.0.1'
    clientSocket = socket(AF_INET, SOCK_DGRAM)
    fullnodeSocket = socket(AF_INET, SOCK_DGRAM)
    balance += 30
    balance += 8
    tx = open("Temp_T.txt", "r")
    lines = tx.readlines()

    # get 4 transactions from Temp_Tx.txt and remove them from Temp_t.txt
    lines = [x.strip('\n') for x in lines]
    minedTransactions = "".join(lines)
    clientSocket.sendto(minedTransactions.encode(), (serverName, clientPort))
    tx.close()
    print(lines)
    removeTx()
    newBlock = ""
    print(turn)
    if (turn % 2 == 0):
        print("Turn is odd, F1 mining...")
        lastblockInfo = 0
        if os.path.getsize('Blockchain.txt') == 0:  # if no blocks in blockchain yet
            print('No Blocks in blockchain')
            lastblockInfo = "0000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000"
        else:  # get last block from blockchain
            bchain = open("Blockchain.txt", "r")
            temp = bchain.readlines()
            temp = [x.strip('\n') for x in temp]
            lastblockInfo = temp[-1]
            lastblockInfo = lastblockInfo[:136]
            bchain.close()

        bchain = open("Blockchain.txt", "a")
        newBlock = makeBlock(lastblockInfo, lines[0], lines[1], lines[2], lines[3])
        bchain.write(newBlock)  # makes new block and adds to blockchain file
        # To do: need to send newBlock to everyone
        bchain.close()
        # send newBlock to other node.
        print("Mining finished, sending block to other node : " + newBlock)
        fullnodeSocket.sendto(newBlock.encode(), (serverName, fullNodePort))
    else:
        return


def main():
    global turn
    while 0 != 1:
        serverPort = 10000  # server port // CHANGE DEPENDING ON IF THIS IS F1 OR F2
        serverSocket = socket(AF_INET, SOCK_DGRAM)  # set listening port
        serverSocket.bind(('', serverPort))  # listen

        print('The server is ready to receive')
        message, clientAddress = serverSocket.recvfrom(2048)  # wait for request

        # old debug messages - keeping incase new debugging is needed
        print("DEBUG: IP ADDRESS TUPLE OF REQUESTER: " + clientAddress[0])
        # print("DEBUG: SIZE OF MESSAGE (use bytes to determine if Tx or block??) " + str(getsizeof(message)))
        # print("DEBUG: message sent: " + message.decode("utf-8"))

        # determine if requester is client or full node - using address (127.0.0.1 for full node, 192.168.1.255 for client)
        # client address may change, unsure how to get a better method to unique identify requesters.
        if clientAddress[0] == '127.0.0.1':
            print("Requester is a full node...")
            print("size of message " + str(getsizeof(message)))
            if getsizeof(message) <= 59:
                print("The message received is a Tx.")
                message = message.decode("utf-8")
                writeToTx(message)
                if (getNumberOfTx() == 4):
                    print("Number of Tx is 4, removing and mining...")
                    turn += 1
                    mine()

            else:
                serverName = "127.0.0.1"
                print("The message received is a block.")
                bchain = open("Blockchain.txt", "a+")
                message = message.decode("utf-8")
                print("Block appended to Blockchain.txt :  " + message)
                bchain.write(message)
                bchain.close();
                print("Block received from other full node: " + message)
                print("Removing 4 Tx from blockchain")
                removeTx()
                clientPort = 10001
                clientSocket = socket(AF_INET, SOCK_DGRAM)
                # sliced block from blockchain
                minedTransactions = message[136:]
                # sliced transactions
                revisedTransaction = minedTransactions[72:]
                print("4 transactiosn sliced from block: " + revisedTransaction)
                print("transactions removed from block" + minedTransactions)
                clientSocket.sendto(minedTransactions.encode(), (serverName, clientPort))




        else:
            if message.decode("UTF-8") == "print":
                # loop through blockchain file and send to client
                tx = open("Temp_T.txt", "r")
                lines = tx.readlines()

                # get 4 transactions from Temp_Tx.txt and remove them from Temp_t.txt
                lines = [x.strip('\n') for x in lines]
            else:
                print("Requester is client...")
                print("The message received is a Tx.")
                print("Sending too other full node...")
                fullNodePort = 20000  # other full node, used to send the blocks // CHANGE DEPENDING ON IF THIS IS F1 OR F2
                serverName = '127.0.0.1'
                fullnodeSocket = socket(AF_INET, SOCK_DGRAM)
                message = message.decode("utf-8")
                fullnodeSocket.sendto(message.encode(), (serverName, fullNodePort))
                writeToTx(message)
                if (getNumberOfTx() == 4):
                    print("Number of Tx is 4, preparing mining...")
                    turn += 1
                    mine()


if __name__ == '__main__':
    main()
