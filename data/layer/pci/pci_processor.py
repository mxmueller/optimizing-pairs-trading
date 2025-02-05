import numpy as np
from scipy.optimize import minimize
import logging


class PCIProcessor:
    def __init__(self):
        self.beta = None
        self.rho = None
        self.sigma_m = None
        self.sigma_r = None
        self.pci_settings = None

    def normalize_prices(self, x1, x2):
        return x1 / x1[0], x2 / x2[0]

    def compute_restricted_likelihood(self, x1_norm, x2_norm):
        def neg_log_likelihood(params):
            beta, sigma_r = params
            n = len(x1_norm)
            rt = llh = 0

            for t in range(1, n):
                pred = beta * x1_norm[t] + rt
                innov = x2_norm[t] - pred
                var = sigma_r ** 2
                llh += -0.5 * (np.log(var) + innov ** 2 / var)
                rt += innov
            return -llh

        # Nur beta und sigma_r schätzen für RW Modell
        beta_init = np.cov(x1_norm, x2_norm)[0, 1] / np.var(x1_norm)
        std_init = np.std(x2_norm - beta_init * x1_norm)

        result = minimize(
            neg_log_likelihood,
            x0=[beta_init, std_init],
            bounds=[(-2, 2), (1e-6, 1)],
            method='L-BFGS-B'
        )
        return -result.fun

    def compute_full_likelihood(self, x1_norm, x2_norm):
        def neg_log_likelihood(params):
            beta, rho, sigma_m, sigma_r = params
            n = len(x1_norm)
            mt = rt = llh = 0

            for t in range(1, n):
                mt = rho * mt
                pred = beta * x1_norm[t] + mt + rt
                innov = x2_norm[t] - pred
                var = sigma_m ** 2 * (1 - rho ** 2) + sigma_r ** 2
                llh += -0.5 * (np.log(var) + innov ** 2 / var)
                rt += innov * 0.001
            return -llh

        beta_init = np.cov(x1_norm, x2_norm)[0, 1] / np.var(x1_norm)
        std_init = np.std(x2_norm - beta_init * x1_norm)

        result = minimize(
            neg_log_likelihood,
            x0=[beta_init, 0.9, std_init * 0.5, std_init * 0.5],
            bounds=[(-2, 2), (0.6, 0.99), (0.1, 1), (0.1, 1)],
            method='L-BFGS-B'
        )
        return -result.fun

    def compute_lr_score(self, x1, x2):
        x1_norm, x2_norm = self.normalize_prices(x1, x2)
        L_rw = self.compute_restricted_likelihood(x1_norm, x2_norm)
        L_full = self.compute_full_likelihood(x1_norm, x2_norm)
        return np.log(L_rw / L_full)

    def compute_r2_mr(self, x1, x2):
        params = self.estimate_parameters(x1, x2)
        sigma_m, sigma_r = params['sigma_m'], params['sigma_r']
        rho = params['rho']
        r2_mr = (2 * sigma_m ** 2) / (2 * sigma_m ** 2 + sigma_r ** 2 * (1 + rho))
        return r2_mr

    def select_pairs(self, all_pairs):
        # 1. LR-Score für alle Paare
        lr_scores = []
        for pair in all_pairs:
            x1 = np.array([d['close'] for d in pair['data1']])
            x2 = np.array([d['close'] for d in pair['data2']])
            score = self.compute_lr_score(x1, x2)
            lr_scores.append((pair, score))

        # Top 5% basierend auf LR-Score
        n_select = max(1, int(len(lr_scores) * 0.05))
        top_pairs = sorted(lr_scores, key=lambda x: x[1])[:n_select]

        # 2. R²_MR und Rho Filter
        final_pairs = []
        for pair, _ in top_pairs:
            x1 = np.array([d['close'] for d in pair['data1']])
            x2 = np.array([d['close'] for d in pair['data2']])
            r2_mr = self.compute_r2_mr(x1, x2)
            rho = self.estimate_parameters(x1, x2)['rho']

            if r2_mr > 0.5 and rho > 0.5:
                final_pairs.append(pair)

        return final_pairs

    def estimate_parameters(self, x1, x2):
        x1_norm, x2_norm = self.normalize_prices(x1, x2)

        def neg_log_likelihood(params):
            beta, rho, sigma_m, sigma_r = params
            n = len(x1_norm)
            mt = rt = llh = 0

            for t in range(1, n):
                mt = rho * mt
                pred = beta * x1_norm[t] + mt + rt
                innov = x2_norm[t] - pred
                var = sigma_m ** 2 * (1 - rho ** 2) + sigma_r ** 2
                llh += -0.5 * (np.log(var) + innov ** 2 / var)
                rt += innov * 0.001
            return -llh

        beta_init = np.cov(x1_norm, x2_norm)[0, 1] / np.var(x1_norm)
        std_init = np.std(x2_norm - beta_init * x1_norm)

        result = minimize(
            neg_log_likelihood,
            x0=[beta_init, 0.9, std_init * 0.5, std_init * 0.5],
            bounds=[(-2, 2), (0.6, 0.99), (0.1, 1), (0.1, 1)],
            method='L-BFGS-B'
        )

        beta, rho, sigma_m, sigma_r = result.x
        r2_mr = (2 * sigma_m ** 2) / (2 * sigma_m ** 2 + sigma_r ** 2 * (1 + rho))

        self.beta = beta
        self.rho = rho
        self.sigma_m = sigma_m
        self.sigma_r = sigma_r

        return {
            'beta': beta * x2[0] / x1[0],
            'rho': rho,
            'sigma_m': sigma_m,
            'sigma_r': sigma_r,
            'r2_mr': r2_mr,
            'lr_score': -2 * result.fun
        }

    def kalman_filter(self, x1, x2):
        x1_norm, x2_norm = self.normalize_prices(x1, x2)
        n = len(x1_norm)
        mt = np.zeros(n)
        rt = np.zeros(n)

        # Kalman Gain als closed-form
        kappa = (self.sigma_m ** 2 * (1 - self.rho ** 2)) / (
                    self.sigma_m ** 2 * (1 - self.rho ** 2) + self.sigma_r ** 2)

        for t in range(n):
            wt = x2_norm[t] - self.beta * x1_norm[t]
            if t > 0:
                pred_mt = self.rho * mt[t - 1]
                pred_rt = rt[t - 1]
                et = wt - (pred_mt + pred_rt)

                mt[t] = pred_mt + kappa * et
                rt[t] = pred_rt + (1 - kappa) * et
            else:
                mt[t] = 0
                rt[t] = wt

        window = min(63, len(mt))
        rolling_std = np.array([np.std(mt[max(0, i - window):i + 1])
                                for i in range(len(mt))])
        zscore = mt / rolling_std

        return {
            'mt': mt * x2[0],
            'rt': rt * x2[0],
            'zscore': np.clip(zscore, -5, 5)
        }

    def process_pair(self, data1, data2):
        x1 = np.array([d['close'] for d in data1])
        x2 = np.array([d['close'] for d in data2])

        if not np.all(np.isfinite(x1)) or not np.all(np.isfinite(x2)):
            return []

        params = self.estimate_parameters(x1, x2)

        if params['r2_mr'] < self.pci_settings['min_r2_mr']:
            return []

        states = self.kalman_filter(x1, x2)

        results = []
        for i, (d1, d2) in enumerate(zip(data1, data2)):
            results.append({
                'date': d1['date'],
                'symbol_pair': f"{d1['symbol']}_{d2['symbol']}",
                'symbol1': d1['symbol'],
                'symbol2': d2['symbol'],
                'beta': float(params['beta']),
                'rho': float(params['rho']),
                'sigma_m': float(params['sigma_m']),
                'sigma_r': float(params['sigma_r']),
                'mt': float(states['mt'][i]),
                'rt': float(states['rt'][i]),
                'zscore': float(states['zscore'][i]),
                'r2_mr': float(params['r2_mr']),
                'lr_score': float(params['lr_score'])
            })

        return results