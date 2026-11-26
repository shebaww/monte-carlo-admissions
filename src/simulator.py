import types
from pathlib import Path
import time
import numpy as np
import pandas as pd
import yaml
import matplotlib.pyplot as plt


class Operations():
    def __init__(self, output: str, DataIngestor: types.ModuleType, config: str):
        self.output = Path(output)
        self.output.mkdir(parents=True, exist_ok=True)
        self.config = config
        self.gpa, self.sat, self.essay, self.ecs, self.rec, self.awards, self.college_df = DataIngestor.run()
        with open(self.config) as file:
            self.config_data = yaml.safe_load(file)
        print(f"Hello {self.config_data["applicant"]["name"]}. Please wait a while.")
        self.trials = self.config_data["config"]["trials"]
        self.capacity_c = self.config_data["config"]["capacity_c"]
        self.mu = self.config_data["config"]["mu"]
        self.sigma = self.config_data["config"]["sigma"]
        self._lambda = self.config_data["config"]["lambda"]
        self.alpha = self.config_data["config"]["alpha"]
        self.beta_default = self.config_data["config"]["beta_default"]
        self.beta_max = self.config_data["config"]["beta_max"]
        self.beta_min = self.config_data["config"]["beta_min"]
        self.decay_min = 0.5
        self.college_num = len(self.college_df)
        
        self.essay_eff = self.decay_function() * self.essay
        
        self.betas = {cluster: [self.beta_default] for cluster in self.config_data["clusters"]  }
        
        self.seed = self.config_data["config"]["seed"]
        self.rng = np.random.default_rng(self.seed)
        self.cluster_noise = {cluster: self.rng.normal(loc=self.mu, scale=self.sigma) for cluster in self.config_data["clusters"]  } 
        self.rho = {cluster: data["rho"] for cluster, data in self.config_data["clusters"].items()  } 

        # Analysis trackers
        self.trials_with_at_least_one_win = 0
        self.total_individual_wins = 0
        self.college_win_counts = {college['name']: 0 for idx, college in self.college_df.iterrows()}
        self.college_triage_fails = {college['name']: 0 for idx, college in self.college_df.iterrows()}
        self.cluster_win_counts = {cluster: 0 for cluster in self.config_data["clusters"] }
        
    def decay_function(self):
        decay = max(self.decay_min, 1 - self._lambda * max(0, self.college_num - self.capacity_c))
        return decay
    
    def weighted_sum(self, c: pd.DataFrame, beta: float, T_c: int, xi: float, p_c: float):
        _sat = self.sat # Throw away variable for test optionality
        if c["submitting_sat"] == False:
