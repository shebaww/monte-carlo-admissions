# Monte-Carlo Admissions

A Monte Carlo simulator for estimating your probability of winning a **full-ride scholarship** across a portfolio of colleges and government scholarships. It models holistic admissions noise, correlated outcomes within scholarship clusters, academic triage, and essay quality decay — giving you a realistic picture of your odds and actionable advice on your college list.

---

## How It Works

The simulator runs thousands of independent trials. In each trial, every college on your list is evaluated in a randomized order. For each college, the simulator:

1. **Academic triage** — checks whether your GPA and SAT meet the college's minimum competitive threshold. If not, the college is skipped (`T_c = 0`).
2. **Computes a competitiveness score** `S_c` — a weighted sum of your normalized applicant stats, scaled by the college's published full-ride probability (`p_c`) and a dynamic beta.
3. **Draws a Bernoulli outcome** — `Y_c ~ Bernoulli(S_c)`, determining whether you "win" that trial for that college.
4. **Updates beta** — a cluster-specific dynamic beta adjusts based on whether past outcomes were above or below expectation, capturing momentum within a cluster.
5. **Applies correlated noise** — colleges in the same cluster share a common noise term (`ξ_c = ρ·u_i + (1-ρ)·ε_c`), reflecting real-world correlation (e.g., government scholarship committees move together).

After all trials, the simulator reports:

- **P(at least 1 full ride)** across your entire portfolio
- **Expected number of wins** per trial
- **Per-college win percentages** (bar chart)
- **Per-cluster win totals** (bar chart)
- **Actionable recommendations** to trim or expand your list

---

## Quickstart

### 1. Clone and install dependencies

```bash
git clone https://github.com/your-username/monte-carlo-admissions.git
cd monte-carlo-admissions
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

### 2. Set up your config files

Copy the templates and fill them in:

```bash
cp templates/config_template.yaml data/config.yaml
cp templates/colleges_template.json data/colleges.json
```

Edit `config.yaml` with your profile and `colleges.json` with your college list. See [Configuration](#configuration) below.

### 3. Run the simulator

```bash
python main.py
```

By default it looks for `templates/config_template.yaml` and `templates/colleges_template.json`. To use your own files:

```bash
python main.py --config data/config.yaml --colleges data/colleges.json --out outputs
```

**CLI arguments:**

| Argument     | Default                            | Description                     |
| ------------ | ---------------------------------- | ------------------------------- |
| `--config`   | `templates/config_template.yaml`   | Path to your YAML config file   |
| `--colleges` | `templates/colleges_template.json` | Path to your colleges JSON file |
| `--out`      | `outputs`                          | Directory where plots are saved |

---

## Configuration

### `config.yaml`

```yaml
config:
  trials: 10000 # Number of Monte Carlo trials
  sigma: 0.008 # Noise standard deviation
  alpha: 0.05 # Beta learning rate
  lambda: 0.03 # Essay decay rate per college beyond capacity_c
  capacity_c: 20 # Number of colleges before essay decay kicks in
  beta_min: 0.5 # Minimum beta clamp
  beta_max: 1.3 # Maximum beta clamp
  beta_default: 1.0 # Starting beta (trials are independent)
  mu: 0 # Noise mean
  seed: 42 # RNG seed for reproducibility

clusters:
  Need:
    rho: 0.45 # Cluster correlation strength (0.0 to 1.0)
  Merit:
    rho: 0.35
  Government:
    rho: 0.40
  Special:
    rho: 0.07

applicant:
  name: "Your Name"
  gpa: 3.55 # Raw GPA on a 4.0 scale
  sat: 1370 # Raw SAT out of 1600
  essay: 0.80 # Self-rating out of 1.0
  ecs: 0.70 # Extracurriculars out of 1.0
  rec: 0.85 # Recommendation letters out of 1.0
  awards: 0.63 # Awards/honors out of 1.0
