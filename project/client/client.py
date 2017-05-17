import glob
import random
import math
import sys
import mysocket
import bitstring
from bitstring import *
import time
import os.path

PRIME = 622288097498926496141095869268883999563096063592498055290461  # 60 cifre
SERVER_ADDR = "localhost"
PORT = 50000
LUNG_INFO = 24
LUNG_FILENAME = 256
LUNG_BLOCK = 16
FILE_INPUT = "image_omura.jpg"


def rabinMiller(n):
    s = n - 1
    t = 0
    while s & 1 == 0:
        s = s / 2
        t += 1
    k = 0
    while k < 128:
        a = random.randrange(2, n - 1)
        # a^s is computationally infeasible.  we need a more intelligent approach
        # v = (a**s)%n
        # python s core math module can do modular exponentiation
        v = pow(a, s, n)  # where values are (num,exp,mod)
        if v != 1:
            i = 0
            while v != (n - 1):
                if i == t - 1:
                    return False
                else:
                    i = i + 1
                    v = (v ** 2) % n
        k += 2
    return True


def isPrime(n):
    # lowPrimes is all primes (sans 2, which is covered by the bitwise and operator)
    # under 1000. taking n modulo each lowPrime allows us to remove a huge chunk
    # of composite numbers from our potential pool without resorting to Rabin-Miller
    lowPrimes = [3, 5, 7, 11, 13, 17, 19, 23, 29, 31, 37, 41, 43, 47, 53, 59, 61, 67, 71, 73, 79, 83, 89, 97
        , 101, 103, 107, 109, 113, 127, 131, 137, 139, 149, 151, 157, 163, 167, 173, 179
        , 181, 191, 193, 197, 199, 211, 223, 227, 229, 233, 239, 241, 251, 257, 263, 269
        , 271, 277, 281, 283, 293, 307, 311, 313, 317, 331, 337, 347, 349, 353, 359, 367
        , 373, 379, 383, 389, 397, 401, 409, 419, 421, 431, 433, 439, 443, 449, 457, 461
        , 463, 467, 479, 487, 491, 499, 503, 509, 521, 523, 541, 547, 557, 563, 569, 571
        , 577, 587, 593, 599, 601, 607, 613, 617, 619, 631, 641, 643, 647, 653, 659, 661
        , 673, 677, 683, 691, 701, 709, 719, 727, 733, 739, 743, 751, 757, 761, 769, 773
        , 787, 797, 809, 811, 821, 823, 827, 829, 839, 853, 857, 859, 863, 877, 881, 883
        , 887, 907, 911, 919, 929, 937, 941, 947, 953, 967, 971, 977, 983, 991, 997]
    if (n >= 3):
        if (n & 1 != 0):  # mi interessa che il primo bit di n sia 1
            for p in lowPrimes:
                if (n == p):
                    return True
                if (n % p == 0):
                    return False
            return rabinMiller(n)
    return False


def generateLargePrime(k):
    # k is the desired bit length
    r = 100 * (math.log(k, 2) + 1)  # number of attempts max
    r_ = r
    while r > 0:
        # randrange is mersenne twister and is completely deterministic
        # unusable for serious crypto purposes
        n = random.randrange(2 ** (k - 1), 2 ** (k))
        r -= 1
        if isPrime(n) == True:
            return n
    return "Failure after " + `r_` + " tries."


# funzione che calcola il Massimo Comun Divisore fra due numeri
def MCD(a, b):
    while (b != 0):
        a, b = b, a % b
    return a


# funzione che controlla se due numeri hanno MCD =1
def check_mcd(a, b):
    if MCD(a, b) == 1:
        return True
    else:
        return False


# genero una chiave key in modo che sia prima con il numero p PRIMO scelto
def getkey(prime):
    # genera un altro primo random da 40 cifre
    key = generateLargePrime(40)  # 40 la lunghezza voluta
    # se il numero che ho generato e p-1 sono primi, allora restituisco la chiave
    if not (check_mcd(key, prime - 1)):
        return getkey(prime)
    else:
        return key


