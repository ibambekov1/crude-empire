"""
Crude Empire - Oil & Gas Tycoon Simulator
Core game engine with realistic well economics
"""

import random
import math
import time
from dataclasses import dataclass, field
from typing import List, Optional, Dict
from enum import Enum
import json


class WellStatus(Enum):
    LEASE_ACQUIRED = "Lease Acquired"
    PERMITTING = "Permitting"
    DRILLING = "Drilling"
    COMPLETING = "Completing"
    FLOWBACK = "Flowback"
    PRODUCING = "Producing"
    SHUT_IN = "Shut-In"
    PLUGGED = "Plugged & Abandoned"


class LiftType(Enum):
    NATURAL_FLOW = "Natural Flow"
    ROD_PUMP = "Rod Pump"
    ESP = "ESP"
    GAS_LIFT = "Gas Lift"
    PLUNGER_LIFT = "Plunger Lift"


class BasinName(Enum):
    PERMIAN = "Permian Basin"
    BAKKEN = "Bakken"
    EAGLE_FORD = "Eagle Ford"
    DJ_BASIN = "DJ Basin"
    SCOOP_STACK = "SCOOP/STACK"


@dataclass
class BasinConfig:
    name: BasinName
    description: str
    lease_cost_per_acre: tuple  # (min, max)
    drill_cost: tuple  # (min, max) per well
    completion_cost: tuple  # (min, max) per well
    facility_cost: tuple  # (min, max)
    # Type curve parameters (Arps hyperbolic)
    ip_oil: tuple  # Initial production oil (bbl/day) range
    ip_gas: tuple  # Initial production gas (mcf/day) range
    b_factor: tuple  # Arps b-factor range
    di: tuple  # Initial decline rate range (annual)
    initial_gor: tuple  # Initial GOR (scf/bbl) range
    gor_increase_rate: float  # Annual GOR increase factor
    water_cut_initial: tuple  # Initial water cut range
    water_cut_increase: float  # Annual water cut increase
    typical_lateral_length: int  # feet
    loe_per_boe: tuple  # LOE cost range per BOE
    drilling_days: tuple  # days range
    completion_days: tuple  # days range
    facility_days: tuple  # days range
    event_risk_factor: float  # 0-1, higher = more risky


