##############################
# File :: vector.py
# Written on Saturday,  4 September 2021.
# Author: Henrik Peteri
##############################
import math

def Length(arr):
    total = 0
    for i in arr:
        total += i ** 2
                
    return math.sqrt(total)

def DotProduct(a, b):
    total = 0
    for i in range(len(a)):
        total += a[i] * b[i]

    return total

def Normal(arr):
    return [arr[1], arr[0]]

def Normalize(arr):
    l = Length(arr)
    for i in range(len(arr)):
        arr[i] /= l
    return arr

def Reflect(a, b):
    reflection = a[:]
    dot = DotProduct(a, b)
    for i in range(len(reflection)):
        reflection[i] = reflection[i] - (2.0 * dot * b[i])

    return reflection
