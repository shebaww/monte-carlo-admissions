# Monte-Carlo-Admissions

---

Everything here is assuming you're looking for full ride.

## What's needed

- Number of colleges
- Colleges with specified parameters (their specific weight, also whether you pass their academic triage, probability of acceptance) in a JSON file (acceptance rate is used for reference)
- Number of trials
- Number of colleges when decay starts
- Applicant info

## Pipeline

- Validate Data (College and config information)
- Ingesting Data
- Running Individual College chances
- Running Portfolio Chances
- Outputting Calculation

## Notes

- When conducting individual probabilities, if they are in the same cluster then you update event success according to the past event result. Define the definitions of the clusters, make it only
- Consider adding a logistic link
- Holistic Admission — chaotic noise is relatively high compared to pure college selectivity
- Colleges in the same cluster are correlated
- Beta is a local walk, not global; it's trial specific

---

## Formulae

### College Formula

$$
C_{\text{weight}} = w_{\text{gpa}} + w_{\text{SAT}} + w_{\text{essay}} + w_{\text{EC's}} + w_{\text{rec}} + w_{\text{Awards}}
$$

$$
w_j \ge 0, \quad \sum_j w_j \approx 1
$$

Where:

- $C_{\text{weight}}$ : How the colleges weigh their decision out of 1.00
- $w_{\text{gpa}}$ : How the colleges weigh your GPA
- $w_{\text{SAT}}$ : How the colleges weigh your SAT
- $w_{\text{essay}}$ : How the colleges weigh your Essays
- $w_{\text{EC's}}$ : How the colleges weigh your Extra-Curriculars
- $w_{\text{Awards}}$ : How the colleges weigh your Awards
- $w_{\text{rec}}$ : How the colleges weigh your Recommendation Letters

### Conversion metric

$$
a_{\text{gpa}} = \frac{\text{(Unweighted GPA - 2.5})}{1.5}
$$

$$
a_{\text{SAT}} = \frac{\text{SAT Score - 1000}}{600}
$$

$$
a_{\text{GPA}}, a_{\text{SAT}} \in [0,1]
$$

Where:

- $a_{\text{gpa}}$ : Converted GPA Score out of 1
- $a_{\text{SAT}}$ : Converted SAT Score out of 1
- $a_{\text{essay}}$ : Essay out of 1
- $a_{\text{EC's}}$ : Extra-Curriculars out of 1
- $a_{\text{Awards}}$ : Awards out of 1
- $a_{\text{rec}}$ : Recommendation Letters out of 1

Note: Since everything else is holistic, the user enters an accurate and unbiased rating out of 1.

### Application Depreciation

$$
q(N) = \max\left(0.5,\; 1 - \lambda \cdot \max(0, N - N_0)\right)
$$

Where:

- $q(N)$ : Scalar Multiplier of Application Decay for $N$ number of colleges
- $N_0$ : Number of colleges where effort starts affecting application
- $\lambda$ : Decay Rate
- $N$ : Number of Colleges you're applying to

### Essay against Decay

$$
a_{\text{essay, eff}} = a_{\text{essay}} \cdot q(N)
$$

Where:

- $a_{\text{essay, eff}}$ : Effective Essay, essay score calculated against Application decay
- $a_{\text{essay}}$ : Essay score out of 1
- $q(N)$ : Scalar Multiplier of Application Decay for $N$ number of colleges

### College Chances

$$
S(\beta)^{k}_c = T_c \cdot \left( \beta \cdot p_c \left[ (w_{c,\text{gpa}} a_{\text{gpa}}) + (w_{c,\text{SAT}} a_{\text{SAT}}) + (w_{c,\text{essay}} a_{\text{essay, eff}}) + (w_{c,\text{EC's}} a_{\text{EC's}}) + (w_{c,\text{rec}} a_{\text{rec}}) + (w_{c,\text{Awards}} a_{\text{Awards}}) \right] + \xi_c \right)
$$

$$
S_c(\beta) \in [0,1]
$$

Where:

- $S(\beta)^{k}_c$ : Estimated Competitiveness Probability of Full ride at college $c$ of index $k$
- $p_c$ : Full ride percentage published by college or estimated
- $a_{\text{gpa}}$ : Converted GPA Score out of 1
- $a_{\text{SAT}}$ : Converted SAT Score out of 1
- $a_{\text{essay, eff}}$ : Effective Essay, essay score calculated against Application decay
- $a_{\text{EC's}}$ : Extra-Curriculars out of 1
- $a_{\text{Awards}}$ : Awards out of 1
- $a_{\text{rec}}$ : Recommendation Letters out of 1
- $\xi_c$ : Noise Mixture of School Individual Noise, Environment Noise and positive correlation of college $c$
- $w_{c,\text{gpa}}$ : How the colleges weigh your GPA
- $w_{c,\text{SAT}}$ : How the colleges weigh your SAT
- $w_{c,\text{essay}}$ : How the colleges weigh your Essays
- $w_{c,\text{EC's}}$ : How the colleges weigh your Extra-Curriculars
- $T_c$ : Binary academic triage results
- $w_{c,\text{Awards}}$ : How the colleges weigh your Awards
- $w_{c,\text{rec}}$ : How the colleges weigh your Recommendation Letters
- $\beta$ : Cluster Specific Dynamic Beta, Likelihood of success based on past events, default = 1

Note: When analyzed, everything is taken out of 1. GPA, SAT, etc. is converted to an out-of-1 metric and $S_c$ is calculated out of 1.

### Portfolio Chances

$$
\hat P(\text{At least 1}) = \frac{1}{T} \sum^{T}_{t=1} \left( \text{wins}_t \ge 1 \right)
$$

$$
\text{wins}_t = \sum_c \text{Bernoulli}(S(\beta)_{c}^{k})
$$

Where:

- $\hat P(\text{At least 1})$ : Probability of 1 full ride
- $T$ : Amount of Trials
- $\text{wins}_t$ : Trial Wins of full ride college chances
- $S(\beta)^{k}_c$ : Estimated Competitiveness Probability of Full ride at college $c$ of index $k$

### Gaussian Distribution

$$
f(X) = \frac{1}{\sigma \sqrt{2\pi}} \exp\left(-\frac{(x-\mu)^2}{2\sigma^2}\right)
$$

Where:

- $f(X)$ : Gaussian Distribution of a random variable $X$
- $\sigma^2$ : Variance
- $\sigma$ : Standard Deviation
- $\mu$ : Mean

### Noise

$$
\epsilon_c, u_i = \mathcal{N}(0, \sigma^2) \quad \text{independently}
$$

$$
\xi_c = \rho_i \cdot u_i + (1-\rho_i) \cdot \epsilon_c
$$

Where:

- $\xi_c$ : Noise Mixture of School Individual Noise, Environment Noise and positive correlation of college $c$
- $\epsilon_c$ : College Specific Noise
- $u_i$ : Cluster Specific Environment Noise of $c$
- $\rho$ : Cluster Specific correlation strength
- $\mathcal{N}(0, \sigma^2)$ : Gaussian distribution of center 0, and variation of $\sigma^2$

### Dynamic Beta

$$
\beta_k = \beta_{k, i(c)}
$$

$$
\beta_k = \beta_{k-1} + \alpha \cdot \left(Y_c - S(\beta)_c^{k-1}\right)
$$

$$
0.5 \le \beta_k \le 1.3
$$

$$
Y_c = \text{Bernoulli}(S(\beta)^k_c)
$$

$$
Y_c \in \{0,1\}
$$

$$
\text{Default } \beta_k = 1.0, \quad \text{Trials remain independent}
$$

Where:

- $\beta_k$ : Cluster Specific Dynamic Beta, Likelihood of success based on $\beta_{k-1}$ and predicted $Y_c$ and $S_c$
- $S_c$ : College Application Strength for college $c$
- $Y_c$ : Binary estimated Full ride result
- $\alpha$ : Learning Step Rate

### Academic Triage

$$
T_c = (\text{GPA} \ge \text{Colleges Minimum GPA}) \wedge (\text{SAT} \ge \text{Colleges Minimum SAT})
$$

$$
T_c \in \{0,1\}
$$

Where:

- $T_c$ : Binary Academic Triage Result; if $T_c = 0 \implies S_c = 0 \implies$ College is skipped, no trial conducted for college $c$.

### Percent of full ride

$$
p_c = P(\text{admit}_c) \times P(\text{full ride} \mid \text{admit})_c
$$

Where:

- $p_c$ : Probability of Full ride, when inputting in JSON file

### Variables

- Default $\beta$ : 1.00
- Default $S_c$ : 0.5
- Standard Deviation ($\sigma$) : 0.005
- Mean ($\mu$) : 0
- Maximum essay decay coefficient : 0.5
- $\beta$ Clip $(0.5, 1.3)$
- Increment Step ($\alpha$) : 0.05
- $a_{\text{SAT}} = 0.5$, if test optional

---

## Personal Note

I have changed the minimum GPA for NYUAD, ViniUni, Clark, DKU because they actually view academics themselves holistically and they won't even be considered in the Monte as they will fail the academic triage (not in real life hopefully), because I have some chance of passing the academic triage in real life I will mimic that in the Monte by decreasing their minimum GPA.

---

## Calculation — more direct pipeline

- Check College weight sums, proper data types, file exists
- Convert actual GPA and SAT, turn JSON into proper DataFrame
- Calculate essay, effective essay against decay
- Calculate $S_c^k$ of college $c$ of index $k$ against beta, $p$, academic triage, noise, weighted sum, then clamped, then stored
  - beta is calculated against default $S_c$, $Y_c$ (Bernoulli), and constant increment $\alpha$
  - noise is calculated based on Gaussian distribution of college specific noise (random), cluster specific noise, cluster specific $\rho$
- both $P(\text{At least 1})$ is calculated based on Bernoulli of newly calculated $S_c$
- Then you can calculate other external information

---

## Clusters

- **Need (Institutional Full-Need / Need-Based Aid):** Universities that meet demonstrated financial need for international students (need-aware or need-blind). Correlation comes from shared international aid budgets and financial-need evaluation.
- **Merit (Competitive Merit / Named Full-Ride Scholarships):** Merit scholarships or full-ride fellowships (e.g., Stamps, Presidential/Honors merit awards, KAIST/VinUni merit tracks). Correlation reflects competition among high-achieving/high-output applicants and merit pool caps.
- **Government (National / Bilateral Government Scholarships):** State-funded scholarships (e.g., MEXT, CSC, Türkiye Bursları, Stipendium Hungaricum). Correlation reflects country quotas, embassy/bilateral selection dynamics, and government funding rules.
- **Special (Mission-, Partner-, or Region-Specific Tracks):** Programs with distinct structural criteria or dedicated pipelines (e.g., Berea's work/low-income model, Mastercard Foundation partner cohorts, Bocconi's Nuovo Fiore Ethiopia track).
