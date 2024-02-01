#!/usr/bin/python3
import sys
import matplotlib.pyplot as plt
import numpy as np
from scipy.optimize import curve_fit


ctr = []
bids = []

# python3 assess.py ./make-ipinyou-data/1458/train.yzx.txt.lr.pred ./make-ipinyou-data/1458/train.yzx.txt ./make-ipinyou-data/1458/test.yzx.txt.lr.pred ./make-ipinyou-data/1458/test.yzx.txt

fi = open(sys.argv[3], 'r') 
for line in fi:
    ctr.append(float(line))

fi = open(sys.argv[4], 'r')
for line in fi:
    bids.append(float(line.split()[1]))

tmp = [(ctr[i], bids[i]) for i in range(len(ctr))]
tmp.sort()

k = 1000
freq = len(ctr) // k
ix = 0

x = []
y = []

for i in range(k):
    lim = freq
    avgc = 0
    avgb = 0
    if i < len(ctr) % k:
        lim += 1
    for j in range(lim):
        avgc += tmp[ix][0]
        avgb += tmp[ix][1]
        ix += 1
    avgc = avgc / float(lim)
    avgb = avgb / float(lim)
    if avgc > 0.01:
        continue
    x.append(avgc)
    y.append(avgb)


def objective(x, a, b, c, d):
    return (a * x) + (b * x**2) + (c * x**3) + d

popt, _ = curve_fit(objective, x, y)
a, b, c, d = popt

t = np.arange(0, 0.0015, 0.00005)
y_line = objective(t, a, b, c, d)
# plt.scatter(x,y)
# plt.plot(t, 40 + 100 * t/(t+0.05), 'r--')
# plt.plot(t, 110000 * t, 'g--')
# plt.plot(t, y_line, '--', color='red')
# plt.show()



ctr_test = []
bids_test = []
clicks_test = []
fi = open(sys.argv[3], 'r') 
for line in fi:
    ctr_test.append(float(line))

fi = open(sys.argv[4], 'r')
for line in fi:
    bids_test.append(float(line.split()[1]))
    clicks_test.append(int(line.split()[0]))


def bid(i, cost):
    if cost > bids_test[i]:
        return True
    return False


# python3 assess.py ./make-ipinyou-data/1458/train.yzx.txt.lr.pred ./make-ipinyou-data/1458/train.yzx.txt ./make-ipinyou-data/1458/test.yzx.txt.lr.pred ./make-ipinyou-data/1458/test.yzx.txt
# python3 assess.py ./make-ipinyou-data/1458/train.yzx.txt.lr.pred ./make-ipinyou-data/1458/train.yzx.txt ./make-ipinyou-data/1458/train.yzx.txt.lr.pred ./make-ipinyou-data/1458/train.yzx.txt

portion = 1/8
B = sum(bids_test) * portion
goal = 1.1 * portion
# K_const = 20000
K_lim = 400000
K = K_lim
bidFactor = 0.2

window = []
winsize = 100000
# winsize = 20000
winsm = 0

cnt = 0
N = len(bids_test)
resu = []
bud = []
x_axis=[]
clickcnt = 0
sm = 0

lucky_wins = 0

def get_bid_price(i):
    # global ca
    # global cb
    dif = K * ctr_test[i] - objective(ctr_test[i], a, b, c, d)
    if dif < 0: # curve above line
        # ca += 1
        return (min(K * ctr_test[i], B), 1)
    else: 
        # cb += 1
        return (min(objective(ctr_test[i], a, b, c, d) + dif * bidFactor, B), 0)



for i in range(N):
    # keep sliding window of cost usage: make sure the budget is not exhausted too quickly
    bidPrice, res = get_bid_price(i)
    win = bid(i, bidPrice)
    window.append(win)
    winsm += win
    # print(bidPrice, bids_test[i], B, K, bidFactor, cnt)
    if win:
        B -= bids_test[i]
        window.append(1)
        sm += bids_test[i]
        clickcnt += clicks_test[i]
        cnt += 1
        if res == 1: 
            lucky_wins += 1
    else:
        window.append(0)
    resu.append(K)
    # resu.append(cnt)
    # resu.append(bidFactor)
    bud.append(B)
    x_axis.append(i)
    # if res == 0: # under line: on curve

    # else: # on line: random bid!!

    if len(window) >= winsize:
        winrate = winsm / winsize
        print(winsm)
        # resu.append(winrate)
        winsm -= window[-winsize]
        if i%50 == 0 and winrate > goal:
            K -= K * ((winrate - goal) / goal / (winsize/50))
        # if winrate > portion:
        #     K -= K * ((winrate - portion) / portion / winsize)
    # else:
    #     resu.append(0)
    
    if i % winsize == 0 and (i // winsize)%10 == 0:
        K = K_lim
        

    # if bidFactor >= 1: 
    #     bidFactor = 1

    # if bet is on line:
        # if win, shift line down
            # K *= 0.99
        # if lose, shift line up
            # K *= 1.01

    # if len(window) >= winsize:
    #     avg = sm / winsize
    #     res = N - i - 1 # how many bids are left
    #     res * avg
    #     if res * avg > B:
    #         K *= 0.9999
    #     else: 
    #         K *= 1.0001
    #         K = min(K, Klim)
    #     if len(window) - 1 - winsize >= 0:
    #         sm -= window[len(window) - 1 - winsize]
    # print(K)


print("Number of bids won:", cnt)
print("Number of bids expected:", len(clicks_test)/8)
print("Number of clicks won:", clickcnt)
print("Number of clicks expected:", sum(clicks_test)/8)

# print(clickcnt)
print("Budget remaining:", B, "out of", sum(bids_test) / 8)
print("Total impressions:", len(bids_test))
# print(sum(bids_test) / 8)
# print(sum(clicks_test) / 8)
# print(sum(clicks_test) / 8)
print("Lucky Wins:" , lucky_wins)
plt.scatter(x_axis,resu)
# plt.scatter(x_axis,[0.125 for i in range len(bids_test)]])
plt.plot(x_axis, [0.125 for i in range(len(bids_test))], '--', color='red')
# plt.scatter(x_axis,cbb)

plt.show()