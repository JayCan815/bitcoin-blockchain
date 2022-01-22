from socket import *
import re
from re import search


serverPort = 20001


def isClientPayer(message):
    print(message)
    print(message.find("B"))
    indexOfAccount = int(message.find("B"))
    if indexOfAccount == 0:
        return True
    return False


def checkIfTxIsAvailable(transaction):
    print("checkIfTxIsAvailable")
    file = open("Unconfirmed_T.txt", "r")
    ledger = file.read().splitlines()
    for line in ledger:
        print(line, transaction)
        if line.find(transaction) != -1:
            file.close()
            return True
    file.close()
    return False


def creditConfirmedBalance(transaction):
    # account is the first 8 chars of transaction string
    accountToCharge = transaction[:8]
    # amount to charge is last 8 chars
    amountInHex = transaction[16:]
    # adding 0x to convert to proper hex
    amountInHex = "0x" + amountInHex
    print("Charging account:", accountToCharge)
    print("Amount due in hex:", amountInHex)
    accountB1Balance = ""
    accountB2Balance = ""
    confirmedB1Balance = ""
    confirmedB2Balance = ""
    index = 1
    file = open("ClientBBalance.txt", "r")
    ledger = file.read().splitlines()
    file.close()
    for line in ledger:
        # if re.search("[0-9A-Za-z]", line) is None:
        #     break
        # first line always has Account A1
        if index == 1:
            accountB1Balance = line
            # confirmed balance is last 8 chars of string
            confirmedB1Balance = accountB1Balance[18:]
            confirmedB1Balance = "0x" + confirmedB1Balance
        # second line is always Account A2
        if index == 2:
            accountB2Balance = line
            confirmedB2Balance = accountB2Balance[18:]
            confirmedB2Balance = "0x" + confirmedB2Balance
        index = index + 1

    # subtract amount from respective confirmed account balance and then write back both accounts to file
    if accountToCharge == "B0000001":
        confirmedB1Balance = int(confirmedB1Balance, 16) - int(amountInHex, 16) - 2
        confirmedB1Balance = hex(confirmedB1Balance)
        confirmedB1Balance = confirmedB1Balance[2:]
        confirmedB1Balance = prependZeros(confirmedB1Balance)
        ledger = open("ClientBBalance.txt", "w")
        accountB1Balance = accountB1Balance[:18]
        accountB1Balance = accountB1Balance + confirmedB1Balance
        ledger.writelines([accountB1Balance + "\n", accountB2Balance + "\n"])
        ledger.close()

    if accountToCharge == "B0000002":
        confirmedB2Balance = int(confirmedB2Balance, 16) - int(amountInHex, 16) - 2
        confirmedB2Balance = hex(confirmedB2Balance)
        confirmedB2Balance = confirmedB2Balance[2:]
        confirmedB2Balance = prependZeros(confirmedB2Balance)
        ledger = open("ClientBBalance.txt", "w")
        accountB2Balance = accountB2Balance[:18]
        accountB2Balance = accountB2Balance + confirmedB2Balance
        ledger.writelines([accountB1Balance + "\n", accountB2Balance + "\n"])
        ledger.close()


def removeTransactionFromUnconfirmed(transaction):
    transactions = []
    file = open("Unconfirmed_T.txt", "r")
    ledger = file.read().splitlines()
    for line in ledger:
        if re.search("[0-9A-Za-z]", line) is None:
            print("empty line removed")
        transactions.append(line)
    file.close()

    file = open("Unconfirmed_T.txt", "r+")
    file.truncate(0)
    file.close()

    print("Transactions read from Unconfirmed_T.txt:", transactions)

    ledger = open("Unconfirmed_T.txt", "w")
    # loop through transactions read from file, write each tx back to Unconfirmed_T.txt unless it is a match
    # for the tx we are processing, in which case we skip writing this tx back to file.
    transactionFound = False # flag will prevent us removing more than one tx
    for tx in transactions:
        if search(transaction, tx) and not transactionFound:
            print("transaction found in Unconfirmed.txt, removing transaction...")
            transactionFound = True
        else:
            ledger.write(tx + "\n")
    ledger.close()


def appendTransactionToConfirmed(transaction):
    print("in append fn")
    file = open("Confirmed_T.txt", "r")
    lines = file.read().splitlines()
    file.close()
    # if the document is empty, then we write to file
    # otherwise we append
    if len(lines) == 0:
        writeToFile = open("Confirmed_T.txt", "w")
        writeToFile.write(transaction + "\n")
        writeToFile.close()
    else:
        print("writing...")
        appendToFile = open("Confirmed_T.txt", "a")
        appendToFile.write(transaction + "\n")
        appendToFile.close()


def prependZeros(hexAmount):
    numOfZerosToAdd = len(hexAmount)
    numOfZerosToAdd = 8 - numOfZerosToAdd

    while not numOfZerosToAdd == 0:
        hexAmount = "0" + hexAmount
        numOfZerosToAdd = numOfZerosToAdd - 1
    return str(hexAmount.upper())


