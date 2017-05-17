import mysocket
import bitstring
import random
import math
import sys
from bitstring import *		
import time
import os.path

PRIME=622288097498926496141095869268883999563096063592498055290461
SERVER_ADDR = "localhost"
PORT = 50000
LUNG_INFO = 24
LUNG_FILENAME = 256
LUNG_BLOCK = 16


def rabinMiller(n):
     s = n-1
     t = 0
     while s&1 == 0:
         s = s/2
         t +=1
     k = 0
     while k<128:
         a = random.randrange(2,n-1)
         #a^s is computationally infeasible.  we need a more intelligent approach
         #v = (a**s)%n
         #python s core math module can do modular exponentiation
         v = pow(a,s,n) #where values are (num,exp,mod)
         if v != 1:
             i=0
             while v != (n-1):
                 if i == t-1:
                     return False
                 else:
                     i = i+1
                     v = (v**2)%n
         k+=2
     return True

def isPrime(n):
     #lowPrimes is all primes (sans 2, which is covered by the bitwise and operator)
     #under 1000. taking n modulo each lowPrime allows us to remove a huge chunk
     #of composite numbers from our potential pool without resorting to Rabin-Miller
     lowPrimes =   [3,5,7,11,13,17,19,23,29,31,37,41,43,47,53,59,61,67,71,73,79,83,89,97
                   ,101,103,107,109,113,127,131,137,139,149,151,157,163,167,173,179
                   ,181,191,193,197,199,211,223,227,229,233,239,241,251,257,263,269
                   ,271,277,281,283,293,307,311,313,317,331,337,347,349,353,359,367
                   ,373,379,383,389,397,401,409,419,421,431,433,439,443,449,457,461
                   ,463,467,479,487,491,499,503,509,521,523,541,547,557,563,569,571
                   ,577,587,593,599,601,607,613,617,619,631,641,643,647,653,659,661
                   ,673,677,683,691,701,709,719,727,733,739,743,751,757,761,769,773
                   ,787,797,809,811,821,823,827,829,839,853,857,859,863,877,881,883
                   ,887,907,911,919,929,937,941,947,953,967,971,977,983,991,997]
     if (n >= 3):
         if (n&1 != 0):
             for p in lowPrimes:
                 if (n == p):
                    return True
                 if (n % p == 0):
                     return False
             return rabinMiller(n)
     return False

def generateLargePrime(k):
     #k is the desired bit length
     r=100*(math.log(k,2)+1) #number of attempts max
     r_ = r
     while r>0:
        #randrange is mersenne twister and is completely deterministic
        #unusable for serious crypto purposes
         n = random.randrange(2**(k-1),2**(k))
         r-=1
         if isPrime(n) == True:
             return n
     return "Failure after "+`r_` + " tries."


def MCD(a,b):
	while ( b != 0 ):
		a, b = b, a % b
	return a

#funzione che controlla se due numeri hanno MCD =1
def check_mcd(a,b):
	if MCD(a,b)==1:
		return True
	else:
		return False	


def getkey(prime):
	#key=1111111111111111111111777777755555333221
	key = generateLargePrime(40) #40 la lunghezza voluta
	if not(check_mcd(key, prime-1)):
		return getkey(prime)
	else:
		return key	

def getdecryptkey(a, b): # ax + by = g = gcd(a, b) [gcd=great common divisor]
    modulo = b
    x,y, u,v = 0,1, 1,0
    while a != 0:
        q,r = b//a,b%a; m,n = x-u*q,y-v*q
        b,a, x,y, u,v = a,r, u,v, m,n
    if x<0:
    	x=modulo+x
    return x

#funzione che restituisce una stringa (lunga length) codificata in ascii, contenente una serie di 0 davanti al numero n
def myzfill(n, length):
    string = str(n)
    string=string.zfill(length)
    return string.encode('ascii')

#=================================INIZIO "MAIN"=================================
#inizializzazione socket e apertura di connessione
sock = mysocket.mysocket()
sock.bind("0.0.0.0", PORT)
sock.listen(5)
print("Server on.")
print("Waiting for connection...")
new_sock, address = sock.accept()
print("Connection established with: ", address)
#creazione nuova socket verso il client
new_sock = mysocket.mysocket(new_sock)

#ricezione del numero di blocchi
num_block = int(new_sock.receive(LUNG_INFO))
print("Number of chunks: "+str(num_block))

#ricezione del filename
file_name = new_sock.receive(LUNG_FILENAME).decode('utf-8')
file_name=file_name.replace(" ", "")
print(file_name)

#inizializzazione variabili
message = BitStream()
primo=PRIME
time.sleep(3)

#iterazione sul numero di blocchi con conseguente ricezione del blocco cifrato con ka, cifratura con kb, re-invio del
#blocco cifrato con kakb, ricezione del blocco cifrato con kb e decifratura finale per ottenere il blocco in chiaro
for i in range(num_block):
    print("---------------------------------------------------------------------------\nChunk n. %d" % i)
    #ricevo la lunghezza blocco
    len_block = int(new_sock.receive(LUNG_INFO))
	#ricevo il blocco cifrato con ka
    block_ka = int(new_sock.receive(len_block))
    print(block_ka)
    #genero una chiave di cifratura e una di decifratura
    ekb = getkey(primo)
    dkb = getdecryptkey(ekb,(primo-1))
    #cifro ulteriormente il blocco cifrato con ka e lo preparo all'invio
    block_ka_kb = pow(block_ka, ekb, primo)
    block_ka_kb = str(block_ka_kb).encode('ascii')
    #invio blocco cifrato con kakb
    new_sock.send(myzfill(len(block_ka_kb), LUNG_INFO) + block_ka_kb )
	#ricevo blocco cifrato con kb e relativa dimensione
    len_block = int(new_sock.receive(LUNG_INFO))
    block_kb = int(new_sock.receive(len_block))
    #ottengo il blocco in chiaro usando la mia chiave di decifratura sul blocco cifrato con kb
    block = pow(block_kb, dkb, primo)
    #append di tutti i blocchi in un'unica variabile
    if i==0:
		message=BitStream(uint=block, length=128)
    else:
		block=BitStream(uint=block, length=128)
		message.append(block)
#scrivo la variabile su file
message = message.bytes
received_file = open(file_name, 'wb')
received_file.write(message)
received_file.close()

print '\n\033[92mimage create! \033[0m'
new_sock.close()