BASIN_CONFIGS = {
    BasinName.PERMIAN: BasinConfig(
        name=BasinName.PERMIAN,
        description="Premier unconventional play. High IP, excellent economics. Wolfcamp & Bone Spring targets.",
        lease_cost_per_acre=(8000, 25000),
        drill_cost=(3_500_000, 6_000_000),
        completion_cost=(4_000_000, 8_000_000),
        facility_cost=(500_000, 1_500_000),
        ip_oil=(800, 2200),
        ip_gas=(1500, 5000),
        b_factor=(1.0, 1.6),
        di=(0.65, 0.85),
        initial_gor=(800, 2500),
        gor_increase_rate=0.15,
        water_cut_initial=(0.15, 0.40),
        water_cut_increase=0.08,
        typical_lateral_length=10000,
        loe_per_boe=(6.0, 12.0),
        drilling_days=(12, 25),
        completion_days=(14, 30),
        facility_days=(20, 45),
        event_risk_factor=0.15,
    ),
    BasinName.BAKKEN: BasinConfig(
        name=BasinName.BAKKEN,
        description="Mature Williston Basin play. Strong oil cut, harsh winters. Middle Bakken & Three Forks.",
        lease_cost_per_acre=(3000, 12000),
        drill_cost=(4_000_000, 7_000_000),
        completion_cost=(3_500_000, 6_500_000),
        facility_cost=(600_000, 1_800_000),
        ip_oil=(600, 1800),
        ip_gas=(800, 2500),
        b_factor=(0.8, 1.4),
        di=(0.60, 0.80),
        initial_gor=(600, 1800),
        gor_increase_rate=0.12,
        water_cut_initial=(0.20, 0.50),
        water_cut_increase=0.10,
        typical_lateral_length=9500,
        loe_per_boe=(8.0, 15.0),
        drilling_days=(15, 30),
        completion_days=(12, 25),
        facility_days=(25, 50),
        event_risk_factor=0.20,
    ),
    BasinName.EAGLE_FORD: BasinConfig(
        name=BasinName.EAGLE_FORD,
        description="South Texas play with oil, condensate & gas windows. Excellent rock quality.",
        lease_cost_per_acre=(5000, 18000),
        drill_cost=(3_000_000, 5_500_000),
        completion_cost=(3_500_000, 7_000_000),
        facility_cost=(400_000, 1_200_000),
        ip_oil=(700, 2000),
        ip_gas=(2000, 8000),
        b_factor=(0.9, 1.5),
        di=(0.70, 0.90),
        initial_gor=(1000, 4000),
        gor_increase_rate=0.20,
        water_cut_initial=(0.10, 0.35),
        water_cut_increase=0.06,
        typical_lateral_length=7500,
        loe_per_boe=(5.0, 10.0),
        drilling_days=(10, 20),
        completion_days=(10, 22),
        facility_days=(15, 35),
        event_risk_factor=0.12,
    ),
    BasinName.DJ_BASIN: BasinConfig(
        name=BasinName.DJ_BASIN,
        description="Colorado Niobrara & Codell play. Waxy crude, strict regulations. Solid returns.",
        lease_cost_per_acre=(4000, 15000),
        drill_cost=(2_800_000, 5_000_000),
        completion_cost=(3_000_000, 6_000_000),
        facility_cost=(450_000, 1_300_000),
        ip_oil=(500, 1400),
        ip_gas=(1000, 3500),
        b_factor=(0.9, 1.3),
        di=(0.55, 0.75),
        initial_gor=(700, 2200),
        gor_increase_rate=0.10,
        water_cut_initial=(0.15, 0.45),
        water_cut_increase=0.09,
        typical_lateral_length=8000,
        loe_per_boe=(7.0, 13.0),
        drilling_days=(12, 22),
        completion_days=(12, 24),
        facility_days=(20, 40),
        event_risk_factor=0.18,
    ),
    BasinName.SCOOP_STACK: BasinConfig(
        name=BasinName.SCOOP_STACK,
        description="Oklahoma's Anadarko Basin. High GOR, gassy wells. Woodford & Meramec targets.",
        lease_cost_per_acre=(3000, 10000),
        drill_cost=(3_200_000, 5_500_000),
        completion_cost=(3_500_000, 6_500_000),
        facility_cost=(500_000, 1_400_000),
        ip_oil=(400, 1200),
        ip_gas=(3000, 10000),
        b_factor=(0.8, 1.4),
        di=(0.55, 0.78),
        initial_gor=(2000, 8000),
        gor_increase_rate=0.18,
        water_cut_initial=(0.10, 0.30),
        water_cut_increase=0.05,
        typical_lateral_length=9000,
        loe_per_boe=(5.5, 11.0),
        drilling_days=(14, 28),
        completion_days=(14, 28),
        facility_days=(22, 45),
        event_risk_factor=0.14,
    ),
}


