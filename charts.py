import os
import matplotlib.pyplot as plt

def make_chart(df, title: str, path: str):
    x = range(len(df))
    close = df["close"].values

    fig = plt.figure(figsize=(9, 5))
    ax1 = plt.gca()
    ax1.plot(x, close)

    if "ema20" in df.columns:
        ax1.plot(x, df["ema20"].values)
    if "ema50" in df.columns:
        ax1.plot(x, df["ema50"].values)

    ax1.set_title(title)
    ax1.grid(True)

    if "volume" in df.columns:
        ax2 = ax1.twinx()
        ax2.bar(x, df["volume"].fillna(0).values, alpha=0.2)
        ax2.set_yticks([])

    os.makedirs(os.path.dirname(path), exist_ok=True)
    plt.tight_layout()
    fig.savefig(path, dpi=140)
    plt.close(fig)
