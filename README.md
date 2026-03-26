# 🛢️ CRUDE EMPIRE — Williston Basin Edition

An immersive oil & gas upstream simulation game set in the Bakken. Build multi-well pads, drill horizontal wells, manage artificial lift, and grow your empire on a satellite-style map of North Dakota's Williston Basin — all in a single HTML file.

## 🎮 [Play Now →](https://ibambekov1.github.io/crude-empire/)

![Crude Empire Screenshot](https://img.shields.io/badge/Status-Live-brightgreen) ![Single File](https://img.shields.io/badge/Single_File-HTML-orange) ![No Dependencies](https://img.shields.io/badge/Dependencies-Zero-blue)

---

## 🗺️ The Map

A satellite-style rendering of the Williston Basin featuring:

- Prairie, grassland, scrubland, and badlands terrain
- Missouri River and Lake Sakakawea
- Real North Dakota towns — Williston, Watford City, Tioga, New Town, Dickinson, Minot, and more
- Township and section grid overlays
- Pan (drag) and zoom (scroll) navigation
- Double-click anywhere to place a new well pad

## ⛏️ Animated Equipment

Every piece of equipment is hand-drawn on the canvas and fully animated:

| Equipment | Animation |
|-----------|-----------|
| **Pumpjack** | Walking beam rocks, polished rod reciprocates, crank arm rotates, horse head bobs |
| **Drilling Rig** | Derrick with cross-braces, traveling block bounces, drill string moves, rotary table spins, rig lights glow |
| **Frac Spread** | Red pump trucks vibrate, pressure readout animates, iron manifold visible |
| **Flowback** | Separator with animated flare stack and flame |
| **Facilities** | Tank battery, separator, heater treater, pipeline tie-in |

## 🏗️ Multi-Well Pad Development

- Build pads with **1, 2, 3, 4, or 6 wells**
- Shared surface facilities — 30% marginal cost savings per additional well
- Choose your **formation target**:
  - **Middle Bakken** — Higher oil cut, standard cost
  - **Three Forks** — Higher GOR, 10% cheaper
- Select **lateral length**: 5,000 / 10,000 / 15,000 ft
  - Longer laterals = higher IP but higher cost

## 🔧 Artificial Lift

When natural flow declines, choose your lift method — each with different cost, efficiency, and OPEX impact:

| Lift Type | Install Cost | Best For | Map Visual |
|-----------|-------------|----------|------------|
| ⚙️ **Rod Pump** | $80–180K | Reliable, low-rate wells | Animated pumpjack |
| ⚡ **ESP** | $150–350K | High-rate wells | Electrical VSD box |
| 💨 **Gas Lift** | $200–400K | Gassy wells, low maintenance | Compressor + gas lines |

## 📊 Well Economics

- **Arps hyperbolic decline curves** with Bakken-specific b-factors and Di
- **Rising GOR** over well life (formation-dependent rate)
- **Increasing water cut** requiring disposal at $1.50/bbl
- **LOE** of $8–15/BOE (Bakken average)
- **5% severance tax** on revenue
- **Workovers** available after 6 months to restore production
- Commodity prices simulate month-to-month using **mean-reverting GBM**

## ⚠️ Random Events

Bakken-specific operational risks:

- 🔥 **Blowouts** — $1–5M, 3 months downtime
- ❄️ **Polar Vortex Freeze-Off** — All pad wells shut in
- 🌊 **Spring Breakup** — Road restrictions, no rig moves
- 🔩 **Stuck Pipe** — Fishing job or sidetrack, $300K–1.5M
- 💥 **Frac Hits** — Offset well communication
- 🏭 **Gas Plant Curtailment** — Hess Tioga at capacity
- 🧪 **Saltwater Spill** — NDIC remediation, $250K–2M
- ✅ **Outperforming Type Curve** — 35% production boost (the good kind)
- 💰 **Tax Incentive** — ND extraction tax holiday

## 🎮 How to Play

1. **Start** with $100,000,000
2. **Click + NEW PAD** or double-click the map to place a well pad
3. **Configure** — pick well count, formation, lateral length
4. **Start permitting** each well, then watch them progress through Drilling → Completing → Flowback → Producing
5. **Manage operations** — install artificial lift when decline hits, perform workovers
6. **Advance time** — click ▶ MONTH, ▶▶ 6MO, or ▶▶▶ YEAR
7. **Don't go bankrupt** — game over if cash drops below -$10M

## 🚀 Deploy

### GitHub Pages (recommended)
1. Fork or clone this repo
2. Go to **Settings → Pages → Source: main branch, / (root)**
3. Your game is live at `https://yourusername.github.io/crude-empire/`

### Local
Just open `index.html` in any browser. That's it.

## 🏗️ Tech Stack

- **Canvas 2D** — All map rendering, terrain, and equipment animations
- **Vanilla JavaScript** — Complete game engine, no frameworks
- **CSS3** — HUD, panels, animations
- **Zero dependencies** — Single file, no build step, no server needed

## 📁 Project Structure

```
crude-empire/
├── index.html    ← The entire game (single file)
└── README.md     ← You are here
```

## 📜 License

MIT — Fork it, mod it, drill it.

---

*Built for the love of the Bakken. Not financial advice. Drill baby drill.* 🛢️
