# first check frequencies of all integers

# have a function that precomputes combinations

# iterate on starting digits, rest should be easy

# assume we have frequency map freq where freq[i] = number of times i occurs as a digit

def getfac(i):
    out = 1
    for i in range(1, i+1):
        out *= i
    return out

def findsim(freq):
    tot = 0
    l = sum(freq)
    for i in range(1, 10):
        if freq[i] == 0:
            continue
        comb = getfac(l - 1)
        for j in range(10):
            if i == j: 
                comb /= getfac(freq[j] - 1)
            else:
                comb /= getfac(freq[j])
        tot += comb
    return tot
    
def func(a, b):
    freqa = [0 for i in range(10)]
    freqb = [0 for i in range(10)]
    for c in a:
        freqa[ord(c) - ord('0')] += 1
    for c in b:
        freqb[ord(c) - ord('0')] += 1
    
    if freqa == freqb:
        print("A")
        return findsim(freqa)
    else:
        return findsim(freqb)


A = "1234"
B = "1213"
print(func(A, B))