```

GPA and SAT are automatically converted to a [0, 1] scale internally. All other applicant fields must be entered as values between 0.0 and 1.0.

**Rating guide (essay, ECs, rec, awards):**

| Range   | Description                                                                      |
| ------- | -------------------------------------------------------------------------------- |
| 0.0–0.3 | Weak — generic participation, basic essay                                        |
| 0.4–0.6 | Average/Good — club leadership, local awards, solid essay                        |
| 0.7–0.8 | Strong — state/national leadership, unique essay, strong rec                     |
| 0.9–1.0 | Elite — international olympiads, founded major initiatives, exceptional research |

### `colleges.json`

Each key is the college/scholarship name. All weights must sum to approximately 1.0.

```json
{
  "Example University (Full Ride Program)": {
    "w_gpa": 0.3,
    "w_sat": 0.2,
    "w_essay": 0.2,
    "w_ecs": 0.15,
    "w_rec": 0.05,
    "w_awards": 0.1,
    "min_sat": 1350,
    "min_gpa": 3.5,
    "test_optionality": true,
    "full_ride_perc": 0.03,
    "submitting_sat": true,
    "cluster": "Merit"
  }
}
```

| Field              | Type   | Description                                            |
| ------------------ | ------ | ------------------------------------------------------ | ------- |
| `w_gpa`            | float  | College's weight on GPA (must sum to ~1.0 with others) |
| `w_sat`            | float  | College's weight on SAT                                |
| `w_essay`          | float  | College's weight on essays                             |
| `w_ecs`            | float  | College's weight on extracurriculars                   |
| `w_rec`            | float  | College's weight on recommendation letters             |
| `w_awards`         | float  | College's weight on awards/honors                      |
| `min_gpa`          | float  | Competitive minimum GPA (4.0 scale)                    |
| `min_sat`          | int    | Competitive minimum SAT (1600 scale)                   |
| `test_optionality` | bool   | Whether the school is test-optional                    |
| `full_ride_perc`   | float  | `P(Admit) × P(Full Ride                                | Admit)` |
| `submitting_sat`   | bool   | Whether you are submitting your SAT to this school     |
| `cluster`          | string | Must match a cluster name defined in `config.yaml`     |

**Computing `full_ride_perc`:** Use the international acceptance rate if available, otherwise apply a 0.8× penalty on the overall rate for international applicants. Multiply by the proportion of admitted students who receive a full ride (tuition + stipend). For government scholarships where admission = full ride, `full_ride_perc = P(Admit)`. Be conservative — round down to the nearest 0.005.

**Minimum GPA/SAT:** These are not official cutoffs — they represent the lowest stats at which an admissions officer would still consider your application. This determines whether your application passes academic triage.

---

## Output

After the run, the simulator prints a summary and saves plots to your output directory:

```
Expected Wins (Average Full Rides per Trial): 0.47
P(At least 1 Full Ride): 38.21%

--- Colleges to Consider Removing ---
[Triage Failure] Emory University (Woodruff Scholarship): Failed academic triage 100.0% of the time.
[Low ROI] University of Richmond (Richmond Scholars Program): Win rate is under 0.9% (0.21%), draining essay effort.

