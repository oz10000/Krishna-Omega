
#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import numpy as np

def calculate_metrics(trades, initial_capital, final_equity):
    n = len(trades)
    if n == 0:
        return {'Win Rate': 0, 'Profit Factor': 0, 'Sharpe': 0, 'Max Drawdown': 0, 'Expectancy': 0}

    pnls = [t['pnl_usdt'] for t in trades]
    wins = [p for p in pnls if p > 0]
    losses = [p for p in pnls if p < 0]
    win_rate = len(wins)/n*100
    total_win = sum(wins) if wins else 0
    total_loss = abs(sum(losses)) if losses else 0
    profit_factor = total_win / total_loss if total_loss > 0 else float('inf')
    expectancy = np.mean(pnls)

    equity = [initial_capital]
    for p in pnls:
        equity.append(equity[-1] + p)
    peak = initial_capital
    dd = 0
    for e in equity:
        if e > peak:
            peak = e
        dd = max(dd, (peak - e)/peak*100 if peak > 0 else 0)

    returns = pnls
    if len(returns) > 1:
        mean_ret = np.mean(returns)
        std_ret = np.std(returns) if np.std(returns) > 0 else 0.01
        sharpe = (mean_ret / std_ret) * np.sqrt(30*24*12)
    else:
        sharpe = 0

    return {
        'Win Rate': round(win_rate, 2),
        'Profit Factor': round(profit_factor, 3) if profit_factor != float('inf') else float('inf'),
        'Sharpe': round(sharpe, 3),
        'Max Drawdown': round(dd, 2),
        'Expectancy': round(expectancy, 2),
        'Total Trades': n,
        'Total PnL': round(sum(pnls), 2),
        'Final Equity': round(final_equity, 2)
    }
