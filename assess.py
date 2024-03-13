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



# python3 assess.py ./make-ipinyou-data/1458/train.yzx.txt.lr.pred ./make-ipinyou-data/1458/train.yzx.txt ./make-ipinyou-data/1458/test.yzx.txt.lr.pred ./make-ipinyou-data/1458/test.yzx.txt
# python3 assess.py ./make-ipinyou-data/1458/train.yzx.txt.lr.pred ./make-ipinyou-data/1458/train.yzx.txt ./make-ipinyou-data/1458/train.yzx.txt.lr.pred ./make-ipinyou-data/1458/train.yzx.txt

def run_test(portion = 1/8, bids = bids_test, ctr = ctr_test, clicks = clicks_test, window_size = 20000, goal_portion = 1.1, K_lim = 400000, bid_factor = 0.2):
    B = sum(bids) * portion
    goal = goal_portion * portion
    K = K_lim

    window = []
    winsm = 0

    cnt = 0
    N = len(bids_test)
    k_change = []
    b_change = []
    winrate_change = []
    x_axis = []
    clickcnt = 0
    sm = 0
    lucky_wins = 0
    clicks_ev  =0

    def bid(i, cost):
        if cost > bids[i]:
            return True
        return False

    def get_bid_price(i):
        dif = K * ctr[i] - objective(ctr[i], a, b, c, d)
        if dif < 0: # curve above line
            return (min(K * ctr[i], B), 1)
        else: 
            return (min(objective(ctr[i], a, b, c, d) + dif * bid_factor, B), 0)
        
    for i in range(N):
        # keep sliding window of cost usage: make sure the budget is not exhausted too quickly
        bid_price, res = get_bid_price(i)
        win = bid(i, bid_price)
        window.append(win)
        winsm += win
        if win:
            B -= bids[i]
            window.append(1)
            sm += bids[i]
            clickcnt += clicks[i]
            cnt += 1
            if res == 1: 
                lucky_wins += 1
            clicks_ev += ctr[i]
        else:
            window.append(0)

        k_change.append(K)
        b_change.append(B)

        if len(window) >= window_size:
            winrate = winsm / window_size
            winsm -= window[-window_size]
            winrate_change.append(winrate)
            # x_axis.append(len(winrate_change))
            if i%50 == 0 and winrate > goal:
                K -= K * ((winrate - goal) / goal / (window_size/50))
        
        if i % window_size == 0 and (i // window_size)%10 == 0:
            K = K_lim - (K_lim - K) / 2.0

    print("Number of bids won:", cnt)
    print("Number of bids expected:", len(clicks) * portion)
    print("Number of clicks won:", clickcnt)
    print("Number of clicks expected:", sum(clicks) * portion)
    print("Budget remaining:", B, "out of", sum(bids) * portion)
    print("Percent of udget remaining:", B/(sum(bids) * portion))
    print("Total impressions:", len(bids))
    print("Lucky Wins:" , lucky_wins)
    print("EV of clicks:" , clicks_ev)
    fig, axs = plt.subplots(3, figsize=(9, 9));
    axs[0].scatter([i for i in range(len(k_change))], k_change)
    axs[1].scatter([i for i in range(len(winrate_change))], winrate_change)
    axs[2].scatter([i for i in range(len(b_change))], b_change)
    # plt.scatter(x_axis,b_change)
    axs[1].plot([i for i in range(len(winrate_change))], [portion for i in range(len(winrate_change))], '--', color='red')
    plt.show()

run_test()