--- Portfolio Size Recommendation ---
You do not necessarily need to increase your list based on current odds.
```

**Plots saved to `outputs/`:**

- `college_wins.png` — horizontal bar chart of win probability per college, sorted descending
- `cluster_wins.png` — bar chart of total wins per cluster across all trials

---

## Using AI to Build Your Input Files

The `prompts/` directory contains two prompts you can paste into an AI assistant (ChatGPT, Claude, etc.) to generate your input files accurately.

### Generate `colleges.json`

Paste `prompts/generate_colleges_prompt.md` into your AI and attach your college list. The AI will research each program and produce the full JSON — including weights, minimum thresholds, full-ride percentages, and cluster assignments.

### Generate `config.yaml`

Paste `prompts/generate_config_prompt.md` into your AI and provide your raw stats (GPA, SAT, resume/activities list). The AI will rate your holistic profile, assign clusters, and produce a valid `config.yaml`.

Using these prompts ensures the numbers going into the simulator are grounded in research rather than guesses.

---

## Mathematical Model

Full derivations are in [`docs/methodology.md`](docs/methodology.md). Here is a summary.

### Score normalization

```
a_gpa  = (GPA - 2.5) / 1.5
a_sat  = (SAT - 1000) / 600
```

GPA and SAT are mapped to [0, 1]. All other inputs are entered directly as [0, 1] values.

### Essay decay

When applying to more than `capacity_c` schools, essay quality degrades:

```
q(N) = max(0.5, 1 - λ · max(0, N - N₀))
a_essay_eff = a_essay · q(N)
```

### Competitiveness score

```
S_c = clamp(T_c · (β · p_c · weighted_sum + ξ_c), 0, 1)
```

where `weighted_sum = w_gpa·a_gpa + w_sat·a_sat + w_essay·a_essay_eff + w_ecs·a_ecs + w_rec·a_rec + w_awards·a_awards`

### Academic triage

```
T_c = 1 if GPA ≥ min_gpa AND (SAT ≥ min_sat OR test_optionality)
T_c = 0 otherwise  →  S_c = 0, college is skipped
```

### Correlated noise

```
ξ_c = ρ_i · u_i + (1 - ρ_i) · ε_c
ε_c, u_i ~ N(0, σ²)  independently
```

Colleges in the same cluster share `u_i`, creating realistic correlated outcomes.

### Dynamic beta

Beta tracks whether outcomes in a cluster are running above or below expectation:

```
β_k = β_{k-1} + α · (Y_c - S_c)
β_k ∈ [0.5, 1.3]
```

Beta resets at the start of each trial, keeping trials independent.

### Portfolio probability

```
P̂(at least 1) = (1/T) · Σ_t 𝟙[wins_t ≥ 1]
wins_t = Σ_c Bernoulli(S_c)
```

---

## Project Structure

```
monte-carlo-admissions/
├── main.py                        # Entry point, CLI parsing
├── requirements.txt               # Dependencies
├── src/
│   ├── simulator.py               # Core Monte Carlo engine (Operations class)
│   └── loader.py                  # Data ingestion and normalization (DataIngestor class)
├── data/
│   ├── config.yaml                # Active applicant config (gitignored)
│   └── colleges.json              # Active college list (gitignored)
├── templates/
│   ├── config_template.yaml       # Starter config template
│   └── colleges_template.json     # Starter colleges template
├── prompts/
│   ├── generate_colleges_prompt.md  # AI prompt for building colleges.json
│   └── generate_config_prompt.md   # AI prompt for building config.yaml
├── docs/
│   └── methodology.md             # Full mathematical documentation
└── outputs/
    ├── college_wins.png            # Per-college win probability chart
    └── cluster_wins.png            # Per-cluster win totals chart
```

---

## Dependencies

- Python 3.10+
- `numpy`
- `pandas`
- `pyyaml`
- `matplotlib`
- `scipy`

Install with:

```bash
pip install -r requirements.txt
```

---

## Limitations and Assumptions

- This model is heuristic and can't be backtested, it's only purpose is to guide build the strongest college list you can based on statistics. It is not a final predictor of your admission results. It is a tool, use it apporpriately. This model is **only** accurate if your inputs are make sure to input unbiased and accurate information.
- The model is calibrated for **full rides only** (tuition + stipend). Partial scholarships are not modeled.
- College weights (`w_gpa`, `w_essay`, etc.) are estimates based on publicly available information — no simulator can replicate a real admissions committee.
- `full_ride_perc` is a rough estimate. Small errors here compound significantly, so research each program carefully.
- Dynamic beta captures within-trial correlation between colleges in the same cluster, not across trials.
- The noise term is small by design (`σ = 0.008`). The model represents systematic competitiveness, not lottery-level randomness.

---

## Improvements

- Add logistic Link
- Other Functions to estimate other parts of the application like P(At least 2)
- Code architecture in architecture.md
- Tutorials
- How to guides
- References
- Explanation
- Citation
- Effort variable and function, either calculated by supplemental amount, or just effort variable
- Applying through where? (Should be in effort) calculates if common app or coalition is greater than maximum

## License

MIT License. See [`LICENSE`](LICENSE).
