import sys
from socket import *
import re
# Global Variables
transactionFee = 2
# accountA1Balance = 1000
# accountA2Balance = 1000
clientMenuDispatcher = {}  # used to invoke functions
serverName = '192.168.254.45'
serverPort = 10000
clientSocket = socket(AF_INET, SOCK_DGRAM)

def getUnconfirmedBalance(account):
    ledger = open("ClientABalance.txt", "r")
    accountA1Balance = ""
    accountA2Balance = ""
    a1UnconfirmedBalance = ""
    a2UnconfirmedBalance = ""
    index = 1
    for line in ledger:
        if index == 1:
            accountA1Balance = line
        index = index + 1
        accountA2Balance = line
    ledger.close()

    if account == "A0000001":
        indexToParseTo = accountA1Balance.find(":")
        temp = accountA1Balance[indexToParseTo+1:]
        indexToParseTo = temp.find(":")
        a1UnconfirmedBalance = temp[:indexToParseTo]
        a1UnconfirmedBalance = "0x" + a1UnconfirmedBalance
        a1UnconfirmedBalance = int(a1UnconfirmedBalance, 16)
        return str(a1UnconfirmedBalance)
    if account == "A0000002":
        indexToParseTo = accountA2Balance.find(":")
        temp = accountA2Balance[indexToParseTo+1:]
        indexToParseTo = temp.find(":")
        a2UnconfirmedBalance = temp[:indexToParseTo]
        a2UnconfirmedBalance = "0x" + a2UnconfirmedBalance
        a2UnconfirmedBalance = int(a2UnconfirmedBalance, 16)
        return str(a2UnconfirmedBalance)

def doesAmountExceedBalance(txAmount, balance):
    txAmount = int(txAmount) + 2
    if txAmount > int(balance):
        return True
    return False


def appendUnconfirmedTx(accounFrom, accountTo, unconfirmedTx):
    unconfirmedTx = hex(unconfirmedTx)
    unconfirmedTx = unconfirmedTx.upper()
    parsedHex = unconfirmedTx[2:]
    numOfZerosToPrepend = 8 - len(parsedHex)
    while not numOfZerosToPrepend == 0:
        parsedHex = "0" + parsedHex
        numOfZerosToPrepend = numOfZerosToPrepend - 1
    unconfirmedTx = accounFrom + accountTo + parsedHex
    ledger = open("Unconfirmed_T.txt", "a")
    ledger.write("\n" + unconfirmedTx)
    ledger.close()
    return unconfirmedTx

def clientMenu():
    print("Client Menu")
    print("1. Enter a new transaction.")
    print("2. Current Account(s) balance.")
    print("3. View unconfirmed transactions.")
    print("4. View last X amount of confirmed transactions.")
    print("5. Print the blockchain.")
    print("6. Exit")
    userSelection = input()
    validSelection = re.findall("[1-6]", userSelection)
    if len(validSelection) == 0:
        print("Invalid selection please try again\n\n")
        clientMenu()
    validSelection = range(1, 7)

    if int(userSelection) not in validSelection:
        print("Invalid selection please try again\n\n")
        clientMenu()

    functionIndex = str(userSelection)
    clientMenuDispatcher[functionIndex]()