# Neutral stand point on test optionality
            _sat = 0.5
        S_c = T_c * (beta * p_c * ((c["w_gpa"] * self.gpa) + (c["w_sat"] * _sat) + (c["w_essay"] * self.essay_eff) + (c["w_ecs"] * self.ecs) + (c["w_rec"] * self.rec) + (c["w_awards"] * self.awards)) + xi)
        # Clamping
        if S_c > 1.0:
            S_c = 1.0
        elif S_c < 0.0:
            S_c = 0.0
        return S_c

    def binary_estimate(self, college: pd.DataFrame, S_c: float):
        return int(self.rng.random() < S_c)

    def academic_triage(self, college: pd.DataFrame):
        if self.gpa >= college["min_gpa"]:
            if (self.sat * 600) + 1000 < college["min_sat"] and not college["test_optionality"]:
                T_c = 0
            else:
                T_c = 1
        else:
            T_c = 0
        return T_c
    
    def current_beta(self, college: pd.DataFrame):
        return self.betas[college["cluster"]][-1]

    def dynamic_beta(self, Y_c: int, college: pd.DataFrame, S_c: float):
        beta = self.betas[college["cluster"]][-1] + self.alpha * (Y_c - S_c)
        self.betas[college["cluster"]].append(beta)
        
    def noise(self, college):
        epsilon_c = self.rng.normal(loc=self.mu, scale=self.sigma)
        xi_c = self.rho[college["cluster"]] * self.cluster_noise[college["cluster"]]  + (1 - self.rho[college["cluster"]] ) * epsilon_c
        return xi_c

    def reset(self):
        # Randomizes college order
        self.college_df = self.college_df.sample(frac=1, random_state=self.rng).reset_index(drop=True)
        # Cleans Beta lists and cluster noise for the next trial
        self.betas = {cluster: [self.beta_default] for cluster in self.config_data["clusters"]  }
        self.cluster_noise = {cluster: self.rng.normal(loc=self.mu, scale=self.sigma) for cluster in self.config_data["clusters"]  } 

    def expected_wins(self):
        return self.total_individual_wins / self.trials

    def portfolio_chances(self):
        return (self.trials_with_at_least_one_win / self.trials) * 100

    def plot_college_wins(self):
        names = list(self.college_win_counts.keys())
        win_percs = [(self.college_win_counts[n] / self.trials) * 100 for n in names]

        sorted_indices = np.argsort(win_percs)[::-1]
        sorted_names = [names[i] for i in sorted_indices]
        sorted_percs = [win_percs[i] for i in sorted_indices]

        fig, ax = plt.subplots(figsize=(12, 6))
        ax.barh(sorted_names, sorted_percs, color='skyblue')
        ax.set_xlabel('Win Percentage (%)')
        ax.set_title('Full Ride Probability by College')
        ax.invert_yaxis()
        fig.tight_layout()
        fig.savefig(self.output / "college_wins.png", dpi=300, bbox_inches="tight")
        plt.close(fig)

    def plot_cluster_wins(self):
        clusters = list(self.cluster_win_counts.keys())
        wins = list(self.cluster_win_counts.values())

        fig, ax = plt.subplots(figsize=(8, 5))
        colors = plt.cm.tab10(np.linspace(0, 1, len(clusters)))
        ax.bar(clusters, wins, color=colors)
        ax.set_ylabel(f'Total Wins (Out of {self.trials} Trials)')
        ax.set_title('Total Full Ride Wins by Cluster')
        fig.tight_layout()
        fig.savefig(self.output / "cluster_wins.png", dpi=300, bbox_inches="tight")
        plt.close(fig)

    def plot_beta_trajectories(self):
        fig, ax = plt.subplots(figsize=(10, 6))
        for cluster in self.config_data["clusters"]:
            ax.plot(self.betas[cluster], label=cluster)
        ax.axhline(y=1.0, color='black', linestyle='--', alpha=0.5, label="Default (1.0)")
        ax.set_xlabel('Order of Colleges Evaluated')
        ax.set_ylabel('Beta Value')
        ax.set_title('Dynamic Beta Trajectory (Final Trial)')
        ax.legend()
        fig.tight_layout()
        fig.savefig(self.output / "beta_trajectories.png", dpi=300, bbox_inches="tight")
        plt.close(fig)
        
    def recommend_colleges_to_remove(self):
        print("--- Colleges to Consider Removing ---")
        for name, fails in self.college_triage_fails.items():
            fail_rate = (fails / self.trials) * 100
            if fail_rate > 0:
                print(f"[Triage Failure] {name}: Failed academic triage {fail_rate:.1f}% of the time.")

        for name, wins in self.college_win_counts.items():
            win_rate = (wins / self.trials) * 100
            if win_rate < 0.9 and self.college_triage_fails[name] == 0:
                print(f"[Low ROI] {name}: Win rate is under 0.9% ({win_rate:.2f}%), draining essay effort.")

    def should_increase_list(self):
        p_at_least_one = self.portfolio_chances()
        print("\n--- Portfolio Size Recommendation ---")
        if p_at_least_one < 30.0:
            print(f"RECOMMENDATION: INCREASE LIST. Your probability of at least one full ride is {p_at_least_one:.1f}% (under 30%). Add more target/safety schools.")
        else:
            print("You do not necessarily need to increase your list based on current odds.")

    def should_decrease_list(self):
        p_at_least_one = self.portfolio_chances()
        e_wins = self.expected_wins()
        decay = self.decay_function()
        
        if p_at_least_one > 90.0 and e_wins > 2.0:
            print("RECOMMENDATION: DECREASE LIST. You have a >90% chance of winning at least one, averaging more than 2 wins. Cut some safeties to reduce essay fatigue.")
        elif decay <= 0.5 and p_at_least_one > 75.0:
            print("RECOMMENDATION: DECREASE LIST. Your essay decay has hit the floor (0.5). Cutting 2-3 colleges will boost your essay quality for the remaining ones.")

    def run_trial(self):
        trial_win = 0
        for idx, college in self.college_df.iterrows():
            beta_c = self.current_beta(college)
            T_c = self.academic_triage(college)
            xi_c = self.noise(college)
            p_c = college["full_ride_perc"] 
            S_c = self.weighted_sum(college, beta_c, T_c, xi_c, p_c)
            
            # Update beta
            Y_c = self.binary_estimate(college, S_c)
            self.dynamic_beta(Y_c, college, S_c)


            # TRACK STATISTICS
            c_name = college['name']
            if T_c == 0:
                self.college_triage_fails[c_name] += 1
            else:
                if Y_c == 1:
                    trial_win += 1
                    self.college_win_counts[c_name] += 1
                    self.cluster_win_counts[college['cluster']] += 1
            
        # Track trial-level stats
        self.total_individual_wins += trial_win
        if trial_win >= 1:
            self.trials_with_at_least_one_win += 1
            
        self.reset()

    def monte_run(self):
        i = 1
        for trial in range(self.trials):
            print(f"\rProcessing {i} / {self.trials}", end="")
            i+=1
            self.run_trial()
            
        print(f"\nExpected Wins (Average Full Rides per Trial): {self.expected_wins():.2f}")
        print(f"P(At least 1 Full Ride): {self.portfolio_chances():.2f}%\n")
        
        self.plot_college_wins()
        self.plot_cluster_wins()
     #   self.plot_beta_trajectories()
        self.recommend_colleges_to_remove()
        self.should_increase_list()
        self.should_decrease_list()
        
        # Keep plots open at the end
       # plt.show()

