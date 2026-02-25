import time
import json
from dataclasses import dataclass
import pandas as pd

from moex import fetch_candles
from indicators import ema, rsi, atr, money_flow

STATE_FILE = "state.json"

@dataclass
class Signal:
    kind: str
    symbol: str
    tf: str
    text: str
    chart_df: pd.DataFrame

def _load_state():
    try:
        with open(STATE_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return {"last_sent": {}, "events_today": []}

def _save_state(state):
    with open(STATE_FILE, "w", encoding="utf-8") as f:
        json.dump(state, f, ensure_ascii=False, indent=2)

def _cooldown_ok(state, key: str, cooldown_sec: int) -> bool:
    last = state["last_sent"].get(key, 0)
    return (time.time() - last) >= cooldown_sec

def scan_once(watch_futures, watch_stocks, interval_min: int, anomaly_k: float = 3.0):
    state = _load_state()
    out = []
    tf = f"{interval_min}m" if interval_min != 60 else "1h"

    # ---- FUTURES ----
    for sym in watch_futures:
        try:
            df = fetch_candles("futures", "forts", sym, interval_min, limit=140)
            if len(df) < 60:
                continue

            df["ema20"] = ema(df["close"], 20)
            df["ema50"] = ema(df["close"], 50)
            df["rsi14"] = rsi(df["close"], 14)
            df["money"] = money_flow(df)

            base = df["money"].iloc[-60:-1].median()
            cur = df["money"].iloc[-1]
            ratio = cur / (base + 1e-12)

            move_pct = (df["close"].iloc[-1] - df["open"].iloc[-1]) / df["open"].iloc[-1] * 100
            above_trend = df["close"].iloc[-1] > df["ema50"].iloc[-1]
            below_trend = df["close"].iloc[-1] < df["ema50"].iloc[-1]

            key = f"FUT:{sym}:{tf}"

            if ratio >= anomaly_k and _cooldown_ok(state, key, 3600):

                r = df["rsi14"].iloc[-1]

                if move_pct > 0 and above_trend and r >= 55:
                    direction = "LONG"
                elif move_pct < 0 and below_trend and r <= 45:
                    direction = "SHORT"
                else:
                    continue

                text = (
                    f"⚡ ФЬЮЧЕРС {direction}\n"
                    f"{sym} • TF {tf}\n"
                    f"💰 Деньги: {cur:,.0f} (в {ratio:.1f}× выше нормы)\n"
                    f"📈 Свеча: {move_pct:+.2f}% • RSI {r:.0f}\n"
                    f"⚠️ Не финсовет"
                )

                state["last_sent"][key] = time.time()
                state["events_today"].append(
                    {"type": direction, "sym": sym, "tf": tf, "ratio": float(ratio)}
                )

                out.append(Signal(direction, sym, tf, text, df.tail(80)))

        except Exception:
            continue

    # ---- STOCKS ----
    for sym in watch_stocks:
        try:
            df = fetch_candles("stock", "shares", sym, interval_min, limit=140)
            if len(df) < 60:
                continue

            df["money"] = money_flow(df)

            base = df["money"].iloc[-60:-1].median()
            cur = df["money"].iloc[-1]
            ratio = cur / (base + 1e-12)

            move_pct = (df["close"].iloc[-1] - df["open"].iloc[-1]) / df["open"].iloc[-1] * 100
            key = f"STK:{sym}:{tf}"

            if ratio >= anomaly_k and abs(move_pct) >= 0.4 and _cooldown_ok(state, key, 3600):

                if move_pct > 0:
                    title = "🟢 ВХОД ДЕНЕГ"
                else:
                    title = "🔴 ВЫХОД ДЕНЕГ"

                text = (
                    f"{title}\n"
                    f"{sym} • TF {tf}\n"
                    f"💰 Деньги: {cur:,.0f} (в {ratio:.1f}× выше нормы)\n"
                    f"📌 Свеча: {move_pct:+.2f}%\n"
                    f"⚠️ Не финсовет"
                )

                state["last_sent"][key] = time.time()
                state["events_today"].append(
                    {"type": title, "sym": sym, "tf": tf, "ratio": float(ratio)}
                )

                out.append(Signal(title, sym, tf, text, df.tail(80)))

        except Exception:
            continue

    _save_state(state)
    return out