@dataclass
class Well:
    id: str
    name: str
    basin: BasinName
    status: WellStatus
    lease_acres: int
    lease_cost: float
    drill_cost: float
    completion_cost: float
    facility_cost: float
    # Type curve params (set at completion)
    ip_oil: float = 0.0
    ip_gas: float = 0.0
    b_factor: float = 1.2
    di: float = 0.72
    gor: float = 1000.0
    gor_increase_rate: float = 0.15
    water_cut: float = 0.25
    water_cut_increase: float = 0.08
    loe_per_boe: float = 8.0
    # Artificial lift
    lift_type: LiftType = LiftType.NATURAL_FLOW
    lift_install_cost: float = 0.0
    # Production tracking
    months_online: int = 0
    cumulative_oil: float = 0.0
    cumulative_gas: float = 0.0
    cumulative_water: float = 0.0
    cumulative_revenue: float = 0.0
    cumulative_opex: float = 0.0
    current_oil_rate: float = 0.0
    current_gas_rate: float = 0.0
    current_water_rate: float = 0.0
    # Timeline tracking
    days_in_current_phase: int = 0
    days_required_current_phase: int = 0
    # Workover tracking
    last_workover_month: int = 0
    workover_count: int = 0

    @property
    def total_capex(self):
        return self.lease_cost + self.drill_cost + self.completion_cost + self.facility_cost + self.lift_install_cost

    @property
    def net_revenue(self):
        return self.cumulative_revenue - self.cumulative_opex

    def get_decline_rate(self, months: int) -> float:
        """Arps hyperbolic decline: q(t) = qi / (1 + b * Di * t)^(1/b)"""
        t = months
        denominator = (1 + self.b_factor * self.di * (t / 12)) ** (1 / self.b_factor)
        return max(1.0 / denominator, 0.05)  # Floor at 5% of IP

    def calculate_monthly_production(self) -> dict:
        """Calculate current month production volumes"""
        if self.status != WellStatus.PRODUCING:
            return {"oil": 0, "gas": 0, "water": 0}

        decline_factor = self.get_decline_rate(self.months_online)

        # Oil rate with decline
        oil_rate = self.ip_oil * decline_factor  # bbl/day

        # GOR increases over time
        current_gor = self.gor * (1 + self.gor_increase_rate * (self.months_online / 12))
        gas_rate = oil_rate * current_gor / 1000  # mcf/day

        # Water cut increases over time
        current_wc = min(self.water_cut + self.water_cut_increase * (self.months_online / 12), 0.95)
        # Total fluid = oil / (1 - water_cut)
        total_fluid = oil_rate / max(1 - current_wc, 0.05)
        water_rate = total_fluid - oil_rate  # bbl/day

        # Monthly volumes (30.4 days)
        days = 30.4
        self.current_oil_rate = oil_rate
        self.current_gas_rate = gas_rate
        self.current_water_rate = water_rate

        return {
            "oil": oil_rate * days,
            "gas": gas_rate * days,
            "water": water_rate * days,
            "oil_rate": oil_rate,
            "gas_rate": gas_rate,
            "water_rate": water_rate,
            "decline_factor": decline_factor,
            "current_gor": current_gor,
            "current_wc": current_wc,
        }

    def needs_artificial_lift(self) -> Optional[LiftType]:
        """Check if well needs artificial lift based on production"""
        if self.lift_type != LiftType.NATURAL_FLOW:
            return None
        if self.status != WellStatus.PRODUCING:
            return None
        # Typically after natural flow declines significantly
        decline = self.get_decline_rate(self.months_online)
        if decline < 0.35:
            # Recommend based on well characteristics
            if self.current_gas_rate > 500:
                return LiftType.GAS_LIFT
            elif self.current_oil_rate < 50:
                return LiftType.PLUNGER_LIFT
            elif self.current_oil_rate < 200:
                return LiftType.ROD_PUMP
            else:
                return LiftType.ESP
        return None


LIFT_COSTS = {
    LiftType.ROD_PUMP: (80_000, 180_000),
    LiftType.ESP: (150_000, 350_000),
    LiftType.GAS_LIFT: (200_000, 400_000),
    LiftType.PLUNGER_LIFT: (30_000, 80_000),
}

LIFT_EFFICIENCY = {
    LiftType.NATURAL_FLOW: 1.0,
    LiftType.ROD_PUMP: 0.90,
    LiftType.ESP: 0.95,
    LiftType.GAS_LIFT: 0.92,
    LiftType.PLUNGER_LIFT: 0.85,
}


@dataclass
class RandomEvent:
    name: str
    description: str
    category: str  # "operational", "weather", "regulatory", "market"
    cost: float = 0.0
    production_impact: float = 1.0  # multiplier
    duration_months: int = 0
    affects_well_id: Optional[str] = None


