import matplotlib.pyplot as plt
import pandas as pd


def plot_windowed_counts(window_size=1000):
    """
        Feromone Sum,Ants Count 1 Short,Ants Count 2 Short,Ants Count 1 Long,Ants Count 2 Long
    0.0,0,0,0,0
    0.0,0,0,0,0
    0.0,0,0,0,0
    0.0,0,0,0,0
    0.0,0,0,0,0
    0.0,0,0,0,0
    0.0,0,0,0,0

    """
    df = pd.read_csv("model_data.csv")
    counts_1_short = df["Ants Count 1 Short"].rolling(window=window_size).sum()
    counts_2_short = df["Ants Count 2 Short"].rolling(window=window_size).sum()
    counts_1_long = df["Ants Count 1 Long"].rolling(window=window_size).sum()
    counts_2_long = df["Ants Count 2 Long"].rolling(window=window_size).sum()

    plt.plot(counts_1_short, label="Branch 1 Short")
    plt.plot(counts_2_short, label="Branch 2 Short")
    plt.plot(counts_1_long, label="Branch 1 Long")
    plt.plot(counts_2_long, label="Branch 2 Long")
    plt.xlabel("Time step")
    plt.ylabel("Windowed ant count")
    plt.title(f"Windowed ant count (window size = {window_size})")
    plt.legend()
    plt.show()


if __name__ == "__main__":
    plot_windowed_counts()
