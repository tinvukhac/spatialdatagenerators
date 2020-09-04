import math
import numpy as np
import pandas as pd


def extract_acc(filename):
    ratios = [0.01, 0.02, 0.03, 0.04, 0.05, 0.06, 0.07, 0.08, 0.09, 0.1]
    budgets = [0.01, 0.02, 0.03, 0.04, 0.05, 0.06, 0.07, 0.08, 0.09, 0.1, 0.11, 0.12, 0.13, 0.14, 0.15, 0.16, 0.17,
               0.18, 0.19, 0.2]
    df = pd.read_csv(filename, header=None)
    df = df.iloc[:, 1:]
    data = pd.DataFrame.to_numpy(df)
    print(data.shape)

    estimated_counts = {}
    for i in range(data.shape[0] - 10):
        budget = data[i][0]
        ratio = data[i][1]
        key = '{}-{}'.format(budget, ratio)
        estimated_counts[key] = data[i][2:]

    actual_counts = {}
    for i in range(200, 210):
        budget = data[i][0]
        ratio = data[i][1]
        key = '{}-{}'.format(budget, ratio)
        actual_counts[key] = data[i][2:]

    for budget in budgets:
        for ratio in ratios:
            key = '{}-{}'.format(budget, ratio)
            actual_key = '{}-{}'.format(1.0, ratio)
            estimated_count = estimated_counts[key]
            actual_count = actual_counts[actual_key]
            diff = abs(estimated_count / budget - actual_count)
            acc = [1.0 if diff[i] == 0 else max(0.0, 1.0 - diff[i] / actual_count[i]) for i in range(len(diff))]
            # acc = max(0, 1 - abs(estimated_count - actual_count) / actual_count)
            estimated_counts[key] = np.mean(acc)

    for budget in budgets:
        for ratio in ratios:
            key = '{}-{}'.format(budget, ratio)
            print ('{}, acc = {}'.format(key, estimated_counts[key]))


def main():
    print('Compute SE accuracy')
    extract_acc('se/result_DiagonalRot_002.csv')


if __name__ == "__main__":
    main()
