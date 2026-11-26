from __future__ import annotations

from http.server import HTTPServer, SimpleHTTPRequestHandler
import json
import math
import os
import sys
import webbrowser

BASE_DIR = os.path.dirname(os.path.abspath(__file__))


TOPOLOGY_UNIT_COUNTS = {
    "Single": 1,
    "Dual": 2,
    "Tri": 3,
    "Quad": 4,
    "In-Wheel": 4,
}

TOPOLOGY_LABELS = {
    "Single": "Single Motor (1x)",
    "Dual": "Dual Motor AWD (2x)",
    "Tri": "Tri Motor Vector (3x)",
    "Quad": "Quad Motor (4x)",
    "In-Wheel": "Hub Motors (4x Roda)",
}

MOTOR_TYPES = {
    "PMSM": {"label": "PMSM (Íman Permanente)", "tq": 1.00, "eff": 0.962, "fw_keep": 0.94, "low_slip": 1.00},
    "Induction AC": {"label": "Indução AC (Gaiola)", "tq": 0.88, "eff": 0.928, "fw_keep": 0.88, "low_slip": 0.88},
    "Axial Flux": {"label": "Fluxo Axial (Disco)", "tq": 1.24, "eff": 0.968, "fw_keep": 0.91, "low_slip": 1.00},
    "SynRM": {"label": "Relutância (EESM/SynRM)", "tq": 0.92, "eff": 0.945, "fw_keep": 0.86, "low_slip": 0.96},
}

WINDING_PROFILES = {
    "Hairpin Cobre": {"tq": 1.06, "eff": 1.012},
    "Distribuído Litz": {"tq": 1.00, "eff": 1.002},
    "Concentrado": {"tq": 0.97, "eff": 0.995},
    "Alumínio Leve": {"tq": 0.88, "eff": 0.980},
}

HOUSING_MATERIALS = (
    "Alumínio Fundido",
    "Alumínio Billet",
    "Magnésio",
    "Fibra de Carbono",
    "Titânio",
)

ROTOR_PROFILES = {
    "Neodímio N52 (V-Shape)": {"tq": 1.02, "eff": 1.000, "mass_mult": 1.00, "tip_lim": 205.0},
    "Halbach Array": {"tq": 1.12, "eff": 1.010, "mass_mult": 0.96, "tip_lim": 192.0},
    "Gaiola de Cobre": {"tq": 0.90, "eff": 0.970, "mass_mult": 1.12, "tip_lim": 185.0},
    "Rotor Bobinado (EESM)": {"tq": 0.95, "eff": 0.985, "mass_mult": 1.05, "tip_lim": 172.0},
    "Manga Carbono (Alta RPM)": {"tq": 1.08, "eff": 1.010, "mass_mult": 0.84, "tip_lim": 275.0},
}

COOLING_PROFILES = {
    "Ar (Aletas)": {"gain": 0.92, "cap_kw": 160.0},
    "Glicol (Camisa Água)": {"gain": 1.00, "cap_kw": 480.0},
    "Óleo Direto": {"gain": 1.04, "cap_kw": 650.0},
    "Imersão Dielétrica": {"gain": 1.07, "cap_kw": 880.0},
}

BEARING_TIP_BONUS = {
    "Aço Padrão": 0.0,
    "Cerâmica Si3N4": 20.0,
    "Magnético Ativo": 38.0,
}

FW_PROFILES = {
    "Conservador": {"fw": 0.84, "rpm_mult": 0.88},
    "Equilibrado": {"fw": 0.96, "rpm_mult": 1.04},
    "Agressivo": {"fw": 1.08, "rpm_mult": 1.24},
}

INVERTER_PROFILES = {
    "IGBT Silício": {"eff": 0.960, "gain": 0.93},
    "SiC Dual": {"eff": 0.986, "gain": 1.00},
    "SiC Racing 1200A": {"eff": 0.989, "gain": 1.08},
    "GaN Alta Freq.": {"eff": 0.992, "gain": 1.04},
}

BATTERY_PROFILES = {
    "LFP (LiFePO4)": {"crate": 4.5, "sag": 0.95},
    "NMC 811": {"crate": 6.8, "sag": 1.00},
    "NCA Performance": {"crate": 8.2, "sag": 1.03},
    "Estado Sólido": {"crate": 10.0, "sag": 1.06},
    "Supercondensador": {"crate": 14.0, "sag": 1.09},
}

DRIVE_MODE_PROFILES = {
    "Eco": {"tq": 0.72, "pwr": 0.70},
    "Normal": {"tq": 1.00, "pwr": 1.00},
    "Sport": {"tq": 1.08, "pwr": 1.12},
    "Ludicrous": {"tq": 1.22, "pwr": 1.28},
}

GEARBOX_PROFILES = {
    "Redutor 1V Direto": {"tq": 0.988, "hp": 0.988},
    "Caixa EV 2V": {"tq": 1.065, "hp": 0.982},
    "E-CVT Planetária": {"tq": 1.020, "hp": 0.965},
    "Coaxial Direto": {"tq": 0.995, "hp": 0.994},
}

DIFF_EFF_MAP = {
    "Diferencial Aberto": 0.994,
    "LSD Mecânico": 0.986,
    "e-LSD Vetorizado": 0.992,
    "Spool Direto": 0.996,
}

REGEN_KW_MAP = {
    "Desligada": 0,
    "Standard (50 kW)": 50,
    "One-Pedal Alta (180 kW)": 180,
    "Track Regen (Max)": 320,
}


def clamp_units_topology(topology: str) -> int:
    return TOPOLOGY_UNIT_COUNTS.get(topology, 1)


def _desenhar_unidade_ev_svg(cx: float, cy: float, r: float, is_axial: bool = False) -> str:
    outer_r = r * 1.12
    stator_r = r * 0.88
    rotor_r = r * 0.56
    stroke_col = "#38bdf8" if is_axial else "#818cf8"
    return (
        f'<circle cx="{cx:.1f}" cy="{cy:.1f}" r="{outer_r:.1f}" fill="#131924" stroke="#475569" stroke-width="2.2"/>'
        f'<circle cx="{cx:.1f}" cy="{cy:.1f}" r="{stator_r:.1f}" fill="#1e293b" stroke="{stroke_col}" stroke-width="2.6" stroke-dasharray="6 4"/>'
        f'<circle cx="{cx:.1f}" cy="{cy:.1f}" r="{rotor_r:.1f}" fill="#0f172a" stroke="#f97316" stroke-width="2.0"/>'
        f'<circle cx="{cx:.1f}" cy="{cy:.1f}" r="{r * 0.18:.1f}" fill="#e2e8f0"/>'
    )


def gerar_svg_motor_eletrico(
    topology: str = "Single",
    motor_type: str = "PMSM",
    voltage: int = 800,
) -> tuple[str, str]:
    topo = topology if topology in TOPOLOGY_UNIT_COUNTS else "Single"
    m_type = motor_type if motor_type in MOTOR_TYPES else "PMSM"
    units = clamp_units_topology(topo)
    is_axial = m_type == "Axial Flux" or topo == "In-Wheel"

    w, h = 540, 220
    elems: list[str] = []

    # Barramento HV + pack central
    hv_col = "#f97316"
    if topo == "Single":
        elems.append(
            f'<rect x="180" y="164" width="180" height="36" rx="7" fill="#111827" stroke="#334155" stroke-width="1.8"/>'
            f'<rect x="190" y="170" width="160" height="24" rx="4" fill="#1e293b" stroke="{hv_col}" stroke-width="1.5"/>'
            f'<text x="270" y="186" fill="#e2e8f0" font-size="10.5" font-weight="600" text-anchor="middle" font-family="JetBrains Mono, monospace">HV PACK {int(voltage)}V</text>'
            f'<line x1="270" y1="164" x2="270" y2="96" stroke="{hv_col}" stroke-width="3" stroke-linecap="round"/>'
        )
        coords = [(270.0, 92.0, 42.0)]
    else:
        elems.append(
            f'<rect x="170" y="74" width="200" height="72" rx="10" fill="#111827" stroke="#334155" stroke-width="2"/>'
            f'<rect x="184" y="88" width="172" height="44" rx="5" fill="#1e293b" stroke="{hv_col}" stroke-width="1.6"/>'
            f'<text x="270" y="114" fill="#e2e8f0" font-size="11" font-weight="600" text-anchor="middle" font-family="JetBrains Mono, monospace">HV PACK {int(voltage)}V</text>'
        )
        if topo == "Dual":
            coords = [(96.0, 110.0, 34.0), (444.0, 110.0, 34.0)]
        elif topo == "Tri":
            coords = [(96.0, 110.0, 33.0), (444.0, 64.0, 29.0), (444.0, 156.0, 29.0)]
        elif topo == "Quad":
            coords = [(96.0, 64.0, 28.0), (96.0, 156.0, 28.0), (444.0, 64.0, 28.0), (444.0, 156.0, 28.0)]
        else:  # In-Wheel
            coords = [(84.0, 56.0, 26.0), (84.0, 164.0, 26.0), (456.0, 56.0, 26.0), (456.0, 164.0, 26.0)]

    for ux, uy, ur in coords:
        bx = 170.0 if ux < 270.0 else (370.0 if ux > 270.0 else 270.0)
        if topo != "Single":
            elems.append(
                f'<line x1="{bx:.1f}" y1="110" x2="{ux:.1f}" y2="{uy:.1f}" stroke="{hv_col}" stroke-width="3" stroke-linecap="round"/>'
            )
        elems.append(_desenhar_unidade_ev_svg(ux, uy, ur, is_axial=is_axial))

    svg = (
        f'<svg viewBox="0 0 {w} {h}" width="100%" height="100%" xmlns="http://www.w3.org/2000/svg">'
        + "".join(elems)
        + "</svg>"
    )
    rotulo = f"{topo.upper()} · {m_type.upper()} · {int(voltage)}V ({units}x)"
    return svg, rotulo


def widget_motor_inline(
    topology: str = "Single",
    motor_type: str = "PMSM",
    voltage: int = 800,
) -> str:
    svg_motor, rotulo = gerar_svg_motor_eletrico(topology, motor_type, voltage)
    units = clamp_units_topology(topology)
    return f"""
    <div class="widget-card widget-motor">
        <div class="widget-header">
            <span class="ficha-titulo">ARQUITETURA EV</span>
            <span class="widget-badge" id="motor-badge-tipo">{rotulo}</span>
        </div>
        <div class="svg-stage" id="motor-svg-container">
            {svg_motor}
        </div>
        <div class="motor-footer">
            <div class="info-bloco-num">
                <span class="info-label">UNIDADES</span>
                <span class="info-valor" id="motor-num-units">{units}</span>
            </div>
        </div>
    </div>
    """


def widget_dyno_modular(potencia_txt: str = "402 kW", torque_txt: str = "535 Nm") -> str:
    return f"""
    <div class="panels-right-col" id="panels-right-col">
        <section class="widget-card widget-dyno" id="widget-dyno">
            <div class="widget-header">
                <span class="ficha-titulo" id="dyno-title">DYNO CURVES</span>
                <div class="dyno-header-actions">
                    <span class="widget-badge" id="dyno-peak-badge">{potencia_txt} · {torque_txt}</span>
                    <button type="button" class="btn-3d-ctrl btn-unit-toggle" id="btn-unit-toggle" aria-pressed="false" title="Alternar unidades entre kW / Nm e hp / lb-ft">kW / Nm</button>
                </div>
            </div>
            <div class="dyno-legend-row">
                <div class="dyno-legend">
                    <span class="dyno-key"><span class="dyno-swatch" style="background:#ef4444;"></span><span id="dyno-legend-power">Potência (kW)</span></span>
                    <span class="dyno-key"><span class="dyno-swatch" style="background:#d49b4b;"></span><span id="dyno-legend-torque">Binário (Nm)</span></span>
                </div>
                <span class="dyno-readout" id="dyno-live-readout">Motor desligado</span>
            </div>
            <div class="dyno-canvas-wrap">
                <canvas id="dyno-canvas" class="dyno-canvas" aria-label="Gráfico de curvas de potência e binário EV (Dyno)"></canvas>
            </div>
        </section>
    </div>
    """


def calcular_peso_ideal_rotor(
    motor_type: str = "PMSM",
    stator_diam: float = 240.0,
    stack_len: float = 165.0,
    rotor_type: str = "Neodímio N52 (V-Shape)",
    max_rpm: int = 16000,
) -> float:
    """Sugere o peso ideal do conjunto do rotor EV (kg) para equilibrar inércia, fluxo magnético e tensão centrífuga."""
    d_m = max(0.10, float(stator_diam or 240.0) / 1000.0)
    l_m = max(0.03, float(stack_len or 165.0) / 1000.0)
    cyl_vol_ratio = (d_m * d_m * l_m) / (0.24 * 0.24 * 0.165)

    m_type_mult = {
        "PMSM": 1.00,
        "Induction AC": 1.18,
        "Axial Flux": 0.62,
        "SynRM": 0.94,
    }.get(motor_type, 1.00)
    r_type_mult = ROTOR_PROFILES.get(rotor_type, ROTOR_PROFILES["Neodímio N52 (V-Shape)"])["mass_mult"]
    max_r = max(3000, int(max_rpm or 16000))
    rpm_mult = max(0.68, min(1.18, 1.05 - (max_r - 14000) * 0.000018))

    ideal = 14.5 * math.pow(max(0.18, cyl_vol_ratio), 0.78) * m_type_mult * r_type_mult * rpm_mult
    return round(max(1.0, min(500.0, ideal)) * 2.0) / 2.0


def processar_eletrico(
    topology: str = "Single",
    motor_type: str = "PMSM",
    stator_diam: float = 240.0,
    stack_len: float = 165.0,
    poles: int = 8,
    winding: str = "Hairpin Cobre",
    housing_mat: str = "Alumínio Fundido",
    rotor_type: str = "Neodímio N52 (V-Shape)",
    cooling: str = "Glicol (Camisa Água)",
    bearing_type: str = "Aço Padrão",
    field_weakening: str = "Equilibrado",
    regen_mode: str = "One-Pedal Alta (180 kW)",
    rotor_mass: float = 14.5,
    voltage: int = 800,
    inverter: str = "SiC Dual",
    current_limit: float = 650.0,
    battery_chem: str = "NMC 811",
    battery_kwh: float = 85.0,
    drive_mode: str = "Normal",
    max_rpm: int = 16000,
    gearbox_type: str = "Redutor 1V Direto",
    gearbox_speeds: str = "1",
    diff_type: str = "Diferencial Aberto",
    final_drive: float = 9.73,
) -> dict[str, object]:
    """Calcula curvas EV, eficiência global, teto Back-EMF, limite térmico e velocidade periférica do rotor."""
    topo_map = {
        "Single": (1, 1.00, 1.00),
        "Dual": (2, 1.88, 1.65),
        "Tri": (3, 2.70, 2.25),
        "Quad": (4, 3.45, 2.80),
        "In-Wheel": (4, 3.15, 2.40),
    }
    units, tq_scale, pwr_bus = topo_map.get(topology, (1, 1.00, 1.00))

    m_prof = MOTOR_TYPES.get(motor_type, MOTOR_TYPES["PMSM"])
    r_prof = ROTOR_PROFILES.get(rotor_type, ROTOR_PROFILES["Neodímio N52 (V-Shape)"])
    w_prof = WINDING_PROFILES.get(winding, WINDING_PROFILES["Hairpin Cobre"])
    inv_prof = INVERTER_PROFILES.get(inverter, INVERTER_PROFILES["SiC Dual"])
    batt_prof = BATTERY_PROFILES.get(battery_chem, BATTERY_PROFILES["NMC 811"])
    dm_prof = DRIVE_MODE_PROFILES.get(drive_mode, DRIVE_MODE_PROFILES["Normal"])
    fw_prof = FW_PROFILES.get(field_weakening, FW_PROFILES["Equilibrado"])
    cool_prof = COOLING_PROFILES.get(cooling, COOLING_PROFILES["Glicol (Camisa Água)"])
    gb_prof = GEARBOX_PROFILES.get(gearbox_type, GEARBOX_PROFILES["Redutor 1V Direto"])
    diff_eff = DIFF_EFF_MAP.get(diff_type, 0.994)

    pole_tq = {4: 0.94, 6: 0.98, 8: 1.00, 12: 1.05, 16: 1.09}.get(int(poles or 8), 1.00)
    diam_mm = max(120.0, min(450.0, float(stator_diam or 240.0)))
    stack_mm = max(50.0, min(400.0, float(stack_len or 165.0)))
    rpm_max = max(3000, min(35000, int(max_rpm or 16000)))
    v_bus = max(200, int(voltage or 800))
    i_bus = max(100.0, min(2400.0, float(current_limit or 650.0)))
    kwh_val = max(20.0, min(250.0, float(battery_kwh or 85.0)))

    rotor_ideal = calcular_peso_ideal_rotor(motor_type, diam_mm, stack_mm, rotor_type, rpm_max)
    r_mass = max(1.0, min(500.0, float(rotor_mass or rotor_ideal)))
    m_ratio = r_mass / max(1.0, rotor_ideal)
    tip_stress_penalty = min(35.0, (m_ratio - 1.5) * 18.0) if m_ratio > 1.5 else (-5.0 if 0.8 <= m_ratio <= 1.25 else 0.0)

    diam_scale = math.pow(diam_mm / 240.0, 2)
    stack_scale = stack_mm / 165.0
    curr_ratio = math.sqrt(max(0.25, min(2.6, i_bus / 650.0)))
    eff_total = min(0.985, m_prof["eff"] * r_prof["eff"] * w_prof["eff"] * inv_prof["eff"] * gb_prof["hp"] * diff_eff)

    unit_peak_tq = 495.0 * diam_scale * stack_scale * m_prof["tq"] * r_prof["tq"] * w_prof["tq"] * pole_tq * curr_ratio * dm_prof["tq"]
    shaft_peak_tq = round(unit_peak_tq * tq_scale * batt_prof["sag"] * gb_prof["tq"] * diff_eff)

    inv_pwr_kw = (v_bus * i_bus / 1000.0) * pwr_bus * inv_prof["gain"] * dm_prof["pwr"] * cool_prof["gain"] * 0.86
    pack_pwr_kw = (kwh_val * batt_prof["crate"]) * eff_total * (1.12 if drive_mode == "Ludicrous" else 1.00)
    elec_pwr_ceiling = min(inv_pwr_kw, pack_pwr_kw)

    base_speed_rpm = max(1200.0, min(rpm_max * 0.88, (elec_pwr_ceiling * 9549.3) / max(40.0, float(shaft_peak_tq))))
    v_headroom = (v_bus / 800.0) * fw_prof["fw"] * (1.14 if gearbox_type == "Caixa EV 2V" else 1.00)

    best_p = 0.0
    best_t = 0.0
    for idx in range(51):
        rpm_i = (rpm_max * idx) / 50.0
        u = rpm_i / rpm_max
        omega = (rpm_i * math.pi * 2.0) / 60.0
        tq_factor = 1.0
        if m_prof["low_slip"] < 0.99 and rpm_i < 950.0:
            x = max(0.0, min(1.0, rpm_i / 950.0))
            low_mix = x * x * (3.0 - 2.0 * x)
            tq_factor = m_prof["low_slip"] + (1.0 - m_prof["low_slip"]) * low_mix
        torque_nm = shaft_peak_tq * tq_factor
        if rpm_i > base_speed_rpm:
            pwr_at_rpm = elec_pwr_ceiling * (1.0 - max(0.0, u - 0.72) * (0.24 / max(0.55, v_headroom * m_prof["fw_keep"])))
            fw_tq = (pwr_at_rpm * 9549.3) / max(1.0, rpm_i)
            torque_nm = min(torque_nm, max(shaft_peak_tq * 0.14, fw_tq))
        drag_drop = 1.0 - max(0.0, u - 0.85) * 0.35
        torque_nm = max(15.0, torque_nm * drag_drop)
        pwr_kw = (torque_nm * omega) / 1000.0
        if pwr_kw > best_p:
            best_p = pwr_kw
        if torque_nm > best_t:
            best_t = torque_nm

    peak_kw = round(best_p)
    peak_nm = round(best_t)
    regen_kw = REGEN_KW_MAP.get(regen_mode, 180)
    if regen_mode == "Track Regen (Max)":
        regen_kw = round(min(450, peak_kw * 0.55))

    is_axial = motor_type == "Axial Flux" or topology == "In-Wheel"
    rotor_dia_m = (diam_mm * (0.86 if is_axial else 0.62)) / 1000.0
    tip_speed_ms = (math.pi * rotor_dia_m * rpm_max) / 60.0
    bearing_bonus = BEARING_TIP_BONUS.get(bearing_type, 0.0)
    base_tip_lim = r_prof["tip_lim"] * (0.86 if is_axial else 1.0)
    tip_limit_ms = max(120.0, base_tip_lim + bearing_bonus - tip_stress_penalty)

    gb_rpm_mult = 1.15 if gearbox_type == "Caixa EV 2V" else 1.00
    back_emf_limit_rpm = 17500.0 * (v_bus / 800.0) * fw_prof["rpm_mult"] * gb_rpm_mult

    cooling_cap_kw = cool_prof["cap_kw"] * (1.10 if is_axial else 1.00)
    unit_kw = peak_kw / max(1, units)

    motivos_alerta: list[str] = []
    if tip_speed_ms > tip_limit_ms:
        motivos_alerta.append(f"Vel. periférica do rotor elevada ({tip_speed_ms:.1f} m/s > {tip_limit_ms:.1f} m/s)")
    if rpm_max > back_emf_limit_rpm:
        motivos_alerta.append(f"RPM > teto Back-EMF para {v_bus}V ({round(back_emf_limit_rpm)} RPM)")
    if unit_kw > cooling_cap_kw:
        motivos_alerta.append(f"Sobrecarga térmica ({round(unit_kw)} kW/un > {round(cooling_cap_kw)} kW arrefecimento)")

    return {
        "potencia_kw": f"{peak_kw} kW",
        "torque_nm": f"{peak_nm} Nm",
        "peak_kw": peak_kw,
        "peak_nm": peak_nm,
        "efficiency_pct": round(eff_total * 100.0, 1),
        "regen_kw": regen_kw,
        "rotor_ideal_kg": rotor_ideal,
        "tip_speed_ms": round(tip_speed_ms, 1),
        "tip_limit_ms": round(tip_limit_ms, 1),
        "back_emf_limit_rpm": round(back_emf_limit_rpm),
        "cooling_cap_kw": round(cooling_cap_kw),
        "unit_kw": round(unit_kw),
        "housing_mat": housing_mat,
        "gearbox_speeds": gearbox_speeds,
        "final_drive": float(final_drive or 9.73),
        "alerta_rpm": len(motivos_alerta) > 0,
        "motivos_alerta": motivos_alerta,
    }


def widget_3_modular(
    topology: str = "Single",
    motor_type: str = "PMSM",
    voltage: int = 800,
) -> str:
    dados = processar_eletrico(topology=topology, motor_type=motor_type, voltage=voltage)
    return f"""
    <section class="widget-card widget-configs config-bar-inferior" id="widget-3">
        <div class="widget-header config-bar-header">
            <span class="ficha-titulo" id="cfg-page-title">1 · ARQUITETURA &amp; ESTATOR</span>
            <div class="config-pager">
                <button type="button" class="pager-btn" id="btn-page-prev" aria-label="Anterior" disabled>◀</button>
                <div class="pager-dots">
                    <button type="button" class="pager-dot ativo" id="page-dot-0" data-page="0" aria-current="page"></button>
                    <button type="button" class="pager-dot" id="page-dot-1" data-page="1"></button>
                    <button type="button" class="pager-dot" id="page-dot-2" data-page="2"></button>
                    <button type="button" class="pager-dot" id="page-dot-3" data-page="3"></button>
                </div>
                <button type="button" class="pager-btn" id="btn-page-next" aria-label="Seguinte">▶</button>
            </div>
            <span class="widget-badge" id="cfg-live-badge">TEMPO REAL</span>
        </div>
        <div class="config-page ativo" id="cfg-page-0" data-page="0">
            <div class="summary-pill"><strong id="mod-arch">{topology} · {motor_type} · {voltage}V</strong><small>{dados["potencia_kw"]} · {dados["torque_nm"]}</small></div>
        </div>
    </section>
    """


def gerar_dashboard_html(
    topology: str = "Single",
    motor_type: str = "PMSM",
    voltage: int = 800,
) -> str:
    """Gera o HTML completo EV alinhado com o index.html."""
    topo_clean = topology if topology in TOPOLOGY_UNIT_COUNTS else "Single"
    mtype_clean = motor_type if motor_type in MOTOR_TYPES else "PMSM"
    v_clean = int(voltage or 800)
    units = clamp_units_topology(topo_clean)
    dados = processar_eletrico(topology=topo_clean, motor_type=mtype_clean, voltage=v_clean)
    badge_txt = f"{topo_clean.upper()} · {mtype_clean.upper()} · {v_clean}V"
    potencia_txt = str(dados["potencia_kw"])
    torque_txt = str(dados["torque_nm"])
    return f"""<!DOCTYPE html>
<html lang="pt">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Custom Electric Motor</title>
    <link rel="preconnect" href="https://fonts.googleapis.com">
    <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&family=JetBrains+Mono:wght@500;600;700&display=swap" rel="stylesheet">
    <style>
        :root {{
            color-scheme: dark;
            --bg-base: #000000;
            --bg-elevated: rgba(13, 15, 20, 0.80);
            --bg-surface: rgba(20, 23, 31, 0.88);
            --bg-surface-hover: rgba(28, 32, 43, 0.94);
            --border-subtle: rgba(255, 255, 255, 0.12);
            --border-strong: rgba(255, 255, 255, 0.24);
            --text-primary: #f3f4f6;
            --text-secondary: #9ca3af;
            --text-muted: #6b7280;
            --accent-primary: #64748b;
            --accent-primary-soft: rgba(148, 163, 184, 0.14);
            --accent-primary-border: rgba(148, 163, 184, 0.36);
            --accent-warm: #d49b4b;
            --accent-teal: #6ea8a6;
            --accent-alert: #ef4444;
            --btn-hover-grad: linear-gradient(135deg, #dc2626 0%, #7f1d1d 100%);
            --radius-lg: 12px;
            --radius-md: 8px;
            --shadow-card: 0 14px 36px -14px rgba(0, 0, 0, 0.88), inset 0 1px 0 rgba(255, 255, 255, 0.05);
            --font-sans: 'Inter', 'Segoe UI Variable', 'Segoe UI', system-ui, -apple-system, sans-serif;
            --font-mono: 'JetBrains Mono', 'Cascadia Code', 'Consolas', monospace;
        }}

        * {{
            box-sizing: border-box;
            margin: 0;
            padding: 0;
        }}

        /* Fundo preto em grelha sutil com o motor 3D no background */
        body {{
            background-color: var(--bg-base);
            background-image:
                radial-gradient(circle at 30% 42%, rgba(255, 255, 255, 0.045), transparent 56%),
                linear-gradient(rgba(255, 255, 255, 0.05) 1px, transparent 1px),
                linear-gradient(90deg, rgba(255, 255, 255, 0.05) 1px, transparent 1px);
            background-size: 100% 100%, 28px 28px, 28px 28px;
            background-attachment: fixed;
            color: var(--text-primary);
            font-family: var(--font-sans);
            min-height: 100vh;
            display: flex;
            flex-direction: column;
            align-items: stretch;
            justify-content: space-between;
            padding: 10px 16px 12px;
            position: relative;
            overflow-x: hidden;
        }}

        /* Palco 3D em Background (ligeiramente transparente, interativo) */
        .motor-bg-stage {{
            position: fixed;
            inset: 0;
            z-index: 0;
            pointer-events: auto;
            overflow: hidden;
        }}

        .motor-3d-canvas {{
            position: absolute;
            inset: 0;
            width: 100%;
            height: 100%;
            display: block;
            opacity: 0.78;
            cursor: grab;
            touch-action: none;
            user-select: none;
        }}

        .motor-3d-canvas:active {{
            cursor: grabbing;
        }}

        /* Camada de UI sobre o background (cliques fora dos painéis passam para o motor 3D) */
        .ui-layer {{
            position: relative;
            z-index: 1;
            width: 100%;
            max-width: none;
            display: flex;
            flex-direction: column;
            gap: 8px;
            flex: 1;
            pointer-events: none;
        }}

        .dashboard-topbar,
        .subsystem-popover,
        .widget-card,
        .engine-action-dock,
        .motor-3d-hint {{
            pointer-events: auto;
        }}

        /* Linha Superior: Barra pequena do Redutor/Caixa EV à esquerda + Controlos 3D à direita */
        .topbar-row {{
            width: 100%;
            display: flex;
            flex-wrap: wrap;
            align-items: flex-start;
            justify-content: space-between;
            gap: 10px;
            pointer-events: none;
        }}

        .topbar-subsystems-wrap {{
            position: relative;
            display: flex;
            flex-direction: column;
            align-items: flex-start;
            gap: 6px;
            pointer-events: none;
            max-width: 100%;
        }}

        /* Barra Superior Compacta (sem título/subtítulo para libertar visualização 3D) */
        .dashboard-topbar {{
            align-self: flex-end;
            width: auto;
            max-width: 100%;
            display: flex;
            flex-wrap: wrap;
            justify-content: flex-end;
            align-items: center;
            gap: 8px;
            padding: 7px 12px;
            background: var(--bg-elevated);
            backdrop-filter: blur(12px);
            -webkit-backdrop-filter: blur(12px);
            border: 1px solid var(--border-subtle);
            border-radius: var(--radius-lg);
            box-shadow: var(--shadow-card);
        }}

        .topbar-subsystems {{
            align-self: flex-start;
            justify-content: flex-start;
            padding: 6px 10px;
            gap: 7px;
        }}

        .subsystem-popover {{
            display: none;
            position: absolute;
            top: calc(100% + 6px);
            left: 0;
            z-index: 25;
            width: min(372px, calc(100vw - 32px));
            background: linear-gradient(180deg, rgba(16, 19, 27, 0.94) 0%, rgba(10, 12, 18, 0.96) 100%);
            backdrop-filter: blur(16px);
            -webkit-backdrop-filter: blur(16px);
            border: 1px solid var(--border-strong);
            border-top: 3px solid var(--accent-primary);
            border-radius: var(--radius-lg);
            padding: 11px 13px;
            box-shadow: var(--shadow-card);
            flex-direction: column;
            gap: 9px;
        }}

        .subsystem-popover.aberto {{
            display: flex;
        }}

        .subsystem-popover-header {{
            display: flex;
            align-items: center;
            justify-content: space-between;
            gap: 8px;
            padding-bottom: 6px;
            border-bottom: 1px solid var(--border-subtle);
        }}

        .subsystem-popover-header .ficha-titulo {{
            font-size: 0.74rem;
        }}

        .btn-popover-close {{
            background: transparent;
            color: var(--text-secondary);
            border: 1px solid var(--border-subtle);
            border-radius: 5px;
            width: 24px;
            height: 24px;
            font-size: 0.9rem;
            line-height: 1;
            cursor: pointer;
            display: inline-flex;
            align-items: center;
            justify-content: center;
        }}

        .btn-popover-close:hover {{
            background: var(--btn-hover-grad);
            border-color: #ef4444;
            color: #ffffff;
        }}

        .subsystem-footer-row {{
            display: flex;
            align-items: center;
            justify-content: space-between;
            gap: 8px;
            padding-top: 4px;
            border-top: 1px solid var(--border-subtle);
        }}

        .subsystem-readout-pill {{
            font-family: var(--font-mono);
            font-size: 0.66rem;
            color: var(--accent-teal);
            font-variant-numeric: tabular-nums;
        }}

        .diam-control-row {{
            display: flex;
            align-items: center;
            gap: 8px;
        }}

        .diam-control-row input[type="range"] {{
            flex: 1;
            accent-color: #ef4444;
            cursor: pointer;
            height: 5px;
        }}

        .diam-control-row input[type="number"] {{
            width: 74px;
            flex: 0 0 74px;
            text-align: center;
        }}

        .topbar-right {{
            display: flex;
            flex-wrap: wrap;
            align-items: center;
            justify-content: flex-end;
            gap: 7px;
        }}

        button {{
            transition: background 0.18s ease, border-color 0.18s ease, color 0.18s ease, transform 0.15s ease, box-shadow 0.18s ease, opacity 0.15s ease;
        }}

        /* Grelha principal: Esquerda ampla para o Motor 3D no background + Dyno encostado à direita na última página */
        .dashboard-container {{
            display: grid;
            grid-template-columns: minmax(0, 1fr) clamp(360px, 26vw, 430px);
            gap: 14px;
            width: 100%;
            flex: 1;
            align-items: stretch;
            pointer-events: none;
        }}

        .dashboard-container.dyno-hidden {{
            grid-template-columns: 1fr;
        }}

        .dashboard-container.dyno-hidden .panels-right-col {{
            display: none;
        }}

        .dashboard-container.dyno-compact {{
            grid-template-columns: minmax(0, 1fr) clamp(248px, 19.5vw, 295px);
        }}

        .engine-foreground-col {{
            display: flex;
            flex-direction: column;
            justify-content: flex-end;
            gap: 8px;
            min-height: 280px;
            pointer-events: none;
        }}

        .engine-viewport-space {{
            flex: 1;
            min-height: 160px;
            pointer-events: none;
            display: flex;
            align-items: flex-start;
            justify-content: flex-start;
        }}

        .motor-3d-hint {{
            background: rgba(13, 15, 20, 0.72);
            backdrop-filter: blur(8px);
            -webkit-backdrop-filter: blur(8px);
            border: 1px solid var(--border-subtle);
            border-radius: 6px;
            padding: 5px 10px;
            font-family: var(--font-mono);
            font-size: 0.66rem;
            color: var(--text-secondary);
            pointer-events: none;
        }}

        /* Barra de Controlo do Motor (Ligar/Desligar + Acelerar + RPM) */
        .engine-action-dock {{
            align-self: flex-start;
            background: var(--bg-elevated);
            backdrop-filter: blur(12px);
            -webkit-backdrop-filter: blur(12px);
            border: 1px solid var(--border-subtle);
            border-left: 4px solid var(--accent-primary);
            border-radius: var(--radius-lg);
            padding: 9px 13px;
            display: flex;
            flex-wrap: wrap;
            align-items: center;
            justify-content: space-between;
            gap: 10px;
            box-shadow: var(--shadow-card);
        }}

        .engine-dock-buttons {{
            display: flex;
            flex-wrap: wrap;
            align-items: center;
            gap: 8px;
        }}

        .btn-engine-ctrl {{
            background: var(--bg-surface);
            color: var(--text-primary);
            border: 1px solid var(--border-strong);
            border-radius: var(--radius-md);
            padding: 8px 14px;
            font-family: var(--font-sans);
            font-size: 0.75rem;
            font-weight: 700;
            letter-spacing: 0.06em;
            text-transform: uppercase;
            cursor: pointer;
            display: inline-flex;
            align-items: center;
            justify-content: center;
            gap: 7px;
            user-select: none;
            -webkit-user-select: none;
            touch-action: none;
            -webkit-tap-highlight-color: transparent;
        }}

        .btn-engine-ctrl .dot-ind {{
            width: 8px;
            height: 8px;
            border-radius: 99px;
            background: #6b7280;
            transition: background-color 0.18s ease, box-shadow 0.18s ease;
        }}

        .btn-engine-ctrl.ligado {{
            background: rgba(34, 197, 94, 0.14);
            border-color: rgba(74, 222, 128, 0.45);
            color: #dcfce7;
        }}

        .btn-engine-ctrl.ligado .dot-ind {{
            background: #4ade80;
            box-shadow: 0 0 8px rgba(74, 222, 128, 0.75);
        }}

        .btn-engine-ctrl.slow-ativo {{
            background: rgba(110, 168, 166, 0.16);
            border-color: rgba(110, 168, 166, 0.62);
            color: #d1fae5;
            box-shadow: 0 4px 14px -6px rgba(110, 168, 166, 0.45);
        }}

        .btn-engine-ctrl:disabled {{
            opacity: 0.45;
            cursor: not-allowed;
        }}

        .btn-engine-ctrl:not(:disabled):hover,
        .btn-engine-ctrl.ligado:not(:disabled):hover,
        .btn-engine-ctrl.slow-ativo:not(:disabled):hover {{
            background: rgba(127, 29, 29, 0.26);
            border-color: rgba(239, 68, 68, 0.68);
            color: #ffffff;
            transform: translateY(-1px);
            box-shadow: 0 4px 14px -6px rgba(220, 38, 38, 0.45);
        }}

        .btn-engine-ctrl:not(:disabled):active {{
            transform: translateY(0);
        }}

        .throttle-bar-control {{
            display: flex;
            flex-direction: column;
            justify-content: center;
            gap: 5px;
            min-width: 185px;
            flex: 1 1 200px;
            max-width: 245px;
            padding: 6px 12px;
            background: var(--bg-surface);
            border: 1px solid var(--border-strong);
            border-radius: var(--radius-md);
            transition: border-color 0.16s ease, box-shadow 0.16s ease, opacity 0.15s ease;
            user-select: none;
            -webkit-user-select: none;
        }}

        .throttle-bar-control.ativo {{
            border-color: rgba(239, 68, 68, 0.58);
            box-shadow: 0 0 14px -4px rgba(239, 68, 68, 0.45);
        }}

        .throttle-bar-control.disabled {{
            opacity: 0.45;
            cursor: not-allowed;
        }}

        .throttle-bar-header {{
            display: flex;
            align-items: baseline;
            justify-content: space-between;
            gap: 8px;
        }}

        .throttle-bar-header label {{
            font-size: 0.62rem;
            font-weight: 700;
            letter-spacing: 0.08em;
            color: var(--text-secondary);
            text-transform: uppercase;
            cursor: pointer;
        }}

        .throttle-bar-control.disabled .throttle-bar-header label {{
            cursor: not-allowed;
        }}

        .throttle-bar-header strong {{
            font-family: var(--font-mono);
            font-size: 0.78rem;
            font-weight: 700;
            color: var(--text-primary);
            font-variant-numeric: tabular-nums;
            line-height: 1;
        }}

        .throttle-bar-control.ativo .throttle-bar-header strong {{
            color: #fca5a5;
        }}

        #range-throttle {{
            -webkit-appearance: none;
            appearance: none;
            width: 100%;
            height: 8px;
            border-radius: 999px;
            background: rgba(255, 255, 255, 0.12);
            outline: none;
            cursor: pointer;
            margin: 0;
            touch-action: none;
        }}

        #range-throttle:disabled {{
            cursor: not-allowed;
        }}

        #range-throttle::-webkit-slider-runnable-track {{
            height: 8px;
            background: transparent;
            border-radius: 999px;
        }}

        #range-throttle::-webkit-slider-thumb {{
            -webkit-appearance: none;
            appearance: none;
            width: 14px;
            height: 14px;
            border-radius: 50%;
            background: #ffffff;
            border: 2px solid #ef4444;
            box-shadow: 0 0 8px rgba(239, 68, 68, 0.55);
            margin-top: -3px;
            cursor: grab;
        }}

        #range-throttle:disabled::-webkit-slider-thumb {{
            background: #9ca3af;
            border-color: #6b7280;
            box-shadow: none;
            cursor: not-allowed;
        }}

        #range-throttle::-moz-range-track {{
            height: 8px;
            background: transparent;
            border-radius: 999px;
        }}

        #range-throttle::-moz-range-thumb {{
            width: 14px;
            height: 14px;
            border-radius: 50%;
            background: #ffffff;
            border: 2px solid #ef4444;
            box-shadow: 0 0 8px rgba(239, 68, 68, 0.55);
            cursor: grab;
        }}

        #range-throttle:focus-visible {{
            outline: 2px solid #ef4444;
            outline-offset: 3px;
        }}

        .engine-dock-telemetry {{
            display: flex;
            align-items: center;
            gap: 14px;
        }}

        .telemetry-pill {{
            display: flex;
            flex-direction: column;
            align-items: flex-end;
            gap: 1px;
        }}

        #telemetry-rpm-pill {{
            padding: 5px 10px;
            border-radius: 8px;
            border: 1px solid rgba(255, 255, 255, 0.08);
            background: rgba(255, 255, 255, 0.02);
            min-width: 112px;
            transition: border-color 0.08s linear, box-shadow 0.08s linear;
        }}

        .telemetry-pill span {{
            font-size: 0.62rem;
            font-weight: 600;
            letter-spacing: 0.08em;
            color: var(--text-secondary);
            text-transform: uppercase;
        }}

        .telemetry-pill strong {{
            font-family: var(--font-mono);
            font-size: 1.05rem;
            font-weight: 700;
            color: var(--text-primary);
            font-variant-numeric: tabular-nums;
        }}

        .btn-3d-ctrl {{
            background: var(--bg-surface);
            color: var(--text-primary);
            border: 1px solid var(--border-strong);
            border-radius: 6px;
            padding: 6px 11px;
            font-family: var(--font-sans);
            font-size: 0.72rem;
            font-weight: 600;
            cursor: pointer;
        }}

        .btn-3d-ctrl.ativo {{
            background: rgba(255, 255, 255, 0.16);
            border-color: rgba(255, 255, 255, 0.42);
            color: #ffffff;
        }}

        .btn-3d-ctrl:hover,
        .btn-3d-ctrl.ativo:hover {{
            background: var(--btn-hover-grad);
            border-color: #ef4444;
            color: #ffffff;
            transform: translateY(-1px);
            box-shadow: 0 4px 14px -4px rgba(220, 38, 38, 0.6);
        }}

        .btn-3d-ctrl:active {{
            transform: translateY(0);
        }}

        .btn-3d-ctrl:focus-visible,
        .btn-engine-ctrl:focus-visible {{
            outline: 2px solid #ef4444;
            outline-offset: 2px;
        }}

        /* Coluna Direita: Configurações + Dyno Curves encostados ao lado direito */
        .panels-right-col {{
            display: flex;
            flex-direction: column;
            gap: 14px;
            width: 100%;
            justify-self: end;
            pointer-events: none;
        }}

        .btn-lang-toggle {{
            font-family: var(--font-mono);
            font-size: 0.68rem;
            font-weight: 700;
            letter-spacing: 0.06em;
            padding: 6px 11px;
        }}

        .widget-card {{
            position: relative;
            background: linear-gradient(180deg, rgba(18, 21, 29, 0.86) 0%, rgba(11, 13, 18, 0.88) 100%);
            backdrop-filter: blur(14px);
            -webkit-backdrop-filter: blur(14px);
            border: 1px solid var(--border-subtle);
            border-radius: var(--radius-lg);
            padding: 14px 16px;
            display: flex;
            flex-direction: column;
            align-items: stretch;
            justify-content: space-between;
            gap: 10px;
            box-shadow: var(--shadow-card), inset 0 1px 0 rgba(255, 255, 255, 0.06);
            transition: border-color 0.18s ease, box-shadow 0.18s ease;
        }}

        .widget-card:hover {{
            border-color: var(--border-strong);
        }}

        .widget-header {{
            width: 100%;
            display: flex;
            align-items: center;
            justify-content: space-between;
            gap: 10px;
            padding-bottom: 9px;
            border-bottom: 1px solid var(--border-subtle);
        }}

        .ficha-titulo {{
            font-size: 0.82rem;
            font-weight: 700;
            letter-spacing: 0.08em;
            color: var(--text-primary);
            text-transform: uppercase;
            display: inline-flex;
            align-items: center;
            gap: 8px;
        }}

        .widget-header .ficha-titulo::before {{
            content: '';
            width: 4px;
            height: 14px;
            border-radius: 2px;
            background: var(--accent-primary);
            display: inline-block;
        }}

        .widget-badge {{
            font-family: var(--font-mono);
            font-size: 0.65rem;
            font-weight: 600;
            letter-spacing: 0.07em;
            padding: 4px 9px;
            border-radius: 99px;
            background: var(--bg-surface);
            color: var(--text-secondary);
            border: 1px solid var(--border-subtle);
            white-space: nowrap;
        }}

        .widget-badge.badge-live {{
            color: var(--accent-teal);
            background: rgba(110, 168, 166, 0.11);
            border-color: rgba(110, 168, 166, 0.30);
            display: inline-flex;
            align-items: center;
            gap: 6px;
        }}

        .widget-badge.badge-live::before {{
            content: '';
            width: 6px;
            height: 6px;
            border-radius: 99px;
            background: var(--accent-teal);
        }}

        /* Widget Configurações */
        .widget-configs {{
            justify-content: flex-start;
        }}

        .widget-form {{
            width: 100%;
            display: flex;
            flex-direction: column;
            gap: 9px;
        }}

        .grid-2-col {{
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: 9px;
        }}

        .campo-grupo {{
            display: flex;
            flex-direction: column;
            gap: 4px;
        }}

        .campo-largura-total {{
            grid-column: 1 / -1;
        }}

        .campo-grupo label {{
            font-size: 0.65rem;
            font-weight: 600;
            letter-spacing: 0.07em;
            color: var(--text-secondary);
            text-transform: uppercase;
        }}

        .input-cyber {{
            background-color: rgba(9, 11, 16, 0.90);
            color: var(--text-primary);
            border: 1px solid var(--border-subtle);
            border-radius: var(--radius-md);
            padding: 8px 10px;
            font-family: var(--font-mono);
            font-size: 0.80rem;
            outline: none;
            width: 100%;
            transition: border-color 0.15s ease, box-shadow 0.15s ease, background-color 0.15s ease;
        }}

        select.input-cyber {{
            font-family: var(--font-sans);
            font-weight: 600;
            appearance: none;
            -webkit-appearance: none;
            padding-right: 28px;
            background-image: url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='14' height='14' viewBox='0 0 24 24' fill='none' stroke='%239ca3af' stroke-width='2.2' stroke-linecap='round' stroke-linejoin='round'%3E%3Cpolyline points='6 9 12 15 18 9'%3E%3C/polyline%3E%3C/svg%3E");
            background-repeat: no-repeat;
            background-position: right 10px center;
            cursor: pointer;
        }}

        select.input-cyber option {{
            background-color: #0d0f14;
            color: #f3f4f6;
        }}

        .input-cyber:hover {{
            border-color: var(--border-strong);
        }}

        .input-cyber:focus {{
            border-color: #94a3b8;
            background-color: #11141c;
            box-shadow: 0 0 0 3px var(--accent-primary-soft);
        }}

        .input-cyber:disabled {{
            opacity: 0.42;
            cursor: not-allowed;
        }}

        .input-cyber.input-alerta {{
            border-color: var(--accent-alert);
            background-color: rgba(220, 38, 38, 0.16);
            color: #fca5a5;
            font-weight: 700;
            box-shadow: 0 0 0 3px rgba(239, 68, 68, 0.18);
        }}

        .rpm-alerta-msg {{
            font-size: 0.72rem;
            line-height: 1.35;
            min-height: 0;
        }}

        .rpm-alerta-msg:not(:empty) {{
            margin-top: 2px;
            padding: 7px 10px;
            border-radius: var(--radius-md);
            background: rgba(220, 38, 38, 0.14);
            border: 1px solid rgba(239, 68, 68, 0.42);
            border-left: 3px solid var(--accent-alert);
            color: #fca5a5;
            font-weight: 600;
        }}

        /* Widget Dyno Curves (exibido na última página à direita) */
        .panels-right-col {{
            align-self: end;
        }}

        .widget-dyno {{
            justify-content: flex-start;
            gap: 9px;
        }}

        .dyno-header-actions {{
            display: flex;
            align-items: center;
            gap: 8px;
        }}

        .btn-unit-toggle {{
            font-family: var(--font-mono);
            font-size: 0.66rem;
            font-weight: 700;
            letter-spacing: 0.04em;
            padding: 4px 9px;
            border-radius: 6px;
        }}

        .dyno-legend-row {{
            display: flex;
            flex-wrap: wrap;
            align-items: center;
            justify-content: space-between;
            gap: 8px;
        }}

        .dyno-legend {{
            display: flex;
            align-items: center;
            gap: 12px;
            font-family: var(--font-mono);
            font-size: 0.68rem;
            color: var(--text-secondary);
        }}

        .dyno-key {{
            display: inline-flex;
            align-items: center;
            gap: 6px;
        }}

        .dyno-swatch {{
            width: 12px;
            height: 3px;
            border-radius: 2px;
        }}

        .dyno-readout {{
            font-family: var(--font-mono);
            font-size: 0.70rem;
            color: var(--text-primary);
            font-variant-numeric: tabular-nums;
        }}

        .dyno-canvas-wrap {{
            position: relative;
            width: 100%;
            height: 224px;
            background: rgba(7, 9, 13, 0.85);
            border: 1px solid var(--border-subtle);
            border-radius: var(--radius-md);
            overflow: hidden;
        }}

        .dashboard-container.dyno-compact .widget-dyno {{
            padding: 10px 12px;
            gap: 6px;
        }}

        .dashboard-container.dyno-compact .widget-dyno .widget-header {{
            padding-bottom: 6px;
        }}

        .dashboard-container.dyno-compact .widget-dyno .ficha-titulo {{
            font-size: 0.72rem;
        }}

        .dashboard-container.dyno-compact .dyno-header-actions {{
            gap: 5px;
        }}

        .dashboard-container.dyno-compact .widget-dyno .widget-badge {{
            font-size: 0.59rem;
            padding: 3px 7px;
        }}

        .dashboard-container.dyno-compact .btn-unit-toggle {{
            font-size: 0.60rem;
            padding: 3px 7px;
        }}

        .dashboard-container.dyno-compact .dyno-legend {{
            font-size: 0.61rem;
            gap: 8px;
        }}

        .dashboard-container.dyno-compact .dyno-readout {{
            display: none;
        }}

        .dashboard-container.dyno-compact .dyno-canvas-wrap {{
            height: 132px;
        }}

        .rotor-mass-row {{
            display: flex;
            align-items: stretch;
            gap: 5px;
            width: 100%;
        }}

        .rotor-mass-row input[type="number"] {{
            flex: 1 1 54px;
            min-width: 54px;
            width: 0;
        }}

        .btn-rotor-ideal {{
            flex: 0 1 auto;
            white-space: nowrap;
            background: rgba(110, 168, 166, 0.14);
            color: #a7f3d0;
            border: 1px solid rgba(110, 168, 166, 0.48);
            border-radius: var(--radius-md);
            padding: 0 7px;
            font-family: var(--font-mono);
            font-size: 0.62rem;
            font-weight: 700;
            letter-spacing: 0.02em;
            cursor: pointer;
            display: inline-flex;
            align-items: center;
            justify-content: center;
        }}

        .btn-rotor-ideal.warn {{
            background: rgba(212, 155, 75, 0.16);
            border-color: rgba(212, 155, 75, 0.55);
            color: #fde68a;
        }}

        .btn-rotor-ideal.alert {{
            background: rgba(220, 38, 38, 0.18);
            border-color: rgba(239, 68, 68, 0.62);
            color: #fca5a5;
        }}

        .btn-rotor-ideal:hover {{
            background: var(--btn-hover-grad);
            border-color: #ef4444;
            color: #ffffff;
            box-shadow: 0 4px 12px -4px rgba(220, 38, 38, 0.55);
        }}

        .btn-rotor-ideal:focus-visible {{
            outline: 2px solid #ef4444;
            outline-offset: 2px;
        }}

        .dyno-canvas {{
            position: absolute;
            inset: 0;
            width: 100%;
            height: 100%;
            display: block;
            cursor: crosshair;
        }}

        /* Barra Inferior Compacta com Paginação por Setas */
        .config-bar-inferior {{
            width: 100%;
            border-top: 3px solid var(--accent-primary);
            padding: 9px 14px 10px;
            gap: 8px;
        }}

        .config-bar-inferior .config-bar-header {{
            padding-bottom: 6px;
        }}

        .config-bar-inferior .campo-grupo {{
            gap: 3px;
        }}

        .config-bar-inferior .campo-grupo label {{
            font-size: 0.60rem;
        }}

        .config-bar-inferior .input-cyber {{
            padding: 6px 8px;
            font-size: 0.76rem;
        }}

        .config-header-right {{
            display: flex;
            align-items: center;
            flex-wrap: wrap;
            gap: 8px;
        }}

        .page-nav {{
            display: inline-flex;
            align-items: center;
            gap: 5px;
            background: rgba(9, 11, 16, 0.72);
            border: 1px solid var(--border-subtle);
            border-radius: 8px;
            padding: 2px 4px;
        }}

        .btn-page-arrow {{
            padding: 3px 8px;
            font-size: 0.68rem;
            line-height: 1.2;
            border-radius: 5px;
        }}

        .btn-page-arrow:disabled {{
            opacity: 0.32;
            cursor: not-allowed;
            transform: none;
            box-shadow: none;
        }}

        .page-dots {{
            display: inline-flex;
            align-items: center;
            gap: 3px;
        }}

        .btn-page-num {{
            min-width: 22px;
            height: 22px;
            padding: 0 5px;
            border-radius: 5px;
            border: 1px solid transparent;
            background: transparent;
            color: var(--text-secondary);
            font-family: var(--font-mono);
            font-size: 0.68rem;
            font-weight: 700;
            cursor: pointer;
        }}

        .btn-page-num:hover {{
            color: var(--text-primary);
            background: rgba(255, 255, 255, 0.08);
        }}

        .btn-page-num.ativo {{
            background: rgba(110, 168, 166, 0.22);
            border-color: rgba(110, 168, 166, 0.55);
            color: #e2e8f0;
        }}

        .config-page {{
            display: none;
            width: 100%;
        }}

        .config-page.ativo {{
            display: block;
        }}

        .config-page-grid {{
            display: grid;
            gap: 8px;
            width: 100%;
            align-items: end;
        }}

        .config-page-grid.grid-cols-7 {{
            grid-template-columns: repeat(7, minmax(0, 1fr));
        }}

        .config-page-grid.grid-cols-6 {{
            grid-template-columns: repeat(6, minmax(0, 1fr));
        }}

        .config-page-grid.grid-cols-5-intake {{
            grid-template-columns: repeat(5, minmax(0, 1fr));
        }}

        .config-page-grid.grid-cols-4 {{
            grid-template-columns: repeat(4, minmax(0, 1fr));
        }}

        .campo-grupo.campo-span-2 {{
            grid-column: span 2;
        }}

        /* Última página: Cartões de Resumo do Motor (Arquitetura, Potência Est., Binário Est., etc.) */
        .summary-stats-grid {{
            display: grid;
            grid-template-columns: repeat(6, minmax(0, 1fr));
            gap: 8px;
            width: 100%;
        }}

        .summary-pill {{
            background: linear-gradient(180deg, rgba(22, 26, 36, 0.85) 0%, rgba(12, 15, 22, 0.90) 100%);
            border: 1px solid var(--border-subtle);
            border-bottom: 2px solid var(--border-strong);
            border-radius: var(--radius-md);
            padding: 7px 10px;
            display: flex;
            flex-direction: column;
            gap: 2px;
            min-width: 0;
        }}

        .summary-pill span {{
            font-size: 0.58rem;
            font-weight: 700;
            letter-spacing: 0.08em;
            color: var(--text-secondary);
            text-transform: uppercase;
            white-space: nowrap;
            overflow: hidden;
            text-overflow: ellipsis;
        }}

        .summary-pill strong {{
            font-family: var(--font-mono);
            font-size: 0.86rem;
            font-weight: 700;
            color: var(--text-primary);
            font-variant-numeric: tabular-nums;
            white-space: nowrap;
            overflow: hidden;
            text-overflow: ellipsis;
        }}

        .summary-pill small {{
            font-family: var(--font-mono);
            font-size: 0.62rem;
            color: var(--text-muted);
            white-space: nowrap;
            overflow: hidden;
            text-overflow: ellipsis;
        }}

        .summary-pill.summary-arch {{
            border-bottom-color: var(--accent-teal);
        }}

        .summary-pill.summary-arch strong {{
            color: #99f6e4;
        }}

        .summary-pill.dyno-est-power {{
            border-bottom-color: #ef4444;
        }}

        .summary-pill.dyno-est-power strong {{
            color: #f87171;
        }}

        .summary-pill.dyno-est-torque {{
            border-bottom-color: var(--accent-warm);
        }}

        .summary-pill.dyno-est-torque strong {{
            color: var(--accent-warm);
        }}

        @media (max-width: 1220px) {{
            .config-page-grid.grid-cols-7,
            .config-page-grid.grid-cols-5-intake {{
                grid-template-columns: repeat(4, minmax(0, 1fr));
            }}
            .config-page-grid.grid-cols-6,
            .summary-stats-grid {{
                grid-template-columns: repeat(3, minmax(0, 1fr));
            }}
        }}

        @media (max-width: 1020px) {{
            .topbar-row {{
                flex-direction: column;
                align-items: stretch;
            }}
            .topbar-subsystems-wrap {{
                align-items: stretch;
            }}
            .subsystem-popover {{
                width: 100%;
            }}
            .topbar-subsystems,
            .dashboard-topbar {{
                align-self: stretch;
                justify-content: center;
            }}
            .subsystem-popover {{
                width: 100%;
            }}
            .dashboard-container {{
                grid-template-columns: 1fr;
            }}
            .engine-action-dock {{
                align-self: stretch;
            }}
            .engine-foreground-col {{
                min-height: 240px;
            }}
            .engine-viewport-space {{
                min-height: 150px;
            }}
        }}

        @media (max-width: 680px) {{
            body {{
                padding: 10px 10px 14px;
            }}
            .widget-card {{
                padding: 10px 12px;
            }}
            .engine-action-dock {{
                padding: 10px 12px;
            }}
            .throttle-bar-control {{
                min-width: 150px;
                flex: 1 1 160px;
                max-width: none;
            }}
            .config-page-grid.grid-cols-7,
            .config-page-grid.grid-cols-6,
            .config-page-grid.grid-cols-5-intake,
            .config-page-grid.grid-cols-4,
            .summary-stats-grid {{
                grid-template-columns: repeat(2, minmax(0, 1fr));
            }}
            .dyno-canvas-wrap {{
                height: 195px;
            }}
            .dashboard-container.dyno-compact .dyno-canvas-wrap {{
                height: 118px;
            }}
        }}
    </style>
</head>
<body>
    <!-- Motor 3D no background sobre a grelha -->
    <div id="motor-bg-stage" class="motor-bg-stage">
        <canvas id="motor-3d-canvas" class="motor-3d-canvas" aria-label="Modelo 3D interativo do motor no background"></canvas>
    </div>

    <div class="ui-layer">
        <div class="topbar-row">
            <div class="topbar-subsystems-wrap">
                <nav class="dashboard-topbar topbar-subsystems" aria-label="Subsistema EV e Conjunto Propulsor">
                    <button type="button" class="btn-3d-ctrl" id="btn-top-engine" style="display:none;" title="Voltar ao modelo 3D do Motor Elétrico">← Motor Elétrico</button>
                    <button type="button" class="btn-3d-ctrl" id="btn-top-gearbox" aria-expanded="false" title="Ver modelo separado do Redutor / Caixa EV 3D">Redutor EV · 1V</button>
                    <button type="button" class="btn-3d-ctrl" id="btn-top-battery" aria-expanded="false" title="Ver modelo separado do Pack de Bateria HV 3D">Bateria · 85 kWh</button>
                    <button type="button" class="btn-3d-ctrl" id="btn-top-all" aria-pressed="false" title="Ver Motor Elétrico, Redutor EV e Pack de Bateria HV juntos em 3D">Ver Tudo Junto</button>
                </nav>

                <div class="subsystem-popover" id="popover-gearbox" role="region" aria-label="Redutor e Caixa EV">
                    <div class="subsystem-popover-header">
                        <span class="ficha-titulo" id="gb-panel-title">REDUTOR &amp; CAIXA EV</span>
                        <button type="button" class="btn-popover-close" id="btn-close-gearbox" aria-label="Fechar">×</button>
                    </div>
                    <div class="grid-2-col">
                        <div class="campo-grupo">
                            <label for="select-gearbox-type" id="lbl-gb-type">TIPO DE REDUTOR</label>
                            <select id="select-gearbox-type" class="input-cyber">
                                <option value="Redutor 1V Direto" selected>Redutor 1V Direto</option>
                                <option value="Caixa EV 2V">Caixa EV 2V (Tipo Taycan)</option>
                                <option value="E-CVT Planetária">Planetária (E-CVT)</option>
                                <option value="Coaxial Direto">Coaxial Concêntrico</option>
                            </select>
                        </div>
                        <div class="campo-grupo">
                            <label for="select-gearbox-speeds" id="lbl-gb-speeds">ESTÁGIOS / VEL.</label>
                            <select id="select-gearbox-speeds" class="input-cyber">
                                <option value="1" selected>1 Velocidade (Direta)</option>
                                <option value="2">2 Velocidades (Baixa/Alta)</option>
                                <option value="Contínua">Contínua (Planetária)</option>
                            </select>
                        </div>
                        <div class="campo-grupo">
                            <label for="select-diff-type" id="lbl-diff-type">DIFERENCIAL / VETOR.</label>
                            <select id="select-diff-type" class="input-cyber">
                                <option value="Diferencial Aberto" selected>Diferencial Aberto</option>
                                <option value="LSD Mecânico">LSD Mecânico</option>
                                <option value="e-LSD Vetorizado">e-LSD Vetorizado</option>
                                <option value="Spool Direto">Bloqueio Direto (Spool)</option>
                            </select>
                        </div>
                        <div class="campo-grupo">
                            <label for="select-final-drive" id="lbl-gb-final">REDUÇÃO FINAL</label>
                            <select id="select-final-drive" class="input-cyber">
                                <option value="6.80">6.80:1 (Alta Vel.)</option>
                                <option value="8.20">8.20:1 (Equilibrada)</option>
                                <option value="9.73" selected>9.73:1 (Padrão EV)</option>
                                <option value="11.20">11.20:1 (Arranque)</option>
                                <option value="13.50">13.50:1 (Torque Máx.)</option>
                            </select>
                        </div>
                    </div>
                    <div class="subsystem-footer-row">
                        <span class="subsystem-readout-pill" id="gearbox-summary-info">Redutor 1V · 1V · Aberto · 9.73:1</span>
                        <button type="button" class="btn-3d-ctrl" id="btn-gb-back-engine">Ver Motor</button>
                    </div>
                </div>

                <div class="subsystem-popover" id="popover-battery" role="region" aria-label="Pack de Bateria HV">
                    <div class="subsystem-popover-header">
                        <span class="ficha-titulo" id="bat-panel-title">PACK DE BATERIA HV</span>
                        <button type="button" class="btn-popover-close" id="btn-close-battery" aria-label="Fechar">×</button>
                    </div>
                    <div class="grid-2-col">
                        <div class="campo-grupo">
                            <label for="select-battery-chem" id="lbl-battery-chem">QUÍMICA BATERIA</label>
                            <select id="select-battery-chem" class="input-cyber">
                                <option value="LFP (LiFePO4)">LFP (Ferro-Fosfato)</option>
                                <option value="NMC 811" selected>NMC 811 (Alta Densidade)</option>
                                <option value="NCA Performance">NCA (Descarga Alta)</option>
                                <option value="Estado Sólido">Estado Sólido (Solid)</option>
                                <option value="Supercondensador">Híbrido Supercap.</option>
                            </select>
                        </div>
                        <div class="campo-grupo">
                            <label for="input-battery-kwh" id="lbl-battery-kwh">CAPACIDADE (kWh)</label>
                            <input type="number" id="input-battery-kwh" class="input-cyber" value="85" step="5" min="20" max="250">
                        </div>
                        <div class="campo-grupo">
                            <label for="select-cell-format" id="lbl-cell-format">FORMATO DE CÉLULAS</label>
                            <select id="select-cell-format" class="input-cyber">
                                <option value="Prismática" selected>Prismática (Módulos)</option>
                                <option value="Cilíndrica 4680">Cilíndrica 4680</option>
                                <option value="Blade (Lâmina)">Lâmina (Cell-to-Pack)</option>
                                <option value="Pouch (Bolsa)">Bolsa (Pouch Empilhada)</option>
                            </select>
                        </div>
                        <div class="campo-grupo">
                            <label for="select-pack-arch" id="lbl-pack-arch">ARQUITETURA PACK</label>
                            <select id="select-pack-arch" class="input-cyber">
                                <option value="Skateboard (Piso)" selected>Skateboard (Piso)</option>
                                <option value="T-Pack Central">T-Pack Central</option>
                                <option value="Estrutural 800V">Estrutural Monobloco</option>
                            </select>
                        </div>
                    </div>
                    <div class="subsystem-footer-row">
                        <span class="subsystem-readout-pill" id="battery-summary-info">NMC 811 · 85 kWh · Prismática · Skateboard</span>
                        <button type="button" class="btn-3d-ctrl" id="btn-bat-back-engine">Ver Motor</button>
                    </div>
                </div>
            </div>

            <header class="dashboard-topbar">
                <div class="topbar-right">
                    <span class="widget-badge badge-live" id="motor-3d-badge">{badge_txt}</span>
                    <button type="button" class="btn-3d-ctrl ativo" id="btn-3d-cutaway" aria-pressed="true" title="Alternar vista de corte transparente">Vista Corte</button>
                    <button type="button" class="btn-3d-ctrl" id="btn-3d-autorotate" aria-pressed="false" title="Rodar o modelo automaticamente">Auto-Rodar</button>
                    <button type="button" class="btn-3d-ctrl" id="btn-3d-reset" title="Repor ângulo inicial da câmara">Repor Vista</button>
                    <button type="button" class="btn-3d-ctrl btn-lang-toggle" id="btn-lang-toggle" aria-pressed="false" title="Mudar idioma (Português / English)">PT → EN</button>
                </div>
            </header>
        </div>

        <main class="dashboard-container dyno-hidden" id="dashboard-main">
            <!-- Lado Esquerdo: Palco 3D do Motor Elétrico + Controlos de Potência/Acelerador -->
            <div class="engine-foreground-col">
                <div class="engine-viewport-space">
                    <div class="motor-3d-hint" id="motor-3d-hint">Arrastar fundo: rodar · Scroll: zoom · Botão dir.: mover</div>
                </div>

                <div class="engine-action-dock">
                    <div class="engine-dock-buttons">
                        <button type="button" class="btn-engine-ctrl" id="btn-engine-power" aria-pressed="false">
                            <span class="dot-ind" aria-hidden="true"></span>
                            <span id="btn-engine-power-label">Ligar Motor</span>
                        </button>
                        <div class="throttle-bar-control disabled" id="throttle-control-wrap" title="Posição do acelerador (0% – 100%) · Arraste ou prima Espaço para 100%">
                            <div class="throttle-bar-header">
                                <label for="range-throttle" id="lbl-throttle-pos">ACELERADOR</label>
                                <strong id="throttle-pct-value">0%</strong>
                            </div>
                            <input type="range" id="range-throttle" min="0" max="100" step="1" value="0" disabled aria-label="Posição do acelerador em percentagem">
                        </div>
                        <button type="button" class="btn-engine-ctrl" id="btn-slow-mo" aria-pressed="false" title="Alternar câmara lenta: 1x → 2x → 5x → 10x → Desligado">
                            <span id="btn-slow-mo-label">Slow Mo</span>
                        </button>
                    </div>
                    <div class="engine-dock-telemetry">
                        <div class="telemetry-pill" id="telemetry-rpm-pill">
                            <span id="lbl-tel-rpm">ROTAÇÃO ATUAL</span>
                            <strong id="live-rpm-value">0 RPM</strong>
                        </div>
                        <div class="telemetry-pill">
                            <span id="lbl-tel-units">UNIDADES</span>
                            <strong id="motor-num-units">{units}</strong>
                        </div>
                        <div class="telemetry-pill">
                            <span id="lbl-tel-geo">ARQUITETURA</span>
                            <strong id="motor-3d-spec">PMSM · 8P · Ø240×165 mm</strong>
                        </div>
                    </div>
                </div>
            </div>

            <!-- Lado Direito: Dyno Curves -->
            <div class="panels-right-col" id="panels-right-col">
                <section class="widget-card widget-dyno" id="widget-dyno">
                    <div class="widget-header">
                        <span class="ficha-titulo" id="dyno-title">DYNO CURVES</span>
                        <div class="dyno-header-actions">
                            <span class="widget-badge" id="dyno-peak-badge">{potencia_txt} · {torque_txt}</span>
                            <button type="button" class="btn-3d-ctrl btn-unit-toggle" id="btn-unit-toggle" aria-pressed="false" title="Alternar unidades entre kW / Nm e hp / lb-ft">kW / Nm</button>
                        </div>
                    </div>
                    <div class="dyno-legend-row">
                        <div class="dyno-legend">
                            <span class="dyno-key"><span class="dyno-swatch" style="background:#ef4444;"></span><span id="dyno-legend-power">Potência (kW)</span></span>
                            <span class="dyno-key"><span class="dyno-swatch" style="background:#d49b4b;"></span><span id="dyno-legend-torque">Binário (Nm)</span></span>
                        </div>
                        <span class="dyno-readout" id="dyno-live-readout">Motor desligado</span>
                    </div>
                    <div class="dyno-canvas-wrap">
                        <canvas id="dyno-canvas" class="dyno-canvas" aria-label="Gráfico de curvas de potência e binário EV (Dyno)"></canvas>
                    </div>
                </section>
            </div>
        </main>

        <!-- Barra inferior compacta paginada (1: Arquitetura & Estator, 2: Rotor & Arrefecimento, 3: Inversor & Bateria, 4: Dados + Dyno) -->
        <section class="widget-card widget-configs config-bar-inferior" id="widget-3">
            <div class="widget-header config-bar-header">
                <span class="ficha-titulo" id="cfg-page-title">1 · ARQUITETURA &amp; ESTATOR</span>
                <div class="config-header-right">
                    <div id="rpm-alerta-msg" class="rpm-alerta-msg"></div>
                    <div class="page-nav" role="navigation" aria-label="Páginas do configurador">
                        <button type="button" class="btn-3d-ctrl btn-page-arrow" id="btn-page-prev" title="Página anterior" aria-label="Página anterior" disabled>&#9664;</button>
                        <div class="page-dots" id="page-dots">
                            <button type="button" class="btn-page-num ativo" id="page-dot-0" data-page-target="0" aria-current="page">1</button>
                            <button type="button" class="btn-page-num" id="page-dot-1" data-page-target="1">2</button>
                            <button type="button" class="btn-page-num" id="page-dot-2" data-page-target="2">3</button>
                            <button type="button" class="btn-page-num" id="page-dot-3" data-page-target="3">4</button>
                        </div>
                        <button type="button" class="btn-3d-ctrl btn-page-arrow" id="btn-page-next" title="Próxima página" aria-label="Próxima página">&#9654;</button>
                    </div>
                    <span class="widget-badge badge-live" id="cfg-live-badge">TEMPO REAL</span>
                </div>
            </div>

            <!-- Página 1: Arquitetura & Estator -->
            <div class="config-page ativo" id="cfg-page-0" data-page="0">
                <div class="config-page-grid grid-cols-7">
                    <div class="campo-grupo">
                        <label for="select-topology" id="lbl-topology">TOPOLOGIA</label>
                        <select id="select-topology" class="input-cyber">
                            <option value="Single" selected>Single Motor (1x)</option>
                            <option value="Dual">Dual Motor AWD (2x)</option>
                            <option value="Tri">Tri Motor Vector (3x)</option>
                            <option value="Quad">Quad Motor (4x)</option>
                            <option value="In-Wheel">Hub Motors (4x Roda)</option>
                        </select>
                    </div>
                    <div class="campo-grupo">
                        <label for="select-motor-type" id="lbl-motor-type">TIPO DE MOTOR</label>
                        <select id="select-motor-type" class="input-cyber">
                            <option value="PMSM" selected>PMSM (Íman Permanente)</option>
                            <option value="Induction AC">Indução AC (Gaiola)</option>
                            <option value="Axial Flux">Fluxo Axial (Disco)</option>
                            <option value="SynRM">Relutância (EESM/SynRM)</option>
                        </select>
                    </div>
                    <div class="campo-grupo">
                        <label for="input-stator-diam" id="lbl-stator-diam">DIÂM. ESTATOR (mm)</label>
                        <input type="number" id="input-stator-diam" class="input-cyber" value="240" step="5" min="120" max="450">
                    </div>
                    <div class="campo-grupo">
                        <label for="input-stack-len" id="lbl-stack-len">COMPR. NÚCLEO (mm)</label>
                        <input type="number" id="input-stack-len" class="input-cyber" value="165" step="5" min="50" max="400">
                    </div>
                    <div class="campo-grupo">
                        <label for="select-poles" id="lbl-poles">POLOS MAGNÉTICOS</label>
                        <select id="select-poles" class="input-cyber">
                            <option value="4">4 Polos</option>
                            <option value="6">6 Polos</option>
                            <option value="8" selected>8 Polos</option>
                            <option value="12">12 Polos</option>
                            <option value="16">16 Polos</option>
                        </select>
                    </div>
                    <div class="campo-grupo">
                        <label for="select-winding" id="lbl-winding">ENROLAMENTO</label>
                        <select id="select-winding" class="input-cyber">
                            <option value="Hairpin Cobre" selected>Hairpin (Barras Cobre)</option>
                            <option value="Distribuído Litz">Distribuído (Cobre Litz)</option>
                            <option value="Concentrado">Concentrado (Bobines)</option>
                            <option value="Alumínio Leve">Alumínio Revestido</option>
                        </select>
                    </div>
                    <div class="campo-grupo">
                        <label for="select-housing-mat" id="lbl-housing-mat">MATERIAL CARCAÇA</label>
                        <select id="select-housing-mat" class="input-cyber">
                            <option value="Alumínio Fundido" selected>Alumínio Fundido</option>
                            <option value="Alumínio Billet">Alumínio Billet CNC</option>
                            <option value="Magnésio">Liga de Magnésio</option>
                            <option value="Fibra de Carbono">Fibra de Carbono</option>
                            <option value="Titânio">Titânio</option>
                        </select>
                    </div>
                </div>
            </div>

            <!-- Página 2: Rotor, Arrefecimento & Eficiência -->
            <div class="config-page" id="cfg-page-1" data-page="1">
                <div class="config-page-grid grid-cols-6">
                    <div class="campo-grupo">
                        <label for="select-rotor-type" id="lbl-rotor-type">ROTOR &amp; ÍMANES</label>
                        <select id="select-rotor-type" class="input-cyber">
                            <option value="Neodímio N52 (V-Shape)" selected>Neodímio N52 (Em V)</option>
                            <option value="Halbach Array">Halbach Array</option>
                            <option value="Gaiola de Cobre">Gaiola de Esquilo (Cobre)</option>
                            <option value="Rotor Bobinado (EESM)">Rotor Bobinado (Sem Ímanes)</option>
                            <option value="Manga Carbono (Alta RPM)">Manga Carbono (Alta RPM)</option>
                        </select>
                    </div>
                    <div class="campo-grupo">
                        <label for="select-cooling" id="lbl-cooling">ARREFECIMENTO</label>
                        <select id="select-cooling" class="input-cyber">
                            <option value="Ar (Aletas)">Arrefecido a Ar (Aletas)</option>
                            <option value="Glicol (Camisa Água)" selected>Líquido · Camisa Glicol</option>
                            <option value="Óleo Direto">Spray Direto de Óleo</option>
                            <option value="Imersão Dielétrica">Imersão Dielétrica</option>
                        </select>
                    </div>
                    <div class="campo-grupo">
                        <label for="select-bearing-type" id="lbl-bearing-type">ROLAMENTOS</label>
                        <select id="select-bearing-type" class="input-cyber">
                            <option value="Aço Padrão" selected>Esferas em Aço</option>
                            <option value="Cerâmica Si3N4">Híbrido Cerâmica (Si3N4)</option>
                            <option value="Magnético Ativo">Magnéticos (Ultra-RPM)</option>
                        </select>
                    </div>
                    <div class="campo-grupo">
                        <label for="select-field-weakening" id="lbl-field-weakening">ENFRAQ. CAMPO (FW)</label>
                        <select id="select-field-weakening" class="input-cyber">
                            <option value="Conservador">Conservador (Eficiência)</option>
                            <option value="Equilibrado" selected>Equilibrado (MTPA+FW)</option>
                            <option value="Agressivo">Agressivo (Alta Rotação)</option>
                        </select>
                    </div>
                    <div class="campo-grupo">
                        <label for="select-regen-mode" id="lbl-regen-mode">TRAVAGEM REGEN.</label>
                        <select id="select-regen-mode" class="input-cyber">
                            <option value="Desligada">Desligada (Coast)</option>
                            <option value="Standard (50 kW)">Padrão (~50 kW)</option>
                            <option value="One-Pedal Alta (180 kW)" selected>One-Pedal (~180 kW)</option>
                            <option value="Track Regen (Max)">Track Regen (Máx.)</option>
                        </select>
                    </div>
                    <div class="campo-grupo">
                        <label for="input-rotor-mass" id="lbl-rotor-mass">PESO DO ROTOR (kg)</label>
                        <div class="rotor-mass-row">
                            <input type="number" id="input-rotor-mass" class="input-cyber" value="14.5" step="0.5" min="1.0" max="500" aria-label="Peso do conjunto do rotor em quilogramas (máximo 500 kg)">
                            <button type="button" class="btn-rotor-ideal" id="btn-rotor-ideal" title="Peso/inércia ideal para este rotor · Clique para aplicar">Ideal: 14.5 kg</button>
                        </div>
                    </div>
                </div>
            </div>

            <!-- Página 3: Inversor, Mapa & Rotação (Bateria movida para o painel separado no topo) -->
            <div class="config-page" id="cfg-page-2" data-page="2">
                <div class="config-page-grid grid-cols-5-intake">
                    <div class="campo-grupo">
                        <label for="select-voltage" id="lbl-voltage">TENSÃO HV (V)</label>
                        <select id="select-voltage" class="input-cyber">
                            <option value="400">400 V (Standard EV)</option>
                            <option value="800" selected>800 V (Performance HV)</option>
                            <option value="900">900 V (Ultra-HV)</option>
                            <option value="1200">1200 V (Track HV)</option>
                        </select>
                    </div>
                    <div class="campo-grupo">
                        <label for="select-inverter" id="lbl-inverter">INVERSOR</label>
                        <select id="select-inverter" class="input-cyber">
                            <option value="IGBT Silício">IGBT Silício</option>
                            <option value="SiC Dual" selected>SiC (Carboneto Silício)</option>
                            <option value="SiC Racing 1200A">SiC Dual-Stage Track</option>
                            <option value="GaN Alta Freq.">GaN (Alta Frequência)</option>
                        </select>
                    </div>
                    <div class="campo-grupo">
                        <label for="input-current-limit" id="lbl-current-limit">CORRENTE INV. (A)</label>
                        <input type="number" id="input-current-limit" class="input-cyber" value="650" step="25" min="100" max="2400">
                    </div>
                    <div class="campo-grupo">
                        <label for="select-drive-mode" id="lbl-drive-mode">MAPA / MODO</label>
                        <select id="select-drive-mode" class="input-cyber">
                            <option value="Eco">Eco (70% Potência)</option>
                            <option value="Normal" selected>Normal (Equilibrado)</option>
                            <option value="Sport">Sport (Resposta Rápida)</option>
                            <option value="Ludicrous">Ludicrous (Boost Máx.)</option>
                        </select>
                    </div>
                    <div class="campo-grupo">
                        <label for="input-rpm" id="lbl-rpm">ROTAÇÃO MÁX. (RPM)</label>
                        <input type="number" id="input-rpm" class="input-cyber" value="16000" step="250" min="3000" max="35000">
                    </div>
                </div>
            </div>

            <!-- Página 4 (Última Página): Dados Elétricos + Dyno Curves à direita -->
            <div class="config-page" id="cfg-page-3" data-page="3">
                <div class="summary-stats-grid">
                    <div class="summary-pill summary-arch">
                        <span id="lbl-sum-arch">ARQUITETURA EV</span>
                        <strong id="sum-arch-val">Single · PMSM · 8P</strong>
                        <small id="sum-arch-sub">800 V · Inversor SiC · Hairpin Cobre</small>
                    </div>
                    <div class="summary-pill">
                        <span id="lbl-sum-disp">ESTATOR &amp; REGIME</span>
                        <strong id="sum-disp-val">Ø240×165 mm</strong>
                        <small id="sum-geo-sub">16000 RPM · Redutor 9.73:1</small>
                    </div>
                    <div class="summary-pill dyno-est-power">
                        <span id="lbl-est-power">POTÊNCIA EST.</span>
                        <strong id="dyno-est-power-val">{potencia_txt}</strong>
                        <small id="dyno-est-power-rpm">@ 10500 RPM</small>
                    </div>
                    <div class="summary-pill dyno-est-torque">
                        <span id="lbl-est-torque">BINÁRIO EST.</span>
                        <strong id="dyno-est-torque-val">{torque_txt}</strong>
                        <small id="dyno-est-torque-rpm">@ 0–6200 RPM</small>
                    </div>
                    <div class="summary-pill">
                        <span id="lbl-sum-adm">BATERIA &amp; EFICIÊNCIA</span>
                        <strong id="sum-adm-val">85 kWh · NMC 811</strong>
                        <small id="sum-adm-sub">Efic. 95.4% · Regen 180 kW</small>
                    </div>
                    <div class="summary-pill">
                        <span id="lbl-sum-build">CONSTRUÇÃO &amp; TÉRMICA</span>
                        <strong id="sum-build-val">Alumínio Fundido</strong>
                        <small id="sum-build-sub">Rotor: Neodímio N52 · Glicol · 650 A</small>
                    </div>
                </div>
            </div>
        </section>
    </div>

    <script>
        const selectTopology = document.getElementById('select-topology');
        const selectMotorType = document.getElementById('select-motor-type');
        const inputStatorDiam = document.getElementById('input-stator-diam');
        const inputStackLen = document.getElementById('input-stack-len');
        const selectPoles = document.getElementById('select-poles');
        const selectWinding = document.getElementById('select-winding');
        const selectHousingMat = document.getElementById('select-housing-mat');

        const selectRotorType = document.getElementById('select-rotor-type');
        const selectCooling = document.getElementById('select-cooling');
        const selectBearingType = document.getElementById('select-bearing-type');
        const selectFieldWeakening = document.getElementById('select-field-weakening');
        const selectRegenMode = document.getElementById('select-regen-mode');
        const inputRotorMass = document.getElementById('input-rotor-mass');
        const btnRotorIdeal = document.getElementById('btn-rotor-ideal');

        const selectVoltage = document.getElementById('select-voltage');
        const selectInverter = document.getElementById('select-inverter');
        const inputCurrentLimit = document.getElementById('input-current-limit');
        const selectBatteryChem = document.getElementById('select-battery-chem');
        const inputBatteryKwh = document.getElementById('input-battery-kwh');
        const selectDriveMode = document.getElementById('select-drive-mode');
        const inputRpm = document.getElementById('input-rpm');

        const motorNumUnits = document.getElementById('motor-num-units');
        const motor3dBadge = document.getElementById('motor-3d-badge');
        const motor3dSpec = document.getElementById('motor-3d-spec');

        const btnTopEngine = document.getElementById('btn-top-engine');
        const btnTopGearbox = document.getElementById('btn-top-gearbox');
        const btnTopBattery = document.getElementById('btn-top-battery');
        const btnTopAll = document.getElementById('btn-top-all');
        const popoverGearbox = document.getElementById('popover-gearbox');
        const btnCloseGearbox = document.getElementById('btn-close-gearbox');
        const btnGbBackEngine = document.getElementById('btn-gb-back-engine');
        const selectGearboxType = document.getElementById('select-gearbox-type');
        const selectGearboxSpeeds = document.getElementById('select-gearbox-speeds');
        const selectDiffType = document.getElementById('select-diff-type');
        const selectFinalDrive = document.getElementById('select-final-drive');
        const gearboxSummaryInfo = document.getElementById('gearbox-summary-info');

        const popoverBattery = document.getElementById('popover-battery');
        const btnCloseBattery = document.getElementById('btn-close-battery');
        const btnBatBackEngine = document.getElementById('btn-bat-back-engine');
        const selectCellFormat = document.getElementById('select-cell-format');
        const selectPackArch = document.getElementById('select-pack-arch');
        const batterySummaryInfo = document.getElementById('battery-summary-info');

        let savedRotorForPmsm = 'Neodímio N52 (V-Shape)';
        let viewMode = 'engine';
        let activeTopPopover = null;
        const rpmAlertaMsg = document.getElementById('rpm-alerta-msg');

        const btnEnginePower = document.getElementById('btn-engine-power');
        const btnEnginePowerLabel = document.getElementById('btn-engine-power-label');
        const throttleControlWrap = document.getElementById('throttle-control-wrap');
        const rangeThrottle = document.getElementById('range-throttle');
        const throttlePctValue = document.getElementById('throttle-pct-value');
        const btnSlowMo = document.getElementById('btn-slow-mo');
        const btnSlowMoLabel = document.getElementById('btn-slow-mo-label');
        const btnLangToggle = document.getElementById('btn-lang-toggle');
        const btnCutaway = document.getElementById('btn-3d-cutaway');
        const btnAutoRotate3D = document.getElementById('btn-3d-autorotate');
        const btnReset3D = document.getElementById('btn-3d-reset');
        const telemetryRpmPill = document.getElementById('telemetry-rpm-pill');
        const lblTelRpm = document.getElementById('lbl-tel-rpm');
        const liveRpmValue = document.getElementById('live-rpm-value');
        const dynoCanvas = document.getElementById('dyno-canvas');
        const dynoPeakBadge = document.getElementById('dyno-peak-badge');
        const dynoLiveReadout = document.getElementById('dyno-live-readout');
        const btnUnitToggle = document.getElementById('btn-unit-toggle');
        const dynsRightCol = document.getElementById('panels-right-col');
        const dashboardMain = document.getElementById('dashboard-main');
        const cfgPageTitle = document.getElementById('cfg-page-title');
        const btnPagePrev = document.getElementById('btn-page-prev');
        const btnPageNext = document.getElementById('btn-page-next');
        const dynoEstPowerVal = document.getElementById('dyno-est-power-val');
        const dynoEstTorqueVal = document.getElementById('dyno-est-torque-val');
        const dynoEstPowerRpm = document.getElementById('dyno-est-power-rpm');
        const dynoEstTorqueRpm = document.getElementById('dyno-est-torque-rpm');
        const sumArchVal = document.getElementById('sum-arch-val');
        const sumArchSub = document.getElementById('sum-arch-sub');
        const sumDispVal = document.getElementById('sum-disp-val');
        const sumGeoSub = document.getElementById('sum-geo-sub');
        const sumAdmVal = document.getElementById('sum-adm-val');
        const sumAdmSub = document.getElementById('sum-adm-sub');
        const sumBuildVal = document.getElementById('sum-build-val');
        const sumBuildSub = document.getElementById('sum-build-sub');
        const dynoLegendPower = document.getElementById('dyno-legend-power');
        const dynoLegendTorque = document.getElementById('dyno-legend-torque');
        let motor3D = null;
        let currentPageIdx = 0;

        let currentLang = 'pt';
        const I18N = {{
            pt: {{
                cutawayOn: 'Vista Corte',
                cutawayOff: 'Carcaça Sólida',
                cutawayTitle: 'Alternar vista de corte transparente',
                autoRotate: 'Auto-Rodar',
                autoRotateTitle: 'Rodar o modelo automaticamente',
                resetView: 'Repor Vista',
                resetViewTitle: 'Repor ângulo inicial da câmara',
                langBtn: 'PT → EN',
                langBtnTitle: 'Mudar idioma (Português / English)',
                hint: 'Arrastar fundo: rodar · Scroll: zoom · Botão dir.: mover',
                startEngine: 'Ligar Motor',
                stopEngine: 'Desligar Motor',
                throttleLabel: 'ACELERADOR',
                throttleTitle: 'Posição do acelerador (0% – 100%) · Arraste ou prima Espaço para 100%',
                throttleAria: 'Posição do acelerador em percentagem',
                slowMo: 'Slow Mo',
                slowMoTitle: 'Alternar câmara lenta: 1x → 2x → 5x → 10x → Desligado',
                unitBtnTitle: 'Alternar unidades entre kW / Nm e hp / lb-ft',
                telRpm: 'ROTAÇÃO ATUAL',
                telUnits: 'UNIDADES',
                telGeo: 'ARQUITETURA',
                dynoTitle: 'DYNO CURVES',
                estPower: 'POTÊNCIA EST.',
                estTorque: 'BINÁRIO EST.',
                powerWord: 'Potência',
                torqueWord: 'Binário',
                engineOff: 'Motor desligado',
                standbyReady: 'Armado · 0 RPM (pronto)',
                cursorPrefix: 'Cursor',
                liveBadge: 'TEMPO REAL',
                pageTitles: [
                    '1 · ARQUITETURA & ESTATOR',
                    '2 · ROTOR & ARREFECIMENTO',
                    '3 · INVERSOR, MAPA & RPM',
                    '4 · DADOS ELÉTRICOS & DYNO'
                ],
                pagePrevTitle: 'Página anterior',
                pageNextTitle: 'Próxima página',
                topEngine: '← Motor Elétrico',
                topEngineTitle: 'Voltar ao modelo 3D do Motor Elétrico',
                topGearbox: 'Redutor EV',
                topGearboxTitle: 'Ver modelo separado do Redutor / Caixa EV 3D',
                topBattery: 'Bateria',
                topBatteryTitle: 'Ver modelo separado do Pack de Bateria HV 3D',
                topAll: 'Ver Tudo Junto',
                topAllTitle: 'Ver Motor Elétrico, Redutor EV e Bateria HV juntos em 3D',
                viewEngineBtn: 'Ver Motor',
                gbPanelTitle: 'REDUTOR & CAIXA EV',
                lblGbType: 'TIPO DE REDUTOR',
                lblGbSpeeds: 'ESTÁGIOS / VEL.',
                lblDiffType: 'DIFERENCIAL / VETOR.',
                lblGbFinal: 'REDUÇÃO FINAL',
                batPanelTitle: 'PACK DE BATERIA HV',
                lblCellFormat: 'FORMATO DE CÉLULAS',
                lblPackArch: 'ARQUITETURA PACK',
                cellFormatOpts: {{
                    'Prismática': 'Prismática (Módulos)',
                    'Cilíndrica 4680': 'Cilíndrica 4680',
                    'Blade (Lâmina)': 'Lâmina (Cell-to-Pack)',
                    'Pouch (Bolsa)': 'Bolsa (Pouch Empilhada)'
                }},
                cellFormatShort: {{
                    'Prismática': 'Prismática',
                    'Cilíndrica 4680': '4680',
                    'Blade (Lâmina)': 'Blade',
                    'Pouch (Bolsa)': 'Pouch'
                }},
                packArchOpts: {{
                    'Skateboard (Piso)': 'Skateboard (Piso)',
                    'T-Pack Central': 'T-Pack Central',
                    'Estrutural 800V': 'Estrutural Monobloco'
                }},
                packArchShort: {{
                    'Skateboard (Piso)': 'Skateboard',
                    'T-Pack Central': 'T-Pack',
                    'Estrutural 800V': 'Estrutural'
                }},
                gbTypeOpts: {{
                    'Redutor 1V Direto': 'Redutor 1V Direto',
                    'Caixa EV 2V': 'Caixa EV 2V (Tipo Taycan)',
                    'E-CVT Planetária': 'Planetária (E-CVT)',
                    'Coaxial Direto': 'Coaxial Concêntrico'
                }},
                gbTypeShort: {{
                    'Redutor 1V Direto': 'Redutor 1V',
                    'Caixa EV 2V': 'Caixa 2V',
                    'E-CVT Planetária': 'E-CVT',
                    'Coaxial Direto': 'Coaxial'
                }},
                gbSpeedOpts: {{
                    '1': '1 Velocidade (Direta)',
                    '2': '2 Velocidades (Baixa/Alta)',
                    'Contínua': 'Contínua (Planetária)'
                }},
                gbSteplessLabel: 'Contínua',
                gbSteplessShort: 'Cont.',
                gbSpeedsEcvtTitle: 'Planetária E-CVT tem variação contínua (sem estágios fixos)',
                diffOpts: {{
                    'Diferencial Aberto': 'Diferencial Aberto',
                    'LSD Mecânico': 'LSD Mecânico',
                    'e-LSD Vetorizado': 'e-LSD Vetorizado',
                    'Spool Direto': 'Bloqueio Direto (Spool)'
                }},
                diffShort: {{
                    'Diferencial Aberto': 'Aberto',
                    'LSD Mecânico': 'LSD',
                    'e-LSD Vetorizado': 'e-LSD',
                    'Spool Direto': 'Spool'
                }},
                finalDriveOpts: {{
                    '6.80': '6.80:1 (Alta Vel.)',
                    '8.20': '8.20:1 (Equilibrada)',
                    '9.73': '9.73:1 (Padrão EV)',
                    '11.20': '11.20:1 (Arranque)',
                    '13.50': '13.50:1 (Torque Máx.)'
                }},
                lblSumArch: 'ARQUITETURA EV',
                lblSumDisp: 'ESTATOR & REGIME',
                lblSumAdm: 'BATERIA & EFICIÊNCIA',
                lblSumBuild: 'CONSTRUÇÃO & TÉRMICA',
                lblTopology: 'TOPOLOGIA',
                lblMotorType: 'TIPO DE MOTOR',
                lblStatorDiam: 'DIÂM. ESTATOR (mm)',
                lblStackLen: 'COMPR. NÚCLEO (mm)',
                lblPoles: 'POLOS MAGNÉTICOS',
                lblWinding: 'ENROLAMENTO',
                lblHousingMat: 'MATERIAL CARCAÇA',
                lblRotorType: 'ROTOR & ÍMANES',
                lblCooling: 'ARREFECIMENTO',
                lblBearingType: 'ROLAMENTOS',
                lblFieldWeakening: 'ENFRAQ. CAMPO (FW)',
                lblRegenMode: 'TRAVAGEM REGEN.',
                lblRotorMass: 'PESO DO ROTOR (kg)',
                rotorMassAria: 'Peso do conjunto do rotor em quilogramas (máximo 500 kg)',
                rotorIdealPrefix: 'Ideal',
                rotorIdealTitle: (motorTag, kg, statusTxt) => `Sugestão para ${{motorTag}}: ${{kg}} kg (${{statusTxt}}) — clique para aplicar`,
                rotorStatusOk: 'inércia equilibrada',
                rotorStatusLight: 'leve demais · menor estabilidade térmica',
                rotorStatusHeavy: 'acima do ideal · resposta mais lenta',
                lblVoltage: 'TENSÃO HV (V)',
                lblInverter: 'INVERSOR',
                lblCurrentLimit: 'CORRENTE INV. (A)',
                lblBatteryChem: 'QUÍMICA BATERIA',
                lblBatteryKwh: 'CAPACIDADE (kWh)',
                lblDriveMode: 'MAPA / MODO',
                lblRpm: 'ROTAÇÃO MÁX. (RPM)',
                topologyOpts: {{
                    'Single': 'Single Motor (1x)',
                    'Dual': 'Dual Motor AWD (2x)',
                    'Tri': 'Tri Motor Vector (3x)',
                    'Quad': 'Quad Motor (4x)',
                    'In-Wheel': 'Hub Motors (4x Roda)'
                }},
                motorTypeOpts: {{
                    'PMSM': 'PMSM (Íman Permanente)',
                    'Induction AC': 'Indução AC (Gaiola)',
                    'Axial Flux': 'Fluxo Axial (Disco)',
                    'SynRM': 'Relutância (EESM/SynRM)'
                }},
                poleOpts: {{
                    '4': '4 Polos',
                    '6': '6 Polos',
                    '8': '8 Polos',
                    '12': '12 Polos',
                    '16': '16 Polos'
                }},
                windingOpts: {{
                    'Hairpin Cobre': 'Hairpin (Barras Cobre)',
                    'Distribuído Litz': 'Distribuído (Cobre Litz)',
                    'Concentrado': 'Concentrado (Bobines)',
                    'Alumínio Leve': 'Alumínio Revestido'
                }},
                windingShort: {{
                    'Hairpin Cobre': 'Hairpin',
                    'Distribuído Litz': 'Litz Cobre',
                    'Concentrado': 'Concentrado',
                    'Alumínio Leve': 'Alu. Leve'
                }},
                housingOpts: {{
                    'Alumínio Fundido': 'Alumínio Fundido',
                    'Alumínio Billet': 'Alumínio Billet CNC',
                    'Magnésio': 'Liga de Magnésio',
                    'Fibra de Carbono': 'Fibra de Carbono',
                    'Titânio': 'Titânio'
                }},
                rotorOpts: {{
                    'Neodímio N52 (V-Shape)': 'Neodímio N52 (Em V)',
                    'Halbach Array': 'Halbach Array',
                    'Gaiola de Cobre': 'Gaiola de Esquilo (Cobre)',
                    'Rotor Bobinado (EESM)': 'Rotor Bobinado (Sem Ímanes)',
                    'Manga Carbono (Alta RPM)': 'Manga Carbono (Alta RPM)'
                }},
                rotorShort: {{
                    'Neodímio N52 (V-Shape)': 'N52 V-Shape',
                    'Halbach Array': 'Halbach',
                    'Gaiola de Cobre': 'Gaiola Cobre',
                    'Rotor Bobinado (EESM)': 'EESM Bobinado',
                    'Manga Carbono (Alta RPM)': 'Manga Carbono'
                }},
                coolingOpts: {{
                    'Ar (Aletas)': 'Arrefecido a Ar (Aletas)',
                    'Glicol (Camisa Água)': 'Líquido · Camisa Glicol',
                    'Óleo Direto': 'Spray Direto de Óleo',
                    'Imersão Dielétrica': 'Imersão Dielétrica'
                }},
                coolingShort: {{
                    'Ar (Aletas)': 'Ar (Aletas)',
                    'Glicol (Camisa Água)': 'Glicol',
                    'Óleo Direto': 'Óleo Direto',
                    'Imersão Dielétrica': 'Imersão Diel.'
                }},
                bearingOpts: {{
                    'Aço Padrão': 'Esferas em Aço',
                    'Cerâmica Si3N4': 'Híbrido Cerâmica (Si3N4)',
                    'Magnético Ativo': 'Magnéticos (Ultra-RPM)'
                }},
                fwOpts: {{
                    'Conservador': 'Conservador (Eficiência)',
                    'Equilibrado': 'Equilibrado (MTPA+FW)',
                    'Agressivo': 'Agressivo (Alta Rotação)'
                }},
                regenOpts: {{
                    'Desligada': 'Desligada (Coast)',
                    'Standard (50 kW)': 'Padrão (~50 kW)',
                    'One-Pedal Alta (180 kW)': 'One-Pedal (~180 kW)',
                    'Track Regen (Max)': 'Track Regen (Máx.)'
                }},
                regenShort: {{
                    'Desligada': 'Off',
                    'Standard (50 kW)': '50 kW',
                    'One-Pedal Alta (180 kW)': '180 kW',
                    'Track Regen (Max)': 'Max'
                }},
                voltageOpts: {{
                    '400': '400 V (Standard EV)',
                    '800': '800 V (Performance HV)',
                    '900': '900 V (Ultra-HV)',
                    '1200': '1200 V (Track HV)'
                }},
                inverterOpts: {{
                    'IGBT Silício': 'IGBT Silício',
                    'SiC Dual': 'SiC (Carboneto Silício)',
                    'SiC Racing 1200A': 'SiC Dual-Stage Track',
                    'GaN Alta Freq.': 'GaN (Alta Frequência)'
                }},
                inverterShort: {{
                    'IGBT Silício': 'IGBT',
                    'SiC Dual': 'SiC Dual',
                    'SiC Racing 1200A': 'SiC Track',
                    'GaN Alta Freq.': 'GaN HV'
                }},
                batteryOpts: {{
                    'LFP (LiFePO4)': 'LFP (Ferro-Fosfato)',
                    'NMC 811': 'NMC 811 (Alta Densidade)',
                    'NCA Performance': 'NCA (Descarga Alta)',
                    'Estado Sólido': 'Estado Sólido (Solid)',
                    'Supercondensador': 'Híbrido Supercap.'
                }},
                driveModeOpts: {{
                    'Eco': 'Eco (70% Potência)',
                    'Normal': 'Normal (Equilibrado)',
                    'Sport': 'Sport (Resposta Rápida)',
                    'Ludicrous': 'Ludicrous (Boost Máx.)'
                }},
                effWord: 'Efic.',
                regenWord: 'Regen',
                rotorWord: 'Rotor',
                reducerWord: 'Redutor',
                invWord: 'Inv.',
                warnTipSpeed: (v, lim) => `Vel. periférica do rotor elevada (${{v}} m/s > ${{lim}} m/s)`,
                warnBackEmf: (rpm, v) => `RPM > teto Back-EMF para ${{v}}V (${{rpm}} RPM)`,
                warnThermal: (kw, cap) => `Sobrecarga térmica (${{kw}} kW/un > ${{cap}} kW arrefecimento)`
            }},
            en: {{
                cutawayOn: 'Cutaway View',
                cutawayOff: 'Solid Housing',
                cutawayTitle: 'Toggle transparent cutaway view',
                autoRotate: 'Auto-Rotate',
                autoRotateTitle: 'Rotate the model automatically',
                resetView: 'Reset View',
                resetViewTitle: 'Reset initial camera angle',
                langBtn: 'EN → PT',
                langBtnTitle: 'Switch language (Português / English)',
                hint: 'Drag background: orbit · Scroll: zoom · Right-click: pan',
                startEngine: 'Arm Motor',
                stopEngine: 'Power Off',
                throttleLabel: 'THROTTLE',
                throttleTitle: 'Throttle demand (0% – 100%) · Drag or hold Spacebar for 100%',
                throttleAria: 'Throttle demand percentage',
                slowMo: 'Slow Mo',
                slowMoTitle: 'Toggle slow motion: 1x -> 2x -> 5x -> 10x -> Off',
                unitBtnTitle: 'Switch units between kW / Nm and hp / lb-ft',
                telRpm: 'CURRENT RPM',
                telUnits: 'MOTORS',
                telGeo: 'ARCHITECTURE',
                dynoTitle: 'EV DYNO CURVES',
                estPower: 'EST. POWER',
                estTorque: 'EST. TORQUE',
                powerWord: 'Power',
                torqueWord: 'Torque',
                engineOff: 'Motor off',
                standbyReady: 'Armed · 0 RPM (ready)',
                cursorPrefix: 'Cursor',
                liveBadge: 'REAL TIME',
                pageTitles: [
                    '1 · ARCHITECTURE & STATOR',
                    '2 · ROTOR & COOLING',
                    '3 · INVERTER, MAP & RPM',
                    '4 · EV SPECS & DYNO'
                ],
                pagePrevTitle: 'Previous page',
                pageNextTitle: 'Next page',
                topEngine: '← Electric Motor',
                topEngineTitle: 'Return to 3D Electric Motor model',
                topGearbox: 'EV Gearbox',
                topGearboxTitle: 'View standalone 3D EV Reducer / Gearbox model',
                topBattery: 'Battery',
                topBatteryTitle: 'View standalone 3D HV Battery Pack model',
                topAll: 'View All Together',
                topAllTitle: 'View Electric Motor, EV Reducer & HV Battery Pack together in 3D',
                viewEngineBtn: 'View Motor',
                gbPanelTitle: 'EV REDUCER & GEARBOX',
                lblGbType: 'REDUCER / GEARBOX TYPE',
                lblGbSpeeds: 'STAGES / SPEEDS',
                lblDiffType: 'DIFFERENTIAL / TV',
                lblGbFinal: 'FINAL REDUCTION',
                batPanelTitle: 'HV BATTERY PACK',
                lblCellFormat: 'CELL FORMAT',
                lblPackArch: 'PACK ARCHITECTURE',
                cellFormatOpts: {{
                    'Prismática': 'Prismatic Modules',
                    'Cilíndrica 4680': '4680 Cylindrical Array',
                    'Blade (Lâmina)': 'Blade (Cell-to-Pack)',
                    'Pouch (Bolsa)': 'Stacked Pouch Cells'
                }},
                cellFormatShort: {{
                    'Prismática': 'Prismatic',
                    'Cilíndrica 4680': '4680 Cyl.',
                    'Blade (Lâmina)': 'Blade CTP',
                    'Pouch (Bolsa)': 'Pouch'
                }},
                packArchOpts: {{
                    'Skateboard (Piso)': 'Flat Skateboard Tray',
                    'T-Pack Central': 'Central T-Pack Spine',
                    'Estrutural 800V': 'Structural Monocoque'
                }},
                packArchShort: {{
                    'Skateboard (Piso)': 'Skateboard',
                    'T-Pack Central': 'T-Pack',
                    'Estrutural 800V': 'Structural'
                }},
                gbTypeOpts: {{
                    'Redutor 1V Direto': '1-Speed Direct Reduction',
                    'Caixa EV 2V': '2-Speed EV (Taycan-Style)',
                    'E-CVT Planetária': 'Planetary E-CVT',
                    'Coaxial Direto': 'Concentric Coaxial Drive'
                }},
                gbTypeShort: {{
                    'Redutor 1V Direto': '1-Spd Red.',
                    'Caixa EV 2V': '2-Spd EV',
                    'E-CVT Planetária': 'E-CVT',
                    'Coaxial Direto': 'Coaxial'
                }},
                gbSpeedOpts: {{
                    '1': '1-Speed (Direct)',
                    '2': '2-Speed (Launch / Cruise)',
                    'Contínua': 'Stepless (Planetary)'
                }},
                gbSteplessLabel: 'Stepless',
                gbSteplessShort: 'Stepless',
                gbSpeedsEcvtTitle: 'Planetary E-CVT is continuously variable (no fixed gear ratios)',
                diffOpts: {{
                    'Diferencial Aberto': 'Open Differential',
                    'LSD Mecânico': 'Mechanical Clutch LSD',
                    'e-LSD Vetorizado': 'Active Torque-Vectoring e-LSD',
                    'Spool Direto': 'Locked Direct Spool'
                }},
                diffShort: {{
                    'Diferencial Aberto': 'Open',
                    'LSD Mecânico': 'LSD',
                    'e-LSD Vetorizado': 'e-LSD',
                    'Spool Direto': 'Spool'
                }},
                finalDriveOpts: {{
                    '6.80': '6.80:1 (High Speed)',
                    '8.20': '8.20:1 (Balanced)',
                    '9.73': '9.73:1 (Standard EV)',
                    '11.20': '11.20:1 (Launch)',
                    '13.50': '13.50:1 (Max Torque)'
                }},
                lblSumArch: 'EV ARCHITECTURE',
                lblSumDisp: 'STATOR & REGIME',
                lblSumAdm: 'BATTERY & EFFICIENCY',
                lblSumBuild: 'BUILD & THERMAL',
                lblTopology: 'TOPOLOGY',
                lblMotorType: 'MOTOR TYPE',
                lblStatorDiam: 'STATOR DIAM. (mm)',
                lblStackLen: 'STACK LENGTH (mm)',
                lblPoles: 'MAGNETIC POLES',
                lblWinding: 'WINDING',
                lblHousingMat: 'HOUSING MATERIAL',
                lblRotorType: 'ROTOR & MAGNETS',
                lblCooling: 'COOLING SYSTEM',
                lblBearingType: 'BEARINGS',
                lblFieldWeakening: 'FIELD WEAKENING',
                lblRegenMode: 'REGEN BRAKING',
                lblRotorMass: 'ROTOR MASS (kg)',
                rotorMassAria: 'Rotor assembly weight in kilograms (max 500 kg)',
                rotorIdealPrefix: 'Ideal',
                rotorIdealTitle: (motorTag, kg, statusTxt) => `Suggested for ${{motorTag}}: ${{kg}} kg (${{statusTxt}}) — click to apply`,
                rotorStatusOk: 'balanced inertia',
                rotorStatusLight: 'too light · reduced thermal mass',
                rotorStatusHeavy: 'heavier than ideal · slower rev response',
                lblVoltage: 'HV VOLTAGE (V)',
                lblInverter: 'INVERTER STAGE',
                lblCurrentLimit: 'PHASE CURRENT (A)',
                lblBatteryChem: 'BATTERY CHEMISTRY',
                lblBatteryKwh: 'BATTERY PACK (kWh)',
                lblDriveMode: 'DRIVE MAP',
                lblRpm: 'MAX ROTOR RPM',
                topologyOpts: {{
                    'Single': 'Single Motor (1x)',
                    'Dual': 'Dual Motor AWD (2x)',
                    'Tri': 'Tri Motor Vector (3x)',
                    'Quad': 'Quad Motor (4x)',
                    'In-Wheel': 'In-Wheel Hubs (4x)'
                }},
                motorTypeOpts: {{
                    'PMSM': 'PMSM (Permanent Magnet)',
                    'Induction AC': 'AC Induction (Squirrel Cage)',
                    'Axial Flux': 'Axial Flux (Disc YASA)',
                    'SynRM': 'Switched / EESM (Magnet-Free)'
                }},
                poleOpts: {{
                    '4': '4 Poles',
                    '6': '6 Poles',
                    '8': '8 Poles',
                    '12': '12 Poles',
                    '16': '16 Poles'
                }},
                windingOpts: {{
                    'Hairpin Cobre': 'Hairpin Copper Bars',
                    'Distribuído Litz': 'Distributed Copper Litz',
                    'Concentrado': 'Concentrated Wound Coils',
                    'Alumínio Leve': 'Copper-Clad Aluminum'
                }},
                windingShort: {{
                    'Hairpin Cobre': 'Hairpin',
                    'Distribuído Litz': 'Litz Cu',
                    'Concentrado': 'Concentrated',
                    'Alumínio Leve': 'Alu. Clad'
                }},
                housingOpts: {{
                    'Alumínio Fundido': 'Cast Aluminum',
                    'Alumínio Billet': 'CNC Billet Aluminum',
                    'Magnésio': 'Magnesium Alloy',
                    'Fibra de Carbono': 'Carbon Fiber Sleeve',
                    'Titânio': 'Titanium Housing'
                }},
                rotorOpts: {{
                    'Neodímio N52 (V-Shape)': 'Neodymium N52 (V-IPM)',
                    'Halbach Array': 'Halbach Magnet Array',
                    'Gaiola de Cobre': 'Copper Squirrel Cage',
                    'Rotor Bobinado (EESM)': 'Wound Field Rotor (EESM)',
                    'Manga Carbono (Alta RPM)': 'Carbon-Sleeved High-RPM'
                }},
                rotorShort: {{
                    'Neodímio N52 (V-Shape)': 'N52 V-IPM',
                    'Halbach Array': 'Halbach',
                    'Gaiola de Cobre': 'Cu Cage',
                    'Rotor Bobinado (EESM)': 'EESM Wound',
                    'Manga Carbono (Alta RPM)': 'Carbon Sleeve'
                }},
                coolingOpts: {{
                    'Ar (Aletas)': 'Air-Cooled Fins',
                    'Glicol (Camisa Água)': 'Liquid Glycol Jacket',
                    'Óleo Direto': 'Direct Oil Spray Cooling',
                    'Imersão Dielétrica': 'Dielectric Full Immersion'
                }},
                coolingShort: {{
                    'Ar (Aletas)': 'Air Fins',
                    'Glicol (Camisa Água)': 'Glycol',
                    'Óleo Direto': 'Direct Oil',
                    'Imersão Dielétrica': 'Dielectric'
                }},
                bearingOpts: {{
                    'Aço Padrão': 'Steel Ball Bearings',
                    'Cerâmica Si3N4': 'Hybrid Ceramic (Si3N4)',
                    'Magnético Ativo': 'Active Magnetic (Ultra-RPM)'
                }},
                fwOpts: {{
                    'Conservador': 'Conservative (Efficiency)',
                    'Equilibrado': 'Balanced (MTPA+FW)',
                    'Agressivo': 'Aggressive (High-RPM Top End)'
                }},
                regenOpts: {{
                    'Desligada': 'Off (Free Coast)',
                    'Standard (50 kW)': 'Standard (~50 kW)',
                    'One-Pedal Alta (180 kW)': 'One-Pedal High (~180 kW)',
                    'Track Regen (Max)': 'Track Regen (Max)'
                }},
                regenShort: {{
                    'Desligada': 'Off',
                    'Standard (50 kW)': '50 kW',
                    'One-Pedal Alta (180 kW)': '180 kW',
                    'Track Regen (Max)': 'Max'
                }},
                voltageOpts: {{
                    '400': '400 V (Standard EV)',
                    '800': '800 V (Performance HV)',
                    '900': '900 V (Ultra-HV)',
                    '1200': '1200 V (Track HV)'
                }},
                inverterOpts: {{
                    'IGBT Silício': 'Silicon IGBT',
                    'SiC Dual': 'Silicon Carbide (SiC)',
                    'SiC Racing 1200A': 'Dual-Stage SiC Track',
                    'GaN Alta Freq.': 'Gallium Nitride (GaN)'
                }},
                inverterShort: {{
                    'IGBT Silício': 'IGBT',
                    'SiC Dual': 'SiC Dual',
                    'SiC Racing 1200A': 'SiC Track',
                    'GaN Alta Freq.': 'GaN HV'
                }},
                batteryOpts: {{
                    'LFP (LiFePO4)': 'LFP (Lithium Iron)',
                    'NMC 811': 'NMC 811 (High Energy)',
                    'NCA Performance': 'NCA (High Discharge)',
                    'Estado Sólido': 'Solid-State Cell',
                    'Supercondensador': 'Hybrid Supercapacitor'
                }},
                driveModeOpts: {{
                    'Eco': 'Eco (70% Current)',
                    'Normal': 'Normal (Balanced)',
                    'Sport': 'Sport (Instant Response)',
                    'Ludicrous': 'Ludicrous (Overboost)'
                }},
                effWord: 'Eff.',
                regenWord: 'Regen',
                rotorWord: 'Rotor',
                reducerWord: 'Reducer',
                invWord: 'Inv.',
                warnTipSpeed: (v, lim) => `High rotor tip speed (${{v}} m/s > ${{lim}} m/s)`,
                warnBackEmf: (rpm, v) => `RPM exceeds ${{v}}V back-EMF ceiling (${{rpm}} RPM)`,
                warnThermal: (kw, cap) => `Thermal overload (${{kw}} kW/unit > ${{cap}} kW cooling limit)`
            }}
        }};

        /* ----------------------------------------------------------------------
           ESTADO DE SIMULAÇÃO EM TEMPO REAL (Ligar/Desligar + Acelerar + Dyno)
           ---------------------------------------------------------------------- */
        const engineSim = {{
            on: false,
            throttlePct: 0,
            spaceHeld: false,
            preSpaceThrottlePct: 0,
            currentRpm: 0,
            idleRpm: 0,
            maxRpm: 16000,
            inertiaFactor: 1.0,
            rotInertia: 0.14,
            slowMo: 1,
            unitMode: 'metric',
            dynoPoints: [],
            peakPowerKw: 402,
            peakPowerRpm: 10500,
            peakTorqueNm: 535,
            peakTorqueRpm: 0,
            baseRpm: 7200,
            effPct: 95.4,
            regenKw: 180,
            rotorIdealKg: 14.5,
            isRegening: false,
            hoverRpm: null
        }};

        function convertPower(kw) {{
            return engineSim.unitMode === 'imperial' ? (kw / 0.74569987) : kw;
        }}

        function convertTorque(nm) {{
            return engineSim.unitMode === 'imperial' ? (nm * 0.73756215) : nm;
        }}

        function powerUnitLabel() {{
            return engineSim.unitMode === 'imperial' ? 'hp' : 'kW';
        }}

        function torqueUnitLabel() {{
            return engineSim.unitMode === 'imperial' ? 'lb-ft' : 'Nm';
        }}

        function formatPowerStr(kw) {{
            return `${{Math.round(convertPower(kw))}} ${{powerUnitLabel()}}`;
        }}

        function formatTorqueStr(nm) {{
            return `${{Math.round(convertTorque(nm))}} ${{torqueUnitLabel()}}`;
        }}

        function syncUnitDisplays() {{
            const pStr = formatPowerStr(engineSim.peakPowerKw);
            const tStr = formatTorqueStr(engineSim.peakTorqueNm);
            if (btnUnitToggle) {{
                const isImp = engineSim.unitMode === 'imperial';
                btnUnitToggle.textContent = isImp ? 'hp / lb-ft' : 'kW / Nm';
                btnUnitToggle.classList.toggle('ativo', isImp);
                btnUnitToggle.setAttribute('aria-pressed', isImp ? 'true' : 'false');
            }}
            if (dynoEstPowerVal) dynoEstPowerVal.textContent = pStr;
            if (dynoEstTorqueVal) dynoEstTorqueVal.textContent = tStr;
            if (dynoEstPowerRpm) dynoEstPowerRpm.textContent = `@ ${{engineSim.peakPowerRpm}} RPM`;
            if (dynoEstTorqueRpm) {{
                const topPlateau = Math.max(engineSim.peakTorqueRpm, engineSim.baseRpm || engineSim.peakTorqueRpm);
                dynoEstTorqueRpm.textContent = `@ 0–${{topPlateau}} RPM`;
            }}
            if (dynoPeakBadge) dynoPeakBadge.textContent = `${{pStr}} · ${{tStr}}`;
            const t = I18N[currentLang];
            if (dynoLegendPower) dynoLegendPower.textContent = `${{t.powerWord}} (${{powerUnitLabel()}})`;
            if (dynoLegendTorque) dynoLegendTorque.textContent = `${{t.torqueWord}} (${{torqueUnitLabel()}})`;

            if (dynoLiveReadout) {{
                if (!engineSim.on && engineSim.currentRpm < 20) {{
                    if (engineSim.hoverRpm !== null) {{
                        const s = sampleDynoAtRpm(engineSim.hoverRpm);
                        dynoLiveReadout.textContent = `${{t.cursorPrefix}}: ${{Math.round(engineSim.hoverRpm)}} RPM · ${{formatPowerStr(s.powerKw)}} · ${{formatTorqueStr(s.torqueNm)}}`;
                    }} else {{
                        dynoLiveReadout.textContent = t.engineOff;
                    }}
                }} else if (engineSim.on && engineSim.currentRpm < 20 && engineSim.hoverRpm === null) {{
                    dynoLiveReadout.textContent = t.standbyReady;
                }} else {{
                    const refRpm = engineSim.hoverRpm !== null ? engineSim.hoverRpm : engineSim.currentRpm;
                    const s = sampleDynoAtRpm(refRpm);
                    dynoLiveReadout.textContent = `${{Math.round(refRpm)}} RPM · ${{formatPowerStr(s.powerKw)}} · ${{formatTorqueStr(s.torqueNm)}}`;
                }}
            }}
            drawDynoChart();
        }}

        const TOPOLOGY_UNIT_COUNTS = {{
            'Single': 1,
            'Dual': 2,
            'Tri': 3,
            'Quad': 4,
            'In-Wheel': 4
        }};

        function syncMotorAndRotorUI(motorChanged = false) {{
            if (!selectMotorType || !selectRotorType) return;
            const mType = selectMotorType.value || 'PMSM';
            if (motorChanged) {{
                if (mType === 'Induction AC') {{
                    selectRotorType.value = 'Gaiola de Cobre';
                }} else if (mType === 'SynRM') {{
                    selectRotorType.value = 'Rotor Bobinado (EESM)';
                }} else if (mType === 'Axial Flux') {{
                    selectRotorType.value = (savedRotorForPmsm === 'Gaiola de Cobre' || savedRotorForPmsm === 'Rotor Bobinado (EESM)')
                        ? 'Halbach Array'
                        : savedRotorForPmsm;
                }} else {{
                    selectRotorType.value = (savedRotorForPmsm && savedRotorForPmsm !== 'Gaiola de Cobre' && savedRotorForPmsm !== 'Rotor Bobinado (EESM)')
                        ? savedRotorForPmsm
                        : 'Neodímio N52 (V-Shape)';
                }}
            }} else if (mType === 'PMSM' || mType === 'Axial Flux') {{
                if (selectRotorType.value !== 'Gaiola de Cobre' && selectRotorType.value !== 'Rotor Bobinado (EESM)') {{
                    savedRotorForPmsm = selectRotorType.value;
                }}
            }}
        }}

        function setActivePage(pageIdx) {{
            const clamped = Math.max(0, Math.min(3, pageIdx | 0));
            currentPageIdx = clamped;
            const t = I18N[currentLang];
            const isLast = clamped === 3;
            const showDyno = clamped === 2 || clamped === 3;
            const isCompactDyno = clamped === 2;
            for (let i = 0; i < 4; i++) {{
                const pg = document.getElementById(`cfg-page-${{i}}`);
                const dot = document.getElementById(`page-dot-${{i}}`);
                if (pg) pg.classList.toggle('ativo', i === clamped);
                if (dot) {{
                    dot.classList.toggle('ativo', i === clamped);
                    dot.setAttribute('aria-current', i === clamped ? 'page' : 'false');
                }}
            }}
            if (cfgPageTitle && t.pageTitles && t.pageTitles[clamped]) {{
                cfgPageTitle.textContent = t.pageTitles[clamped];
            }}
            if (btnPagePrev) btnPagePrev.disabled = (clamped === 0);
            if (btnPageNext) btnPageNext.disabled = isLast;
            if (dashboardMain) {{
                dashboardMain.classList.toggle('dyno-hidden', !showDyno);
                dashboardMain.classList.toggle('dyno-compact', isCompactDyno);
            }}
            if (motor3D && typeof motor3D.setRightPanelVisible === 'function') {{
                motor3D.setRightPanelVisible(showDyno, isCompactDyno);
            }}
            if (showDyno) {{
                drawDynoChart();
                if (typeof requestAnimationFrame === 'function') {{
                    requestAnimationFrame(() => drawDynoChart());
                }}
            }}
        }}

        function applyLanguage() {{
            const t = I18N[currentLang];
            document.documentElement.lang = currentLang;
            const setTxt = (id, val) => {{ const el = document.getElementById(id); if (el) el.textContent = val; }};
            setTxt('btn-3d-autorotate', t.autoRotate);
            setTxt('btn-3d-reset', t.resetView);
            setTxt('motor-3d-hint', t.hint);
            setTxt('lbl-throttle-pos', t.throttleLabel);
            setTxt('lbl-tel-rpm', t.telRpm);
            setTxt('lbl-tel-units', t.telUnits);
            setTxt('lbl-tel-geo', t.telGeo);
            setTxt('dyno-title', t.dynoTitle);
            setTxt('lbl-est-power', t.estPower);
            setTxt('lbl-est-torque', t.estTorque);
            setTxt('cfg-live-badge', t.liveBadge);
            setTxt('lbl-sum-arch', t.lblSumArch);
            setTxt('lbl-sum-disp', t.lblSumDisp);
            setTxt('lbl-sum-adm', t.lblSumAdm);
            setTxt('lbl-sum-build', t.lblSumBuild);
            if (cfgPageTitle && t.pageTitles && t.pageTitles[currentPageIdx]) {{
                cfgPageTitle.textContent = t.pageTitles[currentPageIdx];
            }}
            if (btnPagePrev) {{
                btnPagePrev.title = t.pagePrevTitle;
                btnPagePrev.setAttribute('aria-label', t.pagePrevTitle);
            }}
            if (btnPageNext) {{
                btnPageNext.title = t.pageNextTitle;
                btnPageNext.setAttribute('aria-label', t.pageNextTitle);
            }}
            setTxt('lbl-topology', t.lblTopology);
            setTxt('lbl-motor-type', t.lblMotorType);
            setTxt('lbl-stator-diam', t.lblStatorDiam);
            setTxt('lbl-stack-len', t.lblStackLen);
            setTxt('lbl-poles', t.lblPoles);
            setTxt('lbl-winding', t.lblWinding);
            setTxt('lbl-housing-mat', t.lblHousingMat);
            setTxt('lbl-rotor-type', t.lblRotorType);
            setTxt('lbl-cooling', t.lblCooling);
            setTxt('lbl-bearing-type', t.lblBearingType);
            setTxt('lbl-field-weakening', t.lblFieldWeakening);
            setTxt('lbl-regen-mode', t.lblRegenMode);
            setTxt('lbl-rotor-mass', t.lblRotorMass);
            if (inputRotorMass) inputRotorMass.setAttribute('aria-label', t.rotorMassAria);
            setTxt('lbl-voltage', t.lblVoltage);
            setTxt('lbl-inverter', t.lblInverter);
            setTxt('lbl-current-limit', t.lblCurrentLimit);
            setTxt('lbl-battery-chem', t.lblBatteryChem);
            setTxt('lbl-battery-kwh', t.lblBatteryKwh);
            setTxt('lbl-drive-mode', t.lblDriveMode);
            setTxt('lbl-rpm', t.lblRpm);

            if (btnLangToggle) {{
                btnLangToggle.textContent = t.langBtn;
                btnLangToggle.title = t.langBtnTitle;
                btnLangToggle.classList.toggle('ativo', currentLang === 'en');
                btnLangToggle.setAttribute('aria-pressed', currentLang === 'en' ? 'true' : 'false');
            }}
            if (btnCutaway) {{
                const isCut = motor3D ? motor3D.cutaway : true;
                btnCutaway.textContent = isCut ? t.cutawayOn : t.cutawayOff;
                btnCutaway.title = t.cutawayTitle;
            }}
            if (btnAutoRotate3D) btnAutoRotate3D.title = t.autoRotateTitle;
            if (btnReset3D) btnReset3D.title = t.resetViewTitle;
            if (throttleControlWrap) throttleControlWrap.title = t.throttleTitle;
            if (rangeThrottle) rangeThrottle.setAttribute('aria-label', t.throttleAria);
            if (btnUnitToggle) btnUnitToggle.title = t.unitBtnTitle;
            if (btnSlowMo) btnSlowMo.title = t.slowMoTitle;
            if (btnSlowMoLabel) {{
                btnSlowMoLabel.textContent = engineSim.slowMo > 1 ? `${{t.slowMo}} ${{engineSim.slowMo}}x` : t.slowMo;
            }}
            const mapOpts = (sel, dict) => {{
                if (!sel || !dict) return;
                Array.from(sel.options).forEach(opt => {{ if (dict[opt.value]) opt.textContent = dict[opt.value]; }});
            }};
            mapOpts(selectTopology, t.topologyOpts);
            mapOpts(selectMotorType, t.motorTypeOpts);
            mapOpts(selectPoles, t.poleOpts);
            mapOpts(selectWinding, t.windingOpts);
            mapOpts(selectHousingMat, t.housingOpts);
            mapOpts(selectRotorType, t.rotorOpts);
            mapOpts(selectCooling, t.coolingOpts);
            mapOpts(selectBearingType, t.bearingOpts);
            mapOpts(selectFieldWeakening, t.fwOpts);
            mapOpts(selectRegenMode, t.regenOpts);
            mapOpts(selectVoltage, t.voltageOpts);
            mapOpts(selectInverter, t.inverterOpts);
            mapOpts(selectBatteryChem, t.batteryOpts);
            mapOpts(selectDriveMode, t.driveModeOpts);
            mapOpts(selectGearboxType, t.gbTypeOpts);
            mapOpts(selectGearboxSpeeds, t.gbSpeedOpts);
            mapOpts(selectDiffType, t.diffOpts);
            mapOpts(selectFinalDrive, t.finalDriveOpts);
            mapOpts(selectCellFormat, t.cellFormatOpts);
            mapOpts(selectPackArch, t.packArchOpts);

            setTxt('gb-panel-title', t.gbPanelTitle);
            setTxt('lbl-gb-type', t.lblGbType);
            setTxt('lbl-gb-speeds', t.lblGbSpeeds);
            setTxt('lbl-diff-type', t.lblDiffType);
            setTxt('lbl-gb-final', t.lblGbFinal);
            setTxt('bat-panel-title', t.batPanelTitle);
            setTxt('lbl-cell-format', t.lblCellFormat);
            setTxt('lbl-pack-arch', t.lblPackArch);
            setTxt('btn-top-engine', t.topEngine);
            setTxt('btn-top-all', t.topAll);
            setTxt('btn-gb-back-engine', t.viewEngineBtn);
            setTxt('btn-bat-back-engine', t.viewEngineBtn);
            if (btnTopEngine) btnTopEngine.title = t.topEngineTitle;
            if (btnTopGearbox) btnTopGearbox.title = t.topGearboxTitle;
            if (btnTopBattery) btnTopBattery.title = t.topBatteryTitle;
            if (btnTopAll) btnTopAll.title = t.topAllTitle;

            syncSubsystemUI();
            syncEnginePowerUI();
            atualizarMotor3D();
            atualizarWidget3();
        }}

        if (btnLangToggle) {{
            btnLangToggle.addEventListener('click', () => {{
                currentLang = currentLang === 'pt' ? 'en' : 'pt';
                applyLanguage();
            }});
        }}

        if (btnUnitToggle) {{
            btnUnitToggle.addEventListener('click', () => {{
                engineSim.unitMode = engineSim.unitMode === 'metric' ? 'imperial' : 'metric';
                syncUnitDisplays();
            }});
        }}

        if (btnSlowMo) {{
            btnSlowMo.addEventListener('click', () => {{
                engineSim.slowMo = engineSim.slowMo === 1 ? 2 : (engineSim.slowMo === 2 ? 5 : (engineSim.slowMo === 5 ? 10 : 1));
                const ativo = engineSim.slowMo > 1;
                btnSlowMo.classList.toggle('slow-ativo', ativo);
                btnSlowMo.setAttribute('aria-pressed', ativo ? 'true' : 'false');
                if (btnSlowMoLabel) {{
                    const t = I18N[currentLang];
                    btnSlowMoLabel.textContent = ativo ? `${{t.slowMo}} ${{engineSim.slowMo}}x` : t.slowMo;
                }}
            }});
        }}

        function smoothstep(e0, e1, x) {{
            const t = Math.max(0, Math.min(1, (x - e0) / Math.max(1e-6, e1 - e0)));
            return t * t * (3 - 2 * t);
        }}

        function computeIdealRotorKg(params) {{
            const dM = Math.max(0.10, (Number(params.stator_diam) || 240) / 1000.0);
            const lM = Math.max(0.03, (Number(params.stack_len) || 165) / 1000.0);
            const cylVolRatio = (dM * dM * lM) / (0.24 * 0.24 * 0.165);
            const mTypeMult = {{
                'PMSM': 1.00,
                'Induction AC': 1.18,
                'Axial Flux': 0.62,
                'SynRM': 0.94
            }}[params.motor_type] || 1.00;
            const rTypeMult = {{
                'Neodímio N52 (V-Shape)': 1.00,
                'Halbach Array': 0.96,
                'Gaiola de Cobre': 1.12,
                'Rotor Bobinado (EESM)': 1.05,
                'Manga Carbono (Alta RPM)': 0.84
            }}[params.rotor_type] || 1.00;
            const maxR = Math.max(3000, Number(params.max_rpm) || 16000);
            const rpmMult = Math.max(0.68, Math.min(1.18, 1.05 - (maxR - 14000) * 0.000018));
            const rawIdeal = 14.5 * Math.pow(Math.max(0.18, cylVolRatio), 0.78) * mTypeMult * rTypeMult * rpmMult;
            return Math.round(Math.max(1.0, Math.min(500.0, rawIdeal)) * 2.0) / 2.0;
        }}

        function computeRotorMassStats(params) {{
            const idealKg = computeIdealRotorKg(params);
            const rawM = Number(params.rotor_mass);
            const rotorMass = (Number.isFinite(rawM) && rawM > 0) ? Math.max(1.0, Math.min(500.0, rawM)) : idealKg;
            const mRatio = rotorMass / Math.max(1.0, idealKg);
            const mInertia = rotorMass >= idealKg
                ? (1.0 + (rotorMass - idealKg) * 0.042)
                : Math.max(0.62, 1.0 - (1.0 - mRatio) * 0.30);
            const tipStressPenalty = mRatio > 1.5 ? Math.min(35.0, (mRatio - 1.5) * 18.0) : (mRatio >= 0.8 && mRatio <= 1.25 ? -5.0 : 0.0);
            let status = 'ok';
            if (mRatio < 0.72) status = mRatio < 0.48 ? 'alert' : 'warn';
            else if (mRatio > 1.45) status = mRatio > 2.20 ? 'alert' : 'warn';
            return {{ idealKg, rotorMass, mRatio, mInertia, tipStressPenalty, status }};
        }}

        function syncRotorSuggestionUI(params) {{
            const p = params || readEnginePayload();
            const stats = computeRotorMassStats(p);
            engineSim.rotorIdealKg = stats.idealKg;
            if (!btnRotorIdeal) return;
            const t = I18N[currentLang];
            const motorTag = `${{p.motor_type}} · Ø${{Math.round(p.stator_diam)}}×${{Math.round(p.stack_len)}}mm`;
            const statusTxt = stats.status === 'ok'
                ? t.rotorStatusOk
                : (stats.mRatio < 0.72 ? t.rotorStatusLight : t.rotorStatusHeavy);
            const idealStr = stats.idealKg.toFixed(1);
            btnRotorIdeal.textContent = `${{t.rotorIdealPrefix}}: ${{idealStr}} kg`;
            btnRotorIdeal.title = t.rotorIdealTitle(motorTag, idealStr, statusTxt);
            btnRotorIdeal.dataset.idealKg = idealStr;
            btnRotorIdeal.classList.remove('warn', 'alert');
            if (stats.status === 'warn' || stats.status === 'alert') {{
                btnRotorIdeal.classList.add(stats.status);
            }}
        }}

        function computeDynoData(params) {{
            const topoMult = {{
                'Single':   {{ units: 1, tqScale: 1.00, pwrBus: 1.00 }},
                'Dual':     {{ units: 2, tqScale: 1.88, pwrBus: 1.65 }},
                'Tri':      {{ units: 3, tqScale: 2.70, pwrBus: 2.25 }},
                'Quad':     {{ units: 4, tqScale: 3.45, pwrBus: 2.80 }},
                'In-Wheel': {{ units: 4, tqScale: 3.15, pwrBus: 2.40 }}
            }}[params.topology] || {{ units: 1, tqScale: 1.00, pwrBus: 1.00 }};

            const mTypeMap = {{
                'PMSM':         {{ tq: 1.00, eff: 0.962, fwKeep: 0.94, lowSlip: 1.00 }},
                'Induction AC': {{ tq: 0.88, eff: 0.928, fwKeep: 0.88, lowSlip: 0.88 }},
                'Axial Flux':   {{ tq: 1.24, eff: 0.968, fwKeep: 0.91, lowSlip: 1.00 }},
                'SynRM':        {{ tq: 0.92, eff: 0.945, fwKeep: 0.86, lowSlip: 0.96 }}
            }}[params.motor_type] || {{ tq: 1.00, eff: 0.962, fwKeep: 0.94, lowSlip: 1.00 }};

            const rotorMap = {{
                'Neodímio N52 (V-Shape)':   {{ tq: 1.02, eff: 1.000 }},
                'Halbach Array':            {{ tq: 1.12, eff: 1.010 }},
                'Gaiola de Cobre':          {{ tq: 0.90, eff: 0.970 }},
                'Rotor Bobinado (EESM)':    {{ tq: 0.95, eff: 0.985 }},
                'Manga Carbono (Alta RPM)': {{ tq: 1.08, eff: 1.010 }}
            }}[params.rotor_type] || {{ tq: 1.02, eff: 1.000 }};

            const windingMap = {{
                'Hairpin Cobre':    {{ tq: 1.06, eff: 1.012 }},
                'Distribuído Litz': {{ tq: 1.00, eff: 1.002 }},
                'Concentrado':      {{ tq: 0.97, eff: 0.995 }},
                'Alumínio Leve':    {{ tq: 0.88, eff: 0.980 }}
            }}[params.winding] || {{ tq: 1.06, eff: 1.012 }};

            const poleTqMap = {{ 4: 0.94, 6: 0.98, 8: 1.00, 12: 1.05, 16: 1.09 }};
            const poleTq = poleTqMap[parseInt(params.poles, 10)] || 1.00;

            const invMap = {{
                'IGBT Silício':     {{ eff: 0.960, gain: 0.93 }},
                'SiC Dual':         {{ eff: 0.986, gain: 1.00 }},
                'SiC Racing 1200A': {{ eff: 0.989, gain: 1.08 }},
                'GaN Alta Freq.':   {{ eff: 0.992, gain: 1.04 }}
            }}[params.inverter] || {{ eff: 0.986, gain: 1.00 }};

            const battMap = {{
                'LFP (LiFePO4)':    {{ crate: 4.5, sag: 0.95 }},
                'NMC 811':          {{ crate: 6.8, sag: 1.00 }},
                'NCA Performance':  {{ crate: 8.2, sag: 1.03 }},
                'Estado Sólido':    {{ crate: 10.0, sag: 1.06 }},
                'Supercondensador': {{ crate: 14.0, sag: 1.09 }}
            }}[params.battery_chem] || {{ crate: 6.8, sag: 1.00 }};

            const driveModeMap = {{
                'Eco':       {{ tq: 0.72, pwr: 0.70 }},
                'Normal':    {{ tq: 1.00, pwr: 1.00 }},
                'Sport':     {{ tq: 1.08, pwr: 1.12 }},
                'Ludicrous': {{ tq: 1.22, pwr: 1.28 }}
            }}[params.drive_mode] || {{ tq: 1.00, pwr: 1.00 }};

            const fwMap = {{
                'Conservador': 0.84,
                'Equilibrado': 0.96,
                'Agressivo':   1.08
            }}[params.field_weakening] || 0.96;

            const coolingBonus = {{
                'Ar (Aletas)':          0.92,
                'Glicol (Camisa Água)': 1.00,
                'Óleo Direto':          1.04,
                'Imersão Dielétrica':   1.07
            }}[params.cooling] || 1.00;

            const gbEffMap = {{
                'Redutor 1V Direto': {{ tq: 0.988, hp: 0.988, in: 1.00 }},
                'Caixa EV 2V':       {{ tq: 1.065, hp: 0.982, in: 1.12 }},
                'E-CVT Planetária':  {{ tq: 1.020, hp: 0.965, in: 0.94 }},
                'Coaxial Direto':    {{ tq: 0.995, hp: 0.994, in: 0.88 }}
            }}[params.gearbox_type] || {{ tq: 0.988, hp: 0.988, in: 1.00 }};

            const diffEffMap = {{
                'Diferencial Aberto': 0.994,
                'LSD Mecânico':       0.986,
                'e-LSD Vetorizado':   0.992,
                'Spool Direto':       0.996
            }}[params.diff_type] || 0.994;

            const rotorStats = computeRotorMassStats(params);
            engineSim.rotorIdealKg = rotorStats.idealKg;
            engineSim.inertiaFactor = gbEffMap.in * rotorStats.mInertia;

            const diamScale = Math.pow((Number(params.stator_diam) || 240) / 240.0, 2);
            const stackScale = (Number(params.stack_len) || 165) / 165.0;
            const currentRatio = Math.sqrt(Math.max(0.25, Math.min(2.6, (Number(params.current_limit) || 650) / 650.0)));
            const effTotal = Math.min(0.985, mTypeMap.eff * rotorMap.eff * windingMap.eff * invMap.eff * gbEffMap.hp * diffEffMap);

            const unitPeakTorque = 495.0 * diamScale * stackScale * mTypeMap.tq * rotorMap.tq * windingMap.tq * poleTq * currentRatio * driveModeMap.tq;
            const shaftPeakTorque = Math.round(unitPeakTorque * topoMult.tqScale * battMap.sag * gbEffMap.tq * diffEffMap);

            const busVolts = Math.max(200, Number(params.voltage) || 800);
            const busAmps = Math.max(100, Math.min(2400, Number(params.current_limit) || 650));
            const invPowerCeilingKw = (busVolts * busAmps / 1000.0) * topoMult.pwrBus * invMap.gain * driveModeMap.pwr * coolingBonus * 0.86;
            const packPowerCeilingKw = (Math.max(20, Number(params.battery_kwh) || 85) * battMap.crate) * effTotal * (params.drive_mode === 'Ludicrous' ? 1.12 : 1.00);
            const elecPowerCeilingKw = Math.min(invPowerCeilingKw, packPowerCeilingKw);

            const maxRpm = Math.max(3000, Number(params.max_rpm) || 16000);
            const startRpm = 0;
            const steps = 50;

            const raw = [];
            let bestP = {{ val: 0, rpm: maxRpm }};
            let bestT = {{ val: 0, rpm: 0 }};

            const baseSpeedRpm = Math.max(1200, Math.min(maxRpm * 0.88, (elecPowerCeilingKw * 9549.3) / Math.max(40, shaftPeakTorque)));
            const vHeadroom = (busVolts / 800.0) * fwMap * (params.gearbox_type === 'Caixa EV 2V' ? 1.14 : 1.00);

            for (let i = 0; i <= steps; i++) {{
                const rpm = startRpm + (maxRpm - startRpm) * (i / steps);
                const u = rpm / maxRpm;
                const omega = (rpm * Math.PI * 2.0) / 60.0;

                let tqFactor = 1.0;
                if (mTypeMap.lowSlip < 0.99 && rpm < 950) {{
                    const lowMix = smoothstep(0, 950, rpm);
                    tqFactor = mTypeMap.lowSlip + (1.0 - mTypeMap.lowSlip) * lowMix;
                }}
                let torqueNm = shaftPeakTorque * tqFactor;
                if (rpm > baseSpeedRpm) {{
                    const pwrAtRpmKw = elecPowerCeilingKw * (1.0 - Math.max(0, u - 0.72) * (0.24 / Math.max(0.55, vHeadroom * mTypeMap.fwKeep)));
                    const fwTorqueNm = (pwrAtRpmKw * 9549.3) / Math.max(1, rpm);
                    torqueNm = Math.min(torqueNm, Math.max(shaftPeakTorque * 0.14, fwTorqueNm));
                }}
                const dragDrop = 1.0 - Math.max(0, u - 0.85) * 0.35;
                torqueNm = Math.max(15, torqueNm * dragDrop);

                const powerKw = (torqueNm * omega) / 1000.0;
                raw.push({{ rpm, torqueNm, powerKw }});
                if (powerKw >= bestP.val) bestP = {{ val: powerKw, rpm }};
                if (torqueNm >= bestT.val) bestT = {{ val: torqueNm, rpm }};
            }}

            const regenMap = {{
                'Desligada': 0,
                'Standard (50 kW)': 50,
                'One-Pedal Alta (180 kW)': 180,
                'Track Regen (Max)': Math.round(Math.min(450, bestP.val * 0.55))
            }};
            const regenKw = regenMap[params.regen_mode] !== undefined ? regenMap[params.regen_mode] : 180;

            engineSim.rotInertia = Math.max(0.055, (0.075 + (rotorStats.rotorMass / 14.5) * 0.045) * Math.max(0.55, Math.min(6.0, engineSim.inertiaFactor || 1.0)));
            engineSim.maxRpm = maxRpm;
            engineSim.idleRpm = 0;
            engineSim.dynoPoints = raw;
            engineSim.peakPowerKw = Math.round(bestP.val);
            engineSim.peakPowerRpm = Math.round(bestP.rpm);
            engineSim.peakTorqueNm = Math.round(bestT.val);
            engineSim.peakTorqueRpm = Math.round(bestT.rpm);
            engineSim.baseRpm = Math.round(baseSpeedRpm);
            engineSim.effPct = Math.round(effTotal * 1000) / 10;
            engineSim.regenKw = regenKw;

            syncUnitDisplays();
            updateRpmRedlineVisual(engineSim.currentRpm);
        }}

        function sampleDynoAtRpm(rpm) {{
            const pts = engineSim.dynoPoints;
            if (!pts.length) return {{ powerKw: 0, torqueNm: 0 }};
            if (rpm <= pts[0].rpm) {{
                return {{ powerKw: pts[0].powerKw, torqueNm: pts[0].torqueNm }};
            }}
            if (rpm >= pts[pts.length - 1].rpm) {{
                const last = pts[pts.length - 1];
                return {{ powerKw: last.powerKw, torqueNm: last.torqueNm }};
            }}
            for (let i = 0; i < pts.length - 1; i++) {{
                const a = pts[i], b = pts[i + 1];
                if (rpm >= a.rpm && rpm <= b.rpm) {{
                    const t = (rpm - a.rpm) / Math.max(1, b.rpm - a.rpm);
                    return {{
                        powerKw: a.powerKw + (b.powerKw - a.powerKw) * t,
                        torqueNm: a.torqueNm + (b.torqueNm - a.torqueNm) * t
                    }};
                }}
            }}
            return {{ powerKw: 0, torqueNm: 0 }};
        }}

        function niceAxisMax(val) {{
            const target = Math.max(16, val * 1.12);
            const stepRaw = target / 4;
            const mag = Math.pow(10, Math.floor(Math.log10(stepRaw)));
            const norm = stepRaw / mag;
            let niceStep = 1;
            if (norm <= 1.2) niceStep = 1;
            else if (norm <= 2.5) niceStep = 2.5;
            else if (norm <= 5.0) niceStep = 5;
            else niceStep = 10;
            return Math.ceil(target / (niceStep * mag * 4)) * (niceStep * mag * 4);
        }}

        function getDynoChartPadding(cw, ch) {{
            const compact = cw < 320 || ch < 175;
            return {{
                compact,
                padL: compact ? 33 : 42,
                padR: compact ? 33 : 42,
                padT: compact ? 15 : 18,
                padB: compact ? 25 : 34
            }};
        }}

        function drawDynoChart() {{
            if (!dynoCanvas) return;
            const wrap = dynoCanvas.parentElement;
            const rect = wrap.getBoundingClientRect();
            if (!rect.width || !rect.height) return;
            const dpr = Math.min(window.devicePixelRatio || 1, 2);
            const w = Math.max(1, Math.round(rect.width * dpr));
            const h = Math.max(1, Math.round(rect.height * dpr));
            if (dynoCanvas.width !== w || dynoCanvas.height !== h) {{
                dynoCanvas.width = w;
                dynoCanvas.height = h;
            }}

            const ctx = dynoCanvas.getContext('2d');
            if (!ctx) return;
            ctx.save();
            ctx.scale(dpr, dpr);
            const cw = rect.width;
            const ch = rect.height;
            ctx.clearRect(0, 0, cw, ch);

            const {{ compact, padL, padR, padT, padB }} = getDynoChartPadding(cw, ch);
            const pw = Math.max(40, cw - padL - padR);
            const ph = Math.max(40, ch - padT - padB);
            const pts = engineSim.dynoPoints;
            if (!pts.length) {{ ctx.restore(); return; }}

            const minRpm = pts[0].rpm;
            const maxRpm = pts[pts.length - 1].rpm;
            const peakPDisp = convertPower(engineSim.peakPowerKw);
            const peakTDisp = convertTorque(engineSim.peakTorqueNm);
            const maxPowerAxis = niceAxisMax(peakPDisp);
            const maxTorqueAxis = niceAxisMax(peakTDisp);

            const xOf = rpm => padL + ((rpm - minRpm) / Math.max(1, maxRpm - minRpm)) * pw;
            const yPower = p => padT + ph - (p / maxPowerAxis) * ph;
            const yTorque = t => padT + ph - (t / maxTorqueAxis) * ph;

            ctx.strokeStyle = 'rgba(255, 255, 255, 0.07)';
            ctx.lineWidth = 1;
            ctx.font = compact ? '600 8.5px "JetBrains Mono", monospace' : '600 9.5px "JetBrains Mono", monospace';
            ctx.fillStyle = 'rgba(248, 113, 113, 0.90)';
            ctx.textAlign = 'right';
            ctx.fillText(powerUnitLabel(), padL - 5, padT - 4);
            ctx.fillStyle = 'rgba(212, 155, 75, 0.92)';
            ctx.textAlign = 'left';
            ctx.fillText(torqueUnitLabel(), padL + pw + 5, padT - 4);

            ctx.font = compact ? '600 8.5px "JetBrains Mono", monospace' : '600 10px "JetBrains Mono", monospace';
            const rowsY = compact ? 2 : 4;
            for (let g = 0; g <= rowsY; g++) {{
                const gy = padT + (ph * g) / rowsY;
                ctx.beginPath();
                ctx.moveTo(padL, gy);
                ctx.lineTo(padL + pw, gy);
                ctx.stroke();

                const pVal = Math.round(maxPowerAxis * (1 - g / rowsY));
                const tVal = Math.round(maxTorqueAxis * (1 - g / rowsY));
                ctx.fillStyle = 'rgba(248, 113, 113, 0.82)';
                ctx.textAlign = 'right';
                ctx.fillText(String(pVal), padL - 5, gy + 3);

                ctx.fillStyle = 'rgba(212, 155, 75, 0.85)';
                ctx.textAlign = 'left';
                ctx.fillText(String(tVal), padL + pw + 5, gy + 3);
            }}

            // Eixo X simplificado (×1000 RPM: 0, 4, 8, 12...)
            let stepRpm = maxRpm > 20000 ? 5000 : (maxRpm > 12000 ? 4000 : (maxRpm > 7000 ? 2000 : 1000));
            if (compact && pw < 215) {{
                stepRpm = maxRpm > 18000 ? 6000 : (maxRpm > 10000 ? 4000 : 2000);
            }}
            const firstTick = Math.ceil(minRpm / stepRpm) * stepRpm;
            ctx.fillStyle = '#9ca3af';
            ctx.textAlign = 'center';
            for (let rVal = firstTick; rVal <= maxRpm; rVal += stepRpm) {{
                const gx = xOf(rVal);
                ctx.beginPath();
                ctx.moveTo(gx, padT);
                ctx.lineTo(gx, padT + ph);
                ctx.stroke();
                ctx.fillText(String(Math.round(rVal / 1000)), gx, padT + ph + (compact ? 11 : 13));
            }}
            ctx.font = compact ? '600 8px "JetBrains Mono", monospace' : '600 9px "JetBrains Mono", monospace';
            ctx.fillStyle = '#6b7280';
            ctx.fillText(compact ? 'RPM ×1k' : 'RPM (×1000)', padL + pw * 0.5, ch - (compact ? 3 : 4));

            // Área sutil sob a curva de potência
            const gradArea = ctx.createLinearGradient(0, padT, 0, padT + ph);
            gradArea.addColorStop(0, 'rgba(239, 68, 68, 0.24)');
            gradArea.addColorStop(1, 'rgba(239, 68, 68, 0.01)');
            ctx.beginPath();
            pts.forEach((p, idx) => {{
                const x = xOf(p.rpm), y = yPower(convertPower(p.powerKw));
                if (idx === 0) ctx.moveTo(x, y); else ctx.lineTo(x, y);
            }});
            ctx.lineTo(xOf(pts[pts.length - 1].rpm), padT + ph);
            ctx.lineTo(xOf(pts[0].rpm), padT + ph);
            ctx.closePath();
            ctx.fillStyle = gradArea;
            ctx.fill();

            // Curva de Binário
            ctx.beginPath();
            pts.forEach((p, idx) => {{
                const x = xOf(p.rpm), y = yTorque(convertTorque(p.torqueNm));
                if (idx === 0) ctx.moveTo(x, y); else ctx.lineTo(x, y);
            }});
            ctx.strokeStyle = '#d49b4b';
            ctx.lineWidth = compact ? 1.8 : 2.2;
            ctx.stroke();

            // Curva de Potência
            ctx.beginPath();
            pts.forEach((p, idx) => {{
                const x = xOf(p.rpm), y = yPower(convertPower(p.powerKw));
                if (idx === 0) ctx.moveTo(x, y); else ctx.lineTo(x, y);
            }});
            ctx.strokeStyle = '#ef4444';
            ctx.lineWidth = compact ? 2.1 : 2.5;
            ctx.stroke();

            // Marcador ao vivo (hover ou rotação atual do motor)
            const activeRpm = engineSim.hoverRpm !== null
                ? engineSim.hoverRpm
                : (engineSim.on ? Math.max(minRpm, engineSim.currentRpm) : null);

            if (activeRpm !== null) {{
                const clamped = Math.max(minRpm, Math.min(maxRpm, activeRpm));
                const mx = xOf(clamped);
                const sample = sampleDynoAtRpm(clamped);

                ctx.save();
                ctx.setLineDash([4, 4]);
                ctx.strokeStyle = 'rgba(255, 255, 255, 0.42)';
                ctx.lineWidth = 1.2;
                ctx.beginPath();
                ctx.moveTo(mx, padT);
                ctx.lineTo(mx, padT + ph);
                ctx.stroke();
                ctx.restore();

                const py = yPower(convertPower(sample.powerKw));
                const ty = yTorque(convertTorque(sample.torqueNm));

                ctx.fillStyle = '#d49b4b';
                ctx.beginPath(); ctx.arc(mx, ty, compact ? 3.3 : 4.2, 0, Math.PI * 2); ctx.fill();
                ctx.strokeStyle = '#07090d'; ctx.lineWidth = 1.5; ctx.stroke();

                ctx.fillStyle = '#ef4444';
                ctx.beginPath(); ctx.arc(mx, py, compact ? 3.6 : 4.6, 0, Math.PI * 2); ctx.fill();
                ctx.strokeStyle = '#07090d'; ctx.lineWidth = 1.5; ctx.stroke();
            }}

            ctx.restore();
        }}

        if (dynoCanvas) {{
            dynoCanvas.addEventListener('pointermove', e => {{
                const rect = dynoCanvas.getBoundingClientRect();
                const pts = engineSim.dynoPoints;
                if (!pts.length || !rect.width) return;
                const {{ padL, padR }} = getDynoChartPadding(rect.width, rect.height);
                const pw = Math.max(40, rect.width - padL - padR);
                const frac = Math.max(0, Math.min(1, (e.clientX - rect.left - padL) / pw));
                const minRpm = pts[0].rpm;
                const maxRpm = pts[pts.length - 1].rpm;
                engineSim.hoverRpm = minRpm + (maxRpm - minRpm) * frac;
                drawDynoChart();
            }});
            dynoCanvas.addEventListener('pointerleave', () => {{
                engineSim.hoverRpm = null;
                drawDynoChart();
            }});
            if (typeof ResizeObserver !== 'undefined' && dynoCanvas.parentElement) {{
                new ResizeObserver(() => drawDynoChart()).observe(dynoCanvas.parentElement);
            }}
        }}

        /* ----------------------------------------------------------------------
           MOTOR 3D INTERATIVO EM WEBGL (Detalhado, estático na rotação, auto-contido)
           ---------------------------------------------------------------------- */
        class Motor3DViewer {{
            constructor(canvas) {{
                this.canvas = canvas;
                this.gl = canvas.getContext('webgl', {{ antialias: true, alpha: true }})
                    || canvas.getContext('experimental-webgl', {{ antialias: true, alpha: true }});

                this.config = {{
                    topology: 'Single',
                    motorType: 'PMSM',
                    statorDiam: 240,
                    stackLen: 165,
                    poles: 8,
                    winding: 'Hairpin Cobre',
                    housingMat: 'Alumínio Fundido',
                    rotorType: 'Neodímio N52 (V-Shape)',
                    cooling: 'Glicol (Camisa Água)',
                    bearingType: 'Aço Padrão',
                    fieldWeakening: 'Equilibrado',
                    regenMode: 'One-Pedal Alta (180 kW)',
                    rotorMass: 14.5,
                    voltage: 800,
                    inverter: 'SiC Dual',
                    currentLimit: 650,
                    batteryChem: 'NMC 811',
                    batteryKwh: 85,
                    cellFormat: 'Prismática',
                    packArch: 'Skateboard (Piso)',
                    driveMode: 'Normal',
                    maxRpm: 16000,
                    viewMode: 'engine',
                    gearboxType: 'Redutor 1V Direto',
                    gearboxSpeeds: '1',
                    diffType: 'Diferencial Aberto',
                    finalDrive: 9.73
                }};

                this.hvPaths = [];
                this.energyPhase = 0;

                this.cutaway = true;
                this.autoRotate = false;

                const isDesktop = window.innerWidth > 1020;
                this.defaultCam = {{
                    yaw: -0.66,
                    pitch: 0.40,
                    zoom: 1.0,
                    panX: 0.0,
                    panY: isDesktop ? 0.04 : 0.12
                }};
                this.cam = {{ ...this.defaultCam }};
                this.targetCam = {{ ...this.defaultCam }};
                this.baseDist = 7.4;
                this.sceneCenterX = 0;

                this.crankAngle = 0;
                this.lastTime = performance.now();
                this.pointers = new Map();
                this.lastPinchDist = 0;

                this.staticOpaque = [];
                this.staticTrans = [];
                this.dynamicEvRotors = [];
                this.dynamicRotors = [];

                if (this.gl) {{
                    this.initGL();
                }}
                this.bindEvents();
                this.rebuildScene();
                this.resize();
                this.loop(performance.now());
            }}

            initGL() {{
                const gl = this.gl;
                const vsSrc = `
                    attribute vec3 aPos;
                    attribute vec3 aNorm;
                    uniform mat4 uViewProj;
                    uniform mat4 uModel;
                    uniform mat3 uNormalMat;
                    varying vec3 vNorm;
                    varying vec3 vWorldPos;
                    void main() {{
                        vec4 wp = uModel * vec4(aPos, 1.0);
                        vWorldPos = wp.xyz;
                        vNorm = normalize(uNormalMat * aNorm);
                        gl_Position = uViewProj * wp;
                    }}
                `;
                const fsSrc = `
                    precision mediump float;
                    varying vec3 vNorm;
                    varying vec3 vWorldPos;
                    uniform vec4 uColor;
                    uniform vec2 uSpec;
                    uniform vec3 uCamPos;
                    void main() {{
                        vec3 N = normalize(vNorm);
                        vec3 V = normalize(uCamPos - vWorldPos);
                        vec3 R = reflect(-V, N);
                        vec3 L1 = normalize(vec3(0.55, 0.88, 0.65));
                        vec3 L2 = normalize(vec3(-0.78, 0.35, -0.55));
                        vec3 L3 = normalize(vec3(0.15, -0.65, 0.72));

                        float metal = clamp((uSpec.x - 0.32) / 0.58, 0.0, 1.0);
                        float rough = clamp(1.0 - (uSpec.y - 10.0) / 72.0, 0.08, 0.92);

                        float latheGrain = sin(vWorldPos.x * 115.0 + vWorldPos.z * 28.0) * 0.5 + 0.5;
                        float castNoise = fract(sin(dot(floor(vWorldPos * 90.0), vec3(12.9898, 78.233, 37.719))) * 43758.5453);
                        float microTex = mix((castNoise - 0.5) * 0.055, (latheGrain - 0.5) * 0.042, step(0.56, uSpec.x));
                        vec3 baseCol = clamp(uColor.rgb * (1.0 + microTex), 0.0, 1.0);

                        float vertAo = mix(0.68, 1.0, smoothstep(-1.35, 0.75, vWorldPos.y));
                        float cavAo = mix(0.76, 1.0, smoothstep(-0.65, 0.45, N.y));
                        float ao = vertAo * cavAo;

                        float hemi = 0.5 + 0.5 * N.y;
                        vec3 ambient = mix(vec3(0.22, 0.25, 0.31), vec3(0.72, 0.77, 0.85), hemi);
                        float diff1 = max(dot(N, L1), 0.0);
                        float diff2 = max(dot(N, L2), 0.0);
                        float diff3 = max(dot(N, L3), 0.0);

                        vec3 H1 = normalize(L1 + V);
                        vec3 H2 = normalize(L2 + V);
                        float shin = max(4.0, uSpec.y);
                        float spec1 = pow(max(dot(N, H1), 1e-4), shin) * uSpec.x * 1.25;
                        float spec2 = pow(max(dot(N, H2), 1e-4), max(2.0, shin * 0.55)) * uSpec.x * 0.50;

                        float skyRef = smoothstep(0.08 - rough * 0.25, 0.85, R.y) * smoothstep(-0.2, 0.8, 1.0 - abs(R.z));
                        float sideStrip = smoothstep(0.25, 0.92, abs(R.x)) * (1.0 - rough * 0.55);
                        float floorBounce = smoothstep(0.15, -0.75, R.y) * 0.35;
                        vec3 envCol = mix(vec3(0.12, 0.14, 0.18), vec3(0.95, 0.97, 1.0), skyRef)
                                    + vec3(0.55, 0.68, 0.82) * (sideStrip * 0.28)
                                    + vec3(0.32, 0.28, 0.24) * floorBounce;

                        float ndotv = clamp(dot(N, V), 0.0, 1.0);
                        float fres = pow(clamp(1.0 - ndotv, 1e-4, 1.0), 3.0);
                        vec3 F0 = mix(vec3(0.04), baseCol, metal);
                        vec3 fresTint = F0 + (vec3(1.0) - F0) * fres;

                        float diffGain = mix(1.0, 0.66, metal);
                        vec3 specTint = mix(vec3(1.0), baseCol * 0.62 + vec3(0.38), metal);
                        vec3 col = baseCol * (ambient * 0.42 + (diff1 * 0.78 + diff2 * 0.36 + diff3 * 0.20) * diffGain) * ao
                                 + specTint * (spec1 * 1.15 + spec2 * 0.95)
                                 + envCol * fresTint * (0.14 + 0.38 * metal) * ao
                                 + vec3(0.76, 0.86, 1.0) * (fres * (0.12 + 0.18 * uSpec.x));
                        gl_FragColor = vec4(col, uColor.a);
                    }}
                `;

                const compile = (type, src) => {{
                    const s = gl.createShader(type);
                    if (!s) return null;
                    gl.shaderSource(s, src);
                    gl.compileShader(s);
                    if (!gl.getShaderParameter(s, gl.COMPILE_STATUS)) {{
                        console.error('WebGL shader compile error:', gl.getShaderInfoLog(s));
                        gl.deleteShader(s);
                        return null;
                    }}
                    return s;
                }};
                const vs = compile(gl.VERTEX_SHADER, vsSrc);
                const fs = compile(gl.FRAGMENT_SHADER, fsSrc);
                const prog = (vs && fs) ? gl.createProgram() : null;
                if (!prog) {{
                    this.gl = null;
                    return;
                }}
                gl.attachShader(prog, vs);
                gl.attachShader(prog, fs);
                gl.linkProgram(prog);
                if (!gl.getProgramParameter(prog, gl.LINK_STATUS)) {{
                    console.error('WebGL program link error:', gl.getProgramInfoLog(prog));
                    this.gl = null;
                    return;
                }}
                gl.useProgram(prog);

                this.prog = prog;
                this.loc = {{
                    aPos: gl.getAttribLocation(prog, 'aPos'),
                    aNorm: gl.getAttribLocation(prog, 'aNorm'),
                    uViewProj: gl.getUniformLocation(prog, 'uViewProj'),
                    uModel: gl.getUniformLocation(prog, 'uModel'),
                    uNormalMat: gl.getUniformLocation(prog, 'uNormalMat'),
                    uColor: gl.getUniformLocation(prog, 'uColor'),
                    uSpec: gl.getUniformLocation(prog, 'uSpec'),
                    uCamPos: gl.getUniformLocation(prog, 'uCamPos')
                }};

                gl.enableVertexAttribArray(this.loc.aPos);
                gl.enableVertexAttribArray(this.loc.aNorm);
                gl.enable(gl.DEPTH_TEST);
                gl.enable(gl.CULL_FACE);

                this.meshes = {{
                    box: this.makeMesh(this.buildBoxData()),
                    bevelBox: this.makeMesh(this.buildBevelBoxData(0.08)),
                    cyl: this.makeMesh(this.buildCylinderData(32, 1.0, 1.0)),
                    cone: this.makeMesh(this.buildCylinderData(32, 1.0, 0.54)),
                    hex: this.makeMesh(this.buildCylinderData(6, 1.0, 1.0)),
                    gear: this.makeMesh(this.buildGearData(20, 0.88, 1.04)),
                    torus: this.makeMesh(this.buildTorusData(32, 16, 0.42)),
                    sphere: this.makeMesh(this.buildSphereData(12, 16)),
                    spring: this.makeMesh(this.buildHelixSpringData(4.0, 36, 6)),
                    impeller: this.makeMesh(this.buildImpellerData(7))
                }};
            }}

            buildGearData(teeth, rRoot, rTip) {{
                const pos = [], norm = [], idx = [];
                const pts = [];
                for (let t = 0; t < teeth; t++) {{
                    const a0 = (t / teeth) * Math.PI * 2;
                    const da = (Math.PI * 2) / teeth;
                    pts.push([a0 + da * 0.00, rRoot]);
                    pts.push([a0 + da * 0.22, rTip]);
                    pts.push([a0 + da * 0.50, rTip]);
                    pts.push([a0 + da * 0.72, rRoot]);
                }}
                for (let i = 0; i < pts.length; i++) {{
                    const p0 = pts[i], p1 = pts[(i + 1) % pts.length];
                    const x0 = Math.cos(p0[0]) * p0[1], z0 = Math.sin(p0[0]) * p0[1];
                    const x1 = Math.cos(p1[0]) * p1[1], z1 = Math.sin(p1[0]) * p1[1];
                    const dx = x1 - x0, dz = z1 - z0;
                    const nl = Math.hypot(dx, dz) || 1;
                    const nx = dz / nl, nz = -dx / nl;
                    const b0 = [x0, -0.5, z0], t0 = [x0, 0.5, z0], t1 = [x1, 0.5, z1], b1 = [x1, -0.5, z1];
                    pos.push(...b0, ...t0, ...t1, ...b0, ...t1, ...b1);
                    for (let k = 0; k < 6; k++) norm.push(nx, 0, nz);
                    pos.push(0, 0.5, 0, ...t1, ...t0);
                    for (let k = 0; k < 3; k++) norm.push(0, 1, 0);
                    pos.push(0, -0.5, 0, ...b0, ...b1);
                    for (let k = 0; k < 3; k++) norm.push(0, -1, 0);
                }}
                for (let i = 0; i < pos.length / 3; i++) idx.push(i);
                return {{ pos, norm, idx }};
            }}

            makeMesh(data) {{
                const gl = this.gl;
                const posData = data.pos || data.positions;
                const normData = data.norm || data.normals;
                let idxData = data.idx;
                if (!idxData && posData) {{
                    const vCount = posData.length / 3;
                    idxData = new Uint16Array(vCount);
                    for (let i = 0; i < vCount; i++) idxData[i] = i;
                }}
                const posBuf = gl.createBuffer();
                gl.bindBuffer(gl.ARRAY_BUFFER, posBuf);
                gl.bufferData(gl.ARRAY_BUFFER, posData instanceof Float32Array ? posData : new Float32Array(posData), gl.STATIC_DRAW);

                const normBuf = gl.createBuffer();
                gl.bindBuffer(gl.ARRAY_BUFFER, normBuf);
                gl.bufferData(gl.ARRAY_BUFFER, normData instanceof Float32Array ? normData : new Float32Array(normData), gl.STATIC_DRAW);

                const idxBuf = gl.createBuffer();
                gl.bindBuffer(gl.ELEMENT_ARRAY_BUFFER, idxBuf);
                gl.bufferData(gl.ELEMENT_ARRAY_BUFFER, idxData instanceof Uint16Array ? idxData : new Uint16Array(idxData), gl.STATIC_DRAW);

                return {{ posBuf, normBuf, idxBuf, count: idxData.length }};
            }}


            buildBoxData() {{
                const pos = [
                    -0.5,-0.5, 0.5,  0.5,-0.5, 0.5,  0.5, 0.5, 0.5, -0.5, 0.5, 0.5,
                     0.5,-0.5,-0.5, -0.5,-0.5,-0.5, -0.5, 0.5,-0.5,  0.5, 0.5,-0.5,
                    -0.5, 0.5, 0.5,  0.5, 0.5, 0.5,  0.5, 0.5,-0.5, -0.5, 0.5,-0.5,
                    -0.5,-0.5,-0.5,  0.5,-0.5,-0.5,  0.5,-0.5, 0.5, -0.5,-0.5, 0.5,
                     0.5,-0.5, 0.5,  0.5,-0.5,-0.5,  0.5, 0.5,-0.5,  0.5, 0.5, 0.5,
                    -0.5,-0.5,-0.5, -0.5,-0.5, 0.5, -0.5, 0.5, 0.5, -0.5, 0.5,-0.5
                ];
                const norm = [
                     0, 0, 1,  0, 0, 1,  0, 0, 1,  0, 0, 1,
                     0, 0,-1,  0, 0,-1,  0, 0,-1,  0, 0,-1,
                     0, 1, 0,  0, 1, 0,  0, 1, 0,  0, 1, 0,
                     0,-1, 0,  0,-1, 0,  0,-1, 0,  0,-1, 0,
                     1, 0, 0,  1, 0, 0,  1, 0, 0,  1, 0, 0,
                    -1, 0, 0, -1, 0, 0, -1, 0, 0, -1, 0, 0
                ];
                const idx = [];
                for (let f = 0; f < 6; f++) {{
                    const o = f * 4;
                    idx.push(o, o + 1, o + 2, o, o + 2, o + 3);
                }}
                return {{ pos, norm, idx }};
            }}

            buildCylinderData(segs, rBot, rTop) {{
                const pos = [];
                const norm = [];
                const idx = [];
                const slope = rBot - rTop;
                const nLen = Math.hypot(1, slope);

                for (let i = 0; i <= segs; i++) {{
                    const a = (i / segs) * Math.PI * 2;
                    const ca = Math.cos(a);
                    const sa = Math.sin(a);
                    const nx = ca / nLen;
                    const ny = slope / nLen;
                    const nz = sa / nLen;

                    pos.push(ca * rBot, -0.5, sa * rBot);
                    norm.push(nx, ny, nz);
                    pos.push(ca * rTop, 0.5, sa * rTop);
                    norm.push(nx, ny, nz);
                }}
                for (let i = 0; i < segs; i++) {{
                    const b0 = i * 2;
                    const t0 = b0 + 1;
                    const b1 = b0 + 2;
                    const t1 = b0 + 3;
                    idx.push(b0, t0, t1, b0, t1, b1);
                }}

                const topCenter = pos.length / 3;
                pos.push(0, 0.5, 0);
                norm.push(0, 1, 0);
                const topStart = pos.length / 3;
                for (let i = 0; i <= segs; i++) {{
                    const a = (i / segs) * Math.PI * 2;
                    pos.push(Math.cos(a) * rTop, 0.5, Math.sin(a) * rTop);
                    norm.push(0, 1, 0);
                }}
                for (let i = 0; i < segs; i++) {{
                    idx.push(topCenter, topStart + i + 1, topStart + i);
                }}

                const botCenter = pos.length / 3;
                pos.push(0, -0.5, 0);
                norm.push(0, -1, 0);
                const botStart = pos.length / 3;
                for (let i = 0; i <= segs; i++) {{
                    const a = (i / segs) * Math.PI * 2;
                    pos.push(Math.cos(a) * rBot, -0.5, Math.sin(a) * rBot);
                    norm.push(0, -1, 0);
                }}
                for (let i = 0; i < segs; i++) {{
                    idx.push(botCenter, botStart + i, botStart + i + 1);
                }}

                return {{ pos, norm, idx }};
            }}

            buildTorusData(majSegs, minSegs, rTube) {{
                const pos = [];
                const norm = [];
                const idx = [];
                const R = 1.0;

                for (let i = 0; i <= majSegs; i++) {{
                    const u = (i / majSegs) * Math.PI * 2;
                    const cu = Math.cos(u);
                    const su = Math.sin(u);
                    for (let j = 0; j <= minSegs; j++) {{
                        const v = (j / minSegs) * Math.PI * 2;
                        const cv = Math.cos(v);
                        const sv = Math.sin(v);
                        const x = (R + rTube * cv) * cu;
                        const y = (R + rTube * cv) * su;
                        const z = rTube * sv;
                        pos.push(x, y, z);
                        norm.push(cv * cu, cv * su, sv);
                    }}
                }}
                const stride = minSegs + 1;
                for (let i = 0; i < majSegs; i++) {{
                    for (let j = 0; j < minSegs; j++) {{
                        const p00 = i * stride + j;
                        const p10 = (i + 1) * stride + j;
                        const p01 = p00 + 1;
                        const p11 = p10 + 1;
                        idx.push(p00, p10, p11, p00, p11, p01);
                    }}
                }}
                return {{ pos, norm, idx }};
            }}

            buildSphereData(latSegs, lonSegs) {{
                const pos = [];
                const norm = [];
                const idx = [];
                for (let i = 0; i <= latSegs; i++) {{
                    const th = (i / latSegs) * Math.PI;
                    const sth = Math.sin(th), cth = Math.cos(th);
                    for (let j = 0; j <= lonSegs; j++) {{
                        const ph = (j / lonSegs) * Math.PI * 2;
                        const x = sth * Math.cos(ph);
                        const y = cth;
                        const z = sth * Math.sin(ph);
                        pos.push(x, y, z);
                        norm.push(x, y, z);
                    }}
                }}
                const stride = lonSegs + 1;
                for (let i = 0; i < latSegs; i++) {{
                    for (let j = 0; j < lonSegs; j++) {{
                        const a = i * stride + j;
                        const b = a + 1;
                        const c = (i + 1) * stride + j;
                        const d = c + 1;
                        idx.push(a, b, c, b, d, c);
                    }}
                }}
                return {{ pos, norm, idx }};
            }}

            pushCheckedTri(pos, norm, p0, p1, p2, outDir) {{
                const ax = p1[0] - p0[0], ay = p1[1] - p0[1], az = p1[2] - p0[2];
                const bx = p2[0] - p0[0], by = p2[1] - p0[1], bz = p2[2] - p0[2];
                const cx = ay * bz - az * by, cy = az * bx - ax * bz, cz = ax * by - ay * bx;
                const d = cx * outDir[0] + cy * outDir[1] + cz * outDir[2];
                const nLen = Math.hypot(outDir[0], outDir[1], outDir[2]) || 1;
                const nx = outDir[0] / nLen, ny = outDir[1] / nLen, nz = outDir[2] / nLen;
                if (d >= 0) {{
                    pos.push(...p0, ...p1, ...p2);
                }} else {{
                    pos.push(...p0, ...p2, ...p1);
                }}
                for (let k = 0; k < 3; k++) norm.push(nx, ny, nz);
            }}

            pushCheckedQuad(pos, norm, p0, p1, p2, p3, outDir) {{
                this.pushCheckedTri(pos, norm, p0, p1, p2, outDir);
                this.pushCheckedTri(pos, norm, p0, p2, p3, outDir);
            }}

            buildBevelBoxData(bev = 0.08) {{
                const pos = [], norm = [], idx = [];
                const h = 0.5, d = 0.5 - Math.max(0.02, Math.min(0.18, bev));
                const faces = [
                    {{ n: [ 1, 0, 0], pts: [[ h,-d, d],[ h,-d,-d],[ h, d,-d],[ h, d, d]] }},
                    {{ n: [-1, 0, 0], pts: [[-h,-d,-d],[-h,-d, d],[-h, d, d],[-h, d,-d]] }},
                    {{ n: [ 0, 1, 0], pts: [[-d, h, d],[ d, h, d],[ d, h,-d],[-d, h,-d]] }},
                    {{ n: [ 0,-1, 0], pts: [[-d,-h,-d],[ d,-h,-d],[ d,-h, d],[-d,-h, d]] }},
                    {{ n: [ 0, 0, 1], pts: [[-d,-d, h],[ d,-d, h],[ d, d, h],[-d, d, h]] }},
                    {{ n: [ 0, 0,-1], pts: [[ d,-d,-h],[-d,-d,-h],[-d, d,-h],[ d, d,-h]] }}
                ];
                for (const f of faces) {{
                    this.pushCheckedQuad(pos, norm, f.pts[0], f.pts[1], f.pts[2], f.pts[3], f.n);
                }}
                for (const sy of [-1, 1]) {{
                    for (const sz of [-1, 1]) {{
                        this.pushCheckedQuad(pos, norm, [-d, sy * h, sz * d], [d, sy * h, sz * d], [d, sy * d, sz * h], [-d, sy * d, sz * h], [0, sy, sz]);
                    }}
                }}
                for (const sx of [-1, 1]) {{
                    for (const sz of [-1, 1]) {{
                        this.pushCheckedQuad(pos, norm, [sx * h, -d, sz * d], [sx * h, d, sz * d], [sx * d, d, sz * h], [sx * d, -d, sz * h], [sx, 0, sz]);
                    }}
                }}
                for (const sx of [-1, 1]) {{
                    for (const sy of [-1, 1]) {{
                        this.pushCheckedQuad(pos, norm, [sx * h, sy * d, -d], [sx * h, sy * d, d], [sx * d, sy * h, d], [sx * d, sy * h, -d], [sx, sy, 0]);
                    }}
                }}
                for (const sx of [-1, 1]) {{
                    for (const sy of [-1, 1]) {{
                        for (const sz of [-1, 1]) {{
                            this.pushCheckedTri(pos, norm, [sx * h, sy * d, sz * d], [sx * d, sy * h, sz * d], [sx * d, sy * d, sz * h], [sx, sy, sz]);
                        }}
                    }}
                }}
                for (let i = 0; i < pos.length / 3; i++) idx.push(i);
                return {{ pos, norm, idx }};
            }}

            buildHelixSpringData(coils = 4.0, pathSegs = 36, tubeSegs = 6) {{
                const pos = [], norm = [], idx = [];
                const R = 0.84, r = 0.14;
                const spine = (t) => {{
                    const a = t * coils * Math.PI * 2;
                    return [R * Math.cos(a), t - 0.5, R * Math.sin(a), a];
                }};
                const rings = [];
                for (let i = 0; i <= pathSegs; i++) {{
                    const t = i / pathSegs;
                    const [px, py, pz, a] = spine(t);
                    const pPrev = spine(Math.max(0, t - 0.01));
                    const pNext = spine(Math.min(1, t + 0.01));
                    let tx = pNext[0] - pPrev[0], ty = pNext[1] - pPrev[1], tz = pNext[2] - pPrev[2];
                    const tLen = Math.hypot(tx, ty, tz) || 1;
                    tx /= tLen; ty /= tLen; tz /= tLen;
                    const rx0 = Math.cos(a), ry0 = 0, rz0 = Math.sin(a);
                    const dot = rx0 * tx + ry0 * ty + rz0 * tz;
                    let ux = rx0 - tx * dot, uy = ry0 - ty * dot, uz = rz0 - tz * dot;
                    const uLen = Math.hypot(ux, uy, uz) || 1;
                    ux /= uLen; uy /= uLen; uz /= uLen;
                    const bx = ty * uz - tz * uy, by = tz * ux - tx * uz, bz = tx * uy - ty * ux;
                    const ring = [];
                    for (let j = 0; j < tubeSegs; j++) {{
                        const ph = (j / tubeSegs) * Math.PI * 2;
                        const cp = Math.cos(ph), sp = Math.sin(ph);
                        const nx = cp * ux + sp * bx, ny = cp * uy + sp * by, nz = cp * uz + sp * bz;
                        ring.push({{ p: [px + r * nx, py + r * ny, pz + r * nz], n: [nx, ny, nz] }});
                    }}
                    rings.push(ring);
                }}
                for (let i = 0; i < pathSegs; i++) {{
                    for (let j = 0; j < tubeSegs; j++) {{
                        const jn = (j + 1) % tubeSegs;
                        const v00 = rings[i][j], v10 = rings[i + 1][j], v11 = rings[i + 1][jn], v01 = rings[i][jn];
                        const avgN = [
                            v00.n[0] + v10.n[0] + v11.n[0] + v01.n[0],
                            v00.n[1] + v10.n[1] + v11.n[1] + v01.n[1],
                            v00.n[2] + v10.n[2] + v11.n[2] + v01.n[2]
                        ];
                        this.pushCheckedQuad(pos, norm, v00.p, v10.p, v11.p, v01.p, avgN);
                    }}
                }}
                for (let i = 0; i < pos.length / 3; i++) idx.push(i);
                return {{ pos, norm, idx }};
            }}

            buildImpellerData(blades = 7) {{
                const pos = [], norm = [], idx = [];
                for (let b = 0; b < blades; b++) {{
                    const a0 = (b / blades) * Math.PI * 2;
                    const aTip = a0 + 0.38;
                    const rIn = 0.24, rOut = 0.96, th = 0.04;
                    const nx = Math.sin(a0 + 0.2), nz = -Math.cos(a0 + 0.2);
                    const ax = Math.cos(a0) * rIn, az = Math.sin(a0) * rIn;
                    const bx = Math.cos(aTip) * rOut, bz = Math.sin(aTip) * rOut;
                    const offX = nx * th, offZ = nz * th;
                    const pA = [ax - offX, 0.36, az - offZ], pB = [bx - offX, -0.32, bz - offZ];
                    const pC = [bx + offX, -0.32, bz + offZ], pD = [ax + offX, 0.36, az + offZ];
                    const bA = [ax - offX, -0.45, az - offZ], bB = [bx - offX, -0.45, bz - offZ];
                    const bC = [bx + offX, -0.45, bz + offZ], bD = [ax + offX, -0.45, az + offZ];
                    this.pushCheckedQuad(pos, norm, pA, pB, pC, pD, [nx * 0.2, 1.0, nz * 0.2]);
                    this.pushCheckedQuad(pos, norm, bA, pA, pD, bD, [-Math.cos(a0), 0, -Math.sin(a0)]);
                    this.pushCheckedQuad(pos, norm, bB, bC, pC, pB, [Math.cos(aTip), 0, Math.sin(aTip)]);
                    this.pushCheckedQuad(pos, norm, pA, bA, bB, pB, [-nx, 0.2, -nz]);
                    this.pushCheckedQuad(pos, norm, pD, pC, bC, bD, [nx, 0.2, nz]);
                }}
                for (let i = 0; i < pos.length / 3; i++) idx.push(i);
                return {{ pos, norm, idx }};
            }}

            matMul(a, b) {{
                const o = new Float32Array(16);
                for (let c = 0; c < 4; c++) {{
                    const b0 = b[c * 4], b1 = b[c * 4 + 1], b2 = b[c * 4 + 2], b3 = b[c * 4 + 3];
                    o[c * 4]     = a[0] * b0 + a[4] * b1 + a[8]  * b2 + a[12] * b3;
                    o[c * 4 + 1] = a[1] * b0 + a[5] * b1 + a[9]  * b2 + a[13] * b3;
                    o[c * 4 + 2] = a[2] * b0 + a[6] * b1 + a[10] * b2 + a[14] * b3;
                    o[c * 4 + 3] = a[3] * b0 + a[7] * b1 + a[11] * b2 + a[15] * b3;
                }}
                return o;
            }}

            matPersp(fov, aspect, near, far) {{
                const f = 1.0 / Math.tan(fov * 0.5);
                const nf = 1.0 / (near - far);
                const m = new Float32Array(16);
                m[0] = f / aspect;
                m[5] = f;
                m[10] = (far + near) * nf;
                m[11] = -1;
                m[14] = 2 * far * near * nf;
                return m;
            }}

            matLookAt(eye, target, up) {{
                let zx = eye[0] - target[0], zy = eye[1] - target[1], zz = eye[2] - target[2];
                let len = Math.hypot(zx, zy, zz) || 1;
                zx /= len; zy /= len; zz /= len;

                let xx = up[1] * zz - up[2] * zy;
                let xy = up[2] * zx - up[0] * zz;
                let xz = up[0] * zy - up[1] * zx;
                len = Math.hypot(xx, xy, xz) || 1;
                xx /= len; xy /= len; xz /= len;

                const yx = zy * xz - zz * xy;
                const yy = zz * xx - zx * xz;
                const yz = zx * xy - zy * xx;

                const m = new Float32Array(16);
                m[0] = xx; m[4] = xy; m[8]  = xz; m[12] = -(xx * eye[0] + xy * eye[1] + xz * eye[2]);
                m[1] = yx; m[5] = yy; m[9]  = yz; m[13] = -(yx * eye[0] + yy * eye[1] + yz * eye[2]);
                m[2] = zx; m[6] = zy; m[10] = zz; m[14] = -(zx * eye[0] + zy * eye[1] + zz * eye[2]);
                m[15] = 1;
                return m;
            }}

            matTRS(tx, ty, tz, rx, ry, rz, sx, sy, sz) {{
                const cx = Math.cos(rx), sxr = Math.sin(rx);
                const cy = Math.cos(ry), syr = Math.sin(ry);
                const cz = Math.cos(rz), szr = Math.sin(rz);

                const m = new Float32Array(16);
                m[0] = (cy * cz) * sx;
                m[1] = (cy * szr) * sx;
                m[2] = (-syr) * sx;
                m[4] = (sxr * syr * cz - cx * szr) * sy;
                m[5] = (sxr * syr * szr + cx * cz) * sy;
                m[6] = (sxr * cy) * sy;
                m[8] = (cx * syr * cz + sxr * szr) * sz;
                m[9] = (cx * syr * szr - sxr * cz) * sz;
                m[10] = (cx * cy) * sz;
                m[12] = tx;
                m[13] = ty;
                m[14] = tz;
                m[15] = 1;
                return m;
            }}

            // Orienta primeiro a geometria no eixo X e só depois gira exclusivamente em torno do eixo X
            matSpinX(tx, ty, tz, spinX, rx0, ry0, rz0, sx, sy, sz) {{
                const local = this.matTRS(0, 0, 0, rx0, ry0, rz0, sx, sy, sz);
                const rot = this.matTRS(tx, ty, tz, spinX, 0, 0, 1, 1, 1);
                return this.matMul(rot, local);
            }}

            matAxisAngle(tx, ty, tz, ax, ay, az, ang, sx, sy, sz) {{
                const len = Math.hypot(ax, ay, az) || 1;
                const x = ax / len, y = ay / len, z = az / len;
                const c = Math.cos(ang), s = Math.sin(ang), t = 1 - c;
                const m = new Float32Array(16);
                m[0] = (t * x * x + c) * sx;
                m[1] = (t * x * y + s * z) * sx;
                m[2] = (t * x * z - s * y) * sx;
                m[4] = (t * x * y - s * z) * sy;
                m[5] = (t * y * y + c) * sy;
                m[6] = (t * y * z + s * x) * sy;
                m[8] = (t * x * z + s * y) * sz;
                m[9] = (t * y * z - s * x) * sz;
                m[10] = (t * z * z + c) * sz;
                m[12] = tx; m[13] = ty; m[14] = tz; m[15] = 1;
                return m;
            }}

            normalMat3(m) {{
                const a00 = m[0], a01 = m[4], a02 = m[8];
                const a10 = m[1], a11 = m[5], a12 = m[9];
                const a20 = m[2], a21 = m[6], a22 = m[10];

                const c00 =  (a11 * a22 - a12 * a21);
                const c01 = -(a10 * a22 - a12 * a20);
                const c02 =  (a10 * a21 - a11 * a20);
                const c10 = -(a01 * a22 - a02 * a21);
                const c11 =  (a00 * a22 - a02 * a20);
                const c12 = -(a00 * a21 - a01 * a20);
                const c20 =  (a01 * a12 - a02 * a11);
                const c21 = -(a00 * a12 - a02 * a10);
                const c22 =  (a00 * a11 - a01 * a10);

                const det = a00 * c00 + a01 * c01 + a02 * c02 || 1;
                return new Float32Array([
                    c00 / det, c10 / det, c20 / det,
                    c01 / det, c11 / det, c21 / det,
                    c02 / det, c12 / det, c22 / det
                ]);
            }}

            setConfig(cfg) {{
                this.config = {{ ...this.config, ...cfg }};
                this.rebuildScene();
            }}

            addPart(targetList, type, model, color, spec = [0.48, 38]) {{
                targetList.push({{ type, model, color, spec }});
            }}

            addPipe(targetList, points, radius, color, spec = [0.62, 52], couplerIndices = [], smooth = true) {{
                const C_COUPLER = [0.14, 0.19, 0.28, 1.0];
                const C_CLAMP = [0.82, 0.86, 0.90, 1.0];
                const addSeg = (p1, p2, r, col, sp) => {{
                    const dx = p2[0] - p1[0], dy = p2[1] - p1[1], dz = p2[2] - p1[2];
                    const len = Math.hypot(dx, dy, dz);
                    if (len < 0.001) return;
                    const ux = dx / len, uy = dy / len, uz = dz / len;
                    const mx = (p1[0] + p2[0]) * 0.5, my = (p1[1] + p2[1]) * 0.5, mz = (p1[2] + p2[2]) * 0.5;
                    const ax = uz, az = -ux;
                    const axisLen = Math.hypot(ax, az);
                    const m = (axisLen < 1e-4)
                        ? this.matTRS(mx, my, mz, uy < 0 ? Math.PI : 0, 0, 0, r, len, r)
                        : this.matAxisAngle(mx, my, mz, ax, 0, az, Math.acos(Math.max(-1, Math.min(1, uy))), r, len, r);
                    this.addPart(targetList, 'cyl', m, col, sp);
                }};

                for (const ci of couplerIndices) {{
                    if (ci >= 0 && ci < points.length - 1) {{
                        const p1 = points[ci], p2 = points[ci + 1];
                        const len = Math.hypot(p2[0] - p1[0], p2[1] - p1[1], p2[2] - p1[2]);
                        if (len > 0.16) {{
                            const mx = (p1[0] + p2[0]) * 0.5, my = (p1[1] + p2[1]) * 0.5, mz = (p1[2] + p2[2]) * 0.5;
                            const u = [(p2[0] - p1[0]) / len, (p2[1] - p1[1]) / len, (p2[2] - p1[2]) / len];
                            const s0 = [mx - u[0] * 0.06, my - u[1] * 0.06, mz - u[2] * 0.06];
                            const s1 = [mx + u[0] * 0.06, my + u[1] * 0.06, mz + u[2] * 0.06];
                            addSeg(s0, s1, radius * 1.24, C_COUPLER, [0.22, 16]);
                            addSeg([mx - u[0] * 0.052, my - u[1] * 0.052, mz - u[2] * 0.052], [mx - u[0] * 0.036, my - u[1] * 0.036, mz - u[2] * 0.036], radius * 1.31, C_CLAMP, [0.82, 68]);
                            addSeg([mx + u[0] * 0.036, my + u[1] * 0.036, mz + u[2] * 0.036], [mx + u[0] * 0.052, my + u[1] * 0.052, mz + u[2] * 0.052], radius * 1.31, C_CLAMP, [0.82, 68]);
                        }}
                    }}
                }}

                let curvePts = points;
                if (smooth && points.length >= 3) {{
                    const maxFil = (couplerIndices.length > 0) ? 0.18 : 0.24;
                    curvePts = [points[0]];
                    for (let i = 1; i < points.length - 1; i++) {{
                        const pPrev = points[i - 1], pCurr = points[i], pNext = points[i + 1];
                        const d1x = pCurr[0] - pPrev[0], d1y = pCurr[1] - pPrev[1], d1z = pCurr[2] - pPrev[2];
                        const d2x = pNext[0] - pCurr[0], d2y = pNext[1] - pCurr[1], d2z = pNext[2] - pCurr[2];
                        const l1 = Math.hypot(d1x, d1y, d1z), l2 = Math.hypot(d2x, d2y, d2z);
                        if (l1 > 0.04 && l2 > 0.04) {{
                            const f = Math.min(maxFil, l1 * 0.32, l2 * 0.32);
                            const q0 = [pCurr[0] - (d1x / l1) * f, pCurr[1] - (d1y / l1) * f, pCurr[2] - (d1z / l1) * f];
                            const q1 = [pCurr[0] + (d2x / l2) * f, pCurr[1] + (d2y / l2) * f, pCurr[2] + (d2z / l2) * f];
                            for (let st = 0; st <= 3; st++) {{
                                const t = st / 3, it = 1 - t;
                                curvePts.push([
                                    it * it * q0[0] + 2 * it * t * pCurr[0] + t * t * q1[0],
                                    it * it * q0[1] + 2 * it * t * pCurr[1] + t * t * q1[1],
                                    it * it * q0[2] + 2 * it * t * pCurr[2] + t * t * q1[2]
                                ]);
                            }}
                        }} else {{
                            curvePts.push(pCurr);
                        }}
                    }}
                    curvePts.push(points[points.length - 1]);
                }}

                for (let i = 0; i < curvePts.length - 1; i++) {{
                    addSeg(curvePts[i], curvePts[i + 1], radius, color, spec);
                    if (i > 0) {{
                        const p1 = curvePts[i];
                        this.addPart(targetList, 'sphere', this.matTRS(p1[0], p1[1], p1[2], 0, 0, 0, radius * 1.01, radius * 1.01, radius * 1.01), color, spec);
                    }}
                }}
            }}

            getHousingAppearance(matName) {{
                switch (matName) {{
                    case 'Alumínio Billet':
                        return {{ col: [0.80, 0.84, 0.90, 1.0], spec: [0.86, 74], bell: [0.70, 0.75, 0.82, 1.0], bellSpec: [0.82, 68] }};
                    case 'Magnésio':
                        return {{ col: [0.42, 0.39, 0.34, 1.0], spec: [0.44, 32], bell: [0.35, 0.32, 0.28, 1.0], bellSpec: [0.48, 36] }};
                    case 'Fibra de Carbono':
                        return {{ col: [0.13, 0.15, 0.19, 1.0], spec: [0.38, 28], bell: [0.64, 0.69, 0.76, 1.0], bellSpec: [0.80, 66] }};
                    case 'Titânio':
                        return {{ col: [0.65, 0.62, 0.56, 1.0], spec: [0.78, 62], bell: [0.58, 0.55, 0.49, 1.0], bellSpec: [0.76, 60] }};
                    default:
                        return {{ col: [0.56, 0.60, 0.66, 1.0], spec: [0.46, 36], bell: [0.48, 0.52, 0.58, 1.0], bellSpec: [0.50, 40] }};
                }}
            }}

            getWindingStyle(windingName) {{
                switch (windingName) {{
                    case 'Distribuído Litz':
                        return {{ col: [0.79, 0.43, 0.19, 1.0], spec: [0.72, 52], barStyle: 'litz' }};
                    case 'Concentrado':
                        return {{ col: [0.84, 0.45, 0.18, 1.0], spec: [0.78, 58], barStyle: 'bobbin' }};
                    case 'Alumínio Leve':
                        return {{ col: [0.76, 0.80, 0.86, 1.0], spec: [0.84, 68], barStyle: 'alu' }};
                    default:
                        return {{ col: [0.89, 0.49, 0.20, 1.0], spec: [0.86, 68], barStyle: 'hairpin' }};
                }}
            }}

            addInverterUnit(x, y, z, scale = 1.0, phaseTargets = null) {{
                const inv = this.config.inverter || 'SiC Dual';
                const s = scale;
                const isTrack = inv === 'SiC Racing 1200A';
                const isGan = inv === 'GaN Alta Freq.';
                const isIgbt = inv === 'IGBT Silício';

                const wX = (isGan ? 0.34 : (isTrack ? 0.56 : 0.46)) * s;
                const hY = (isIgbt ? 0.19 : (isGan ? 0.11 : 0.15)) * s;
                const dZ = (isTrack ? 0.46 : 0.38) * s;

                const bodyCol = isTrack ? [0.16, 0.18, 0.22, 1.0] : (isGan ? [0.28, 0.33, 0.40, 1.0] : [0.60, 0.65, 0.72, 1.0]);
                const trimCol = isTrack ? [0.84, 0.64, 0.22, 1.0] : (isGan ? [0.18, 0.76, 0.74, 1.0] : (isIgbt ? [0.38, 0.44, 0.52, 1.0] : [0.52, 0.40, 0.90, 1.0]));

                // Caixa principal do inversor + tampa superior anodizada
                this.addPart(this.staticOpaque, 'bevelBox', this.matTRS(x, y, z, 0, 0, 0, wX, hY, dZ), bodyCol, [0.68, 52]);
                this.addPart(this.staticOpaque, 'bevelBox', this.matTRS(x, y + hY * 0.48, z, 0, 0, 0, wX * 0.90, hY * 0.16, dZ * 0.86), trimCol, [0.76, 60]);

                // Aletas de dissipação de calor no topo do inversor
                const finCnt = isGan ? 9 : 7;
                for (let f = 0; f < finCnt; f++) {{
                    const fz = z + (-0.36 + (0.72 * f) / Math.max(1, finCnt - 1)) * dZ;
                    this.addPart(this.staticOpaque, 'box', this.matTRS(x, y + hY * 0.59, fz, 0, 0, 0, wX * 0.80, hY * 0.14, 0.012 * s), [0.74, 0.78, 0.84, 1.0], [0.80, 64]);
                }}

                // Condensadores DC-Link laterais e conectores laranja HV (+/-)
                const C_HV_ORANGE = [0.96, 0.42, 0.08, 1.0];
                const C_COPPER = [0.88, 0.50, 0.20, 1.0];
                this.addPart(this.staticOpaque, 'bevelBox', this.matTRS(x - wX * 0.36, y, z, 0, 0, 0, wX * 0.24, hY * 0.78, dZ * 0.90), [0.22, 0.25, 0.31, 1.0], [0.35, 24]);
                for (const sgn of [-1, 1]) {{
                    const hz = z + sgn * dZ * 0.24;
                    const hx = x - wX * 0.53;
                    this.addPart(this.staticOpaque, 'cyl', this.matTRS(hx, y, hz, 0, 0, Math.PI * 0.5, 0.036 * s, 0.10 * s, 0.036 * s), C_HV_ORANGE, [0.55, 38]);
                    this.addPart(this.staticOpaque, 'cyl', this.matTRS(hx - 0.04 * s, y, hz, 0, 0, Math.PI * 0.5, 0.022 * s, 0.06 * s, 0.022 * s), [0.84, 0.87, 0.92, 1.0], [0.84, 68]);
                }}

                // Barramentos trifásicos U / V / W em cobre do inversor ao estator
                const targets = phaseTargets || [
                    [x + wX * 0.16, y - hY * 1.45, z - dZ * 0.26],
                    [x + wX * 0.16, y - hY * 1.45, z],
                    [x + wX * 0.16, y - hY * 1.45, z + dZ * 0.26]
                ];
                for (let p = 0; p < 3; p++) {{
                    const pz = z + (p - 1) * dZ * 0.24;
                    const pStart = [x + wX * 0.28, y - hY * 0.36, pz];
                    const pMid = [x + wX * 0.34, (pStart[1] + targets[p][1]) * 0.52, (pz + targets[p][2]) * 0.5];
                    this.addPart(this.staticOpaque, 'bevelBox', this.matTRS(pStart[0], pStart[1], pStart[2], 0, 0, 0, 0.055 * s, 0.04 * s, 0.045 * s), C_HV_ORANGE, [0.52, 36]);
                    this.addPipe(this.staticOpaque, [pStart, pMid, targets[p]], 0.020 * s, C_COPPER, [0.86, 68], [], true);
                    this.hvPaths.push({{ pts: [pStart, pMid, targets[p]], r: 0.028 * s, phaseOff: p * 0.22, kind: 'phase' }});
                }}

                return {{
                    hvInputPos: [x - wX * 0.55, y, z - dZ * 0.24],
                    hvInputNeg: [x - wX * 0.55, y, z + dZ * 0.24]
                }};
            }}

            addEvDriveUnit({{ x = 0, y = 0, z = 0, scale = 1.0, isInWheel = false, flipDir = 1, includeInverter = true, rotorIdx = 0 }}) {{
                const s = scale;
                const dMm = Math.max(150, Math.min(440, Number(this.config.statorDiam) || 240));
                const lMm = Math.max(55, Math.min(340, Number(this.config.stackLen) || 165));
                const mType = this.config.motorType || 'PMSM';
                const isAxial = mType === 'Axial Flux' || isInWheel;
                const poles = Math.max(4, Math.min(16, parseInt(this.config.poles, 10) || 8));
                const cooling = this.config.cooling || 'Glicol (Camisa Água)';
                const bearing = this.config.bearingType || 'Aço Padrão';
                const rotorType = this.config.rotorType || 'Neodímio N52 (V-Shape)';

                const hs = this.getHousingAppearance(this.config.housingMat || 'Alumínio Fundido');
                const wd = this.getWindingStyle(this.config.winding || 'Hairpin Cobre');

                const baseR = (0.31 + ((dMm - 160) / 260) * 0.23) * s;
                const rStat = isAxial ? baseR * 1.24 : baseR;
                const lenCore = isAxial
                    ? Math.max(0.14 * s, (0.14 + ((lMm - 60) / 260) * 0.18) * s)
                    : Math.max(0.24 * s, (0.26 + ((lMm - 60) / 260) * 0.44) * s);
                const rRotor = isAxial ? rStat * 0.86 : rStat * 0.60;
                const rInnerEnd = isAxial ? rStat * 0.34 : rStat * 0.65;

                const C_CORE = [0.22, 0.25, 0.31, 1.0];
                const C_STEEL = [0.76, 0.80, 0.86, 1.0];
                const C_INSUL = [0.90, 0.92, 0.95, 1.0];
                const C_HV = [0.96, 0.42, 0.08, 1.0];

                // Eixo principal interno / veio motor (Z para hub de roda, X para motor central)
                const shaftLen = lenCore + (isAxial ? 0.36 : 0.44) * s;
                const shaftM = isInWheel
                    ? this.matTRS(x, y, z, Math.PI * 0.5, 0, 0, 0.052 * s, shaftLen, 0.052 * s)
                    : this.matTRS(x, y, z, 0, 0, Math.PI * 0.5, 0.052 * s, shaftLen, 0.052 * s);
                this.addPart(this.staticOpaque, 'cyl', shaftM, [0.58, 0.63, 0.70, 1.0], [0.80, 68]);

                // Rolamentos nas tampas frontal e traseira do eixo
                const bearOff = lenCore * 0.56 + 0.045 * s;
                for (const bSide of [-1, 1]) {{
                    const bx = isInWheel ? x : x + bSide * bearOff;
                    const bz = isInWheel ? z + bSide * bearOff : z;
                    const raceR = (isAxial ? 0.12 : 0.135) * s;
                    const raceM = isInWheel
                        ? this.matTRS(bx, y, bz, Math.PI * 0.5, 0, 0, raceR, 0.046 * s, raceR)
                        : this.matTRS(bx, y, bz, 0, 0, Math.PI * 0.5, raceR, 0.046 * s, raceR);
                    this.addPart(this.staticOpaque, 'cyl', raceM, C_STEEL, [0.84, 70]);
                    if (bearing === 'Magnético Ativo') {{
                        const torM = isInWheel
                            ? this.matTRS(bx, y, bz, 0, 0, 0, raceR * 1.05, raceR * 1.05, 0.055 * s)
                            : this.matTRS(bx, y, bz, 0, Math.PI * 0.5, 0, raceR * 1.05, raceR * 1.05, 0.055 * s);
                        this.addPart(this.staticOpaque, 'torus', torM, [0.34, 0.42, 0.54, 1.0], [0.72, 60]);
                        for (let c = 0; c < 6; c++) {{
                            const ca = (c * Math.PI * 2) / 6;
                            const cm = isInWheel
                                ? this.matTRS(bx + Math.cos(ca) * raceR * 0.88, y + Math.sin(ca) * raceR * 0.88, bz, 0, 0, ca, 0.032 * s, 0.026 * s, 0.036 * s)
                                : this.matTRS(bx, y + Math.cos(ca) * raceR * 0.88, bz + Math.sin(ca) * raceR * 0.88, ca, 0, 0, 0.036 * s, 0.032 * s, 0.026 * s);
                            this.addPart(this.staticOpaque, 'box', cm, wd.col, wd.spec);
                        }}
                    }} else {{
                        const ballCol = bearing === 'Cerâmica Si3N4' ? [0.14, 0.16, 0.20, 1.0] : [0.82, 0.86, 0.92, 1.0];
                        const ballSpec = bearing === 'Cerâmica Si3N4' ? [0.68, 54] : [0.88, 76];
                        for (let b = 0; b < 8; b++) {{
                            const ba = (b * Math.PI * 2) / 8;
                            const br = raceR * 0.72;
                            const spM = isInWheel
                                ? this.matTRS(bx + Math.cos(ba) * br, y + Math.sin(ba) * br, bz, 0, 0, 0, 0.020 * s, 0.020 * s, 0.020 * s)
                                : this.matTRS(bx, y + Math.cos(ba) * br, bz + Math.sin(ba) * br, 0, 0, 0, 0.020 * s, 0.020 * s, 0.020 * s);
                            this.addPart(this.staticOpaque, 'sphere', spM, ballCol, ballSpec);
                        }}
                    }}
                }}

                // Estator & Bobinagem
                const slotCount = Math.max(8, Math.min(20, poles));
                if (isInWheel) {{
                    // Estator toroidal pancake montado no cubo da roda (eixo Z lateral)
                    this.addPart(this.staticOpaque, 'cyl', this.matTRS(x, y, z, Math.PI * 0.5, 0, 0, rStat * 0.96, lenCore * 0.34, rStat * 0.96), C_CORE, [0.42, 30]);
                    for (let i = 0; i < slotCount; i++) {{
                        const a = (i * Math.PI * 2) / slotCount;
                        const cr = rStat * 0.66;
                        const cx = x + Math.cos(a) * cr;
                        const cy = y + Math.sin(a) * cr;
                        const coilH = (rStat - rInnerEnd) * 0.72;
                        const coilW = Math.min(0.11 * s, (rStat * 1.45) / slotCount);
                        this.addPart(this.staticOpaque, 'bevelBox', this.matTRS(cx, cy, z, 0, 0, a, coilH, coilW, lenCore * 0.54), wd.col, wd.spec);
                    }}
                    this.addPart(this.staticTrans, 'cyl', this.matTRS(x, y, z, Math.PI * 0.5, 0, 0, rStat * 1.07, lenCore * 1.12, rStat * 1.07), hs.col, hs.spec);
                    this.addPart(this.staticOpaque, 'torus', this.matTRS(x, y, z, 0, 0, 0, rStat * 1.03, rStat * 1.03, lenCore * 0.45), hs.bell, hs.bellSpec);
                    // Pinça de travão e manga de suspensão no cubo da roda
                    const sideDir = z >= 0 ? 1 : -1;
                    this.addPart(this.staticOpaque, 'bevelBox', this.matTRS(x - rStat * 0.72, y + rStat * 0.56, z + sideDir * lenCore * 0.62, 0, 0, 0.48, 0.16 * s, 0.24 * s, 0.12 * s), [0.84, 0.18, 0.16, 1.0], [0.76, 58]);
                    this.addPart(this.staticOpaque, 'bevelBox', this.matTRS(x, y - rStat * 0.54, z - sideDir * lenCore * 0.55, 0, 0, 0, 0.14 * s, rStat * 0.85, 0.11 * s), [0.34, 0.38, 0.44, 1.0], [0.58, 44]);
                }} else if (isAxial) {{
                    // Estator central fino estilo disco Axial Flux (bobines toroidais concentradas no eixo X)
                    this.addPart(this.staticOpaque, 'cyl', this.matTRS(x, y, z, 0, 0, Math.PI * 0.5, rStat * 0.96, lenCore * 0.34, rStat * 0.96), C_CORE, [0.42, 30]);
                    for (let i = 0; i < slotCount; i++) {{
                        const a = (i * Math.PI * 2) / slotCount;
                        const cr = rStat * 0.66;
                        const cy = y + Math.cos(a) * cr;
                        const cz = z + Math.sin(a) * cr;
                        const coilH = (rStat - rInnerEnd) * 0.72;
                        const coilW = Math.min(0.11 * s, (rStat * 1.45) / slotCount);
                        this.addPart(this.staticOpaque, 'bevelBox', this.matTRS(x, cy, cz, a, 0, 0, lenCore * 0.54, coilH, coilW), wd.col, wd.spec);
                        if (wd.barStyle === 'bobbin') {{
                            this.addPart(this.staticOpaque, 'box', this.matTRS(x, cy, cz, a, 0, 0, lenCore * 0.58, coilH * 0.32, coilW * 1.12), C_INSUL, [0.25, 16]);
                        }}
                    }}
                    // Discos exteriores da carcaça Axial Flux em corte transparente
                    this.addPart(this.staticTrans, 'cyl', this.matTRS(x, y, z, 0, 0, Math.PI * 0.5, rStat * 1.07, lenCore * 1.12, rStat * 1.07), hs.col, hs.spec);
                    this.addPart(this.staticOpaque, 'torus', this.matTRS(x, y, z, 0, Math.PI * 0.5, 0, rStat * 1.03, rStat * 1.03, lenCore * 0.45), hs.bell, hs.bellSpec);
                    for (let b = 0; b < 10; b++) {{
                        const ba = (b * Math.PI * 2) / 10;
                        const br = rStat * 1.04;
                        this.addPart(this.staticOpaque, 'hex', this.matTRS(x, y + Math.cos(ba) * br, z + Math.sin(ba) * br, 0, 0, Math.PI * 0.5, 0.022 * s, lenCore * 1.18, 0.022 * s), C_STEEL, [0.82, 66]);
                    }}
                }} else {{
                    // Estator radial laminado + ranhuras + coroas Hairpin / Litz / Concentrado
                    const lamSlices = 5;
                    for (let ls = 0; ls < lamSlices; ls++) {{
                        const lx = x + (-0.42 + (0.84 * ls) / (lamSlices - 1)) * lenCore;
                        const colLam = ls % 2 === 0 ? C_CORE : [0.16, 0.19, 0.24, 1.0];
                        this.addPart(this.staticOpaque, 'cyl', this.matTRS(lx, y, z, 0, 0, Math.PI * 0.5, rStat * 0.94, lenCore / lamSlices * 0.92, rStat * 0.94), colLam, [0.38, 28]);
                    }}
                    for (let i = 0; i < slotCount; i++) {{
                        const a = (i * Math.PI * 2) / slotCount;
                        const tr = rStat * 0.82;
                        const ty = y + Math.cos(a) * tr;
                        const tz = z + Math.sin(a) * tr;
                        const toothW = Math.min(0.068 * s, (rStat * 1.35) / slotCount);
                        this.addPart(this.staticOpaque, 'box', this.matTRS(x, ty, tz, a, 0, 0, lenCore * 1.02, rStat * 0.24, toothW), C_CORE, [0.40, 28]);

                        // Cabeças de bobine nas extremidades front/rear do estator
                        for (const endS of [-1, 1]) {{
                            const ex = x + endS * (lenCore * 0.54 + 0.03 * s);
                            const wr = rStat * 0.78;
                            const wy = y + Math.cos(a) * wr;
                            const wz = z + Math.sin(a) * wr;
                            if (wd.barStyle === 'hairpin') {{
                                this.addPart(this.staticOpaque, 'bevelBox', this.matTRS(ex, wy, wz, a, 0, 0, 0.088 * s, rStat * 0.20, toothW * 0.86), wd.col, wd.spec);
                            }} else if (wd.barStyle === 'bobbin') {{
                                this.addPart(this.staticOpaque, 'box', this.matTRS(ex, wy, wz, a, 0, 0, 0.065 * s, rStat * 0.23, toothW * 1.02), C_INSUL, [0.24, 16]);
                                this.addPart(this.staticOpaque, 'cyl', this.matTRS(ex, wy, wz, a, 0, 0, toothW * 0.56, rStat * 0.18, toothW * 0.56), wd.col, wd.spec);
                            }} else {{
                                this.addPart(this.staticOpaque, 'cyl', this.matTRS(ex, wy, wz, a, 0, 0, toothW * 0.60, rStat * 0.22, toothW * 0.60), wd.col, wd.spec);
                            }}
                        }}
                    }}
                    // Anéis coletores front/rear dos enrolamentos
                    for (const endS of [-1, 1]) {{
                        const ex = x + endS * (lenCore * 0.58 + 0.03 * s);
                        this.addPart(this.staticOpaque, 'torus', this.matTRS(ex, y, z, 0, Math.PI * 0.5, 0, rStat * 0.77, rStat * 0.77, 0.045 * s), wd.col, wd.spec);
                    }}

                    // Carcaça exterior translúcida + tampas rígidas dianteira/traseira + parafusos estruturais
                    this.addPart(this.staticTrans, 'cyl', this.matTRS(x, y, z, 0, 0, Math.PI * 0.5, rStat * 1.07, lenCore * 1.24, rStat * 1.07), hs.col, hs.spec);
                    for (const endS of [-1, 1]) {{
                        const bx = x + endS * (lenCore * 0.62);
                        this.addPart(this.staticOpaque, 'cyl', this.matTRS(bx, y, z, 0, 0, Math.PI * 0.5, rStat * 1.09, 0.068 * s, rStat * 1.09), hs.bell, hs.bellSpec);
                        for (let b = 0; b < 8; b++) {{
                            const ba = (b * Math.PI * 2) / 8;
                            const br = rStat * 1.02;
                            this.addPart(this.staticOpaque, 'hex', this.matTRS(bx + endS * 0.042 * s, y + Math.cos(ba) * br, z + Math.sin(ba) * br, 0, 0, Math.PI * 0.5, 0.022 * s, 0.045 * s, 0.022 * s), C_STEEL, [0.84, 68]);
                        }}
                    }}
                }}

                // Hardware de Arrefecimento visível na carcaça
                if (isInWheel) {{
                    if (cooling === 'Ar (Aletas)') {{
                        for (let f = 0; f < 4; f++) {{
                            const fz = z + (-0.36 + (0.72 * f) / 3) * lenCore;
                            this.addPart(this.staticTrans, 'cyl', this.matTRS(x, y, fz, Math.PI * 0.5, 0, 0, rStat * 1.13, 0.015 * s, rStat * 1.13), hs.col, hs.spec);
                        }}
                    }} else if (cooling === 'Glicol (Camisa Água)' || cooling === 'Imersão Dielétrica') {{
                        const cCol = cooling === 'Imersão Dielétrica' ? [0.42, 0.34, 0.68, 1.0] : [0.38, 0.44, 0.52, 1.0];
                        this.addPart(this.staticTrans, 'cyl', this.matTRS(x, y, z, Math.PI * 0.5, 0, 0, rStat * 1.10, lenCore * 0.55, rStat * 1.10), cCol, [0.70, 56]);
                    }}
                }} else if (cooling === 'Ar (Aletas)') {{
                    const finNum = isAxial ? 4 : 8;
                    for (let f = 0; f < finNum; f++) {{
                        const fx = x + (-0.42 + (0.84 * f) / Math.max(1, finNum - 1)) * lenCore;
                        this.addPart(this.staticTrans, 'cyl', this.matTRS(fx, y, z, 0, 0, Math.PI * 0.5, rStat * 1.15, 0.016 * s, rStat * 1.15), hs.col, hs.spec);
                    }}
                    // Ventoinha traseira acoplada ao eixo
                    this.dynamicRotors.push({{
                        type: 'coolingFan',
                        cx: x - lenCore * 0.69,
                        cy: y,
                        cz: z,
                        r: rStat * 0.66,
                        speedMult: flipDir * 1.0,
                        symmetry: 7,
                        colorHub: C_STEEL,
                        colorBlade: [0.64, 0.70, 0.78, 1.0]
                    }});
                }} else if (cooling === 'Glicol (Camisa Água)') {{
                    // Camisa de refrigeração maquilhada na carcaça + tomadas AN metálicas (sem círculos azuis)
                    const C_JACKET = [0.38, 0.43, 0.50, 1.0];
                    const C_PORT = [0.72, 0.77, 0.84, 1.0];
                    const C_AN = [0.22, 0.38, 0.56, 1.0];
                    if (!isAxial) {{
                        this.addPart(this.staticTrans, 'cyl', this.matTRS(x, y, z, 0, 0, Math.PI * 0.5, rStat * 1.10, lenCore * 0.72, rStat * 1.10), C_JACKET, [0.64, 52]);
                    }}
                    const pIn = [x - lenCore * 0.32, y + rStat * 1.08, z + rStat * 0.40];
                    const pOut = [x + lenCore * 0.32, y + rStat * 1.08, z - rStat * 0.40];
                    this.addPart(this.staticOpaque, 'cyl', this.matTRS(pIn[0], pIn[1], pIn[2], 0, 0, 0, 0.034 * s, 0.10 * s, 0.034 * s), C_PORT, [0.80, 64]);
                    this.addPart(this.staticOpaque, 'hex', this.matTRS(pIn[0], pIn[1] + 0.055 * s, pIn[2], 0, 0, 0, 0.042 * s, 0.035 * s, 0.042 * s), C_AN, [0.78, 60]);
                    this.addPart(this.staticOpaque, 'cyl', this.matTRS(pOut[0], pOut[1], pOut[2], 0, 0, 0, 0.034 * s, 0.10 * s, 0.034 * s), C_PORT, [0.80, 64]);
                    this.addPart(this.staticOpaque, 'hex', this.matTRS(pOut[0], pOut[1] + 0.055 * s, pOut[2], 0, 0, 0, 0.042 * s, 0.035 * s, 0.042 * s), C_AN, [0.78, 60]);
                }} else if (cooling === 'Óleo Direto') {{
                    const C_BRASS = [0.82, 0.64, 0.24, 1.0];
                    for (const endS of [-1, 1]) {{
                        this.addPart(this.staticOpaque, 'torus', this.matTRS(x + endS * (lenCore * 0.52), y, z, 0, Math.PI * 0.5, 0, rStat * 0.94, rStat * 0.94, 0.026 * s), C_BRASS, [0.80, 62]);
                    }}
                    this.addPart(this.staticOpaque, 'bevelBox', this.matTRS(x, y - rStat * 1.04, z, 0, 0, 0, lenCore * 0.92, 0.09 * s, rStat * 0.85), [0.18, 0.21, 0.26, 1.0], [0.46, 34]);
                    this.addPipe(this.staticOpaque, [
                        [x - lenCore * 0.45, y - rStat * 0.98, z + rStat * 0.36],
                        [x - lenCore * 0.45, y + rStat * 0.10, z + rStat * 1.05],
                        [x + lenCore * 0.45, y + rStat * 0.10, z + rStat * 1.05],
                        [x + lenCore * 0.45, y + rStat * 0.65, z + rStat * 0.65]
                    ], 0.022 * s, C_BRASS, [0.78, 60], [1], true);
                }} else if (cooling === 'Imersão Dielétrica') {{
                    const C_DIEL = [0.42, 0.28, 0.86, 1.0];
                    this.addPart(this.staticTrans, 'bevelBox', this.matTRS(x, y, z, 0, 0, 0, lenCore * 1.15, rStat * 2.15, rStat * 2.15), [0.16, 0.24, 0.40, 1.0], [0.65, 50]);
                    for (const sgn of [-1, 1]) {{
                        this.addPart(this.staticOpaque, 'bevelBox', this.matTRS(x, y, z + sgn * rStat * 1.16, 0, 0, 0, lenCore * 0.95, 0.14 * s, 0.07 * s), C_DIEL, [0.72, 56]);
                    }}
                }}

                // Rotor dinâmico registado para animação em renderGL
                this.dynamicEvRotors.push({{
                    cx: x,
                    cy: y,
                    cz: z,
                    rRotor,
                    lenCore,
                    poles,
                    rotorType,
                    motorType: mType,
                    isAxial,
                    isInWheel,
                    scale: s,
                    speedMult: flipDir,
                    angle: rotorIdx * 0.42
                }});

                // Bloco de terminais trifásicos + Inversor opcional montado acima da unidade
                const termY = y + rStat * 1.07;
                this.addPart(this.staticOpaque, 'bevelBox', this.matTRS(x, termY, z, 0, 0, 0, 0.16 * s, 0.07 * s, 0.24 * s), C_HV, [0.54, 40]);

                let hvPorts = null;
                if (includeInverter) {{
                    const phaseTargets = [
                        [x, termY + 0.02 * s, z - 0.07 * s],
                        [x, termY + 0.02 * s, z],
                        [x, termY + 0.02 * s, z + 0.07 * s]
                    ];
                    hvPorts = this.addInverterUnit(x - 0.04 * s, termY + 0.26 * s, z, s * 0.88, phaseTargets);
                }}

                return {{
                    x, y, z, rStat, lenCore, shaftR: 0.052 * s,
                    termTop: [x, termY + 0.03 * s, z],
                    hvPorts
                }};
            }}

            addEvGearboxModel(xOrigin, zCenter, scale = 1.0, showHalfShafts = true, dir = 1) {{
                const s = scale;
                const gb = this.config.gearboxType || 'Redutor 1V Direto';
                const diffType = this.config.diffType || 'Diferencial Aberto';
                const fd = Math.max(5.5, Math.min(14.5, parseFloat(this.config.finalDrive) || 9.73));
                const fdNorm = (fd - 6.8) / (13.5 - 6.8);

                const C_CASE = [0.52, 0.57, 0.64, 1.0];
                const C_GEAR = [0.76, 0.80, 0.86, 1.0];
                const C_BRONZE = [0.80, 0.60, 0.24, 1.0];
                const C_AXLE = [0.22, 0.26, 0.34, 1.0];
                const C_ELSD = [0.20, 0.56, 0.92, 1.0];
                const C_BOOT = [0.10, 0.12, 0.15, 1.0];

                const ringR = (0.28 + fdNorm * 0.11) * s;
                const pinR = (0.145 - fdNorm * 0.025) * s;
                const caseR = Math.max(ringR * 1.24, 0.39 * s);
                const isCoaxial = gb === 'Coaxial Direto';
                const isEcvt = gb === 'E-CVT Planetária';
                const isTwoSpd = gb === 'Caixa EV 2V';
                const d = dir < 0 ? -1 : 1;

                const xPin = xOrigin - d * (isCoaxial ? 0.08 : 0.18) * s;
                const xMid = xOrigin + d * 0.04 * s;
                const xDiff = isCoaxial ? xOrigin + d * 0.12 * s : xOrigin + d * 0.24 * s;

                const crownGearR = ringR * 0.88;
                const boxW = Math.max(0.46 * s, crownGearR * 2.28);
                const boxH = Math.max(ringR * 2.10, crownGearR * 2.28);
                const boxD = Math.max(ringR * 2.14, crownGearR * 2.32);

                // Carcaça redutora EV em corte translúcido + parafusos de união
                this.addPart(this.staticTrans, 'cyl', this.matTRS(xOrigin, 0, zCenter, 0, 0, Math.PI * 0.5, caseR, 0.58 * s, caseR), C_CASE, [0.48, 36]);
                this.addPart(this.staticTrans, 'bevelBox', this.matTRS(xDiff, 0, zCenter, 0, 0, 0, boxW, boxH, boxD), C_CASE, [0.46, 34]);
                for (let b = 0; b < 8; b++) {{
                    const ba = (b * Math.PI * 2) / 8;
                    const br = caseR * 0.96;
                    this.addPart(this.staticOpaque, 'hex', this.matTRS(xOrigin - d * 0.26 * s, Math.cos(ba) * br, zCenter + Math.sin(ba) * br, 0, 0, Math.PI * 0.5, 0.020 * s, 0.04 * s, 0.020 * s), C_GEAR, [0.82, 66]);
                }}

                // Veio de entrada + carreto primário
                this.addPart(this.staticOpaque, 'cyl', this.matTRS(xPin - d * 0.08 * s, 0, zCenter, 0, 0, Math.PI * 0.5, 0.045 * s, 0.34 * s, 0.045 * s), C_GEAR, [0.78, 62]);
                this.dynamicRotors.push({{
                    type: 'evGear',
                    cx: xPin,
                    cy: 0,
                    cz: zCenter,
                    r: pinR * 0.94,
                    thick: 0.095 * s,
                    speedMult: d * 1.0,
                    symmetry: 14,
                    colorRim: C_GEAR
                }});

                if (isEcvt || isCoaxial) {{
                    // Engrenagem planetária epicicloidal contida na carcaça (Sol central + 3 satélites, sem anéis/toros exteriores)
                    const sunR = Math.min(pinR * 0.90, caseR * 0.32);
                    const planetR = Math.min(pinR * 0.56, caseR * 0.20);
                    const orbR = sunR + planetR;
                    this.dynamicRotors.push({{
                        type: 'evGear',
                        cx: xMid,
                        cy: 0,
                        cz: zCenter,
                        r: sunR * 0.90,
                        thick: 0.090 * s,
                        speedMult: d * 1.0,
                        symmetry: 14,
                        colorRim: C_GEAR
                    }});
                    this.addPart(this.staticOpaque, 'cyl', this.matTRS((xMid + xDiff) * 0.5, 0, zCenter, 0, 0, Math.PI * 0.5, 0.040 * s, Math.max(0.14 * s, Math.abs(xDiff - xMid)), 0.040 * s), C_GEAR, [0.76, 60]);
                    for (let p = 0; p < 3; p++) {{
                        const pa = (p * Math.PI * 2) / 3;
                        this.dynamicRotors.push({{
                            type: 'evGear',
                            cx: xMid,
                            cy: Math.cos(pa) * orbR,
                            cz: zCenter + Math.sin(pa) * orbR,
                            r: planetR,
                            thick: 0.082 * s,
                            speedMult: -d * 1.45,
                            symmetry: 12,
                            colorRim: C_BRONZE
                        }});
                    }}
                    if (isEcvt) {{
                        // Atuador interno da planetária E-CVT alojado no topo interior da carcaça
                        this.addPart(this.staticOpaque, 'cyl', this.matTRS(xMid, caseR * 0.78, zCenter, 0, 0, Math.PI * 0.5, 0.048 * s, 0.14 * s, 0.048 * s), C_ELSD, [0.72, 56]);
                    }}
                }} else {{
                    // Contra-eixo paralelo (layshaft) + segundo estágio para Caixa EV 2V dentro da carcaça
                    const yLay = -caseR * 0.42;
                    const zLay = zCenter + caseR * 0.26;
                    const distLay = Math.hypot(yLay, zLay - zCenter);
                    const layGear1R = Math.min(pinR * 1.38, (caseR * 0.90 - distLay) / 1.04);
                    const layGear2R = isTwoSpd
                        ? Math.min(pinR * 1.10, (caseR * 0.88 - distLay) / 1.04)
                        : Math.min(pinR * 0.86, (caseR * 0.86 - distLay) / 1.04);
                    this.addPart(this.staticOpaque, 'cyl', this.matTRS(xMid, yLay, zLay, 0, 0, Math.PI * 0.5, 0.036 * s, 0.42 * s, 0.036 * s), C_GEAR, [0.76, 60]);
                    this.dynamicRotors.push({{
                        type: 'evGear',
                        cx: xPin,
                        cy: yLay,
                        cz: zLay,
                        r: layGear1R,
                        thick: 0.088 * s,
                        speedMult: -d * 0.68,
                        symmetry: 18,
                        colorRim: C_GEAR
                    }});
                    this.dynamicRotors.push({{
                        type: 'evGear',
                        cx: xMid + d * 0.08 * s,
                        cy: yLay,
                        cz: zLay,
                        r: layGear2R,
                        thick: 0.078 * s,
                        speedMult: -d * 0.68,
                        symmetry: 14,
                        colorRim: isTwoSpd ? C_BRONZE : C_GEAR
                    }});
                    if (isTwoSpd) {{
                        // Tambor de embraiagem multidisco e atuador de troca da 2ª velocidade alojados na carcaça
                        this.dynamicRotors.push({{
                            type: 'evGear',
                            cx: xMid - d * 0.04 * s,
                            cy: 0,
                            cz: zCenter,
                            r: Math.min(pinR * 1.24, caseR * 0.44),
                            thick: 0.070 * s,
                            speedMult: d * 0.82,
                            symmetry: 16,
                            colorRim: C_BRONZE
                        }});
                        this.addPart(this.staticOpaque, 'bevelBox', this.matTRS(xMid, caseR * 0.78, zCenter, 0, 0, 0, 0.16 * s, 0.07 * s, 0.12 * s), [0.84, 0.30, 0.20, 1.0], [0.68, 52]);
                    }}
                }}

                // Coroa final do diferencial (montada no plano Z para rodar com os semi-eixos)
                this.dynamicRotors.push({{
                    type: 'zAxle',
                    cx: xDiff,
                    cy: 0,
                    cz: zCenter,
                    ringR: crownGearR,
                    shaftR: 0.042 * s,
                    spanZ: showHalfShafts ? 0.78 * s : 0.28 * s,
                    speedMult: 1.0 / (fd / 9.73),
                    diffType,
                    C_GEAR,
                    C_BRONZE,
                    C_AXLE,
                    C_BOOT,
                    C_ELSD,
                    showHalfShafts
                }});

                if (diffType === 'e-LSD Vetorizado') {{
                    this.addPart(this.staticOpaque, 'cyl', this.matTRS(xDiff + boxW * 0.26, 0.06 * s, zCenter + boxD * 0.26, Math.PI * 0.5, 0, 0, 0.068 * s, 0.14 * s, 0.068 * s), C_ELSD, [0.76, 62]);
                }}
            }}

            buildStandaloneGearboxScene() {{
                this.addEvGearboxModel(0, 0, 1.18, true);
                this.sceneCenterX = 0;
                this.baseDist = 3.8;
            }}

            addHvBatteryPack(cx, cy, cz, lenX, widthZ) {{
                const chem = this.config.batteryChem || 'NMC 811';
                const cellFmt = this.config.cellFormat || 'Prismática';
                const packArch = this.config.packArch || 'Skateboard (Piso)';
                const kwh = Math.max(20, Math.min(250, Number(this.config.batteryKwh) || 85));
                const thickY = 0.23 + (kwh - 20) / 230 * 0.12;

                const C_TRAY = packArch === 'Estrutural 800V' ? [0.15, 0.18, 0.24, 1.0] : [0.22, 0.26, 0.32, 1.0];
                const C_COOLPLATE = [0.22, 0.38, 0.48, 1.0];
                const C_HV_ORANGE = [0.96, 0.42, 0.08, 1.0];
                const C_COPPER = [0.86, 0.52, 0.22, 1.0];
                const C_STEEL = [0.76, 0.80, 0.86, 1.0];

                let cellCol = [0.46, 0.38, 0.86, 1.0];
                let cellSpec = [0.68, 52];
                if (chem === 'LFP (LiFePO4)') {{
                    cellCol = [0.24, 0.62, 0.66, 1.0];
                    cellSpec = [0.56, 42];
                }} else if (chem === 'NCA Performance') {{
                    cellCol = [0.22, 0.48, 0.84, 1.0];
                    cellSpec = [0.76, 60];
                }} else if (chem === 'Estado Sólido') {{
                    cellCol = [0.80, 0.66, 0.28, 1.0];
                    cellSpec = [0.84, 68];
                }} else if (chem === 'Supercondensador') {{
                    cellCol = [0.16, 0.78, 0.72, 1.0];
                    cellSpec = [0.80, 64];
                }}

                // Base arrefecida + chapa térmica inferior + tampa superior em corte transparente
                this.addPart(this.staticOpaque, 'bevelBox', this.matTRS(cx, cy - thickY * 0.46, cz, 0, 0, 0, lenX * 1.04, 0.044, widthZ * 1.04), C_TRAY, [0.52, 38]);
                this.addPart(this.staticOpaque, 'box', this.matTRS(cx, cy - thickY * 0.36, cz, 0, 0, 0, lenX * 0.96, 0.020, widthZ * 0.96), C_COOLPLATE, [0.64, 48]);
                this.addPart(this.staticTrans, 'bevelBox', this.matTRS(cx, cy + 0.02, cz, 0, 0, 0, lenX, thickY, widthZ), [0.32, 0.38, 0.48, 1.0], [0.56, 46]);

                // Travessas laterais contra impacto e pernos perimetrais
                for (const sz of [-1, 1]) {{
                    const railZ = cz + sz * widthZ * 0.51;
                    this.addPart(this.staticOpaque, 'bevelBox', this.matTRS(cx, cy, railZ, 0, 0, 0, lenX * 1.03, thickY * 0.85, 0.058), [0.44, 0.48, 0.54, 1.0], [0.62, 46]);
                    for (let lb = 0; lb < 5; lb++) {{
                        const lx = cx + (-0.42 + (0.84 * lb) / 4) * lenX;
                        this.addPart(this.staticOpaque, 'hex', this.matTRS(lx, cy + thickY * 0.44, railZ, 0, 0, 0, 0.022, 0.032, 0.022), C_STEEL, [0.84, 68]);
                    }}
                }}

                // Bocais hidráulicos de refrigeração da placa base (dianteira)
                for (const sz of [-1, 1]) {{
                    this.addPart(this.staticOpaque, 'cyl', this.matTRS(cx - lenX * 0.54, cy - thickY * 0.28, cz + sz * widthZ * 0.26, 0, 0, Math.PI * 0.5, 0.026, 0.11, 0.026), [0.54, 0.62, 0.72, 1.0], [0.80, 62]);
                }}

                if (packArch === 'Estrutural 800V') {{
                    for (let r = 0; r < 3; r++) {{
                        const rxPos = cx + (-0.26 + r * 0.26) * lenX;
                        this.addPart(this.staticOpaque, 'box', this.matTRS(rxPos, cy + thickY * 0.05, cz, 0, 0, 0, 0.032, thickY * 0.80, widthZ * 0.94), [0.28, 0.32, 0.38, 1.0], [0.64, 48]);
                    }}
                }}

                // Módulos internos consoante formato escolhido (Prismática, 4680, Blade, Pouch)
                if (cellFmt === 'Cilíndrica 4680') {{
                    const rows = 9, cols = 6;
                    const cellH = thickY * 0.68;
                    for (let rx = 0; rx < rows; rx++) {{
                        const mx = cx + (-0.39 + (0.72 * rx) / (rows - 1)) * lenX;
                        for (let czIdx = 0; czIdx < cols; czIdx++) {{
                            const mz = cz + (-0.37 + (0.74 * czIdx) / (cols - 1)) * widthZ;
                            this.addPart(this.staticOpaque, 'cyl', this.matTRS(mx, cy - 0.01, mz, 0, 0, 0, 0.052, cellH, 0.052), [0.74, 0.79, 0.86, 1.0], [0.84, 68]);
                            this.addPart(this.staticOpaque, 'cyl', this.matTRS(mx, cy + cellH * 0.50, mz, 0, 0, 0, 0.024, 0.014, 0.024), cellCol, cellSpec);
                        }}
                        this.addPart(this.staticOpaque, 'box', this.matTRS(mx, cy + cellH * 0.53, cz, 0, 0, 0, 0.026, 0.012, widthZ * 0.80), C_COPPER, [0.84, 64]);
                    }}
                }} else if (cellFmt === 'Blade (Lâmina)') {{
                    const blades = 11;
                    const bladeH = thickY * 0.66;
                    for (let bx = 0; bx < blades; bx++) {{
                        const mx = cx + (-0.41 + (0.76 * bx) / (blades - 1)) * lenX;
                        this.addPart(this.staticOpaque, 'bevelBox', this.matTRS(mx, cy - 0.01, cz, 0, 0, 0, (lenX * 0.66) / blades, bladeH, widthZ * 0.86), cellCol, cellSpec);
                        this.addPart(this.staticOpaque, 'box', this.matTRS(mx, cy + bladeH * 0.51, cz + widthZ * 0.34, 0, 0, 0, (lenX * 0.55) / blades, 0.014, 0.065), C_COPPER, [0.82, 62]);
                    }}
                }} else if (cellFmt === 'Pouch (Bolsa)') {{
                    const stacks = 6;
                    const pouchH = thickY * 0.70;
                    for (let sx = 0; sx < stacks; sx++) {{
                        const mx = cx + (-0.39 + (0.72 * sx) / (stacks - 1)) * lenX;
                        for (const sgn of [-1, 1]) {{
                            const mz = cz + sgn * widthZ * 0.23;
                            this.addPart(this.staticOpaque, 'bevelBox', this.matTRS(mx, cy - 0.01, mz, 0, 0, 0, (lenX * 0.64) / stacks, pouchH, widthZ * 0.38), [0.76, 0.79, 0.84, 1.0], [0.80, 62]);
                            this.addPart(this.staticOpaque, 'box', this.matTRS(mx, cy + pouchH * 0.52, mz, 0, 0, 0, (lenX * 0.50) / stacks, 0.020, widthZ * 0.14), C_COPPER, [0.84, 66]);
                        }}
                    }}
                }} else {{
                    // Prismática (módulos padrão)
                    const rowsX = chem === 'LFP (LiFePO4)' ? 8 : 5;
                    const colsZ = chem === 'LFP (LiFePO4)' ? 1 : 2;
                    for (let rx = 0; rx < rowsX; rx++) {{
                        const mx = cx + (-0.39 + (0.72 * rx) / Math.max(1, rowsX - 1)) * lenX;
                        for (let czIdx = 0; czIdx < colsZ; czIdx++) {{
                            const mz = colsZ === 1 ? cz : cz + (czIdx === 0 ? -0.23 : 0.23) * widthZ;
                            const mwX = (lenX * 0.68) / rowsX;
                            const mwZ = (widthZ * 0.82) / colsZ;
                            const mhY = thickY * (chem === 'Estado Sólido' ? 0.55 : 0.70);
                            this.addPart(this.staticOpaque, 'bevelBox', this.matTRS(mx, cy - 0.01, mz, 0, 0, 0, mwX, mhY, mwZ), cellCol, cellSpec);
                            this.addPart(this.staticOpaque, 'box', this.matTRS(mx, cy + mhY * 0.52, mz, 0, 0, 0, mwX * 0.85, 0.014, mwZ * 0.28), C_COPPER, [0.80, 62]);
                        }}
                    }}
                }}

                if (packArch === 'T-Pack Central') {{
                    const spineH = thickY * 0.72;
                    this.addPart(this.staticOpaque, 'bevelBox', this.matTRS(cx - lenX * 0.04, cy + thickY * 0.78, cz, 0, 0, 0, lenX * 0.56, spineH, widthZ * 0.26), cellCol, cellSpec);
                    this.addPart(this.staticTrans, 'bevelBox', this.matTRS(cx - lenX * 0.04, cy + thickY * 0.80, cz, 0, 0, 0, lenX * 0.60, spineH * 1.15, widthZ * 0.30), C_TRAY, [0.56, 44]);
                    this.addPart(this.staticOpaque, 'box', this.matTRS(cx - lenX * 0.04, cy + thickY * 1.16, cz, 0, 0, 0, lenX * 0.50, 0.022, 0.06), C_HV_ORANGE, [0.58, 42]);
                }}

                if (chem === 'Supercondensador') {{
                    // Bancos de supercondensadores cilíndricos no topo dianteiro do pack
                    for (let sc = 0; sc < 6; sc++) {{
                        const scz = cz + (-0.32 + (0.64 * sc) / 5) * widthZ;
                        this.addPart(this.staticOpaque, 'cyl', this.matTRS(cx - lenX * 0.34, cy + thickY * 0.32, scz, 0, 0, Math.PI * 0.5, 0.044, 0.22, 0.044), [0.18, 0.80, 0.74, 1.0], [0.82, 66]);
                    }}
                }}

                // Unidade BMS e Caixa de Contactores HV (BDU)
                const xBdu = cx + lenX * 0.42;
                this.addPart(this.staticOpaque, 'bevelBox', this.matTRS(xBdu, cy + thickY * 0.42, cz, 0, 0, 0, 0.28, 0.14, 0.36), [0.14, 0.16, 0.22, 1.0], [0.46, 36]);
                this.addPart(this.staticOpaque, 'bevelBox', this.matTRS(xBdu, cy + thickY * 0.52, cz, 0, 0, 0, 0.18, 0.04, 0.22), C_HV_ORANGE, [0.58, 42]);
                // Barramento coletor HV central
                this.addPart(this.staticOpaque, 'box', this.matTRS(cx, cy + thickY * 0.36, cz, 0, 0, 0, lenX * 0.76, 0.018, 0.044), C_HV_ORANGE, [0.56, 40]);

                return {{
                    frontHv: [cx - lenX * 0.48, cy + thickY * 0.22, cz],
                    rearHv: [cx + lenX * 0.48, cy + thickY * 0.22, cz]
                }};
            }}

            buildStandaloneBatteryScene() {{
                this.addHvBatteryPack(0, 0, 0, 2.35, 1.48);
                this.sceneCenterX = 0;
                this.baseDist = 3.9;
            }}

            routeHvConduit(pA, pB, r = 0.026) {{
                const C_HV_ORANGE = [0.96, 0.42, 0.08, 1.0];
                const mx = (pA[0] + pB[0]) * 0.5;
                const my = Math.max(pA[1], pB[1]) + 0.08;
                const mz = (pA[2] + pB[2]) * 0.5;
                const pts = [pA, [mx, my, mz], pB];
                this.addPipe(this.staticOpaque, pts, r, C_HV_ORANGE, [0.58, 42], [], true);
                this.hvPaths.push({{ pts, r: r * 1.45, phaseOff: 0.15, kind: 'hv' }});
            }}

            samplePolyline(pts, t) {{
                if (!pts || !pts.length) return [0, 0, 0];
                if (pts.length === 1 || t <= 0) return pts[0];
                if (t >= 1) return pts[pts.length - 1];
                let totalLen = 0;
                const segLens = [];
                for (let i = 0; i < pts.length - 1; i++) {{
                    const d = Math.hypot(
                        pts[i + 1][0] - pts[i][0],
                        pts[i + 1][1] - pts[i][1],
                        pts[i + 1][2] - pts[i][2]
                    );
                    segLens.push(d);
                    totalLen += d;
                }}
                if (totalLen < 1e-6) return pts[0];
                let target = Math.max(0, Math.min(1, t)) * totalLen;
                for (let i = 0; i < segLens.length; i++) {{
                    const seg = segLens[i];
                    if (target <= seg || i === segLens.length - 1) {{
                        const f = seg > 1e-6 ? Math.max(0, Math.min(1, target / seg)) : 0;
                        const a = pts[i], b = pts[i + 1];
                        return [
                            a[0] + (b[0] - a[0]) * f,
                            a[1] + (b[1] - a[1]) * f,
                            a[2] + (b[2] - a[2]) * f
                        ];
                    }}
                    target -= seg;
                }}
                return pts[pts.length - 1];
            }}

            rebuildScene() {{
                this.staticOpaque = [];
                this.staticTrans = [];
                this.dynamicRotors = [];
                this.dynamicEvRotors = [];
                this.hvPaths = [];
                this.crankAngle = 0;

                const viewMode = this.config.viewMode || 'engine';
                if (viewMode === 'gearbox') {{
                    this.buildStandaloneGearboxScene();
                    return;
                }}
                if (viewMode === 'battery') {{
                    this.buildStandaloneBatteryScene();
                    return;
                }}

                const topo = this.config.topology || 'Single';
                const isAll = viewMode === 'all';
                let units = [];
                let xMinAll = -1.2;
                let xMaxAll = 1.2;
                let maxSpanZ = 1.1;

                if (topo === 'Single') {{
                    const u = this.addEvDriveUnit({{ x: isAll ? 1.55 : 0.0, y: 0, z: 0, scale: isAll ? 1.02 : 1.08, flipDir: 1, includeInverter: true, rotorIdx: 0 }});
                    units.push(u);
                    if (isAll) {{
                        this.addEvGearboxModel(u.x + u.lenCore * 0.65 + 0.24, 0, 0.94, true, 1);
                        const pack = this.addHvBatteryPack(-0.28, -0.26, 0, 2.10, 1.28);
                        if (u.hvPorts) this.routeHvConduit(pack.rearHv, u.hvPorts.hvInputPos, 0.028);
                        xMinAll = -1.55;
                        xMaxAll = 2.45;
                        maxSpanZ = 1.25;
                    }} else {{
                        this.sceneCenterX = 0.0;
                        this.baseDist = 3.15;
                        return;
                    }}
                }} else if (topo === 'Dual') {{
                    const xF = isAll ? -1.85 : -1.02;
                    const xR = isAll ? 1.85 : 1.02;
                    const uF = this.addEvDriveUnit({{ x: xF, y: 0, z: 0, scale: 0.90, flipDir: -1, includeInverter: true, rotorIdx: 0 }});
                    const uR = this.addEvDriveUnit({{ x: xR, y: 0, z: 0, scale: 0.96, flipDir: 1, includeInverter: true, rotorIdx: 1 }});
                    units.push(uF, uR);
                    if (isAll) {{
                        this.addEvGearboxModel(xF - uF.lenCore * 0.62 - 0.22, 0, 0.84, true, -1);
                        this.addEvGearboxModel(xR + uR.lenCore * 0.62 + 0.22, 0, 0.88, true, 1);
                        const pack = this.addHvBatteryPack(0, -0.26, 0, 2.25, 1.32);
                        if (uF.hvPorts) this.routeHvConduit(pack.frontHv, uF.hvPorts.hvInputPos, 0.026);
                        if (uR.hvPorts) this.routeHvConduit(pack.rearHv, uR.hvPorts.hvInputPos, 0.026);
                        xMinAll = -2.65;
                        xMaxAll = 2.65;
                    }} else {{
                        xMinAll = -1.65;
                        xMaxAll = 1.65;
                    }}
                    maxSpanZ = 1.15;
                }} else if (topo === 'Tri') {{
                    const xF = isAll ? -1.90 : -1.06;
                    const xR = isAll ? 1.82 : 1.02;
                    const uF = this.addEvDriveUnit({{ x: xF, y: 0, z: 0, scale: 0.88, flipDir: -1, includeInverter: true, rotorIdx: 0 }});
                    const uRL = this.addEvDriveUnit({{ x: xR, y: 0, z: -0.58, scale: 0.80, flipDir: 1, includeInverter: true, rotorIdx: 1 }});
                    const uRR = this.addEvDriveUnit({{ x: xR, y: 0, z: 0.58, scale: 0.80, flipDir: 1, includeInverter: true, rotorIdx: 2 }});
                    units.push(uF, uRL, uRR);
                    if (isAll) {{
                        this.addEvGearboxModel(xF - uF.lenCore * 0.60 - 0.20, 0, 0.82, true, -1);
                        this.addEvGearboxModel(xR + uRL.lenCore * 0.58 + 0.16, -0.58, 0.68, false, 1);
                        this.addEvGearboxModel(xR + uRR.lenCore * 0.58 + 0.16, 0.58, 0.68, false, 1);
                        const pack = this.addHvBatteryPack(0, -0.26, 0, 2.25, 1.36);
                        if (uF.hvPorts) this.routeHvConduit(pack.frontHv, uF.hvPorts.hvInputPos, 0.026);
                        if (uRL.hvPorts) this.routeHvConduit(pack.rearHv, uRL.hvPorts.hvInputPos, 0.024);
                        if (uRR.hvPorts) this.routeHvConduit(pack.rearHv, uRR.hvPorts.hvInputPos, 0.024);
                        xMinAll = -2.65;
                        xMaxAll = 2.55;
                    }} else {{
                        xMinAll = -1.68;
                        xMaxAll = 1.65;
                    }}
                    maxSpanZ = 1.35;
                }} else if (topo === 'Quad') {{
                    const xF = isAll ? -1.88 : -1.04;
                    const xR = isAll ? 1.88 : 1.04;
                    const uFL = this.addEvDriveUnit({{ x: xF, y: 0, z: -0.56, scale: 0.78, flipDir: -1, includeInverter: true, rotorIdx: 0 }});
                    const uFR = this.addEvDriveUnit({{ x: xF, y: 0, z: 0.56, scale: 0.78, flipDir: -1, includeInverter: true, rotorIdx: 1 }});
                    const uRL = this.addEvDriveUnit({{ x: xR, y: 0, z: -0.56, scale: 0.78, flipDir: 1, includeInverter: true, rotorIdx: 2 }});
                    const uRR = this.addEvDriveUnit({{ x: xR, y: 0, z: 0.56, scale: 0.78, flipDir: 1, includeInverter: true, rotorIdx: 3 }});
                    units.push(uFL, uFR, uRL, uRR);
                    if (isAll) {{
                        this.addEvGearboxModel(xF - uFL.lenCore * 0.58 - 0.14, -0.56, 0.64, false, -1);
                        this.addEvGearboxModel(xF - uFR.lenCore * 0.58 - 0.14, 0.56, 0.64, false, -1);
                        this.addEvGearboxModel(xR + uRL.lenCore * 0.58 + 0.14, -0.56, 0.64, false, 1);
                        this.addEvGearboxModel(xR + uRR.lenCore * 0.58 + 0.14, 0.56, 0.64, false, 1);
                        const pack = this.addHvBatteryPack(0, -0.26, 0, 2.15, 1.32);
                        for (const uu of [uFL, uFR]) {{
                            if (uu.hvPorts) this.routeHvConduit(pack.frontHv, uu.hvPorts.hvInputPos, 0.022);
                        }}
                        for (const uu of [uRL, uRR]) {{
                            if (uu.hvPorts) this.routeHvConduit(pack.rearHv, uu.hvPorts.hvInputPos, 0.022);
                        }}
                        xMinAll = -2.65;
                        xMaxAll = 2.65;
                    }} else {{
                        xMinAll = -1.65;
                        xMaxAll = 1.65;
                    }}
                    maxSpanZ = 1.35;
                }} else {{
                    // In-Wheel: 4 motores pancake diretamente nos cubos das rodas + inversores montados em subchassis
                    const corners = [
                        [-1.55, -0.05, -1.16],
                        [-1.55, -0.05, 1.16],
                        [1.55, -0.05, -1.16],
                        [1.55, -0.05, 1.16]
                    ];
                    for (const axX of [-1.15, 1.15]) {{
                        this.addPart(this.staticOpaque, 'bevelBox', this.matTRS(axX, 0.09, 0, 0, 0, 0, 0.24, 0.045, 0.68), [0.24, 0.28, 0.34, 1.0], [0.56, 42]);
                    }}
                    const invF = this.addInverterUnit(-1.15, 0.22, 0, 0.86);
                    const invR = this.addInverterUnit(1.15, 0.22, 0, 0.86);
                    corners.forEach((c, idx) => {{
                        const u = this.addEvDriveUnit({{
                            x: c[0], y: c[1], z: c[2],
                            scale: 0.78, isInWheel: true, flipDir: idx < 2 ? -1 : 1, includeInverter: false, rotorIdx: idx
                        }});
                        const axX = idx < 2 ? -1.15 : 1.15;
                        const sideZ = (c[2] < 0 ? -1 : 1) * 0.16;
                        this.routeHvConduit([axX, 0.20, sideZ], u.termTop, 0.022);
                        units.push(u);
                    }});
                    if (isAll) {{
                        const pack = this.addHvBatteryPack(0, -0.24, 0, 2.05, 1.30);
                        this.routeHvConduit(pack.frontHv, invF.hvInputPos, 0.026);
                        this.routeHvConduit(pack.rearHv, invR.hvInputPos, 0.026);
                    }}
                    xMinAll = -2.25;
                    xMaxAll = 2.25;
                    maxSpanZ = 1.65;
                }}

                this.sceneCenterX = (xMinAll + xMaxAll) * 0.5;
                this.baseDist = Math.max(4.6, (xMaxAll - xMinAll) * 1.18 + maxSpanZ * 1.05);
            }}
            bindEvents() {{
                const bg = document.getElementById('motor-bg-stage');
                const targetEl = bg || this.canvas;
                targetEl.addEventListener('contextmenu', e => e.preventDefault());

                targetEl.addEventListener('pointerdown', e => {{
                    try {{ targetEl.setPointerCapture(e.pointerId); }} catch (_) {{}}
                    this.pointers.set(e.pointerId, {{ x: e.clientX, y: e.clientY, button: e.button, shift: e.shiftKey }});
                    if (this.pointers.size === 2) {{
                        const pts = Array.from(this.pointers.values());
                        this.lastPinchDist = Math.hypot(pts[0].x - pts[1].x, pts[0].y - pts[1].y);
                    }}
                }});

                targetEl.addEventListener('pointermove', e => {{
                    const prev = this.pointers.get(e.pointerId);
                    if (!prev) return;
                    const dx = e.clientX - prev.x;
                    const dy = e.clientY - prev.y;
                    prev.x = e.clientX;
                    prev.y = e.clientY;

                    if (this.pointers.size === 1) {{
                        const isPan = prev.button === 2 || prev.button === 1 || e.shiftKey || (e.buttons & 2) || (e.buttons & 4);
                        if (isPan) {{
                            const panScale = 0.0055 * (this.baseDist / this.targetCam.zoom);
                            this.targetCam.panX -= dx * panScale;
                            this.targetCam.panY += dy * panScale;
                        }} else {{
                            this.targetCam.yaw += dx * 0.0085;
                            this.targetCam.pitch = Math.max(-1.25, Math.min(1.42, this.targetCam.pitch + dy * 0.0085));
                        }}
                    }} else if (this.pointers.size === 2) {{
                        const pts = Array.from(this.pointers.values());
                        const dist = Math.hypot(pts[0].x - pts[1].x, pts[0].y - pts[1].y);
                        if (this.lastPinchDist > 0) {{
                            const ratio = dist / this.lastPinchDist;
                            this.targetCam.zoom = Math.max(0.45, Math.min(2.6, this.targetCam.zoom * ratio));
                        }}
                        this.lastPinchDist = dist;
                    }}
                }});

                const endPtr = e => {{
                    this.pointers.delete(e.pointerId);
                    if (this.pointers.size < 2) this.lastPinchDist = 0;
                }};
                targetEl.addEventListener('pointerup', endPtr);
                targetEl.addEventListener('pointercancel', endPtr);

                targetEl.addEventListener('wheel', e => {{
                    e.preventDefault();
                    const factor = Math.exp(-e.deltaY * 0.0011);
                    this.targetCam.zoom = Math.max(0.45, Math.min(2.6, this.targetCam.zoom * factor));
                }}, {{ passive: false }});

                targetEl.addEventListener('dblclick', () => this.resetView());

                window.addEventListener('resize', () => this.resize());
                if (typeof ResizeObserver !== 'undefined') {{
                    new ResizeObserver(() => this.resize()).observe(this.canvas.parentElement || this.canvas);
                }}
            }}

            setRightPanelVisible(visible, compact = false) {{
                const isDesktop = window.innerWidth > 1020;
                const prevPanX = this.defaultCam.panX;
                const nextPanX = (visible && isDesktop) ? (compact ? 0.42 : 0.78) : 0.0;
                const nextPanY = isDesktop ? (visible ? (compact ? -0.01 : -0.05) : 0.04) : 0.12;
                this.defaultCam.panX = nextPanX;
                this.defaultCam.panY = nextPanY;
                if (Math.abs(this.targetCam.panX - prevPanX) < 0.12) {{
                    this.targetCam.panX = nextPanX;
                    this.targetCam.panY = nextPanY;
                }}
            }}

            resetView() {{
                const isDesktop = window.innerWidth > 1020;
                const dyEl = document.getElementById('dashboard-main');
                const rightVis = dyEl ? !dyEl.classList.contains('dyno-hidden') : false;
                const rightCompact = dyEl ? dyEl.classList.contains('dyno-compact') : false;
                this.defaultCam.panX = (rightVis && isDesktop) ? (rightCompact ? 0.42 : 0.78) : 0.0;
                this.defaultCam.panY = isDesktop ? (rightVis ? (rightCompact ? -0.01 : -0.05) : 0.04) : 0.12;
                this.targetCam = {{ ...this.defaultCam }};
            }}

            resize() {{
                const target = this.canvas.parentElement || this.canvas;
                const rect = target.getBoundingClientRect();
                if (!rect.width || !rect.height) return;
                const dpr = Math.min(window.devicePixelRatio || 1, 2);
                const w = Math.max(1, Math.round(rect.width * dpr));
                const h = Math.max(1, Math.round(rect.height * dpr));
                if (this.canvas.width !== w || this.canvas.height !== h) {{
                    this.canvas.width = w;
                    this.canvas.height = h;
                }}
            }}

            drawItem(mesh, model, color, spec, viewProj) {{
                const gl = this.gl;
                gl.uniformMatrix4fv(this.loc.uModel, false, model);
                gl.uniformMatrix3fv(this.loc.uNormalMat, false, this.normalMat3(model));
                gl.uniformMatrix4fv(this.loc.uViewProj, false, viewProj);
                gl.uniform4fv(this.loc.uColor, color);
                gl.uniform2fv(this.loc.uSpec, spec);

                gl.bindBuffer(gl.ARRAY_BUFFER, mesh.posBuf);
                gl.vertexAttribPointer(this.loc.aPos, 3, gl.FLOAT, false, 0, 0);
                gl.bindBuffer(gl.ARRAY_BUFFER, mesh.normBuf);
                gl.vertexAttribPointer(this.loc.aNorm, 3, gl.FLOAT, false, 0, 0);
                gl.bindBuffer(gl.ELEMENT_ARRAY_BUFFER, mesh.idxBuf);
                gl.drawElements(gl.TRIANGLES, mesh.count, gl.UNSIGNED_SHORT, 0);
            }}

            loop(now) {{
                const dt = Math.min(0.033, Math.max(0.001, (now - this.lastTime) * 0.001));
                this.lastTime = now;

                const inertiaMult = Math.max(0.35, Math.min(12.0, engineSim.inertiaFactor || 1.0));
                const invInertia = 1.0 / inertiaMult;
                const regenMode = selectRegenMode ? selectRegenMode.value : 'One-Pedal Alta (180 kW)';
                const regenDecelMult = {{
                    'Desligada': 0.36,
                    'Standard (50 kW)': 1.05,
                    'One-Pedal Alta (180 kW)': 1.85,
                    'Track Regen (Max)': 2.60
                }}[regenMode] || 1.30;

                if (!engineSim.on) {{
                    if (engineSim.throttlePct !== 0 || engineSim.spaceHeld) {{
                        engineSim.spaceHeld = false;
                        engineSim.preSpaceThrottlePct = 0;
                        setThrottlePercent(0);
                    }}
                    engineSim.isRegening = false;
                    engineSim.currentRpm += (0 - engineSim.currentRpm) * Math.min(1, dt * 4.8 * invInertia);
                    if (engineSim.currentRpm < 15) engineSim.currentRpm = 0;
                }} else {{
                    const thr = Math.max(0, Math.min(1, (engineSim.throttlePct || 0) / 100));
                    const maxR = Math.max(3000, engineSim.maxRpm || 16000);
                    const targetRpm = maxR * Math.pow(thr, 0.85);
                    if (thr <= 0.005) {{
                        if (engineSim.currentRpm > 40) {{
                            const decayFactor = Math.min(1, dt * 3.8 * regenDecelMult * invInertia);
                            const linearDrop = dt * (950 + engineSim.currentRpm * 0.16) * regenDecelMult * invInertia * 0.65;
                            const expDrop = engineSim.currentRpm - engineSim.currentRpm * decayFactor;
                            engineSim.currentRpm = Math.max(0, Math.min(expDrop, engineSim.currentRpm - linearDrop));
                            engineSim.isRegening = regenMode !== 'Desligada' && engineSim.currentRpm > 80;
                        }} else {{
                            engineSim.currentRpm = 0;
                            engineSim.isRegening = false;
                        }}
                    }} else if (engineSim.currentRpm < targetRpm) {{
                        engineSim.isRegening = false;
                        const inst = sampleDynoAtRpm(Math.max(0, engineSim.currentRpm));
                        const rotJ = Math.max(0.05, engineSim.rotInertia || (0.14 * inertiaMult));
                        const rawDrive = (inst.torqueNm * 2.55 + inst.powerKw * 3.25) / rotJ;
                        const thrGain = 0.20 + 0.80 * thr;
                        const climbRate = Math.max(120, Math.min(34000, rawDrive)) * thrGain;
                        const gap = targetRpm - engineSim.currentRpm;
                        const rawStep = Math.min(gap, climbRate * dt);
                        const step = thr >= 0.98 ? rawStep : Math.min(rawStep, gap * Math.min(1, dt * 11.5));
                        engineSim.currentRpm += step;
                    }} else if (engineSim.currentRpm > targetRpm) {{
                        const decayFactor = Math.min(1, dt * 3.5 * regenDecelMult * invInertia);
                        const linearDrop = dt * (950 + engineSim.currentRpm * 0.15) * regenDecelMult * invInertia * 0.60;
                        const expDrop = engineSim.currentRpm - (engineSim.currentRpm - targetRpm) * decayFactor;
                        engineSim.currentRpm = Math.max(targetRpm, Math.min(expDrop, engineSim.currentRpm - linearDrop));
                        engineSim.isRegening = regenMode !== 'Desligada' && (engineSim.currentRpm - targetRpm) > 90;
                    }} else {{
                        engineSim.isRegening = false;
                    }}
                    if (thr >= 0.98 && engineSim.currentRpm >= maxR * 0.992) {{
                        engineSim.currentRpm = maxR * (0.992 + 0.008 * Math.sin(now * 0.032));
                    }}
                }}

                // Velocidade angular proporcional às RPM reais + divisão Slow Mo + limite anti-aliasing
                const slowDiv = Math.max(1, engineSim.slowMo || 1);
                if (engineSim.currentRpm > 5) {{
                    const rpm = engineSim.currentRpm;
                    const omega = Math.min(54.0, 2.5 + Math.pow(rpm / 100, 0.52) * 3.1);
                    const crankStep = Math.min(0.62, (dt * omega) / slowDiv);
                    this.crankAngle += crankStep;
                    for (const er of this.dynamicEvRotors) {{
                        const sym = Math.max(4, er.poles || 8);
                        const maxSafeStep = (Math.PI * 0.56) / sym;
                        const rawStep = crankStep * (er.speedMult || 1);
                        const step = Math.sign(rawStep) * Math.min(maxSafeStep, Math.abs(rawStep));
                        er.angle = ((((er.angle || 0) + step) % (Math.PI * 2)) + Math.PI * 2) % (Math.PI * 2);
                    }}
                    for (const r of this.dynamicRotors) {{
                        const sym = r.symmetry || 8;
                        const maxSafeStep = (Math.PI * 0.56) / sym;
                        const rawStep = crankStep * (r.speedMult || 1);
                        const step = Math.sign(rawStep) * Math.min(maxSafeStep, Math.abs(rawStep));
                        r.angle = ((((r.angle || 0) + step) % (Math.PI * 2)) + Math.PI * 2) % (Math.PI * 2);
                    }}
                    const eRate = 0.6 + Math.min(3.2, (rpm / Math.max(3000, engineSim.maxRpm || 16000)) * 2.8);
                    const dir = engineSim.isRegening ? -1.0 : 1.0;
                    this.energyPhase = ((this.energyPhase + (dir * dt * eRate) / slowDiv) % 1000.0 + 1000.0) % 1000.0;
                }} else if (engineSim.on || (this.config.viewMode || 'engine') === 'all') {{
                    this.energyPhase = (this.energyPhase + dt * 0.22) % 1000.0;
                }}

                if (liveRpmValue) {{
                    liveRpmValue.textContent = `${{Math.round(engineSim.currentRpm)}} RPM`;
                }}
                updateRpmRedlineVisual(engineSim.currentRpm);
                if (dynoLiveReadout) {{
                    const lt = I18N[currentLang];
                    if (!engineSim.on && engineSim.currentRpm < 20) {{
                        if (engineSim.hoverRpm !== null) {{
                            const hs = sampleDynoAtRpm(engineSim.hoverRpm);
                            dynoLiveReadout.textContent = `${{lt.cursorPrefix}}: ${{Math.round(engineSim.hoverRpm)}} RPM · ${{formatPowerStr(hs.powerKw)}} · ${{formatTorqueStr(hs.torqueNm)}}`;
                        }} else {{
                            dynoLiveReadout.textContent = lt.engineOff;
                        }}
                    }} else if (engineSim.on && engineSim.currentRpm < 20 && engineSim.hoverRpm === null) {{
                        dynoLiveReadout.textContent = lt.standbyReady;
                    }} else {{
                        const refRpm = engineSim.hoverRpm !== null ? engineSim.hoverRpm : engineSim.currentRpm;
                        const s = sampleDynoAtRpm(refRpm);
                        const regTag = engineSim.isRegening ? ` · ${{lt.regenWord}}` : '';
                        dynoLiveReadout.textContent = `${{Math.round(refRpm)}} RPM · ${{formatPowerStr(s.powerKw)}} · ${{formatTorqueStr(s.torqueNm)}}${{regTag}}`;
                    }}
                }}
                if (engineSim.currentRpm > 5 || engineSim.on) {{
                    drawDynoChart();
                }}

                if (this.autoRotate && this.pointers.size === 0) {{
                    this.targetCam.yaw += dt * 0.36;
                }}

                const damp = 1 - Math.exp(-14 * dt);
                this.cam.yaw += (this.targetCam.yaw - this.cam.yaw) * damp;
                this.cam.pitch += (this.targetCam.pitch - this.cam.pitch) * damp;
                this.cam.zoom += (this.targetCam.zoom - this.cam.zoom) * damp;
                this.cam.panX += (this.targetCam.panX - this.cam.panX) * damp;
                this.cam.panY += (this.targetCam.panY - this.cam.panY) * damp;

                if (this.gl) {{
                    this.renderGL();
                }} else {{
                    this.renderFallback2D();
                }}
                requestAnimationFrame(t => this.loop(t));
            }}

            renderGL() {{
                const gl = this.gl;
                const w = this.canvas.width, h = this.canvas.height;
                if (!w || !h) return;
                gl.viewport(0, 0, w, h);
                gl.clearColor(0, 0, 0, 0);
                gl.clear(gl.COLOR_BUFFER_BIT | gl.DEPTH_BUFFER_BIT);

                const dist = this.baseDist / this.cam.zoom;
                const cy = Math.cos(this.cam.pitch), sy = Math.sin(this.cam.pitch);
                const cx = Math.cos(this.cam.yaw), sx = Math.sin(this.cam.yaw);

                const rightX = cx, rightZ = -sx;
                const tx = (this.sceneCenterX || 0) + this.cam.panX * rightX;
                const ty = this.cam.panY;
                const tz = this.cam.panX * rightZ;

                const eye = [
                    tx + dist * cy * sx,
                    ty + dist * sy,
                    tz + dist * cy * cx
                ];
                const proj = this.matPersp(0.68, w / h, 0.1, 80.0);
                const view = this.matLookAt(eye, [tx, ty, tz], [0, 1, 0]);
                const viewProj = this.matMul(proj, view);
                gl.uniform3fv(this.loc.uCamPos, eye);

                gl.disable(gl.BLEND);
                gl.depthMask(true);
                gl.enable(gl.CULL_FACE);
                gl.cullFace(gl.BACK);

                for (const item of this.staticOpaque) {{
                    this.drawItem(this.meshes[item.type], item.model, item.color, item.spec, viewProj);
                }}

                // Rotores elétricos dinâmicos (N52 V-Shape, Halbach Array, Gaiola Cobre, EESM Bobinado, Manga Carbono, Fluxo Axial)
                const C_ROTOR_STEEL = [0.36, 0.40, 0.48, 1.0];
                const C_MAG_N52 = [0.84, 0.88, 0.94, 1.0];
                const C_MAG_CYAN = [0.24, 0.78, 0.96, 1.0];
                const C_COPPER = [0.88, 0.48, 0.20, 1.0];
                const C_CARBON = [0.12, 0.14, 0.18, 1.0];

                for (const er of this.dynamicEvRotors) {{
                    const ang = er.angle || 0;
                    const s = er.scale || 1.0;
                    const nP = Math.max(4, Math.min(16, er.poles || 8));
                    if (er.isInWheel) {{
                        // Motor Hub de roda gira em torno de Z (eixo lateral das rodas)
                        for (const discSide of [-1, 1]) {{
                            const dz = er.cz + discSide * er.lenCore * 0.36;
                            const discM = this.matTRS(er.cx, er.cy, dz, Math.PI * 0.5, 0, ang, er.rRotor, er.lenCore * 0.18, er.rRotor);
                            this.drawItem(this.meshes.cyl, discM, er.rotorType === 'Manga Carbono (Alta RPM)' ? C_CARBON : C_ROTOR_STEEL, [0.68, 52], viewProj);
                            for (let p = 0; p < nP; p++) {{
                                const pa = ang + (p * Math.PI * 2) / nP;
                                const mr = er.rRotor * 0.72;
                                const mCol = (er.rotorType === 'Halbach Array' && p % 2 === 1) ? C_MAG_CYAN : C_MAG_N52;
                                const mSize = Math.min(0.11 * s, (er.rRotor * 1.45) / nP);
                                const magM = this.matTRS(er.cx + Math.cos(pa) * mr, er.cy + Math.sin(pa) * mr, dz - discSide * er.lenCore * 0.06, 0, 0, pa, er.rRotor * 0.34, mSize, 0.036 * s);
                                this.drawItem(this.meshes.box, magM, mCol, [0.84, 68], viewProj);
                            }}
                        }}
                        const sideDir = er.cz >= 0 ? 1 : -1;
                        const hubM = this.matTRS(er.cx, er.cy, er.cz + sideDir * er.lenCore * 0.56, Math.PI * 0.5, 0, ang, er.rRotor * 0.82, 0.032 * s, er.rRotor * 0.82);
                        this.drawItem(this.meshes.cyl, hubM, [0.64, 0.68, 0.74, 1.0], [0.82, 66], viewProj);
                        for (let k = 0; k < 5; k++) {{
                            const ka = ang + (k * Math.PI * 2) / 5;
                            const lugR = er.rRotor * 0.32;
                            const lugM = this.matTRS(er.cx + Math.cos(ka) * lugR, er.cy + Math.sin(ka) * lugR, er.cz + sideDir * (er.lenCore * 0.64), Math.PI * 0.5, 0, ka, 0.022 * s, 0.05 * s, 0.022 * s);
                            this.drawItem(this.meshes.hex, lugM, [0.88, 0.90, 0.95, 1.0], [0.88, 72], viewProj);
                        }}
                    }} else if (er.isAxial) {{
                        // Rotores duplos em disco a flanquear o estator central Axial Flux (eixo X)
                        for (const discSide of [-1, 1]) {{
                            const dx = er.cx + discSide * er.lenCore * 0.36;
                            const discM = this.matSpinX(dx, er.cy, er.cz, ang, 0, 0, Math.PI * 0.5, er.rRotor, er.lenCore * 0.18, er.rRotor);
                            this.drawItem(this.meshes.cyl, discM, er.rotorType === 'Manga Carbono (Alta RPM)' ? C_CARBON : C_ROTOR_STEEL, [0.68, 52], viewProj);
                            for (let p = 0; p < nP; p++) {{
                                const pa = ang + (p * Math.PI * 2) / nP;
                                const mr = er.rRotor * 0.72;
                                const mCol = (er.rotorType === 'Halbach Array' && p % 2 === 1) ? C_MAG_CYAN : C_MAG_N52;
                                const mSize = Math.min(0.11 * s, (er.rRotor * 1.45) / nP);
                                const magM = this.matTRS(dx - discSide * er.lenCore * 0.06, er.cy + Math.cos(pa) * mr, er.cz + Math.sin(pa) * mr, pa, 0, 0, 0.036 * s, er.rRotor * 0.34, mSize);
                                this.drawItem(this.meshes.box, magM, mCol, [0.84, 68], viewProj);
                            }}
                        }}
                    }} else {{
                        // Rotor radial
                        const bodyCol = er.rotorType === 'Manga Carbono (Alta RPM)' ? C_CARBON : C_ROTOR_STEEL;
                        const bodySpec = er.rotorType === 'Manga Carbono (Alta RPM)' ? [0.34, 24] : [0.64, 50];
                        const rCore = er.rotorType === 'Manga Carbono (Alta RPM)'
                            ? er.rRotor * 1.02
                            : (er.rotorType === 'Neodímio N52 (V-Shape)' ? er.rRotor * 0.80 : (er.rotorType === 'Rotor Bobinado (EESM)' ? er.rRotor * 0.78 : er.rRotor * 0.88));
                        const coreM = this.matSpinX(er.cx, er.cy, er.cz, ang, 0, 0, Math.PI * 0.5, rCore, er.lenCore * 0.98, rCore);
                        this.drawItem(this.meshes.cyl, coreM, bodyCol, bodySpec, viewProj);

                        if (er.rotorType === 'Gaiola de Cobre') {{
                            for (const eS of [-1, 1]) {{
                                const endRM = this.matSpinX(er.cx + eS * er.lenCore * 0.49, er.cy, er.cz, ang, 0, 0, Math.PI * 0.5, er.rRotor * 0.98, 0.035 * s, er.rRotor * 0.98);
                                this.drawItem(this.meshes.cyl, endRM, C_COPPER, [0.86, 68], viewProj);
                            }}
                            const barCnt = Math.max(10, nP * 2);
                            for (let b = 0; b < barCnt; b++) {{
                                const ba = ang + (b * Math.PI * 2) / barCnt;
                                const br = er.rRotor * 0.92;
                                const barM = this.matTRS(er.cx, er.cy + Math.cos(ba) * br, er.cz + Math.sin(ba) * br, ba, 0, 0, er.lenCore * 1.01, 0.028 * s, 0.024 * s);
                                this.drawItem(this.meshes.box, barM, C_COPPER, [0.86, 68], viewProj);
                            }}
                        }} else if (er.rotorType === 'Rotor Bobinado (EESM)') {{
                            for (let p = 0; p < nP; p++) {{
                                const pa = ang + (p * Math.PI * 2) / nP;
                                const pr = er.rRotor * 0.86;
                                const poleW = Math.min(0.08 * s, (er.rRotor * 1.3) / nP);
                                const poleM = this.matTRS(er.cx, er.cy + Math.cos(pa) * pr, er.cz + Math.sin(pa) * pr, pa, 0, 0, er.lenCore * 0.86, er.rRotor * 0.24, poleW);
                                this.drawItem(this.meshes.bevelBox, poleM, C_COPPER, [0.82, 62], viewProj);
                            }}
                            // Anéis coletores no eixo traseiro
                            for (const srOff of [-0.04, 0.04]) {{
                                const srM = this.matSpinX(er.cx - er.lenCore * 0.56 + srOff * s, er.cy, er.cz, ang, 0, 0, Math.PI * 0.5, er.rRotor * 0.34, 0.024 * s, er.rRotor * 0.34);
                                this.drawItem(this.meshes.cyl, srM, [0.84, 0.62, 0.24, 1.0], [0.84, 68], viewProj);
                            }}
                        }} else if (er.rotorType === 'Halbach Array') {{
                            for (let p = 0; p < nP; p++) {{
                                const pa = ang + (p * Math.PI * 2) / nP;
                                const mr = er.rRotor * 0.96;
                                const mCol = p % 2 === 0 ? C_MAG_N52 : C_MAG_CYAN;
                                const arcW = Math.min(0.11 * s, (er.rRotor * 1.6) / nP);
                                const magM = this.matTRS(er.cx, er.cy + Math.cos(pa) * mr, er.cz + Math.sin(pa) * mr, pa, 0, 0, er.lenCore * 0.94, 0.035 * s, arcW);
                                this.drawItem(this.meshes.box, magM, mCol, [0.86, 70], viewProj);
                            }}
                        }} else if (er.rotorType === 'Manga Carbono (Alta RPM)') {{
                            for (const eS of [-1, 1]) {{
                                const capM = this.matSpinX(er.cx + eS * er.lenCore * 0.48, er.cy, er.cz, ang, 0, 0, Math.PI * 0.5, er.rRotor * 1.04, 0.036 * s, er.rRotor * 1.04);
                                this.drawItem(this.meshes.cyl, capM, [0.76, 0.72, 0.60, 1.0], [0.84, 68], viewProj);
                            }}
                            const stripeM = this.matTRS(er.cx, er.cy + Math.cos(ang) * er.rRotor * 1.03, er.cz + Math.sin(ang) * er.rRotor * 1.03, ang, 0, 0, er.lenCore * 0.84, 0.018 * s, 0.032 * s);
                            this.drawItem(this.meshes.box, stripeM, [0.24, 0.78, 0.96, 1.0], [0.72, 54], viewProj);
                        }} else {{
                            // Neodímio N52 (V-Shape): ranhuras V expostas no núcleo laminado com pratos de retenção
                            for (const eS of [-1, 1]) {{
                                const endPlateM = this.matSpinX(er.cx + eS * er.lenCore * 0.48, er.cy, er.cz, ang, 0, 0, Math.PI * 0.5, er.rRotor * 0.96, 0.024 * s, er.rRotor * 0.96);
                                this.drawItem(this.meshes.cyl, endPlateM, C_ROTOR_STEEL, [0.72, 56], viewProj);
                            }}
                            for (let p = 0; p < nP; p++) {{
                                const pa = ang + (p * Math.PI * 2) / nP;
                                const mr = er.rRotor * 0.88;
                                for (const vSign of [-1, 1]) {{
                                    const va = pa + vSign * 0.16;
                                    const magM = this.matTRS(er.cx, er.cy + Math.cos(va) * mr, er.cz + Math.sin(va) * mr, va + vSign * 0.36, 0, 0, er.lenCore * 0.92, 0.075 * s, 0.024 * s);
                                    this.drawItem(this.meshes.box, magM, C_MAG_N52, [0.86, 72], viewProj);
                                }}
                            }}
                        }}
                        // Veio estriado central que roda sempre com o rotor
                        const markerM = this.matTRS(er.cx, er.cy + Math.cos(ang) * (er.rRotor * 0.25), er.cz + Math.sin(ang) * (er.rRotor * 0.25), ang, 0, 0, er.lenCore * 1.06, 0.032 * s, 0.032 * s);
                        this.drawItem(this.meshes.box, markerM, [0.92, 0.38, 0.24, 1.0], [0.70, 52], viewProj);
                    }}
                }}

                // Engrenagens EV, semi-eixos em Z e ventoinha de arrefecimento
                for (const r of this.dynamicRotors) {{
                    const ang = r.angle !== undefined ? r.angle : this.crankAngle * (r.speedMult || 1);
                    if (r.type === 'evGear') {{
                        const gearM = this.matSpinX(r.cx, r.cy, r.cz, ang, 0, 0, Math.PI * 0.5, r.r, r.thick, r.r);
                        this.drawItem(this.meshes.gear, gearM, r.colorRim, [0.78, 60], viewProj);
                    }} else if (r.type === 'coolingFan') {{
                        const hubM = this.matSpinX(r.cx, r.cy, r.cz, ang, 0, 0, Math.PI * 0.5, r.r * 0.26, 0.045, r.r * 0.26);
                        this.drawItem(this.meshes.cyl, hubM, r.colorHub, [0.78, 62], viewProj);
                        const wheelM = this.matSpinX(r.cx, r.cy, r.cz, ang, 0, 0, Math.PI * 0.5, r.r, 0.068, r.r);
                        this.drawItem(this.meshes.impeller, wheelM, r.colorBlade, [0.82, 66], viewProj);
                    }} else if (r.type === 'zAxle') {{
                        // Coroa principal do diferencial a rodar em torno de Z
                        const crownM = this.matTRS(r.cx, r.cy, r.cz, Math.PI * 0.5, 0, ang, r.ringR, 0.085, r.ringR);
                        this.drawItem(this.meshes.gear, crownM, r.C_GEAR, [0.78, 62], viewProj);
                        const carrierCol = r.diffType === 'LSD Mecânico' ? r.C_BRONZE : (r.diffType === 'e-LSD Vetorizado' ? r.C_ELSD : (r.diffType === 'Spool Direto' ? [0.84, 0.26, 0.22, 1.0] : r.C_GEAR));
                        const carrierLen = Math.min(0.22, r.ringR * 0.64);
                        const carrierM = this.matTRS(r.cx, r.cy, r.cz, Math.PI * 0.5, 0, ang, r.ringR * 0.54, carrierLen, r.ringR * 0.54);
                        this.drawItem(this.meshes.cyl, carrierM, carrierCol, [0.74, 58], viewProj);
                        if (r.showHalfShafts) {{
                            for (const side of [-1, 1]) {{
                                const sz = r.cz + side * (r.spanZ * 0.55);
                                const axM = this.matTRS(r.cx, r.cy, sz, Math.PI * 0.5, 0, ang, r.shaftR, r.spanZ * 0.90, r.shaftR);
                                this.drawItem(this.meshes.cyl, axM, r.C_AXLE, [0.68, 52], viewProj);
                                const bootM = this.matTRS(r.cx, r.cy, r.cz + side * r.spanZ * 0.30, Math.PI * 0.5, 0, ang, r.shaftR * 1.55, 0.14, r.shaftR * 1.55);
                                this.drawItem(this.meshes.cyl, bootM, r.C_BOOT, [0.22, 16], viewProj);
                                const outerFlange = this.matTRS(r.cx, r.cy, r.cz + side * r.spanZ, Math.PI * 0.5, 0, ang, r.shaftR * 2.1, 0.06, r.shaftR * 2.1);
                                this.drawItem(this.meshes.gear, outerFlange, r.C_GEAR, [0.80, 64], viewProj);
                            }}
                        }}
                    }}
                }}

                // Pulsos HV nas cablagens entre bateria/inversor/motor (sem anéis azuis no entreferro)
                const isActive = engineSim.on && (engineSim.currentRpm > 5 || engineSim.throttlePct > 0);
                if (this.hvPaths.length) {{
                    gl.enable(gl.BLEND);
                    gl.blendFunc(gl.SRC_ALPHA, gl.ONE);
                    gl.depthMask(false);

                    const regen = engineSim.isRegening;
                    const pulseAlpha = isActive ? 0.88 : 0.28;
                    const pulseCol = regen
                        ? [0.14, 0.95, 0.56, pulseAlpha]
                        : [1.0, 0.64, 0.22, pulseAlpha];
                    for (const hp of this.hvPaths) {{
                        for (let k = 0; k < 2; k++) {{
                            const s = ((this.energyPhase * 0.85 + hp.phaseOff + k * 0.5) % 1.0 + 1.0) % 1.0;
                            const pt = this.samplePolyline(hp.pts, s);
                            const pm = this.matTRS(pt[0], pt[1], pt[2], 0, 0, 0, hp.r, hp.r, hp.r);
                            this.drawItem(this.meshes.sphere, pm, pulseCol, [0.0, 1.0], viewProj);
                        }}
                    }}

                    gl.blendFunc(gl.SRC_ALPHA, gl.ONE_MINUS_SRC_ALPHA);
                    gl.depthMask(true);
                    gl.disable(gl.BLEND);
                }}

                // Carcaças exteriores em corte transparente
                if (this.cutaway) {{
                    gl.enable(gl.BLEND);
                    gl.blendFunc(gl.SRC_ALPHA, gl.ONE_MINUS_SRC_ALPHA);
                    gl.depthMask(false);
                    for (const cullFace of [gl.FRONT, gl.BACK]) {{
                        gl.cullFace(cullFace);
                        for (const item of this.staticTrans) {{
                            const col = [item.color[0], item.color[1], item.color[2], 0.24];
                            this.drawItem(this.meshes[item.type], item.model, col, item.spec, viewProj);
                        }}
                    }}
                    gl.cullFace(gl.BACK);
                    gl.depthMask(true);
                    gl.disable(gl.BLEND);
                }} else {{
                    for (const item of this.staticTrans) {{
                        this.drawItem(this.meshes[item.type], item.model, item.color, item.spec, viewProj);
                    }}
                }}
            }}

            renderFallback2D() {{
                const ctx = this.canvas.getContext('2d');
                if (!ctx) return;
                const w = this.canvas.width, h = this.canvas.height;
                ctx.clearRect(0, 0, w, h);
                ctx.save();
                ctx.translate(w * 0.40 - this.cam.panX * 40, h * 0.50 - this.cam.panY * 40);
                ctx.scale(this.cam.zoom * 65, this.cam.zoom * 65);
                const cy = Math.cos(this.cam.yaw), sy = Math.sin(this.cam.yaw);
                const cp = Math.cos(this.cam.pitch), sp = Math.sin(this.cam.pitch);
                const proj = (x, y, z) => {{
                    const rx = x * cy + z * sy;
                    const rz = -x * sy + z * cy;
                    const ry = y * cp - rz * sp;
                    return [rx, -ry];
                }};
                ctx.strokeStyle = '#60a5fa';
                ctx.lineWidth = 0.03;
                for (const er of this.dynamicEvRotors) {{
                    const [px, py] = proj(er.cx, er.cy, er.cz);
                    ctx.beginPath();
                    ctx.arc(px, py, er.rRotor, 0, Math.PI * 2);
                    ctx.stroke();
                    const pa = er.angle || 0;
                    const [mx, my] = proj(er.cx, er.cy + Math.cos(pa) * er.rRotor, er.cz + Math.sin(pa) * er.rRotor);
                    ctx.beginPath();
                    ctx.moveTo(px, py);
                    ctx.lineTo(mx, my);
                    ctx.stroke();
                }}
                ctx.restore();
            }}
        }}

        const motorCanvas = document.getElementById('motor-3d-canvas');
        motor3D = motorCanvas ? new Motor3DViewer(motorCanvas) : null;

        if (motor3D) {{
            if (btnCutaway) {{
                btnCutaway.addEventListener('click', () => {{
                    motor3D.cutaway = !motor3D.cutaway;
                    btnCutaway.classList.toggle('ativo', motor3D.cutaway);
                    btnCutaway.setAttribute('aria-pressed', motor3D.cutaway ? 'true' : 'false');
                    const t = I18N[currentLang];
                    btnCutaway.textContent = motor3D.cutaway ? t.cutawayOn : t.cutawayOff;
                }});
            }}
            if (btnAutoRotate3D) {{
                btnAutoRotate3D.addEventListener('click', () => {{
                    motor3D.autoRotate = !motor3D.autoRotate;
                    btnAutoRotate3D.classList.toggle('ativo', motor3D.autoRotate);
                    btnAutoRotate3D.setAttribute('aria-pressed', motor3D.autoRotate ? 'true' : 'false');
                }});
            }}
            if (btnReset3D) {{
                btnReset3D.addEventListener('click', () => {{
                    motor3D.resetView();
                }});
            }}
        }}

        function updateRpmRedlineVisual(rpm) {{
            if (!telemetryRpmPill || !liveRpmValue) return;
            const maxR = Math.max(1000, engineSim.maxRpm || 16000);
            const ratio = engineSim.on && rpm > 20 ? Math.max(0, Math.min(1, rpm / maxR)) : 0;
            const heat = smoothstep(0.35, 0.96, ratio);
            const redline = smoothstep(0.84, 0.99, ratio);

            if (heat <= 0.01) {{
                if (telemetryRpmPill.dataset.heated === '1') {{
                    telemetryRpmPill.dataset.heated = '0';
                    telemetryRpmPill.style.background = '';
                    telemetryRpmPill.style.borderColor = '';
                    telemetryRpmPill.style.boxShadow = '';
                    if (lblTelRpm) lblTelRpm.style.color = '';
                    liveRpmValue.style.color = '';
                    liveRpmValue.style.backgroundImage = '';
                    liveRpmValue.style.webkitBackgroundClip = '';
                    liveRpmValue.style.backgroundClip = '';
                    liveRpmValue.style.webkitTextFillColor = '';
                }}
                return;
            }}

            telemetryRpmPill.dataset.heated = '1';
            const pct = Math.round(ratio * 100);
            const pMid = Math.max(10, pct);
            const pTail = Math.min(100, pMid + 14);
            const aStart = (0.06 + 0.16 * heat).toFixed(3);
            const aFill = (0.14 + 0.34 * heat + 0.14 * redline).toFixed(3);
            const aTail = (0.02 + 0.08 * heat).toFixed(3);
            telemetryRpmPill.style.background = `linear-gradient(90deg, rgba(127, 29, 29, ${{aStart}}) 0%, rgba(220, 38, 38, ${{aFill}}) ${{pMid}}%, rgba(28, 10, 12, ${{aTail}}) ${{pTail}}%, rgba(255, 255, 255, 0.02) 100%)`;
            telemetryRpmPill.style.borderColor = `rgba(239, 68, 68, ${{(0.20 + 0.68 * heat).toFixed(3)}})`;
            telemetryRpmPill.style.boxShadow = `0 0 ${{(6 + 16 * heat + 8 * redline).toFixed(1)}}px rgba(239, 68, 68, ${{(0.10 + 0.42 * heat + 0.18 * redline).toFixed(3)}})`;

            if (lblTelRpm) {{
                const lr = Math.min(255, Math.round(156 + 96 * heat));
                const lg = Math.max(60, Math.round(163 - 68 * heat - 15 * redline));
                const lb = Math.max(60, Math.round(175 - 78 * heat - 15 * redline));
                lblTelRpm.style.color = `rgb(${{lr}}, ${{lg}}, ${{lb}})`;
            }}

            const g1 = Math.max(70, Math.round(255 - 110 * heat - 35 * redline));
            const r2 = Math.round(255 - 12 * redline);
            const g2 = Math.max(45, Math.round(250 - 175 * heat - 25 * redline));
            const r3 = Math.round(248 - 28 * redline);
            const g3 = Math.max(30, Math.round(220 - 182 * heat));
            liveRpmValue.style.color = `rgb(${{r2}}, ${{g2}}, ${{g2}})`;
            liveRpmValue.style.backgroundImage = `linear-gradient(90deg, rgb(255, ${{g1}}, ${{g1}}) 0%, rgb(${{r2}}, ${{g2}}, ${{g2}}) 52%, rgb(${{r3}}, ${{g3}}, ${{g3}}) 100%)`;
            liveRpmValue.style.webkitBackgroundClip = 'text';
            liveRpmValue.style.backgroundClip = 'text';
            liveRpmValue.style.webkitTextFillColor = 'transparent';
        }}

        function setThrottlePercent(rawPct) {{
            const clamped = engineSim.on ? Math.max(0, Math.min(100, Math.round(Number(rawPct) || 0))) : 0;
            engineSim.throttlePct = clamped;
            if (rangeThrottle) {{
                rangeThrottle.value = String(clamped);
                rangeThrottle.style.setProperty('--thr-pct', `${{clamped}}%`);
                rangeThrottle.style.background = clamped > 0
                    ? `linear-gradient(90deg, #fca5a5 0%, #ef4444 ${{Math.max(12, clamped * 0.55)}}%, #dc2626 ${{clamped}}%, rgba(255, 255, 255, 0.12) ${{clamped}}%, rgba(255, 255, 255, 0.12) 100%)`
                    : 'rgba(255, 255, 255, 0.12)';
            }}
            if (throttlePctValue) {{
                throttlePctValue.textContent = `${{clamped}}%`;
            }}
            if (throttleControlWrap) {{
                throttleControlWrap.classList.toggle('ativo', engineSim.on && clamped > 0);
            }}
        }}

        function syncEnginePowerUI() {{
            const t = I18N[currentLang];
            btnEnginePower.classList.toggle('ligado', engineSim.on);
            btnEnginePower.setAttribute('aria-pressed', engineSim.on ? 'true' : 'false');
            btnEnginePowerLabel.textContent = engineSim.on ? t.stopEngine : t.startEngine;
            if (rangeThrottle) rangeThrottle.disabled = !engineSim.on;
            if (throttleControlWrap) throttleControlWrap.classList.toggle('disabled', !engineSim.on);
            if (!engineSim.on) {{
                engineSim.spaceHeld = false;
                engineSim.preSpaceThrottlePct = 0;
                engineSim.isRegening = false;
                setThrottlePercent(0);
            }} else {{
                setThrottlePercent(engineSim.throttlePct);
            }}
            updateRpmRedlineVisual(engineSim.currentRpm);
            drawDynoChart();
        }}

        btnEnginePower.addEventListener('click', e => {{
            engineSim.on = !engineSim.on;
            if (e && e.detail > 0 && typeof btnEnginePower.blur === 'function') btnEnginePower.blur();
            syncEnginePowerUI();
        }});

        const releaseSpaceThrottle = () => {{
            if (!engineSim.spaceHeld) return;
            engineSim.spaceHeld = false;
            setThrottlePercent(engineSim.on ? (engineSim.preSpaceThrottlePct || 0) : 0);
        }};

        if (rangeThrottle) {{
            const onThrottleInput = () => {{
                if (!engineSim.on) {{
                    setThrottlePercent(0);
                    return;
                }}
                engineSim.spaceHeld = false;
                setThrottlePercent(rangeThrottle.value);
            }};
            rangeThrottle.addEventListener('input', onThrottleInput);
            rangeThrottle.addEventListener('change', onThrottleInput);
        }}

        window.addEventListener('blur', releaseSpaceThrottle);
        if (typeof document.addEventListener === 'function') {{
            document.addEventListener('visibilitychange', () => {{
                if (document.hidden) releaseSpaceThrottle();
            }});
        }}
        window.addEventListener('keydown', e => {{
            if (e.code !== 'Space' || !engineSim.on) return;
            const active = document.activeElement;
            if (active && active !== document.body && active !== rangeThrottle && active !== motorCanvas && active.id !== 'motor-bg-stage') return;
            if (e.cancelable) e.preventDefault();
            if (!engineSim.spaceHeld) {{
                engineSim.preSpaceThrottlePct = engineSim.throttlePct || 0;
                engineSim.spaceHeld = true;
            }}
            setThrottlePercent(100);
        }});
        window.addEventListener('keyup', e => {{
            if (e.code !== 'Space') return;
            releaseSpaceThrottle();
        }});

        function readEnginePayload() {{
            const rawDiam = parseFloat(inputStatorDiam ? inputStatorDiam.value : 240);
            const rawStack = parseFloat(inputStackLen ? inputStackLen.value : 165);
            const rawRpm = parseInt(inputRpm ? inputRpm.value : 16000, 10);
            const rawCurr = parseFloat(inputCurrentLimit ? inputCurrentLimit.value : 650);
            const rawKwh = parseFloat(inputBatteryKwh ? inputBatteryKwh.value : 85);
            const rawRotorMass = parseFloat(inputRotorMass ? inputRotorMass.value : 14.5);

            const gbType = selectGearboxType ? selectGearboxType.value : 'Redutor 1V Direto';
            let gbSpeeds = selectGearboxSpeeds ? selectGearboxSpeeds.value : '1';
            if (gbType === 'E-CVT Planetária') gbSpeeds = 'Contínua';
            else if (gbType === 'Caixa EV 2V') gbSpeeds = '2';
            else gbSpeeds = '1';

            return {{
                topology: selectTopology ? selectTopology.value : 'Single',
                motor_type: selectMotorType ? selectMotorType.value : 'PMSM',
                stator_diam: (Number.isFinite(rawDiam) && rawDiam > 0) ? Math.max(120, Math.min(450, rawDiam)) : 240,
                stack_len: (Number.isFinite(rawStack) && rawStack > 0) ? Math.max(50, Math.min(400, rawStack)) : 165,
                poles: selectPoles ? (parseInt(selectPoles.value, 10) || 8) : 8,
                winding: selectWinding ? selectWinding.value : 'Hairpin Cobre',
                housing_mat: selectHousingMat ? selectHousingMat.value : 'Alumínio Fundido',
                rotor_type: selectRotorType ? selectRotorType.value : 'Neodímio N52 (V-Shape)',
                cooling: selectCooling ? selectCooling.value : 'Glicol (Camisa Água)',
                bearing_type: selectBearingType ? selectBearingType.value : 'Aço Padrão',
                field_weakening: selectFieldWeakening ? selectFieldWeakening.value : 'Equilibrado',
                regen_mode: selectRegenMode ? selectRegenMode.value : 'One-Pedal Alta (180 kW)',
                rotor_mass: (Number.isFinite(rawRotorMass) && rawRotorMass > 0) ? Math.max(1.0, Math.min(500.0, rawRotorMass)) : 14.5,
                voltage: selectVoltage ? (parseInt(selectVoltage.value, 10) || 800) : 800,
                inverter: selectInverter ? selectInverter.value : 'SiC Dual',
                current_limit: (Number.isFinite(rawCurr) && rawCurr > 0) ? Math.max(100, Math.min(2400, rawCurr)) : 650,
                battery_chem: selectBatteryChem ? selectBatteryChem.value : 'NMC 811',
                battery_kwh: (Number.isFinite(rawKwh) && rawKwh > 0) ? Math.max(20, Math.min(250, rawKwh)) : 85,
                cell_format: selectCellFormat ? selectCellFormat.value : 'Prismática',
                pack_arch: selectPackArch ? selectPackArch.value : 'Skateboard (Piso)',
                drive_mode: selectDriveMode ? selectDriveMode.value : 'Normal',
                max_rpm: (Number.isFinite(rawRpm) && rawRpm > 0) ? Math.max(3000, Math.min(35000, rawRpm)) : 16000,
                gearbox_type: gbType,
                gearbox_speeds: gbSpeeds,
                diff_type: selectDiffType ? selectDiffType.value : 'Diferencial Aberto',
                final_drive: selectFinalDrive ? (parseFloat(selectFinalDrive.value) || 9.73) : 9.73
            }};
        }}

        function atualizarMotor3D() {{
            const p = readEnginePayload();
            const t = I18N[currentLang];
            const units = TOPOLOGY_UNIT_COUNTS[p.topology] || 1;
            const invShort = (t.inverterShort && t.inverterShort[p.inverter]) ? t.inverterShort[p.inverter] : p.inverter;
            const windShort = (t.windingShort && t.windingShort[p.winding]) ? t.windingShort[p.winding] : p.winding;
            const rotorShort = (t.rotorShort && t.rotorShort[p.rotor_type]) ? t.rotorShort[p.rotor_type] : p.rotor_type;
            const coolShort = (t.coolingShort && t.coolingShort[p.cooling]) ? t.coolingShort[p.cooling] : p.cooling;
            const regenShort = (t.regenShort && t.regenShort[p.regen_mode]) ? t.regenShort[p.regen_mode] : p.regen_mode;
            const houseLabel = (t.housingOpts && t.housingOpts[p.housing_mat]) ? t.housingOpts[p.housing_mat] : p.housing_mat;

            syncRotorSuggestionUI(p);
            computeDynoData(p);

            if (motorNumUnits) motorNumUnits.textContent = String(units);
            if (motor3dBadge) {{
                motor3dBadge.textContent = `${{p.topology.toUpperCase()}} · ${{p.motor_type.toUpperCase()}} · ${{p.voltage}}V ${{invShort.toUpperCase()}}`;
            }}
            if (motor3dSpec) {{
                motor3dSpec.textContent = `${{p.poles}}P · Ø${{Math.round(p.stator_diam)}}×${{Math.round(p.stack_len)}} mm · ${{Math.round(engineSim.peakPowerKw)}} kW`;
            }}

            if (sumArchVal) sumArchVal.textContent = `${{p.topology}} · ${{p.motor_type}} · ${{p.poles}}P`;
            if (sumArchSub) sumArchSub.textContent = `${{p.voltage}} V · ${{t.invWord}} ${{invShort}} · ${{windShort}}`;
            if (sumDispVal) sumDispVal.textContent = `Ø${{Math.round(p.stator_diam)}}×${{Math.round(p.stack_len)}} mm`;
            if (sumGeoSub) sumGeoSub.textContent = `${{p.max_rpm}} RPM · ${{t.reducerWord}} ${{p.final_drive.toFixed(2)}}:1`;
            const fmtShort = (t.cellFormatShort && t.cellFormatShort[p.cell_format]) ? t.cellFormatShort[p.cell_format] : p.cell_format;
            if (sumAdmVal) sumAdmVal.textContent = `${{Math.round(p.battery_kwh)}} kWh · ${{p.battery_chem}} (${{fmtShort}})`;
            if (sumAdmSub) sumAdmSub.textContent = `${{t.effWord}} ${{engineSim.effPct.toFixed(1)}}% · ${{t.regenWord}} ${{regenShort}}`;
            if (sumBuildVal) sumBuildVal.textContent = houseLabel;
            if (sumBuildSub) sumBuildSub.textContent = `${{t.rotorWord}}: ${{rotorShort}} · ${{coolShort}} · ${{Math.round(p.current_limit)}} A`;

            if (motor3D) {{
                motor3D.setConfig({{
                    topology: p.topology,
                    motorType: p.motor_type,
                    statorDiam: p.stator_diam,
                    stackLen: p.stack_len,
                    poles: p.poles,
                    winding: p.winding,
                    housingMat: p.housing_mat,
                    rotorType: p.rotor_type,
                    cooling: p.cooling,
                    bearingType: p.bearing_type,
                    fieldWeakening: p.field_weakening,
                    regenMode: p.regen_mode,
                    rotorMass: p.rotor_mass,
                    voltage: p.voltage,
                    inverter: p.inverter,
                    currentLimit: p.current_limit,
                    batteryChem: p.battery_chem,
                    batteryKwh: p.battery_kwh,
                    cellFormat: p.cell_format,
                    packArch: p.pack_arch,
                    driveMode: p.drive_mode,
                    maxRpm: p.max_rpm,
                    viewMode: viewMode,
                    gearboxType: p.gearbox_type,
                    gearboxSpeeds: p.gearbox_speeds,
                    diffType: p.diff_type,
                    finalDrive: p.final_drive
                }});
            }}
        }}

        function aplicarAlertaRpm(alerta, motivos) {{
            if (!inputRpm) return;
            if (alerta) {{
                inputRpm.classList.add('input-alerta');
                if (rpmAlertaMsg) rpmAlertaMsg.textContent = (motivos || []).join(' | ');
            }} else {{
                inputRpm.classList.remove('input-alerta');
                if (rpmAlertaMsg) rpmAlertaMsg.textContent = '';
            }}
        }}

        async function atualizarWidget3() {{
            const payload = readEnginePayload();
            syncRotorSuggestionUI(payload);
            computeDynoData(payload);

            const t = I18N[currentLang];
            if (window.location.protocol !== 'file:') {{
                try {{
                    const res = await fetch('/api/eletrico', {{
                        method: 'POST',
                        headers: {{ 'Content-Type': 'application/json' }},
                        body: JSON.stringify(payload)
                    }});
                    if (res.ok) {{
                        const data = await res.json();
                        const motivos = [];
                        if (data.tip_speed_ms > data.tip_limit_ms) {{
                            motivos.push(t.warnTipSpeed(Number(data.tip_speed_ms).toFixed(1), Number(data.tip_limit_ms).toFixed(1)));
                        }}
                        if (payload.max_rpm > data.back_emf_limit_rpm) {{
                            motivos.push(t.warnBackEmf(Math.round(data.back_emf_limit_rpm), payload.voltage));
                        }}
                        if (data.unit_kw > data.cooling_cap_kw) {{
                            motivos.push(t.warnThermal(Math.round(data.unit_kw), Math.round(data.cooling_cap_kw)));
                        }}
                        aplicarAlertaRpm(data.alerta_rpm, motivos.length ? motivos : data.motivos_alerta);
                        return;
                    }}
                }} catch (_) {{}}
            }}

            const rotorStats = computeRotorMassStats(payload);
            const isAxial = payload.motor_type === 'Axial Flux' || payload.topology === 'In-Wheel';
            const rotorDiaM = (payload.stator_diam * (isAxial ? 0.86 : 0.62)) / 1000.0;
            const tipSpeedMs = (Math.PI * rotorDiaM * payload.max_rpm) / 60.0;

            const rotorTipMap = {{
                'Neodímio N52 (V-Shape)': 205.0,
                'Halbach Array': 192.0,
                'Gaiola de Cobre': 185.0,
                'Rotor Bobinado (EESM)': 172.0,
                'Manga Carbono (Alta RPM)': 275.0
            }};
            const bearingBonus = {{ 'Aço Padrão': 0.0, 'Cerâmica Si3N4': 20.0, 'Magnético Ativo': 38.0 }}[payload.bearing_type] || 0.0;
            const baseTipLim = (rotorTipMap[payload.rotor_type] || 205.0) * (isAxial ? 0.86 : 1.0);
            const tipLimitMs = Math.max(120.0, baseTipLim + bearingBonus - rotorStats.tipStressPenalty);

            const fwRpmMult = {{ 'Conservador': 0.88, 'Equilibrado': 1.04, 'Agressivo': 1.24 }}[payload.field_weakening] || 1.04;
            const gbRpmMult = payload.gearbox_type === 'Caixa EV 2V' ? 1.15 : 1.00;
            const backEmfRpm = 17500.0 * (payload.voltage / 800.0) * fwRpmMult * gbRpmMult;

            const coolingCapMap = {{
                'Ar (Aletas)': 160.0,
                'Glicol (Camisa Água)': 480.0,
                'Óleo Direto': 650.0,
                'Imersão Dielétrica': 880.0
            }};
            const coolingCapKw = (coolingCapMap[payload.cooling] || 480.0) * (isAxial ? 1.10 : 1.00);
            const units = TOPOLOGY_UNIT_COUNTS[payload.topology] || 1;
            const peakKwSafe = Number.isFinite(engineSim.peakPowerKw) ? engineSim.peakPowerKw : 447;
            const unitKw = peakKwSafe / Math.max(1, units);

            const motivosAlerta = [];
            if (tipSpeedMs > tipLimitMs) {{
                motivosAlerta.push(t.warnTipSpeed(tipSpeedMs.toFixed(1), tipLimitMs.toFixed(1)));
            }}
            if (payload.max_rpm > backEmfRpm) {{
                motivosAlerta.push(t.warnBackEmf(Math.round(backEmfRpm), payload.voltage));
            }}
            if (unitKw > coolingCapKw) {{
                motivosAlerta.push(t.warnThermal(Math.round(unitKw), Math.round(coolingCapKw)));
            }}
            aplicarAlertaRpm(motivosAlerta.length > 0, motivosAlerta);
        }}

        async function atualizarDados() {{
            const p = readEnginePayload();
            atualizarMotor3D();

            if (window.location.protocol !== 'file:') {{
                try {{
                    const res = await fetch('/api/ficha', {{
                        method: 'POST',
                        headers: {{ 'Content-Type': 'application/json' }},
                        body: JSON.stringify({{
                            topology: p.topology,
                            motor_type: p.motor_type,
                            voltage: p.voltage
                        }})
                    }});
                    if (res.ok) {{
                        const data = await res.json();
                        if (motorNumUnits && data.units !== undefined) {{
                            motorNumUnits.textContent = String(data.units);
                        }}
                        atualizarWidget3();
                        return;
                    }}
                }} catch (_) {{}}
            }}
            atualizarWidget3();
        }}

        function syncSubsystemUI() {{
            const t = I18N[currentLang];
            const gb = selectGearboxType ? selectGearboxType.value : 'Redutor 1V Direto';
            const isEcvt = gb === 'E-CVT Planetária';
            const isTwoSpd = gb === 'Caixa EV 2V';
            if (selectGearboxSpeeds) {{
                if (isEcvt) {{
                    selectGearboxSpeeds.value = 'Contínua';
                    selectGearboxSpeeds.disabled = true;
                    selectGearboxSpeeds.title = t.gbSpeedsEcvtTitle || '';
                }} else if (isTwoSpd) {{
                    selectGearboxSpeeds.value = '2';
                    selectGearboxSpeeds.disabled = true;
                    selectGearboxSpeeds.title = '';
                }} else {{
                    selectGearboxSpeeds.value = '1';
                    selectGearboxSpeeds.disabled = true;
                    selectGearboxSpeeds.title = '';
                }}
            }}

            const gbShort = (t.gbTypeShort && t.gbTypeShort[gb]) ? t.gbTypeShort[gb] : gb;
            const diff = selectDiffType ? selectDiffType.value : 'Diferencial Aberto';
            const diffShort = (t.diffShort && t.diffShort[diff]) ? t.diffShort[diff] : diff;
            const fdVal = selectFinalDrive ? (parseFloat(selectFinalDrive.value) || 9.73).toFixed(2) : '9.73';
            const spdShort = isEcvt ? (t.gbSteplessShort || 'Cont.') : (isTwoSpd ? '2V' : '1V');

            if (gearboxSummaryInfo) {{
                gearboxSummaryInfo.textContent = `${{gbShort}} · ${{spdShort}} · ${{diffShort}} · ${{fdVal}}:1`;
            }}

            const chem = selectBatteryChem ? selectBatteryChem.value : 'NMC 811';
            const rawKwh = parseFloat(inputBatteryKwh ? inputBatteryKwh.value : 85);
            const kwhVal = (Number.isFinite(rawKwh) && rawKwh > 0) ? Math.max(20, Math.min(250, rawKwh)) : 85;
            const cFmt = selectCellFormat ? selectCellFormat.value : 'Prismática';
            const pArch = selectPackArch ? selectPackArch.value : 'Skateboard (Piso)';
            const cFmtShort = (t.cellFormatShort && t.cellFormatShort[cFmt]) ? t.cellFormatShort[cFmt] : cFmt;
            const pArchShort = (t.packArchShort && t.packArchShort[pArch]) ? t.packArchShort[pArch] : pArch;
            if (batterySummaryInfo) {{
                batterySummaryInfo.textContent = `${{chem}} · ${{Math.round(kwhVal)}} kWh · ${{cFmtShort}} · ${{pArchShort}}`;
            }}

            if (btnTopEngine) {{
                btnTopEngine.style.display = viewMode === 'engine' ? 'none' : 'inline-flex';
            }}
            if (btnTopGearbox) {{
                btnTopGearbox.textContent = `${{t.topGearbox}} · ${{spdShort}}`;
                btnTopGearbox.classList.toggle('ativo', viewMode === 'gearbox' || activeTopPopover === 'gearbox');
                btnTopGearbox.setAttribute('aria-expanded', activeTopPopover === 'gearbox' ? 'true' : 'false');
            }}
            if (btnTopBattery) {{
                btnTopBattery.textContent = `${{t.topBattery}} · ${{Math.round(kwhVal)}} kWh`;
                btnTopBattery.classList.toggle('ativo', viewMode === 'battery' || activeTopPopover === 'battery');
                btnTopBattery.setAttribute('aria-expanded', activeTopPopover === 'battery' ? 'true' : 'false');
            }}
            if (btnTopAll) {{
                const isAll = viewMode === 'all';
                btnTopAll.classList.toggle('ativo', isAll);
                btnTopAll.setAttribute('aria-pressed', isAll ? 'true' : 'false');
            }}
        }}

        function setViewAndPopover(mode, popoverWhich) {{
            if (mode !== undefined && mode !== null) {{
                viewMode = mode;
            }}
            activeTopPopover = popoverWhich;
            if (popoverGearbox) popoverGearbox.classList.toggle('aberto', activeTopPopover === 'gearbox');
            if (popoverBattery) popoverBattery.classList.toggle('aberto', activeTopPopover === 'battery');
            syncSubsystemUI();
            atualizarMotor3D();
        }}

        if (btnTopEngine) btnTopEngine.addEventListener('click', () => setViewAndPopover('engine', null));
        if (btnTopAll) {{
            btnTopAll.addEventListener('click', () => {{
                setViewAndPopover(viewMode === 'all' ? 'engine' : 'all', null);
            }});
        }}
        if (btnGbBackEngine) btnGbBackEngine.addEventListener('click', () => setViewAndPopover('engine', null));
        if (btnBatBackEngine) btnBatBackEngine.addEventListener('click', () => setViewAndPopover('engine', null));
        if (btnTopGearbox) {{
            btnTopGearbox.addEventListener('click', () => {{
                if (viewMode !== 'gearbox') {{
                    setViewAndPopover('gearbox', 'gearbox');
                }} else {{
                    setViewAndPopover('gearbox', activeTopPopover === 'gearbox' ? null : 'gearbox');
                }}
            }});
        }}
        if (btnTopBattery) {{
            btnTopBattery.addEventListener('click', () => {{
                if (viewMode !== 'battery') {{
                    setViewAndPopover('battery', 'battery');
                }} else {{
                    setViewAndPopover('battery', activeTopPopover === 'battery' ? null : 'battery');
                }}
            }});
        }}
        if (btnCloseGearbox) btnCloseGearbox.addEventListener('click', () => setViewAndPopover(null, null));
        if (btnCloseBattery) btnCloseBattery.addEventListener('click', () => setViewAndPopover(null, null));

        [selectGearboxType, selectGearboxSpeeds, selectDiffType, selectFinalDrive].forEach(el => {{
            if (!el) return;
            el.addEventListener('change', () => {{
                syncSubsystemUI();
                atualizarMotor3D();
                atualizarWidget3();
            }});
        }});

        [selectBatteryChem, inputBatteryKwh, selectCellFormat, selectPackArch].forEach(el => {{
            if (!el) return;
            el.addEventListener('input', () => {{
                syncSubsystemUI();
                atualizarMotor3D();
                atualizarWidget3();
            }});
            el.addEventListener('change', () => {{
                syncSubsystemUI();
                atualizarMotor3D();
                atualizarWidget3();
            }});
        }});

        if (inputRotorMass) {{
            inputRotorMass.addEventListener('input', () => {{
                const raw = parseFloat(inputRotorMass.value);
                if (Number.isFinite(raw) && raw > 500) {{
                    inputRotorMass.value = '500';
                }}
                atualizarMotor3D();
                atualizarWidget3();
            }});
            inputRotorMass.addEventListener('change', () => {{
                const raw = parseFloat(inputRotorMass.value);
                const clamped = (Number.isFinite(raw) && raw > 0) ? Math.max(1.0, Math.min(500.0, raw)) : (engineSim.rotorIdealKg || 14.5);
                inputRotorMass.value = String(Math.round(clamped * 10) / 10);
                atualizarMotor3D();
                atualizarWidget3();
            }});
        }}

        if (btnRotorIdeal) {{
            btnRotorIdeal.addEventListener('click', () => {{
                const p = readEnginePayload();
                const ideal = computeIdealRotorKg(p);
                if (inputRotorMass) inputRotorMass.value = ideal.toFixed(1);
                atualizarMotor3D();
                atualizarWidget3();
            }});
        }}

        if (selectMotorType) {{
            selectMotorType.addEventListener('change', () => {{
                syncMotorAndRotorUI(true);
                atualizarDados();
            }});
        }}
        if (selectTopology) {{
            selectTopology.addEventListener('change', () => {{
                atualizarDados();
            }});
        }}
        if (selectRotorType) {{
            selectRotorType.addEventListener('change', () => {{
                syncMotorAndRotorUI(false);
                atualizarMotor3D();
                atualizarWidget3();
            }});
        }}

        [inputStatorDiam, inputStackLen, selectPoles, selectWinding, selectHousingMat, selectCooling, selectBearingType, selectFieldWeakening, selectRegenMode, selectVoltage, selectInverter, inputCurrentLimit, selectDriveMode, inputRpm].forEach(el => {{
            if (!el) return;
            el.addEventListener('input', () => {{
                atualizarMotor3D();
                atualizarWidget3();
            }});
            el.addEventListener('change', () => {{
                atualizarMotor3D();
                atualizarWidget3();
            }});
        }});

        if (btnPagePrev) {{
            btnPagePrev.addEventListener('click', () => setActivePage(currentPageIdx - 1));
        }}
        if (btnPageNext) {{
            btnPageNext.addEventListener('click', () => setActivePage(currentPageIdx + 1));
        }}
        for (let pi = 0; pi < 4; pi++) {{
            const dotBtn = document.getElementById(`page-dot-${{pi}}`);
            if (dotBtn) dotBtn.addEventListener('click', () => setActivePage(pi));
        }}

        window.addEventListener('resize', () => drawDynoChart());
        syncMotorAndRotorUI(false);
        syncSubsystemUI();
        syncEnginePowerUI();
        setActivePage(0);
        atualizarMotor3D();
        atualizarWidget3();
    </script>
</body>
</html>"""


def guardar_index_html(
    caminho: str | None = None,
    topology: str = "Single",
    motor_type: str = "PMSM",
    voltage: int = 800,
) -> str:
    destino = caminho or os.path.join(os.path.dirname(os.path.abspath(__file__)), "index.html")
    html = gerar_dashboard_html(topology=topology, motor_type=motor_type, voltage=voltage)
    with open(destino, "w", encoding="utf-8") as f:
        f.write(html)
    return destino


class DashboardHandler(SimpleHTTPRequestHandler):
    """Servidor estático + API EV (/api/ficha e /api/eletrico)."""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=os.path.dirname(os.path.abspath(__file__)), **kwargs)

    def do_GET(self):
        if self.path in ("/", "/index.html", "/custom-engine"):
            html = gerar_dashboard_html().encode("utf-8")
            self.send_response(200)
            self.send_header("Content-Type", "text/html; charset=utf-8")
            self.send_header("Content-Length", str(len(html)))
            self.end_headers()
            self.wfile.write(html)
            return
        super().do_GET()

    def do_POST(self):
        if self.path not in ("/api/ficha", "/api/eletrico"):
            self.send_error(404)
            return
        try:
            length = int(self.headers.get("Content-Length", "0"))
            body = self.rfile.read(length).decode("utf-8") if length > 0 else "{}"
            payload = json.loads(body or "{}")
        except (ValueError, UnicodeDecodeError):
            self.send_error(400)
            return

        if self.path == "/api/ficha":
            topo = str(payload.get("topology", "Single"))
            m_type = str(payload.get("motor_type", "PMSM"))
            volt = int(payload.get("voltage", 800) or 800)
            svg, rotulo = gerar_svg_motor_eletrico(topo, m_type, volt)
            resp = json.dumps({
                "ok": True,
                "svg": svg,
                "units": clamp_units_topology(topo),
                "rotulo_tipo": rotulo,
            }).encode("utf-8")
        else:
            dados = processar_eletrico(
                topology=str(payload.get("topology", "Single")),
                motor_type=str(payload.get("motor_type", "PMSM")),
                stator_diam=float(payload.get("stator_diam", 240.0) or 240.0),
                stack_len=float(payload.get("stack_len", 165.0) or 165.0),
                poles=int(payload.get("poles", 8) or 8),
                winding=str(payload.get("winding", "Hairpin Cobre")),
                housing_mat=str(payload.get("housing_mat", "Alumínio Fundido")),
                rotor_type=str(payload.get("rotor_type", "Neodímio N52 (V-Shape)")),
                cooling=str(payload.get("cooling", "Glicol (Camisa Água)")),
                bearing_type=str(payload.get("bearing_type", "Aço Padrão")),
                field_weakening=str(payload.get("field_weakening", "Equilibrado")),
                regen_mode=str(payload.get("regen_mode", "One-Pedal Alta (180 kW)")),
                rotor_mass=float(payload.get("rotor_mass", 14.5) or 14.5),
                voltage=int(payload.get("voltage", 800) or 800),
                inverter=str(payload.get("inverter", "SiC Dual")),
                current_limit=float(payload.get("current_limit", 650.0) or 650.0),
                battery_chem=str(payload.get("battery_chem", "NMC 811")),
                battery_kwh=float(payload.get("battery_kwh", 85.0) or 85.0),
                drive_mode=str(payload.get("drive_mode", "Normal")),
                max_rpm=int(payload.get("max_rpm", 16000) or 16000),
                gearbox_type=str(payload.get("gearbox_type", "Redutor 1V Direto")),
                gearbox_speeds=str(payload.get("gearbox_speeds", "1")),
                diff_type=str(payload.get("diff_type", "Diferencial Aberto")),
                final_drive=float(payload.get("final_drive", 9.73) or 9.73),
            )
            resp = json.dumps({"ok": True, **dados}).encode("utf-8")

        self.send_response(200)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(resp)))
        self.end_headers()
        self.wfile.write(resp)


def iniciar_servidor(porta: int = 8000, open_browser: bool = True) -> None:
    guardar_index_html()
    server = HTTPServer(("127.0.0.1", porta), DashboardHandler)
    url = f"http://127.0.0.1:{porta}/"
    print(f"Servidor EV a correr em {url}", file=sys.stderr)
    if open_browser:
        webbrowser.open(url)
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        server.server_close()


if __name__ == "__main__":
    if "--build-only" in sys.argv:
        guardar_index_html()
    else:
        iniciar_servidor()