POSSIBLE_EVENTS = [
    {
        "name": "Wellbore Integrity Issue",
        "description": "Casing leak detected. Workover required.",
        "category": "operational",
        "cost_range": (200_000, 800_000),
        "production_impact": 0.0,
        "duration": 2,
        "probability": 0.03,
    },
    {
        "name": "Surface Equipment Failure",
        "description": "Separator malfunction. Production curtailed while repairs are made.",
        "category": "operational",
        "cost_range": (25_000, 150_000),
        "production_impact": 0.3,
        "duration": 1,
        "probability": 0.06,
    },
    {
        "name": "Blowout During Drilling",
        "description": "Lost well control! Emergency response activated.",
        "category": "operational",
        "cost_range": (1_000_000, 5_000_000),
        "production_impact": 0.0,
        "duration": 3,
        "probability": 0.008,
    },
    {
        "name": "Severe Winter Storm",
        "description": "Freeze-off conditions. All wells in basin shut in temporarily.",
        "category": "weather",
        "cost_range": (50_000, 300_000),
        "production_impact": 0.0,
        "duration": 1,
        "probability": 0.04,
    },
    {
        "name": "Hurricane Season",
        "description": "Gulf Coast operations impacted by tropical storm.",
        "category": "weather",
        "cost_range": (100_000, 500_000),
        "production_impact": 0.2,
        "duration": 1,
        "probability": 0.03,
    },
    {
        "name": "Regulatory Inspection",
        "description": "State regulator conducting site inspection. Minor compliance issues found.",
        "category": "regulatory",
        "cost_range": (10_000, 100_000),
        "production_impact": 1.0,
        "duration": 0,
        "probability": 0.08,
    },
    {
        "name": "Environmental Violation",
        "description": "Spill reported. Remediation and fine required.",
        "category": "regulatory",
        "cost_range": (200_000, 1_500_000),
        "production_impact": 0.5,
        "duration": 2,
        "probability": 0.02,
    },
    {
        "name": "Frac Hit on Offset Well",
        "description": "Communication with nearby operator's well during completions.",
        "category": "operational",
        "cost_range": (100_000, 600_000),
        "production_impact": 0.7,
        "duration": 1,
        "probability": 0.05,
    },
    {
        "name": "Pipeline Curtailment",
        "description": "Midstream capacity constraints. Gas production curtailed.",
        "category": "operational",
        "cost_range": (0, 50_000),
        "production_impact": 0.6,
        "duration": 2,
        "probability": 0.04,
    },
    {
        "name": "Stuck Pipe",
        "description": "Drill string stuck during drilling operations. Fishing job required.",
        "category": "operational",
        "cost_range": (300_000, 1_200_000),
        "production_impact": 1.0,
        "duration": 1,
        "probability": 0.04,
    },
    {
        "name": "Water Disposal Issue",
        "description": "SWD well capacity issue. Must truck water at higher cost.",
        "category": "operational",
        "cost_range": (50_000, 250_000),
        "production_impact": 0.9,
        "duration": 3,
        "probability": 0.05,
    },
    {
        "name": "Seismicity Moratorium",
        "description": "Induced seismicity concerns. Injection operations suspended in area.",
        "category": "regulatory",
        "cost_range": (100_000, 400_000),
        "production_impact": 0.8,
        "duration": 3,
        "probability": 0.02,
    },
    {
        "name": "Bonus Production",
        "description": "Well outperforming type curve! Better-than-expected reservoir quality.",
        "category": "operational",
        "cost_range": (0, 0),
        "production_impact": 1.3,
        "duration": 6,
        "probability": 0.06,
    },
    {
        "name": "Tax Incentive",
        "description": "State tax holiday on new completions announced.",
        "category": "regulatory",
        "cost_range": (-200_000, -50_000),  # Negative = money back
        "production_impact": 1.0,
        "duration": 0,
        "probability": 0.03,
    },
]


