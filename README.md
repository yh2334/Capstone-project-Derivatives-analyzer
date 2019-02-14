# Capstone-project-Derivatives-analyzer

This is a Python Dash based app that allows the user to:
1) build a structure of plain vanilla derivatives (European calls and puts) on a single underlying (e.g. SPX). 
2) Plot payoff at inception, at “now”, and at T
3) Plot the Greeks (delta, vega, theta, rho, lambda, epsilon, gamma, vanna, charm, vomma, DvegaDtime, veta, vera, speed, zomma, color, ultima) as function of strike, and of time to maturity, and time series)
4) Plot implied vol surface vs T and vs K
5) Calculate the intrinsic value of the structure
6) Build a futures hedge to neutralize delta
7) Instantaneous stress test of the underlying
8) Multiperiod stress testing (path dependent over T days, and intraday)
