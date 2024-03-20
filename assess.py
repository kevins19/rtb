#!/usr/bin/python3
import sys
import matplotlib.pyplot as plt
import numpy as np
from scipy.optimize import curve_fit
from scipy.interpolate import CubicSpline


ctr = []
bids = []

fi = open(sys.argv[1], 'r') 
for line in fi:
    ctr.append(float(line))

fi = open(sys.argv[2], 'r')
for line in fi:
    bids.append(float(line.split()[1]))

tmp = [(ctr[i], bids[i]) for i in range(len(ctr))]
tmp.sort()

k = 10000
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



cs = CubicSpline(x, y)
x_new = np.linspace(0, 0.01, 10000)
y_new = y_new = cs(x_new)

def objective(p):
    return cs(p)

fig, axs = plt.subplots(5, figsize=(9, 9));
axs[4].scatter(x,y, s=5)
axs[4].plot(x_new, y_new, '--', color='red')

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
# python3 assess.py ./make-ipinyou-data/1458/train.yzx.txt.lr.pred ./make-ipinyou-data/1458/train.yzx.txt ./make-ipinyou-data/1458/test.yzx.txt.lr.pred ./make-ipinyou-data/1458/test.yzx.txt



def run_test(portion = 1/32, bids = bids_test, ctr = ctr_test, clicks = clicks_test, window_size = 2000, K_lim = 30000, bid_factor = 0.4):
    B = sum(bids) * portion
    original_budget = B
    goal = portion
    K = K_lim

    window = []
    winsm = 0

    cnt = 0
    N = len(bids_test)
    k_change = []
    b_change = []
    winrate_change = []
    goal_change = []
    adjust_K = []
    k_sum = 0
    last_reset = last_goal_change = -window_size

    clickcnt = 0
    sm = 0
    lucky_wins = 0
    clicks_ev  =0

    losscnt = 0;

    def bid(i, cost):
        if cost > bids[i]:
            return 1
        return 0

    def get_bid_price(i):
        dif = K * ctr[i] - objective(ctr[i])
        # return (min(30000 * ctr[i], B), 1)
        if dif < 0: # curve above line
            return (min(K * ctr[i], B), 1)
        else: 
            # print(min(objective(ctr[i], a, b, c, d) + dif * bid_factor, B))
            return (min(objective(ctr[i]) + dif * bid_factor, B), 0)
        
        # perhaps bid slightly above the line
        
    for i in range(N):
        # keep sliding window of cost usage: make sure the budget is not exhausted too quickly
        bid_price, res = get_bid_price(i)
        win = bid(i, bid_price)
        if win > 0:
            B -= bids[i]
            window.append(1)
            sm += bids[i]
            clickcnt += clicks[i]
            cnt += 1
            if res == 1: 
                lucky_wins += 1
            clicks_ev += ctr[i]
            winsm += 1
        else:
            window.append(0)
            losscnt += clicks[i]

        # k_change.append(K)
        k_change.append(K)
        b_change.append(B)

        if len(window) > window_size:
            winrate = winsm / window_size
            winsm -= window[len(window)-window_size - 1]
            winrate_change.append(winrate)
            # x_axis.append(len(winrate_change))
            if winrate > goal:
                K -= K * ((winrate - goal) / goal) * (1 / window_size)
                adjust_K.append(1)
            else: 
                adjust_K.append(0)
            
            # adjust winrate
            '''
            (n - i)/n : remaining portion of campaign
            B / original_budget : remaining portion of budget

            winrate = B / original_budget 
            
            ''' 
            dif = B / original_budget - (N - i + 1) / N
            if i - last_goal_change > window_size and abs(dif) > 0.01:
                goal += dif * 0.004
                last_goal_change = i

            # using effective budget, to spend within some window
            goal_change.append(goal)
        else:
            adjust_K.append(0)

        k_sum += adjust_K[-1]
        
        if len(adjust_K) > window_size and i - window_size >= last_reset:
            k_sum -= adjust_K[len(adjust_K)-window_size - 1]
            if k_sum / window_size < 0.01:
                K *= 1.02
                last_reset = i
        
        


    print("Number of bids won:", cnt)
    print("Number of bids expected:", len(clicks) * portion)
    print("Number of clicks won:", clickcnt)
    print("Number of clicks expected:", sum(clicks) * portion)
    print("Budget remaining:", B, "out of", sum(bids) * portion)
    print("Percent of Budget remaining:", B/(sum(bids) * portion))
    print("Total impressions:", len(bids))
    print("Lucky Wins:" , lucky_wins)
    print("EV of clicks:" , clicks_ev)
    print(losscnt)
    print(sum(clicks))
    axs[0].scatter([i for i in range(len(k_change))], k_change, s=5)
    axs[1].scatter([i for i in range(len(winrate_change))], winrate_change, s=5)
    axs[2].scatter([i for i in range(len(b_change))], b_change, s=5)
    axs[3].scatter([i for i in range(len(goal_change))], goal_change, s=5)
    # plt.scatter(x_axis,b_change)
    axs[1].plot([i for i in range(len(winrate_change))], [portion for i in range(len(winrate_change))], '--', color='red')
    plt.show()


run_test()