def debitAccounts(transaction):
    # getting account to debit
    accountToDebit = transaction[8:16]
    # getting amount to debit
    amountToDebit = transaction[16:]
    amountToDebit = "0x" + amountToDebit
    file = open("ClientBBalance.txt", "r")
    accountBalances = file.read().splitlines()
    file.close()
    b1Balance = accountBalances[0]
    b2Balance = accountBalances[1]

    if accountToDebit == "B0000001":
        unconfirmedBalance = b1Balance[9:17]
        unconfirmedBalance = "0x" + unconfirmedBalance
        newUnconfirmedBalance = int(unconfirmedBalance, 16) + int(amountToDebit, 16)
        newUnconfirmedBalance = hex(newUnconfirmedBalance)
        newUnconfirmedBalance = newUnconfirmedBalance[2:]
        newUnconfirmedBalance = prependZeros(str(newUnconfirmedBalance))
        confirmedBalance = b1Balance[18:]
        confirmedBalance = "0x" + confirmedBalance
        newConfirmedBalance = int(confirmedBalance, 16) + int(amountToDebit, 16)
        newConfirmedBalance = hex(newConfirmedBalance)
        newConfirmedBalance = newConfirmedBalance[2:]
        newConfirmedBalance = prependZeros(newConfirmedBalance)
        ledger = open("ClientBBalance.txt", "w")
        b1Balance = accountToDebit + ":" + newUnconfirmedBalance + ":" + newConfirmedBalance
        ledger.write(b1Balance + "\n")
        ledger.write(b2Balance + "\n")
        ledger.close()
        print("Account:", accountToDebit, "amount credited in decimal:", int(amountToDebit, 16), "new account balance:", b1Balance)
    if accountToDebit == "B0000002":
        unconfirmedBalance = b2Balance[9:17]
        unconfirmedBalance = "0x" + unconfirmedBalance
        newUnconfirmedBalance = int(unconfirmedBalance, 16) + int(amountToDebit, 16)
        newUnconfirmedBalance = hex(newUnconfirmedBalance)
        newUnconfirmedBalance = newUnconfirmedBalance[2:]
        newUnconfirmedBalance = prependZeros(str(newUnconfirmedBalance))
        confirmedBalance = b2Balance[18:]
        confirmedBalance = "0x" + confirmedBalance
        newConfirmedBalance = int(confirmedBalance, 16) + int(amountToDebit, 16)
        newConfirmedBalance = hex(newConfirmedBalance)
        newConfirmedBalance = newConfirmedBalance[2:]
        newConfirmedBalance = prependZeros(newConfirmedBalance)
        ledger = open("ClientBBalance.txt", "w")
        b2Balance = accountToDebit + ":" + newUnconfirmedBalance + ":" + newConfirmedBalance
        ledger.write(b1Balance + "\n")
        ledger.write(b2Balance + "\n")
        ledger.close()
        print("Account:", accountToDebit, "amount credited in decimal:", int(amountToDebit, 16), "new account balance:", b2Balance)


def transactionHandler(transactions):
    numOfTransactions = len(transactions)
    print("Number of incoming transactions:", numOfTransactions)

    if(numOfTransactions == 4):
        # loop through each tx in our list and handle each one
        while not numOfTransactions == 0:
            # select first element in list and then delete
            transaction = transactions[0]
            del(transactions[0])
            # check if client is payer in this transaction
            isPayer = isClientPayer(transaction)
            print(isPayer)
            if isPayer:
                # make sure Tx is in Unconfirmed_Txt
                isTxAvailable = checkIfTxIsAvailable(transaction)
                print(isTxAvailable, transaction)
                if not isTxAvailable:
                    print("Warning transaction is invalid, client will not be charged for this transaction:", transaction)
                    numOfTransactions = numOfTransactions - 1
                else:
                    # reduce confirmed balance by tx amount
                    creditConfirmedBalance(transaction)

                    # remove tx from unconfirmed.txt
                    removeTransactionFromUnconfirmed(transaction)

                    # append to confirmedTx.txt
                    appendTransactionToConfirmed(transaction)
                    # do this at the end of each iteration
                    numOfTransactions = numOfTransactions - 1
            # payee flow else
            else:
                # debit unconfirmed and confirmed accounts
                debitAccounts(transaction)
                # append transaction to Confirmed_T
                appendTransactionToConfirmed(transaction)
                numOfTransactions = numOfTransactions - 1


# main driver for program
def serverDriver():
    serverSocket = socket(AF_INET, SOCK_DGRAM)
    serverSocket.bind(('', serverPort))
    print('The server is ready to receive')
    while True:
        message, clientAddress = serverSocket.recvfrom(2048)
        # each transaction is 24 chars long, divide to get # of tx
        numOfTransactions = len(message) / 24
        numOfTransactions = int(numOfTransactions)
        # stripping extra chars from socket message
        message = str(message)
        message = message[2:]
        lastIndex = len(message) - 1
        message = message[0:lastIndex]
        # each transaction gets pushed onto a list
        transactions = []
        # transactions come in one long string, so we parse the first 24 chars recursively to extract each tx
        while not numOfTransactions == 0:
            transaction = message[:24]
            transactions.append(transaction)
            message = message[24:]
            numOfTransactions = numOfTransactions - 1
        # handles the transaction flow
        transactionHandler(transactions)

serverDriver()