def reduceUnconfirmedBalance(account, amount):
    ledger = open("ClientABalance.txt", "r+")
    index = 1
    accountA1Balance = ""
    accountA2Balance = ""
    for line in ledger:
        if index == 1:
            accountA1Balance = line
        if index == 2:
            accountA2Balance = line
        index = index + 1
    ledger.truncate(0)
    ledger.close()
    if account == "A0000001":
        accountName = accountA1Balance[:8]
        unconfirmedBalance = accountA1Balance[10:17]
        confirmedBalance = accountA1Balance[18:]

        unconfirmedBalance = "0x" + unconfirmedBalance
        unconfirmedBalance = int(unconfirmedBalance, 16)
        unconfirmedBalance = unconfirmedBalance - amount - 2
        unconfirmedBalance = hex(unconfirmedBalance)
        unconfirmedBalance = unconfirmedBalance[2:]
        numOfZerosToPrePend = 8 - len(unconfirmedBalance)
        while not numOfZerosToPrePend == 0:
            unconfirmedBalance = "0" + unconfirmedBalance
            numOfZerosToPrePend = numOfZerosToPrePend - 1
        unconfirmedBalance = unconfirmedBalance.upper()
        transactions = []
        transactions.append(unconfirmedBalance)

        accountA1Balance = accountName + ":" + unconfirmedBalance + ":" + confirmedBalance
        ledger = open("ClientABalance.txt", "w")
        ledger.write(accountA1Balance)
        ledger.write(accountA2Balance)
        ledger.close()



    if account == "A0000002":
        accountName = accountA2Balance[:8]
        unconfirmedBalance = accountA2Balance[10:17]
        confirmedBalance = accountA2Balance[18:]

        unconfirmedBalance = "0x" + unconfirmedBalance
        unconfirmedBalance = int(unconfirmedBalance, 16)
        unconfirmedBalance = unconfirmedBalance - amount - 2
        unconfirmedBalance = hex(unconfirmedBalance)
        unconfirmedBalance = unconfirmedBalance[2:]
        numOfZerosToPrePend = 8 - len(unconfirmedBalance)
        while not numOfZerosToPrePend == 0:
            unconfirmedBalance = "0" + unconfirmedBalance
            numOfZerosToPrePend = numOfZerosToPrePend - 1
        unconfirmedBalance = unconfirmedBalance.upper()
        transactions = []
        transactions.append(unconfirmedBalance)

        accountA2Balance = accountName + ":" + unconfirmedBalance + ":" + confirmedBalance
        ledger = open("ClientABalance.txt", "w")
        ledger.write(accountA1Balance)
        ledger.write(accountA2Balance)
        ledger.close()


def newTransaction():
    accountTo = ""
    accountFrom = ""
    print("Select account to pay from")
    print("1. Account A0000001")
    print("2. Account A0000002")
    userInput = int(input())
    if userInput == 1:
        accountFrom = "A0000001"
    if userInput == 2:
        accountFrom = "A0000002"

    print("Select account to pay to")
    print("1. Account B0000001")
    print("2. Account B0000002")
    userInput = int(input())

    if userInput == 1:
        accountTo = "B0000001"
    if userInput == 2:
        accountTo = "B0000002"

    amountInDecimal = int(input("Please enter amount to pay in decimal: "))

    # get unconfirmed account balance
    accountBalance = getUnconfirmedBalance(accountFrom)
    # make sure amount they are attempting to pay with, does not exceed their account balance
    amountExceeded = doesAmountExceedBalance(amountInDecimal, accountBalance)
    if amountExceeded:
        print("\n\n\nAmount exceeds account balance, please try again.")
        clientMenu()

    # reduce unconfirmed balance by transaction amount
    reduceUnconfirmedBalance(accountFrom, amountInDecimal)
    print("Tx:", accountFrom, " pays ", accountTo, " the amount of ", amountInDecimal, " BC")

    # append transaction to Unconfirmed_Txt
    unconfirmedTx = appendUnconfirmedTx(accountFrom, accountTo, amountInDecimal)

    # send tx to full node
    clientSocket.sendto(unconfirmedTx.encode(), (serverName, serverPort))

def viewBalance():
    ledger = open("ClientABalance.txt", "r")
    accountA1Balance = ""
    accountA2Balance = ""
    index = 1
    for line in ledger:
        if index == 1:
            accountA1Balance = line
        if index == 2:
            accountA2Balance = line
        index = index + 1

    print(accountA1Balance)
    print(accountA2Balance)
    clientMenu()


def viewUnconfrimedTx():
    ledger = open("Unconfirmed_T.txt", "r")
    for line in ledger:
        print(line)
    clientMenu()


def viewLastXTxs ():
    file = open("Confirmed_T.txt", "r")
    lines = file.read().splitlines()
    file.close()

    numOfTx = input("Enter X amount of tx's to view: ")
    numOfTx = int(numOfTx)
    if len(lines) == 0:
        print("No confirmed tx's yet")
        clientMenu()
    while numOfTx > 0:
        for line in lines:
            print(line)
            numOfTx = numOfTx - 1
    clientMenu()


def printBlockChain():
    print("\n\nprintBlockChain function")
    message = "print"
    clientSocket.sendto(message.encode(), (serverName, serverPort))
    clientMenu()

def exitProgram():
    print("Exiting program...")
    sys.exit(0)

# initialize our dispatcher
clientMenuDispatcher = {
    "1": newTransaction,
    "2": viewBalance,
    "3": viewUnconfrimedTx,
    "4": viewLastXTxs,
    "5": printBlockChain,
    "6": exitProgram
}


while True:
    clientMenu()



# unconfirmedTx = "A0000001B000000100000001B0000001A000000100000002"
# clientSocket.sendto(unconfirmedTx.encode(), (serverName, serverPort))