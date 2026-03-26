# 🛢️ CRUDE EMPIRE — Oil & Gas Tycoon Simulator

A realistic oil & gas upstream simulation game built with Python and Streamlit. Start with $10M, acquire leases across major US basins, drill and complete wells, build facilities, and manage production — all driven by live commodity prices.

![Python](https://img.shields.io/badge/Python-3.9+-blue?logo=python)
![Streamlit](https://img.shields.io/badge/Streamlit-1.30+-red?logo=streamlit)
![License](https://img.shields.io/badge/License-MIT-green)

## 🎮 Gameplay

1. **Acquire Leases** — Choose from 5 major basins (Permian, Bakken, Eagle Ford, DJ Basin, SCOOP/STACK)
2. **Drill & Complete** — Permit, drill, frac, and flowback your wells (with realistic timelines)
3. **Build Facilities** — Separator, tank battery, and pipeline tie-in
4. **Produce** — Watch revenue flow based on **live WTI and Henry Hub prices**
5. **Manage Operations** — Install artificial lift, perform workovers, handle random events
6. **Don't Go Bankrupt** — You lose if cash drops below -$5M

## 🔬 Realistic Well Economics

- **Arps Hyperbolic Decline Curves** with basin-specific type curve parameters
- **GOR Changes** — Gas-oil ratio increases over well life
- **Water Cut** — Rising water production requiring disposal
- **Artificial Lift Selection** — Rod Pump, ESP, Gas Lift, or Plunger Lift when natural flow declines
- **LOE, Severance Tax, and Water Disposal** costs
- **Workovers** to restore production

## 🗺️ Basin Profiles

| Basin | IP Oil (bbl/d) | IP Gas (mcf/d) | D&C Cost | Risk |
|-------|----------------|-----------------|----------|------|
| Permian | 800–2,200 | 1,500–5,000 | $7.5–14M | Medium |
| Bakken | 600–1,800 | 800–2,500 | $7.5–13.5M | High |
| Eagle Ford | 700–2,000 | 2,000–8,000 | $6.5–12.5M | Low |
| DJ Basin | 500–1,400 | 1,000–3,500 | $5.8–11M | Medium-High |
| SCOOP/STACK | 400–1,200 | 3,000–10,000 | $6.7–12M | Medium |

## ⚠️ Random Events

Blowouts, freeze-offs, frac hits, regulatory inspections, environmental violations, stuck pipe, pipeline curtailments, and more — each with basin-specific probabilities.

## 🚀 Quick Start

```bash
# Clone the repo
git clone https://github.com/YOUR_USERNAME/crude-empire.git
cd crude-empire

# Install dependencies
pip install -r requirements.txt

# Run the game
streamlit run app.py
```

## ☁️ Deploy to Streamlit Cloud

1. Push this repo to GitHub
2. Go to [share.streamlit.io](https://share.streamlit.io)
3. Connect your repo and set `app.py` as the main file
4. Deploy!

## 📊 Live Prices

The game fetches live WTI Crude and Henry Hub Natural Gas futures prices via Yahoo Finance at game start. During gameplay, prices simulate realistic month-to-month movements using mean-reverting geometric Brownian motion.

## 🏗️ Project Structure

```
crude-empire/
├── app.py              # Streamlit web application
├── game_engine.py      # Core game logic, well economics, events
├── price_fetcher.py    # Live commodity price fetching
├── requirements.txt    # Python dependencies
└── README.md           # This file
```

## 📜 License

MIT — Build, fork, and drill to your heart's content.

---

*Built for fun. Not financial advice. Drill baby drill.* 🛢️
