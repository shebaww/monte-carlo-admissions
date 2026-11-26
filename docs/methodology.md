---

Everything here is assuming you’re looking for full ride.

Whats needed:

- Number of colleges

- Colleges with specified parameters (Their specific weight, also whether you pass their academic triage, probability of acceptance) in a json file (acceptance rate is used for reference)

- Number of trials

- Number of colleges when decay starts

- Applicant info

Pipeline:

- Validate Data (College and config information)

- Ingesting Data

- Running Individual College chances

- Running Portfolio Chances

- Outputting Calculation

Notes:

- When conducting individual probabilities is they are in the same cluster then you update event success according to the past event result. Define the definitions of the clusters, make it only

- Consider adding a logistic link

- Holistic Admission are chaotic noise is relatively high than pure college selectivity

- Colleges in the same cluster are correlated

- Beta is a local walk not global, its trial specific

Formulae:

College Formula

$$

C_{\text{weight}}= w_{\text{gpa}} + w_{\text{SAT}} + w_{\text{essay}} + w_{\text{EC's}} + w_{\text{rec}} + w_{\text{Awards}}

\\

w_j \ge 0, \quad \sum_jw_j \approx 1


$$

$\text{Where: }

\\

C\_{\text{weight}}: \quad {\text{How the colleges weigh their decision out of 1.00}}

\\

w\_{\text{gpa}}: \quad \text{How the colleges weigh your GPA}

\\

w\_{\text{SAT}}: \quad \text{How the colleges weigh your SAT}

\\

w\_{\text{essay}}: \quad \text{How the colleges weigh your Essays}

\\

w\_{\text{EC's}}: \quad \text{How the colleges weigh your Extra-Curriculars}

\\

w\_{\text{Awards}}: \quad \text{How the colleges weigh your Awards}

\\

w\_{\text{rec}}: \quad \text{How the colleges weigh your Recommendation Letters}$

Conversion metric

$$

a_{\text{gpa}} = \frac{\text{(Unweighted GPA - 2.5})}{1.5}

\\

a_{\text{SAT}} = \frac{\text{SAT Score - 1000}}{600}

\\

a_{\text{GPA}}, a_{\text{SAT}} \in [0,1]


$$

$\text{Where: }

\\

a\_{\text{gpa}}: \quad \text{Converted GPA Score out of 1}

\\

a\_{\text{SAT}}: \quad \text{Converted SAT Score out of 1}

\\

a\_{\text{essay}}: \quad \text{Essay out of 1}

\\

a\_{\text{EC's}}: \quad \text{Extra-Curriculars out of 1}

\\

a\_{\text{Awards}}: \quad \text{Awards out of 1}

\\

a\_{\text{rec}}: \quad \text{Recommendation Letters out of 1} \\

\text{Note}: \quad \text{Since everything else is holisitic} \\ \text{the user enters an accurate and unbiased rating out of 1}$

Application Depreceation

$$

q(N)=\text{max}\left(0.5, 1-\lambda\cdot\text{max}(0, N-N_0)\right)


$$

$\text{Where}:

\\

q(N): \quad \text{Scalar Multiplier of Application Decay for N number of colleges}

\\

N_0: \quad \text{Number of colleges where effort starts affecting application}

\\

\lambda: \quad \text{Decay Rate}

\\

N: \quad \text{Number of Colleges you're applying to}$

Essay against Decay

$$

a_{\text{essay, eff}}= a_{\text{essay}}\cdot q(N)


$$

$\text{Where}:

\\

a\_{\text{essay, eff}}: \quad \text{Effective Essay, essay score calculated against Application decay}

\\

a\_{\text{essay}}: \quad \text{Essay score out of 1}

\\

q(N): \quad \text{Scalar Multiplier of Application Decay for N number of colleges}$

College Chances

$$

S(\beta)^{k}_c=T_c\cdot( \beta\cdot p_c\left[(w_{c,\text{gpa}}a_{\text{gpa}}) + (w_{c, \text{SAT}}a_{\text{SAT}}) + (w_{c, \text{essay}}a_{\text{essay, eff}}) + (w_{c, \text{EC's}}a_{\text{EC's}}) + (w_{c, \text{rec}}a_{\text{rec}}) + (w_{c, \text{Awards}}a_{\text{Awards}})\right] + \xi_c)

\\

S_c(\beta)\in [0,1]


$$

$\text{Where: }

\\

S(\beta)^{k}\_c: \quad \text{Estimated Competitivness Probability of Full ride at college c of index k}

\\

p_c: \quad \text{Full ride percentage published by college or estimated}

\\

a*{\text{gpa}}: \quad \text{Converted GPA Score out of 1}\\a*{\text{SAT}}: \quad \text{Converted SAT Score out of 1}\\a*{\text{essay, eff}}: \quad \text{Effective Essay, essay score calculated against Application decay}\\a*{\text{EC's}}: \quad \text{Extra-Curriculars out of 1}\\a*{\text{Awards}}: \quad \text{Awards out of 1}\\a*{\text{rec}}: \quad \text{Recommendation Letters out of 1}

\\

\xi_c: \quad \text{Noise Mixture of School Individual Noize, Enviroment Noise and} \\ \text{positive correlation of college c}

\\

\\

w\_{c, \text{gpa}}: \quad \text{How the colleges weigh your GPA}

\\

w\_{c, \text{SAT}}: \quad \text{How the colleges weigh your SAT}

\\

w\_{c, \text{essay}}: \quad \text{How the colleges weigh your Essays}

\\

w\_{c, \text{EC's}}: \quad \text{How the colleges weigh your Extra-Curriculars}

\\

T_c: \quad \text{Binary academic triage results}

\\

w\_{c, \text{Awards}}: \quad \text{How the colleges weigh your Awards}

\\

w\_{c, \text{rec}}: \quad \text{How the colleges weigh your Recommendation Letters}

\\

\beta: \quad \text{Cluster Specific Dynamic Beta, Likelyhood of success based on past events, default = 1, }

\\

\text{Note}: \quad \text{When analyzed everything is taken out of 1. GPA, SAT } \\ \text{etc… is converted to a out of 1 metric and} \ S_c \ \text{is calculated out of 1.}$

Portfolio Chances

$$

\hat P(\text{At least 1})=\frac{1}{T}\sum^T_{t=1}(\text{wins}_t\ge1) \\

\text{wins}_t= \sum_c \text{Bernoulli}(S(\beta)_{c}^{k})


$$

$\text{Where}:

\\

\hat P(\text{At least 1}): \quad \text{Probability of 1 full ride}

\\

T: \quad \text{Amount of Trials}

\\

\text{wins}\_t: \quad \text{Trial Wins of full ride college chances}

\\

S(\beta)^{k}\_c: \quad \text{Estimated Competitivness Probability of Full ride at college c of index k}

\\$

Gaussian Distribution

$$

f(X)=\frac{1}{\sigma \sqrt{2\pi}}\text{exp}\left(-\frac{(x-\mu)^2}{2\sigma^2}\right )


$$

$\text{Where:}

\\

f(X): \quad \text{Gaussian Distribution of a random vairable X}

\\

\sigma^2: \quad \text{Variance}

\\

\sigma: \quad \text{Standard Deviation}

\\

\mu: \quad \text{Mean}$

Noise

$$

\epsilon_c, u_i=\mathcal{N}{(0, \sigma^2)} \quad \text{, independently}

\\

\xi_c=\rho_i\cdot u_i +(1-\rho_i)\cdot \epsilon_c


$$

$\text{Where}:

\\

\xi_c: \quad \text{Noise Mixture of School Individual Noize, Enviroment Noise and} \\ \text{positive correlation of college c}

\\

\epsilon_c: \quad \text{College Specific Noice}

\\

u_i: \quad \text{Cluster Specific Enviroment Noise of c}

\\

\rho : \quad \text{Cluster Specific correlation strength}

\\

\mathcal{N}(0, \sigma^2): \quad \text{Guassian distribution of center 0, and variation of }\sigma^2$

Dynamic Beta

$$

\beta_k = \beta_{k, i(c)}

\\

\beta_{k}=\beta_{k-1}+\alpha\cdot(Y_c-S(\beta)_c^{k-1})

\\

0.5 \le \beta_k \le 1.3

\\

Y_c = \text{Bernoulli}(S(\beta)^k_c)

\\

Y_c\in\{0,1\}

\\

\text{Default } \beta_k = 1.0, \quad \text{Trials remain independent}


$$

$\text{Where}:

\\

\beta*k: \quad \text{Cluster Specific Dynamic Beta, Likelyhood of success based on }\\ \beta*{k-1} \text{and predicted }Y_c \text{ and }S_c

\\

S_c: \quad \text{College Application Strength for college c}

\\

Y_c: \quad \text{Binary estimated Full ride result}

\\

\alpha: \quad \text{Learning Step Rate}$

Academic Triage

$$

T_c=(\text{GPA}\ge \text{Colleges Minimum GPA})\wedge(\text{SAT}\ge\text{Colleges Minimum SAT})

\\

T_c\in\{0,1\}


$$

$\text{Where:}

\\

T_c: \quad \text{Binary Academic Triage Result, if } T_c = 0 \implies S_c = 0 \implies \text{ College Pais skipped, No trial conducted for college c}$

Percent of full ride

$$

p_c=P(\text{admit}_c)×P(\text{full ride∣admit})_c


$$

$\text{Where:}

\\

p_c: \quad \text{Probability of Full ride, when inputting in json file}$

Variables

$$

\text{Default }\beta: 1.00

\\

\text{Default }S_c: 0.5

\\

\text{Standard Deviation}(\sigma): 0.005

\\

\text{Mean}(\mu): 0

\\

\text{Maximum essay decay coefficient: } 0.5

\\

\beta \text{ Clip}(0.5, 1.3)

\\

\text{Increment Step }(\alpha): 0.05

\\

a_{\text{SAT}} = 0.5, \quad \text{If test optional}


$$

Personal Note:

I have changed the minimum gpa for NYUAD, ViniUni, Clark, DKU because they actually view academics them selves holistically and they wont even be considered in the monte as they will fail the academic triage (not in real life hopefully), because i have osme chance of passing th eacademic tiage in real life i will mimic that in the monte by decreasing their minimum gpa.

Calculation more direct pipeline.

- Check College weight sums, proper data types, file exists

- Convert actual gpa and sat, turn json into proper df

- calculate essay effective essay against decay

- Calculate S_c_k of college c of index k against beta, p, academic triage, noise, weighted sum then slamoed then stored

  - beta is calculated against default S_c, Y_c (bernoulli), and constant increment alpha

  - noise is calculated based on gausian distribution of college specific noise (random), cluster specific noise, cluster specific rho

- both P(At least 1) is calculuated based on bernoulli of newly calculated S_c

- Then you can calculate other external infromation

- **Need (Institutional Full-Need / Need-Based Aid):** Universities that meet demonstrated financial need for international students (need-aware or need-blind). Correlation comes from shared international aid budgets and financial-need evaluation.

- **Merit (Competitive Merit / Named Full-Ride Scholarships):** Merit scholarships or full-ride fellowships (e.g., Stamps, Presidential/Honors merit awards, KAIST/VinUni merit tracks). Correlation reflects competition among high-achieving/high-output applicants and merit pool caps.

- **Government (National / Bilateral Government Scholarships):** State-funded scholarships (e.g., MEXT, CSC, Türkiye Bursları, Stipendium Hungaricum). Correlation reflects country quotas, embassy/bilateral selection dynamics, and government funding rules.

- **Special (Mission-, Partner-, or Region-Specific Tracks):** Programs with distinct structural criteria or dedicated pipelines (e.g., Berea's work/low-income model, Mastercard Foundation partner cohorts, Bocconi's Nuovo Fiore Ethiopia track).