# ax + by = g = gcd(a, b) [gcd=great common divisor]
def getdecryptkey(a, b):
    modulo = b
    x, y, u, v = 0, 1, 1, 0
    while a != 0:
        q, r = b // a, b % a;
        m, n = x - u * q, y - v * q
        b, a, x, y, u, v = a, r, u, v, m, n
    if x < 0:
        x = modulo + x
    return x


# funzione che restituisce una stringa (lunga length) codificata in ascii, contenente una serie di 0 davanti al numero n
def myzfill(n, length):
    string = str(n)
    string = string.zfill(length)
    return string.encode('ascii')

#######################################################################################################################
#######################################################################################################################

images=[]
image_selected=0

print "\nchoose file:"
images = glob.glob("image*")

# stampo i file da selezionare
i = 0
for num in images:
    print '\t' + str(i) + ') ' + images[i] + '\t\t'+ str(os.path.getsize(images[i]))[:3]+' KB'
    i = i + 1

try:
    image_selected = raw_input()
except SyntaxError:
    option = None

FILE_INPUT = images[int(image_selected)]
print '\n\033[92mimage selected is: '+str(FILE_INPUT)+' \033[0m\n'

print '\033[94m                                                    '
print '      |-----|                           |-----|             '
print '      |  A  |                           |  B  |             '
print '      |_____|                           |_____|             '
print '                                                            '
print '         |                                                  '
print '         |                                                  '
print '         |                                                  '
print '         M - - - -> M1=F(M,ea,P) - - - - > M1               '
print '     (original)                            |                '
print '                                           |                '
print '                                           |                '
print '         M2 < - - - M2=F(M1,eb,P) <- - - - M1               '
print '         |                                                  '
print '         |                                                  '
print '         |                                                  '
print '         M2 - - - > M3=F(M2,da,P) - - - -> M3               '
print '                                           |                '
print '                                           |                '
print '                                       M4=F(M3,db,P)        '
print '                                           |                '
print '                                           |                '
print '                                          M=M4              '
print '                                       (original)           \033[0m\n'

# =================================INIZIO "MAIN"=================================
# preparazione filename
file_name = FILE_INPUT
file_name = file_name.ljust(LUNG_FILENAME)

# apertura socket verso bob
sock = mysocket.mysocket()
print("Starting the connection..")
sock.connect(SERVER_ADDR, PORT)
print("Connected to %s:%d" % (SERVER_ADDR, PORT))

# lettura file e calcolo del numero di chunk
file_bit = BitStream(filename=FILE_INPUT)
num_block = int(file_bit.length / 128)
image_len = file_bit.length
print("File to encrypt: image_computer.png,\nsize: %d Bits (%d Bytes)," % (image_len, num_block / 8))
print("\nNumero di Blocchi da 128bit: " + str(num_block))

# invio del numero di blocchi e in seguito del nome file
sock.send(myzfill(num_block, LUNG_INFO))
sock.send(file_name.encode('utf-8'))
# time.sleep(3)

# iterazione sul numero di blocchi con conseguente cifratura con ka, invio, ricezione di kakb,decifratura con ka e
# re-invio del blocco cifrato con kb
for i in range(num_block):
    print("---------------------------------------------------------------------------\nChunk n. %d" % i)
    block = BitStream(bin=file_bit.read('bin:128'))
    block = block.uint
    # genero una chiave di cifratura e una di decifratura
    eka = getkey(PRIME)
    dka = getdecryptkey(eka, (PRIME - 1))
    # cifro il blocco con ka
    block_ka = pow(block, eka, PRIME)
    # invio il blocco cifrato con ka
    block_ka = str(block_ka).encode('ascii')
    sock.send(myzfill(len(block_ka), LUNG_INFO) + block_ka)
    # ricevo blocco cifrato con kakb e relativa dimensione
    len_block = int(sock.receive(LUNG_INFO))
    block_ka_kb = int(sock.receive(len_block))
    print(block_ka_kb)
    # decifro il blocco kakb con la chiave di decifratura
    block_kb = pow(block_ka_kb, dka, PRIME)
    # preparo il blocco cifrato con kb all'invio e lo invio
    block_kb = str(block_kb).encode('ascii')
    sock.send(myzfill(len(block_kb), LUNG_INFO) + block_kb)

print '\n\033[92mfinish! \033[0m'
sock.close()