@dataclass
class GameState:
    cash: float = 10_000_000.0
    wells: List[Well] = field(default_factory=list)
    month: int = 0
    year: int = 2026
    current_month_name: str = "January"
    total_revenue: float = 0.0
    total_opex: float = 0.0
    total_capex: float = 0.0
    wti_price: float = 70.0
    gas_price: float = 3.50
    active_events: List[RandomEvent] = field(default_factory=list)
    event_log: List[dict] = field(default_factory=list)
    monthly_history: List[dict] = field(default_factory=list)
    game_over: bool = False
    game_speed: float = 1.0  # seconds per tick
    well_counter: int = 0
    paused: bool = False

    MONTH_NAMES = [
        "January", "February", "March", "April", "May", "June",
        "July", "August", "September", "October", "November", "December"
    ]

    @property
    def total_daily_oil(self):
        return sum(w.current_oil_rate for w in self.wells if w.status == WellStatus.PRODUCING)

    @property
    def total_daily_gas(self):
        return sum(w.current_gas_rate for w in self.wells if w.status == WellStatus.PRODUCING)

    @property
    def portfolio_value(self):
        """Estimate total portfolio value: cash + PV of future production"""
        pv = self.cash
        for w in self.wells:
            if w.status == WellStatus.PRODUCING:
                # Simple PV10 estimate: ~24 months of current production
                monthly_rev = (w.current_oil_rate * 30.4 * self.wti_price +
                               w.current_gas_rate * 30.4 * self.gas_price)
                pv += monthly_rev * 18  # rough PV multiplier
            elif w.status in (WellStatus.DRILLING, WellStatus.COMPLETING, WellStatus.PERMITTING):
                pv += w.total_capex * 0.5  # WIP value
        return pv

    def next_well_id(self):
        self.well_counter += 1
        return f"W-{self.well_counter:03d}"

    def advance_month(self):
        """Advance game by one month"""
        self.month += 1
        month_idx = (self.month - 1) % 12
        self.current_month_name = self.MONTH_NAMES[month_idx]
        if month_idx == 0 and self.month > 1:
            self.year += 1

        monthly_revenue = 0.0
        monthly_opex = 0.0
        monthly_oil = 0.0
        monthly_gas = 0.0

        # Process each well
        for well in self.wells:
            # Advance phases
            if well.status in (WellStatus.PERMITTING, WellStatus.DRILLING,
                               WellStatus.COMPLETING, WellStatus.FLOWBACK):
                well.days_in_current_phase += 30
                if well.days_in_current_phase >= well.days_required_current_phase:
                    self._advance_well_phase(well)

            # Production
            if well.status == WellStatus.PRODUCING:
                # Check for event impacts
                event_multiplier = 1.0
                for event in self.active_events:
                    if event.affects_well_id == well.id or event.affects_well_id == "ALL":
                        event_multiplier *= event.production_impact

                prod = well.calculate_monthly_production()
                oil_vol = prod["oil"] * event_multiplier
                gas_vol = prod["gas"] * event_multiplier
                water_vol = prod["water"]

                well.cumulative_oil += oil_vol
                well.cumulative_gas += gas_vol
                well.cumulative_water += water_vol
                well.months_online += 1

                # Revenue
                oil_rev = oil_vol * self.wti_price
                gas_rev = gas_vol * self.gas_price
                rev = oil_rev + gas_rev
                well.cumulative_revenue += rev
                monthly_revenue += rev

                # OPEX
                boe = oil_vol + gas_vol / 6  # 6:1 conversion
                opex = boe * well.loe_per_boe
                # Water disposal cost
                opex += water_vol * 1.50  # $1.50/bbl disposal
                # Severance tax (~5%)
                opex += rev * 0.05
                well.cumulative_opex += opex
                monthly_opex += opex

                monthly_oil += oil_vol
                monthly_gas += gas_vol

        # Apply costs
        self.cash += monthly_revenue - monthly_opex
        self.total_revenue += monthly_revenue
        self.total_opex += monthly_opex

        # Process active events
        remaining_events = []
        for event in self.active_events:
            event.duration_months -= 1
            if event.duration_months > 0:
                remaining_events.append(event)
        self.active_events = remaining_events

        # Random events
        self._check_random_events()

        # Record history
        self.monthly_history.append({
            "month": self.month,
            "label": f"{self.current_month_name} {self.year}",
            "cash": self.cash,
            "revenue": monthly_revenue,
            "opex": monthly_opex,
            "oil_production": monthly_oil,
            "gas_production": monthly_gas,
            "wti_price": self.wti_price,
            "gas_price": self.gas_price,
            "portfolio_value": self.portfolio_value,
            "well_count": len([w for w in self.wells if w.status == WellStatus.PRODUCING]),
        })

        # Game over check
        if self.cash < -5_000_000:
            self.game_over = True

    def _advance_well_phase(self, well: Well):
        config = BASIN_CONFIGS[well.basin]
        if well.status == WellStatus.PERMITTING:
            well.status = WellStatus.DRILLING
            well.days_in_current_phase = 0
            well.days_required_current_phase = random.randint(*config.drilling_days)
            self.cash -= well.drill_cost
            self.total_capex += well.drill_cost
        elif well.status == WellStatus.DRILLING:
            well.status = WellStatus.COMPLETING
            well.days_in_current_phase = 0
            well.days_required_current_phase = random.randint(*config.completion_days)
            self.cash -= well.completion_cost
            self.total_capex += well.completion_cost
        elif well.status == WellStatus.COMPLETING:
            well.status = WellStatus.FLOWBACK
            well.days_in_current_phase = 0
            well.days_required_current_phase = random.randint(7, 21)
            self.cash -= well.facility_cost
            self.total_capex += well.facility_cost
            # Set production parameters
            well.ip_oil = random.uniform(*config.ip_oil)
            well.ip_gas = random.uniform(*config.ip_gas)
            well.b_factor = random.uniform(*config.b_factor)
            well.di = random.uniform(*config.di)
            well.gor = random.uniform(*config.initial_gor)
            well.gor_increase_rate = config.gor_increase_rate
            well.water_cut = random.uniform(*config.water_cut_initial)
            well.water_cut_increase = config.water_cut_increase
            well.loe_per_boe = random.uniform(*config.loe_per_boe)
        elif well.status == WellStatus.FLOWBACK:
            well.status = WellStatus.PRODUCING
            well.days_in_current_phase = 0

    def _check_random_events(self):
        """Check for random events each month"""
        for well in self.wells:
            if well.status not in (WellStatus.PRODUCING, WellStatus.DRILLING, WellStatus.COMPLETING):
                continue
            config = BASIN_CONFIGS[well.basin]
            for event_template in POSSIBLE_EVENTS:
                prob = event_template["probability"] * config.event_risk_factor / 0.15
                if random.random() < prob:
                    cost = random.uniform(*event_template["cost_range"])
                    event = RandomEvent(
                        name=event_template["name"],
                        description=event_template["description"],
                        category=event_template["category"],
                        cost=cost,
                        production_impact=event_template["production_impact"],
                        duration_months=event_template["duration"],
                        affects_well_id=well.id,
                    )
                    self.active_events.append(event)
                    self.cash -= cost
                    self.event_log.append({
                        "month": self.month,
                        "label": f"{self.current_month_name} {self.year}",
                        "well": well.name,
                        "event": event.name,
                        "description": event.description,
                        "cost": cost,
                        "category": event.category,
                    })
                    break  # Max one event per well per month

    def buy_lease(self, basin: BasinName, well_name: str) -> Optional[Well]:
        config = BASIN_CONFIGS[basin]
        acres = random.randint(320, 1280)  # Quarter section to 2 sections
        cost_per_acre = random.uniform(*config.lease_cost_per_acre)
        lease_cost = acres * cost_per_acre

        if self.cash < lease_cost:
            return None

        well = Well(
            id=self.next_well_id(),
            name=well_name,
            basin=basin,
            status=WellStatus.LEASE_ACQUIRED,
            lease_acres=acres,
            lease_cost=lease_cost,
            drill_cost=random.uniform(*config.drill_cost),
            completion_cost=random.uniform(*config.completion_cost),
            facility_cost=random.uniform(*config.facility_cost),
        )

        self.cash -= lease_cost
        self.total_capex += lease_cost
        self.wells.append(well)
        return well

    def start_permitting(self, well_id: str) -> bool:
        well = next((w for w in self.wells if w.id == well_id), None)
        if not well or well.status != WellStatus.LEASE_ACQUIRED:
            return False
        config = BASIN_CONFIGS[well.basin]
        well.status = WellStatus.PERMITTING
        well.days_in_current_phase = 0
        well.days_required_current_phase = random.randint(15, 45)
        return True

    def install_artificial_lift(self, well_id: str, lift_type: LiftType) -> bool:
        well = next((w for w in self.wells if w.id == well_id), None)
        if not well or well.status != WellStatus.PRODUCING:
            return False
        cost = random.uniform(*LIFT_COSTS[lift_type])
        if self.cash < cost:
            return False
        well.lift_type = lift_type
        well.lift_install_cost = cost
        self.cash -= cost
        self.total_capex += cost
        # Slight production boost from lift
        well.ip_oil *= LIFT_EFFICIENCY[lift_type] * 1.15  # Net slight improvement
        return True

    def perform_workover(self, well_id: str) -> tuple:
        """Perform workover to restore production. Returns (success, cost)"""
        well = next((w for w in self.wells if w.id == well_id), None)
        if not well or well.status != WellStatus.PRODUCING:
            return False, 0
        cost = random.uniform(150_000, 600_000)
        if self.cash < cost:
            return False, cost
        self.cash -= cost
        self.total_capex += cost
        well.workover_count += 1
        well.last_workover_month = self.month
        # Reset decline partially
        improvement = random.uniform(1.1, 1.4)
        well.ip_oil *= improvement / (1 + well.workover_count * 0.1)
        return True, cost
