from __future__ import annotations

from http.server import HTTPServer, SimpleHTTPRequestHandler
import json
import math
import os
import sys
import webbrowser

BASE_DIR = os.path.dirname(os.path.abspath(__file__))


# ==============================================================================
# WIDGET 1: BASE DO MOTOR (Design Simplista & Estilizado 2D + Admissão)
# ==============================================================================
SVG_MOTOR_DEFS = """
<defs>
    <linearGradient id="eng-block" x1="0" y1="0" x2="0" y2="1">
        <stop offset="0%" stop-color="#171b24" />
        <stop offset="100%" stop-color="#0b0e14" />
    </linearGradient>
    <radialGradient id="eng-piston" cx="38%" cy="35%" r="65%">
        <stop offset="0%" stop-color="#64748b" />
        <stop offset="65%" stop-color="#1e293b" />
        <stop offset="100%" stop-color="#0f172a" />
    </radialGradient>
    <linearGradient id="eng-accent" x1="0" y1="0" x2="1" y2="0">
        <stop offset="0%" stop-color="#ff1e38" />
        <stop offset="100%" stop-color="#ff6b00" />
    </linearGradient>
    <linearGradient id="eng-amber" x1="0" y1="0" x2="1" y2="0">
        <stop offset="0%" stop-color="#ff9f1c" />
        <stop offset="100%" stop-color="#ff6b00" />
    </linearGradient>
    <linearGradient id="eng-pipe" x1="0" y1="0" x2="0" y2="1">
        <stop offset="0%" stop-color="#94a3b8" />
        <stop offset="100%" stop-color="#475569" />
    </linearGradient>
</defs>
"""


def clamp_cilindros_formato(formato: str, num_cilindros: int) -> int:
    """Restringe o número de cilindros/rotores aos limites válidos por formato."""
    fmt = str(formato).upper()
    limites = {
        "I": [3, 4, 5, 6],
        "VR": [3, 4, 5, 6],
        "V": [4, 6, 8, 10, 12, 16],
        "W": [4, 6, 8, 10, 12, 16],
        "B": [4, 6, 8],
        "WANKEL": [1, 2, 3, 4],
    }
    permitidos = limites.get(fmt, [3, 4, 5, 6])
    n = int(num_cilindros)
    if n in permitidos:
        return n
    return min(permitidos, key=lambda c: (abs(c - n), c))


def gerar_svg_motor_inline(
    num_cilindros: int = 4,
    formato: str = "I",
    admissao: str = "Atmosférico",
    turbo_config: str = "Paralelo",
    radiator_type: str = "OEM Alumínio",
) -> str:
    """
    Desenha o SVG 2D simplista e estilizado do motor de acordo com o formato escolhido
    (I, V, VR, W, B ou WANKEL) e tipo de admissão (Atmosférico, Turbo, Supercompressor,
    Biturbo, Quad Turbo ou Twincharge), respeitando os limites por formato.
    """
    formato = str(formato).upper()
    if formato not in ("I", "V", "VR", "W", "B", "WANKEL"):
        formato = "I"
    num_cilindros = clamp_cilindros_formato(formato, num_cilindros)

    adm = str(admissao) if str(admissao) in (
        "Atmosférico", "Turbo", "Supercompressor", "Biturbo", "Quad Turbo", "Twincharge"
    ) else "Atmosférico"
    t_cfg = "Sequencial" if (adm in ("Biturbo", "Quad Turbo") and str(turbo_config) == "Sequencial") else "Paralelo"

    def desenhar_cilindro(cx: float, cy: float, r: float) -> str:
        r_pistao = max(3.4, r * 0.72)
        r_centro = max(1.3, min(3.2, r * 0.18))
        return (
            f'<circle cx="{cx:.1f}" cy="{cy:.1f}" r="{r:.1f}" fill="#06080c" stroke="#94a3b8" stroke-width="1.35" />\n'
            f'<circle cx="{cx:.1f}" cy="{cy:.1f}" r="{r_pistao:.1f}" fill="url(#eng-piston)" stroke="#334155" stroke-width="0.8" />\n'
            f'<circle cx="{cx:.1f}" cy="{cy:.1f}" r="{r_centro:.1f}" fill="#ff1e38" />\n'
        )

    def desenhar_polia(cx: float, cy: float, r: float, cor_centro: str = "#ff1e38") -> str:
        r_in = max(2.2, r * 0.44)
        return (
            f'<circle cx="{cx:.1f}" cy="{cy:.1f}" r="{r:.1f}" fill="#0d1017" stroke="#94a3b8" stroke-width="1.3" />\n'
            f'<circle cx="{cx:.1f}" cy="{cy:.1f}" r="{r_in:.1f}" fill="none" stroke="{cor_centro}" stroke-width="1.2" />\n'
        )

    def desenhar_parafusos(x: float, y: float, w: float, h: float, pad: float = 6.5) -> str:
        coords = [
            (x + pad, y + pad),
            (x + w - pad, y + pad),
            (x + pad, y + h - pad),
            (x + w - pad, y + h - pad),
        ]
        return "".join(
            f'<circle cx="{px:.1f}" cy="{py:.1f}" r="1.3" fill="#475569" />\n'
            for px, py in coords
        )

    def desenhar_turbo(cx: float, cy: float, escala: float = 1.0) -> str:
        return (
            f'<g transform="translate({cx:.1f},{cy:.1f}) scale({escala:.2f})">\n'
            f'  <line x1="-10" y1="0" x2="10" y2="0" stroke="#94a3b8" stroke-width="2" />\n'
            f'  <rect x="-4" y="-3.5" width="8" height="7" rx="2" fill="#1e293b" stroke="#64748b" stroke-width="0.9" />\n'
            f'  <circle cx="-11" cy="0" r="10.5" fill="#0f141e" stroke="#e2e8f0" stroke-width="1.3" />\n'
            f'  <path d="M -11,-5.5 L -11,5.5 M -16.5,0 L -5.5,0" stroke="#64748b" stroke-width="1.1" />\n'
            f'  <circle cx="-11" cy="0" r="2.2" fill="#ff1e38" />\n'
            f'  <circle cx="11" cy="0" r="9.5" fill="#180d0c" stroke="#ff6b00" stroke-width="1.3" />\n'
            f'  <circle cx="11" cy="0" r="4.0" fill="#0b090a" stroke="#ff6b00" stroke-width="0.9" />\n'
            f'</g>\n'
        )

    def desenhar_intercooler(x: float, y: float, w: float, h: float, vertical: bool = False) -> str:
        rad_col = {
            "OEM Alumínio": "#94a3b8",
            "Duplo Núcleo": "#cbd5e1",
            "Triple-Pass Racing": "#f97316",
            "Cobre / Latão": "#d97706",
            "Água-Ar (Charge Cooler)": "#38bdf8",
        }.get(str(radiator_type), "#94a3b8")
        divs = 6 if str(radiator_type) == "Duplo Núcleo" else 4
        linhas = ""
        for k in range(1, divs):
            if vertical:
                ly = y + k * (h / float(divs))
                linhas += f'<line x1="{x + 4:.1f}" y1="{ly:.1f}" x2="{x + w - 4:.1f}" y2="{ly:.1f}" stroke="#475569" stroke-width="1" />\n'
            else:
                lx = x + k * (w / float(divs))
                linhas += f'<line x1="{lx:.1f}" y1="{y + 4:.1f}" x2="{lx:.1f}" y2="{y + h - 4:.1f}" stroke="#475569" stroke-width="1" />\n'
        return (
            f'<rect x="{x:.1f}" y="{y:.1f}" width="{w:.1f}" height="{h:.1f}" rx="4" fill="#090c12" stroke="{rad_col}" stroke-width="1.3" />\n'
            f'{linhas}'
        )

    def desenhar_filtro_conico(x: float, y: float, w: float, h: float) -> str:
        return (
            f'<polygon points="{x:.1f},{y + 2.5:.1f} {x + w:.1f},{y:.1f} {x + w:.1f},{y + h:.1f} {x:.1f},{y + h - 2.5:.1f}" '
            f'fill="#190c10" stroke="#ff1e38" stroke-width="1.2" stroke-linejoin="round" />\n'
            f'<line x1="{x + w * 0.45:.1f}" y1="{y + 3.5:.1f}" x2="{x + w * 0.45:.1f}" y2="{y + h - 3.5:.1f}" stroke="#7f1d1d" stroke-width="1" />\n'
        )

    def desenhar_supercharger(
        x: float, y: float, w: float, h: float,
        pulley_x: float, pulley_y: float, crank_x: float, crank_y: float
    ) -> str:
        snout_y = y + h / 2.0
        return (
            f'<line x1="{pulley_x:.1f}" y1="{pulley_y:.1f}" x2="{crank_x:.1f}" y2="{crank_y:.1f}" stroke="#475569" stroke-width="2.6" />\n'
            f'<rect x="{pulley_x:.1f}" y="{snout_y - 3.5:.1f}" width="{max(6.0, x - pulley_x + 2):.1f}" height="7" rx="2" fill="#1e293b" stroke="#64748b" stroke-width="1" />\n'
            f'<rect x="{x:.1f}" y="{y:.1f}" width="{w:.1f}" height="{h:.1f}" rx="6" fill="#121620" stroke="#cbd5e1" stroke-width="1.3" />\n'
            f'<rect x="{x + 14:.1f}" y="{snout_y - 2:.1f}" width="{w - 28:.1f}" height="4" rx="2" fill="url(#eng-amber)" />\n'
            f'{desenhar_polia(pulley_x, pulley_y, 7.2, "#ff9f1c")}'
        )

    corpo_svg = ""

    if formato == "WANKEL":
        largura_bloco = 236.0
        inicio_x = 84.0
        espaco = largura_bloco / num_cilindros
        rx_h = min(22.0, max(12.0, (espaco - 8.0) * 0.44))
        rotores_svg = ""
        for i in range(num_cilindros):
            cx = inicio_x + i * espaco + espaco / 2.0
            rotores_svg += (
                f'<rect x="{cx - rx_h:.1f}" y="78" width="{rx_h * 2:.1f}" height="90" rx="10" fill="#090c12" stroke="#94a3b8" stroke-width="1.4" />\n'
                f'<polygon points="{cx:.1f},92 {cx - rx_h * 0.68:.1f},145 {cx + rx_h * 0.68:.1f},145" fill="url(#eng-piston)" stroke="#ff1e38" stroke-width="1.1" stroke-linejoin="round" />\n'
                f'<circle cx="{cx:.1f}" cy="123" r="4.2" fill="#ff1e38" />\n'
            )
        turbo_wankel = ""
        if adm == "Turbo":
            turbo_wankel = desenhar_turbo(210.0, 206.0, 1.28)
        elif adm == "Biturbo":
            if t_cfg == "Sequencial":
                turbo_wankel = (
                    '<path d="M 164,206 L 254,206" stroke="#f59e0b" stroke-width="2.4" stroke-dasharray="4 3" />\n'
                    + desenhar_turbo(152.0, 206.0, 0.96)
                    + desenhar_turbo(266.0, 206.0, 1.32)
                )
            else:
                turbo_wankel = desenhar_turbo(152.0, 206.0, 1.18) + desenhar_turbo(266.0, 206.0, 1.18)
        elif adm == "Quad Turbo":
            if t_cfg == "Sequencial":
                turbo_wankel = (
                    '<path d="M 106,206 L 298,206" stroke="#f59e0b" stroke-width="2.2" stroke-dasharray="4 3" />\n'
                    + "".join(
                        desenhar_turbo(106.0 + k * 64.0, 206.0, 0.84 if k % 2 == 0 else 1.12)
                        for k in range(4)
                    )
                )
            else:
                turbo_wankel = "".join(desenhar_turbo(106.0 + k * 64.0, 206.0, 1.0) for k in range(4))
        elif adm == "Supercompressor":
            turbo_wankel = desenhar_supercharger(92.0, 32.0, 212.0, 22.0, 48.0, 43.0, 48.0, 123.0)
        elif adm == "Twincharge":
            turbo_wankel = desenhar_turbo(216.0, 206.0, 1.2) + desenhar_supercharger(92.0, 32.0, 212.0, 22.0, 48.0, 43.0, 48.0, 123.0)

        corpo_svg = f"""
        <rect x="64" y="68" width="276" height="110" rx="12" fill="url(#eng-block)" stroke="#64748b" stroke-width="1.5" />
        <line x1="52" y1="123" x2="346" y2="123" stroke="#64748b" stroke-width="4" stroke-linecap="round" />
        {rotores_svg}
        {turbo_wankel}
        {desenhar_polia(48.0, 123.0, 10.2)}
        <rect x="342" y="93" width="11" height="60" rx="3" fill="#1e293b" stroke="#64748b" stroke-width="1.2" />
        """
    elif formato in ("I", "VR"):
        largura_bloco = 260.0 if formato == "I" else 248.0
        inicio_x = 72.0 if formato == "I" else 78.0
        espaco = largura_bloco / num_cilindros
        if formato == "I":
            raio = min(21.0, max(5.2, (espaco - 4.5) / 2.0))
        else:
            raio = min(16.0, max(7.0, (espaco * 1.15 - 4.0) / 2.0))
            if num_cilindros >= 10:
                raio = min(raio, 10.2)
        sw_runner = max(2.2, min(5.5, raio * 0.35))

        cilindros = ""
        coletores = ""
        for i in range(num_cilindros):
            cx = inicio_x + i * espaco + espaco / 2.0
            cy = 123.0 if formato == "I" else (104.0 if i % 2 == 0 else 142.0)
            cilindros += desenhar_cilindro(cx, cy, raio)
            coletores += (
                f'<line x1="{cx:.1f}" y1="54" x2="{cx:.1f}" y2="72" stroke="#64748b" stroke-width="{sw_runner:.1f}" stroke-linecap="round" />\n'
                f'<line x1="{cx:.1f}" y1="174" x2="{cx:.1f}" y2="192" stroke="#c2410c" stroke-width="{sw_runner:.1f}" stroke-linecap="round" />\n'
            )

        admissao_svg = ""
        if adm == "Atmosférico":
            admissao_svg = (
                f'<rect x="78" y="40" width="248" height="14" rx="5" fill="#121620" stroke="#94a3b8" stroke-width="1.3" />\n'
                f'<rect x="90" y="45.5" width="224" height="3" rx="1.5" fill="url(#eng-accent)" />\n'
                f'<line x1="54" y1="47" x2="78" y2="47" stroke="#64748b" stroke-width="5" />\n'
                f'{desenhar_filtro_conico(22.0, 38.0, 32.0, 18.0)}'
                f'<rect x="82" y="191" width="240" height="8" rx="4" fill="#1a100e" stroke="#ea580c" stroke-width="1.1" />\n'
            )
        elif adm == "Turbo":
            admissao_svg = (
                f'<path d="M 30,190 L 30,47 L 78,47" fill="none" stroke="url(#eng-pipe)" stroke-width="4.5" stroke-linejoin="round" />\n'
                f'<path d="M 68,210 L 184,210" fill="none" stroke="url(#eng-pipe)" stroke-width="4.5" />\n'
                f'{desenhar_intercooler(16.0, 194.0, 50.0, 26.0)}'
                f'<rect x="78" y="40" width="248" height="14" rx="5" fill="#121620" stroke="#94a3b8" stroke-width="1.3" />\n'
                f'<rect x="90" y="45.5" width="224" height="3" rx="1.5" fill="url(#eng-accent)" />\n'
                f'<rect x="82" y="191" width="240" height="8" rx="4" fill="#1a100e" stroke="#ea580c" stroke-width="1.1" />\n'
                f'{desenhar_turbo(216.0, 211.0, 1.32)}'
            )
        elif adm == "Supercompressor":
            admissao_svg = (
                f'<rect x="82" y="191" width="240" height="8" rx="4" fill="#1a100e" stroke="#ea580c" stroke-width="1.1" />\n'
                f'<line x1="304" y1="43" x2="328" y2="43" stroke="#64748b" stroke-width="5" />\n'
                f'{desenhar_filtro_conico(328.0, 34.0, 30.0, 18.0)}'
                f'{desenhar_supercharger(92.0, 30.0, 212.0, 24.0, 48.0, 42.0, 48.0, 123.0)}'
            )
        elif adm == "Biturbo":
            seq_pipe = '<path d="M 164,211 L 266,211" fill="none" stroke="#f59e0b" stroke-width="2.4" stroke-dasharray="4 3" />\n' if t_cfg == "Sequencial" else ""
            s1, s2 = (1.00, 1.38) if t_cfg == "Sequencial" else (1.24, 1.24)
            admissao_svg = (
                f'<path d="M 30,190 L 30,47 L 78,47" fill="none" stroke="url(#eng-pipe)" stroke-width="4.5" stroke-linejoin="round" />\n'
                f'<path d="M 68,210 L 266,210" fill="none" stroke="url(#eng-pipe)" stroke-width="4.5" />\n'
                f'{seq_pipe}'
                f'{desenhar_intercooler(16.0, 194.0, 50.0, 26.0)}'
                f'<rect x="78" y="40" width="248" height="14" rx="5" fill="#121620" stroke="#94a3b8" stroke-width="1.3" />\n'
                f'<rect x="90" y="45.5" width="224" height="3" rx="1.5" fill="url(#eng-accent)" />\n'
                f'<rect x="82" y="191" width="240" height="8" rx="4" fill="#1a100e" stroke="#ea580c" stroke-width="1.1" />\n'
                f'{desenhar_turbo(146.0, 211.0, s1)}'
                f'{desenhar_turbo(282.0, 211.0, s2)}'
            )
        elif adm == "Quad Turbo":
            seq_pipe = '<path d="M 112,211 L 310,211" fill="none" stroke="#f59e0b" stroke-width="2.2" stroke-dasharray="4 3" />\n' if t_cfg == "Sequencial" else ""
            qs = (0.86, 1.18, 0.86, 1.18) if t_cfg == "Sequencial" else (1.05, 1.05, 1.05, 1.05)
            admissao_svg = (
                f'<path d="M 30,190 L 30,47 L 78,47" fill="none" stroke="url(#eng-pipe)" stroke-width="4.5" stroke-linejoin="round" />\n'
                f'<path d="M 68,210 L 326,210" fill="none" stroke="url(#eng-pipe)" stroke-width="4.5" />\n'
                f'{seq_pipe}'
                f'{desenhar_intercooler(16.0, 194.0, 50.0, 26.0)}'
                f'<rect x="78" y="40" width="248" height="14" rx="5" fill="#121620" stroke="#94a3b8" stroke-width="1.3" />\n'
                f'<rect x="90" y="45.5" width="224" height="3" rx="1.5" fill="url(#eng-accent)" />\n'
                f'<rect x="82" y="191" width="240" height="8" rx="4" fill="#1a100e" stroke="#ea580c" stroke-width="1.1" />\n'
                f'{desenhar_turbo(112.0, 211.0, qs[0])}'
                f'{desenhar_turbo(178.0, 211.0, qs[1])}'
                f'{desenhar_turbo(244.0, 211.0, qs[2])}'
                f'{desenhar_turbo(310.0, 211.0, qs[3])}'
            )
        else:  # Twincharge
            admissao_svg = (
                f'<path d="M 24,190 L 24,38 L 84,38" fill="none" stroke="url(#eng-pipe)" stroke-width="4.2" stroke-linejoin="round" />\n'
                f'<path d="M 68,210 L 194,210" fill="none" stroke="url(#eng-pipe)" stroke-width="4.2" />\n'
                f'{desenhar_intercooler(14.0, 194.0, 50.0, 26.0)}'
                f'<rect x="82" y="191" width="240" height="8" rx="4" fill="#1a100e" stroke="#ea580c" stroke-width="1.1" />\n'
                f'{desenhar_turbo(224.0, 211.0, 1.28)}'
                f'{desenhar_supercharger(92.0, 30.0, 212.0, 24.0, 48.0, 42.0, 48.0, 123.0)}'
            )

        corpo_svg = f"""
        {coletores}
        {admissao_svg}
        <rect x="41" y="84" width="15" height="52" rx="7" fill="#0d1017" stroke="#475569" stroke-width="1.2" />
        {desenhar_polia(48.0, 93.0, 6.4)}
        {desenhar_polia(48.0, 123.0, 11.4)}
        <rect x="342" y="93" width="11" height="60" rx="3" fill="#1e293b" stroke="#64748b" stroke-width="1.2" />
        <rect x="64" y="70" width="276" height="106" rx="10" fill="url(#eng-block)" stroke="#64748b" stroke-width="1.5" />
        {desenhar_parafusos(64.0, 70.0, 276.0, 106.0)}
        {cilindros}
        """

    else:  # formato == "V", "W" ou "B" (Boxer)
        n_sup = (num_cilindros + 1) // 2
        n_inf = num_cilindros // 2
        cols = max(1, n_sup, n_inf)
        largura = 244.0
        inicio_x = 80.0
        espaco_sup = largura / max(1, n_sup)
        espaco_inf = largura / max(1, n_inf)

        if formato == "V":
            raio = min(15.5, max(5.8, (largura / cols - 6.0) / 2.0))
            bank_sup_y, bank_sup_h = 55.0, 50.0
            bank_inf_y, bank_inf_h = 141.0, 50.0
            y_exh_sup, y_exh_inf = 39.0, 193.0
            y_col_sup, y_col_inf = 38.0, 201.0
        elif formato == "B":
            raio = min(14.5, max(5.8, (largura / cols - 6.0) / 2.0))
            bank_sup_y, bank_sup_h = 48.0, 48.0
            bank_inf_y, bank_inf_h = 150.0, 48.0
            y_exh_sup, y_exh_inf = 33.0, 199.0
            y_col_sup, y_col_inf = 32.0, 207.0
        else:
            raio = min(10.8, max(6.6, (largura / cols) * 0.34))
            bank_sup_y, bank_sup_h = 47.0, 58.0
            bank_inf_y, bank_inf_h = 141.0, 58.0
            y_exh_sup, y_exh_inf = 32.0, 200.0
            y_col_sup, y_col_inf = 31.0, 208.0

        sw_runner = max(2.0, min(4.8, raio * 0.35))
        cilindros = ""
        escapes = ""
        trombetas = ""

        for i in range(n_sup):
            cx = inicio_x + i * espaco_sup + espaco_sup / 2.0
            cy = 80.0 if formato == "V" else (64.0 if i % 2 == 0 else 87.0)
            cilindros += desenhar_cilindro(cx, cy, raio)
            escapes += f'<line x1="{cx:.1f}" y1="{y_exh_sup:.1f}" x2="{cx:.1f}" y2="{y_exh_sup + 16:.1f}" stroke="#c2410c" stroke-width="{sw_runner:.1f}" stroke-linecap="round" />\n'
            trombetas += f'<circle cx="{cx:.1f}" cy="116" r="{max(2.2, min(3.4, sw_runner * 0.72)):.1f}" fill="#ff1e38" opacity="0.85" />\n'
        for i in range(n_inf):
            cx = inicio_x + i * espaco_inf + espaco_inf / 2.0
            cy = 166.0 if formato == "V" else (159.0 if i % 2 == 0 else 182.0)
            cilindros += desenhar_cilindro(cx, cy, raio)
            escapes += f'<line x1="{cx:.1f}" y1="{y_exh_inf:.1f}" x2="{cx:.1f}" y2="{y_exh_inf + 16:.1f}" stroke="#c2410c" stroke-width="{sw_runner:.1f}" stroke-linecap="round" />\n'
            trombetas += f'<circle cx="{cx:.1f}" cy="130" r="{max(2.2, min(3.4, sw_runner * 0.72)):.1f}" fill="#ff1e38" opacity="0.85" />\n'

        admissao_vw = ""
        if adm == "Atmosférico":
            admissao_vw = (
                f'<rect x="78" y="109" width="250" height="28" rx="6" fill="#121620" stroke="#94a3b8" stroke-width="1.3" />\n'
                f'{trombetas}'
                f'<line x1="328" y1="123" x2="352" y2="123" stroke="#64748b" stroke-width="5" />\n'
                f'{desenhar_filtro_conico(352.0, 113.0, 30.0, 20.0)}'
            )
        elif adm == "Turbo":
            admissao_vw = (
                f'<path d="M 185,24 L 24,24 L 24,87" fill="none" stroke="url(#eng-pipe)" stroke-width="4.5" stroke-linejoin="round" />\n'
                f'<path d="M 24,159 L 24,123 L 82,123" fill="none" stroke="url(#eng-pipe)" stroke-width="4.5" stroke-linejoin="round" />\n'
                f'{desenhar_intercooler(14.0, 86.0, 20.0, 74.0, True)}'
                f'<rect x="78" y="109" width="250" height="28" rx="6" fill="#121620" stroke="#94a3b8" stroke-width="1.3" />\n'
                f'<rect x="94" y="121.5" width="218" height="3" rx="1.5" fill="url(#eng-accent)" />\n'
                f'{desenhar_turbo(212.0, 24.0, 1.24)}'
            )
        elif adm == "Supercompressor":
            admissao_vw = (
                f'<line x1="318" y1="123" x2="342" y2="123" stroke="#64748b" stroke-width="5" />\n'
                f'{desenhar_filtro_conico(342.0, 113.0, 30.0, 20.0)}'
                f'<line x1="48" y1="80" x2="48" y2="166" stroke="#475569" stroke-width="2.6" />\n'
                f'{desenhar_supercharger(84.0, 108.0, 236.0, 30.0, 48.0, 123.0, 48.0, 123.0)}'
            )
        elif adm == "Biturbo":
            seq_pipe = '<path d="M 212,24 L 212,222" fill="none" stroke="#f59e0b" stroke-width="2.2" stroke-dasharray="4 3" />\n' if t_cfg == "Sequencial" else ""
            s1, s2 = (0.98, 1.35) if t_cfg == "Sequencial" else (1.22, 1.22)
            admissao_vw = (
                f'<path d="M 185,24 L 24,24 L 24,86" fill="none" stroke="url(#eng-pipe)" stroke-width="4.5" stroke-linejoin="round" />\n'
                f'<path d="M 185,222 L 24,222 L 24,160" fill="none" stroke="url(#eng-pipe)" stroke-width="4.5" stroke-linejoin="round" />\n'
                f'<line x1="34" y1="123" x2="82" y2="123" stroke="url(#eng-pipe)" stroke-width="4.5" />\n'
                f'{seq_pipe}'
                f'{desenhar_intercooler(14.0, 86.0, 20.0, 74.0, True)}'
                f'<rect x="78" y="109" width="250" height="28" rx="6" fill="#121620" stroke="#94a3b8" stroke-width="1.3" />\n'
                f'<rect x="94" y="121.5" width="218" height="3" rx="1.5" fill="url(#eng-accent)" />\n'
                f'{desenhar_turbo(212.0, 24.0, s1)}'
                f'{desenhar_turbo(212.0, 222.0, s2)}'
            )
        elif adm == "Quad Turbo":
            seq_pipe = (
                '<path d="M 150,24 L 272,24 M 150,222 L 272,222" fill="none" stroke="#f59e0b" stroke-width="2.2" stroke-dasharray="4 3" />\n'
                if t_cfg == "Sequencial" else ""
            )
            s_pri, s_sec = (0.86, 1.18) if t_cfg == "Sequencial" else (1.05, 1.05)
            admissao_vw = (
                f'<path d="M 120,24 L 24,24 L 24,86" fill="none" stroke="url(#eng-pipe)" stroke-width="4.5" stroke-linejoin="round" />\n'
                f'<path d="M 272,24 L 180,24" fill="none" stroke="url(#eng-pipe)" stroke-width="4.2" />\n'
                f'<path d="M 120,222 L 24,222 L 24,160" fill="none" stroke="url(#eng-pipe)" stroke-width="4.5" stroke-linejoin="round" />\n'
                f'<path d="M 272,222 L 180,222" fill="none" stroke="url(#eng-pipe)" stroke-width="4.2" />\n'
                f'<line x1="34" y1="123" x2="82" y2="123" stroke="url(#eng-pipe)" stroke-width="4.5" />\n'
                f'{seq_pipe}'
                f'{desenhar_intercooler(14.0, 86.0, 20.0, 74.0, True)}'
                f'{desenhar_turbo(150.0, 24.0, s_pri)}'
                f'{desenhar_turbo(272.0, 24.0, s_sec)}'
                f'{desenhar_turbo(150.0, 222.0, s_pri)}'
                f'{desenhar_turbo(272.0, 222.0, s_sec)}'
            )
        else:  # Twincharge
            admissao_vw = (
                f'<path d="M 185,24 L 24,24 L 24,86" fill="none" stroke="url(#eng-pipe)" stroke-width="4.2" stroke-linejoin="round" />\n'
                f'<path d="M 24,160 L 24,226 L 348,226 L 348,123 L 318,123" fill="none" stroke="url(#eng-pipe)" stroke-width="4.2" stroke-linejoin="round" />\n'
                f'{desenhar_intercooler(14.0, 86.0, 20.0, 74.0, True)}'
                f'{desenhar_turbo(212.0, 24.0, 1.22)}'
                f'{desenhar_supercharger(84.0, 108.0, 236.0, 30.0, 48.0, 123.0, 48.0, 123.0)}'
            )

        corpo_svg = f"""
        {escapes}
        <rect x="82" y="{y_col_sup:.1f}" width="240" height="6.5" rx="3" fill="#1a100e" stroke="#ea580c" stroke-width="1" />
        <rect x="82" y="{y_col_inf:.1f}" width="240" height="6.5" rx="3" fill="#1a100e" stroke="#ea580c" stroke-width="1" />
        <path d="M 39,77 L 64,61 L 64,185 L 39,169 Z" fill="#0d1017" stroke="#475569" stroke-width="1.2" />
        {desenhar_polia(48.0, 80.0, 8.2)}
        {desenhar_polia(48.0, 166.0, 8.2)}
        <rect x="342" y="91" width="11" height="64" rx="3" fill="#1e293b" stroke="#64748b" stroke-width="1.2" />
        <rect x="64" y="{bank_sup_y:.1f}" width="276" height="{bank_sup_h:.1f}" rx="9" fill="url(#eng-block)" stroke="#64748b" stroke-width="1.5" />
        <rect x="64" y="{bank_inf_y:.1f}" width="276" height="{bank_inf_h:.1f}" rx="9" fill="url(#eng-block)" stroke="#64748b" stroke-width="1.5" />
        <rect x="76" y="{bank_sup_y - 2.5:.1f}" width="252" height="3" rx="1.5" fill="url(#eng-accent)" />
        <rect x="76" y="{bank_inf_y + bank_inf_h - 0.5:.1f}" width="252" height="3" rx="1.5" fill="url(#eng-accent)" />
        <rect x="64" y="105" width="276" height="36" fill="#080a0f" stroke="rgba(255,255,255,0.06)" stroke-width="0.9" />
        <line x1="54" y1="123" x2="342" y2="123" stroke="#475569" stroke-width="4" stroke-linecap="round" />
        {cilindros}
        {admissao_vw}
        {desenhar_polia(48.0, 123.0, 9.8, "#ff9f1c" if adm in ("Supercompressor", "Twincharge") else "#ff1e38")}
        """

    return f"""
    <svg class="motor-svg" viewBox="0 0 400 246" xmlns="http://www.w3.org/2000/svg"
         aria-label="Motor {formato} {adm} 2D">
        {SVG_MOTOR_DEFS}
        {corpo_svg}
    </svg>
    """


def widget_motor_inline(
    num_cilindros: int = 4,
    formato: str = "I",
    admissao: str = "Atmosférico",
) -> str:
    """
    Gera a coluna esquerda aberta sobre o motor 3D no background com os botões
    de Ligar/Desligar e Acelerar, bem como a telemetria instantânea.
    """
    formato_clean = str(formato).upper() if str(formato).upper() in ("I", "V", "VR", "W", "B") else "I"
    return f"""
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
                            <span id="lbl-tel-cyl">CILINDROS</span>
                            <strong id="motor-num-cilindros">{num_cilindros}</strong>
                        </div>
                        <div class="telemetry-pill">
                            <span id="lbl-tel-geo">GEOMETRIA</span>
                            <strong id="motor-3d-spec">{formato_clean} · 86×86 mm</strong>
                        </div>
                    </div>
                </div>
            </div>
    """


# ==============================================================================
# PERFIS DE FORMATO E ADMISSÃO + WIDGET DYNO CURVES
# ==============================================================================
FORMATOS_MOTOR = {
    "I": "I (Em Linha)",
    "V": "V (Em V)",
    "VR": "VR (V Estreito)",
    "W": "W (Em W)",
    "B": "B (Boxer)",
    "WANKEL": "Wankel (Rotativo)",
}

FORMAT_CYL_OPTIONS = {
    "I": [3, 4, 5, 6],
    "VR": [3, 4, 5, 6],
    "V": [4, 6, 8, 10, 12, 16],
    "W": [4, 6, 8, 10, 12, 16],
    "B": [4, 6, 8],
    "WANKEL": [1, 2, 3, 4],
}

PERFIS_ADMISSAO = {
    "Atmosférico": {
        "pressao": "0.0 bar (Atmosférico)",
        "mult_potencia": 1.00,
        "mult_binario": 1.00,
        "turbo_bar": 0.0,
        "sc_bar": 0.0,
    },
    "Turbo": {
        "pressao": "+1.5 bar",
        "mult_potencia": 1.55,
        "mult_binario": 1.60,
        "turbo_bar": 1.5,
        "sc_bar": 0.0,
    },
    "Supercompressor": {
        "pressao": "+0.8 bar",
        "mult_potencia": 1.35,
        "mult_binario": 1.45,
        "turbo_bar": 0.0,
        "sc_bar": 0.8,
    },
    "Biturbo": {
        "pressao": "+2.0 bar",
        "mult_potencia": 1.80,
        "mult_binario": 1.85,
        "turbo_bar": 2.0,
        "sc_bar": 0.0,
    },
    "Quad Turbo": {
        "pressao": "+2.5 bar",
        "mult_potencia": 2.08,
        "mult_binario": 2.10,
        "turbo_bar": 2.5,
        "sc_bar": 0.0,
    },
    "Twincharge": {
        "pressao": "+1.5 / +0.8 bar",
        "mult_potencia": 1.90,
        "mult_binario": 1.95,
        "turbo_bar": 1.5,
        "sc_bar": 0.8,
    },
}


def widget_dyno_modular(potencia_txt: str = "146 kW", torque_txt: str = "212 Nm") -> str:
    """
    Widget Dyno Curves: gráfico em tempo real das curvas de potência (kW / hp)
    e binário (Nm / lb-ft), leitura instantânea no cursor e seletor de unidades.
    """
    return f"""
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
                        <canvas id="dyno-canvas" class="dyno-canvas" aria-label="Gráfico de curvas de potência e binário (Dyno)"></canvas>
                    </div>
                </section>
    """


# ==============================================================================
# WIDGET 3: CONFIGURAÇÕES DO MOTOR (BARRA INFERIOR EM 3 SECÇÕES) + CÁLCULOS
# ==============================================================================
def calcular_peso_ideal_damper(
    bore: float = 86.0,
    stroke: float = 86.0,
    max_rpm: int = 7500,
    combustivel: str = "Gasolina 95",
    ciclo: str = "4T",
    num_cilindros: int = 4,
    admissao: str = "Atmosférico",
    formato: str = "I",
    piston_material: str = "Alumínio",
    turbo_bar: float = 0.0,
    sc_bar: float = 0.0,
) -> float:
    """Sugere o peso ideal (kg, limite 2000 kg) do harmonic damper conforme a arquitetura do motor."""
    fmt = str(formato).upper() if str(formato).upper() in FORMATOS_MOTOR else "I"
    cyl = clamp_cilindros_formato(fmt, num_cilindros)
    is_wankel = fmt == "WANKEL"
    unit_cc = (math.pi / 4.0) * ((max(10.0, float(bore)) / 10.0) ** 2) * (max(10.0, float(stroke)) / 10.0)
    litros = (unit_cc * (1.308 if is_wankel else 1.0) * cyl) / 1000.0
    base_mass = 1.25 + (max(0.3, litros) ** 0.72) * 1.10

    if is_wankel:
        fmt_mult = 0.42
    elif fmt == "B":
        fmt_mult = 0.82
    elif fmt == "VR":
        fmt_mult = 0.94
    elif fmt == "V":
        fmt_mult = 1.06 if cyl >= 10 else 0.98
    elif fmt == "W":
        fmt_mult = 1.22
    else:
        fmt_mult = 1.12 if cyl >= 5 else (1.04 if cyl == 3 else 1.00)

    is_diesel = combustivel in ("Diesel", "Biodiesel")
    if is_diesel:
        fuel_mult = 1.38
    elif combustivel == "Nitrometano":
        fuel_mult = 1.34
    elif combustivel in ("Etanol (E85)", "Metanol", "Gasolina 102", "Gasolina 110"):
        fuel_mult = 1.06
    else:
        fuel_mult = 1.00

    cycle_mult = 1.00 if is_wankel else (0.90 if str(ciclo).upper() == "2T" else 1.00)
    adm = admissao if admissao in PERFIS_ADMISSAO else "Atmosférico"
    if adm == "Supercompressor":
        boost_total = max(0.0, min(4.0, float(sc_bar)))
    elif adm == "Twincharge":
        boost_total = max(0.0, min(6.0, float(turbo_bar))) + max(0.0, min(4.0, float(sc_bar)))
    elif adm != "Atmosférico":
        boost_total = max(0.0, min(6.0, float(turbo_bar)))
    else:
        boost_total = 0.0
    boost_mult = 1.0 + min(0.45, boost_total * 0.08)

    rpm_mult = max(0.75, min(1.16, 1.06 - (max(1500, int(max_rpm)) - 6500) * 0.000022))
    pis_ideal_map = {"Alumínio": 1.00, "Forged": 1.06, "Forged Heavy": 1.15, "Titânio": 0.88}
    pis_mult = 0.92 if is_wankel else pis_ideal_map.get(piston_material, 1.00)
    raw = base_mass * fmt_mult * fuel_mult * cycle_mult * boost_mult * rpm_mult * pis_mult
    return round(max(0.5, min(2000.0, raw)), 1)


def processar_combustao(
    bore: float = 86.0,
    stroke: float = 86.0,
    compression_ratio: float = 10.5,
    max_rpm: int = 7500,
    combustivel: str = "Gasolina 95",
    ciclo: str = "4T",
    num_cilindros: int = 4,
    admissao: str = "Atmosférico",
    formato: str = "I",
    v_angle: str = "60",
    material: str = "Alumínio",
    piston_material: str = "Alumínio",
    camshaft: str = "DOHC",
    valve_type: str = "Molas",
    num_valvulas: int = 4,
    turbo_bar: float = 1.5,
    sc_bar: float = 0.8,
    turbo_config: str = "Paralelo",
    flywheel: str = "Monomassa Aço",
    damper: str = "Elastómero OEM",
    damper_weight: float | None = None,
    intake_type: str = "Plenum OEM",
    intake_material: str = "Alumínio Fundido",
    gearbox_type: str = "Manual",
    gearbox_speeds: int = 6,
    clutch_type: str = "Monodisco Orgânica",
    exhaust_type: str = "OEM Catalisador",
    exhaust_junction: str = "X-Pipe",
    exhaust_diameter: float = 63.0,
    radiator_type: str = "OEM Alumínio",
) -> dict:
    """
    Calcula automaticamente em Python os parâmetros do motor (potência em kW,
    binário em Nm, cilindrada e alertas mecânicos) para o Dyno Curves.
    """
    bore = max(10.0, float(bore))
    stroke = max(10.0, float(stroke))
    cr = max(2.0, float(compression_ratio))
    max_rpm = max(500, int(max_rpm))
    formato_valido = str(formato).upper() if str(formato).upper() in FORMATOS_MOTOR else "I"
    ciclo = "4T" if formato_valido == "WANKEL" else ("2T" if str(ciclo).upper() == "2T" else "4T")
    num_cilindros = clamp_cilindros_formato(formato_valido, num_cilindros)
    admissao_valida = admissao if admissao in PERFIS_ADMISSAO else "Atmosférico"
    turbo_b = max(0.0, min(6.0, float(turbo_bar)))
    sc_b = max(0.0, min(4.0, float(sc_bar)))
    has_multi_turbo = admissao_valida in ("Biturbo", "Quad Turbo")
    t_cfg = "Sequencial" if (has_multi_turbo and str(turbo_config) == "Sequencial") else "Paralelo"
    tcfg_tq = 1.025 if (has_multi_turbo and t_cfg == "Sequencial") else 1.00
    tcfg_hp = 0.985 if (has_multi_turbo and t_cfg == "Sequencial") else 1.00

    has_radiator = admissao_valida in ("Turbo", "Biturbo", "Quad Turbo", "Twincharge")
    perfis_radiador = {
        "OEM Alumínio": {"tq": 1.000, "hp": 1.000, "cr_tol": 0.0},
        "Duplo Núcleo": {"tq": 1.020, "hp": 1.030, "cr_tol": 0.5},
        "Triple-Pass Racing": {"tq": 1.030, "hp": 1.055, "cr_tol": 1.0},
        "Cobre / Latão": {"tq": 1.015, "hp": 1.022, "cr_tol": 0.4},
        "Água-Ar (Charge Cooler)": {"tq": 1.040, "hp": 1.045, "cr_tol": 1.2},
    }
    p_rad = (
        perfis_radiador.get(radiator_type, perfis_radiador["OEM Alumínio"])
        if has_radiator
        else {"tq": 1.000, "hp": 1.000, "cr_tol": 0.0}
    )

    if admissao_valida == "Atmosférico":
        adm_mb, adm_mp = 1.00, 1.00
        pressao_str = "0.0 bar (Atmosférico)"
    elif admissao_valida == "Turbo":
        adm_mb = 1.0 + turbo_b * 0.40
        adm_mp = 1.0 + turbo_b * 0.367
        pressao_str = f"+{turbo_b:.1f} bar"
    elif admissao_valida == "Supercompressor":
        adm_mb = 1.0 + sc_b * 0.5625
        adm_mp = 1.0 + sc_b * 0.4375
        pressao_str = f"+{sc_b:.1f} bar"
    elif admissao_valida == "Biturbo":
        adm_mb = 1.0 + turbo_b * 0.425
        adm_mp = 1.0 + turbo_b * 0.40
        pressao_str = f"+{turbo_b:.1f} bar"
    elif admissao_valida == "Quad Turbo":
        adm_mb = 1.0 + turbo_b * 0.44
        adm_mp = 1.0 + turbo_b * 0.43
        pressao_str = f"+{turbo_b:.1f} bar"
    else:  # Twincharge
        eff_b = turbo_b + sc_b * 0.70
        adm_mb = 1.0 + eff_b * 0.46
        adm_mp = 1.0 + eff_b * 0.435
        pressao_str = f"+{turbo_b:.1f} / +{sc_b:.1f} bar"

    fatores_combustivel = {
        "Gasolina 91": {"torque": 0.96, "power": 0.95, "cr_lim": 11.0},
        "Gasolina 95": {"torque": 1.00, "power": 1.00, "cr_lim": 12.5},
        "Gasolina": {"torque": 1.00, "power": 1.00, "cr_lim": 12.5},
        "Gasolina 98": {"torque": 1.03, "power": 1.04, "cr_lim": 14.0},
        "Gasolina 102": {"torque": 1.06, "power": 1.08, "cr_lim": 15.5},
        "Gasolina 110": {"torque": 1.09, "power": 1.12, "cr_lim": 17.5},
        "Etanol (E85)": {"torque": 1.10, "power": 1.11, "cr_lim": 16.5},
        "Metanol": {"torque": 1.14, "power": 1.15, "cr_lim": 18.0},
        "Nitrometano": {"torque": 1.45, "power": 1.52, "cr_lim": 14.5},
        "Diesel": {"torque": 1.14, "power": 0.78, "cr_lim": 22.0},
        "Biodiesel": {"torque": 1.10, "power": 0.75, "cr_lim": 21.5},
    }
    perfil_comb = fatores_combustivel.get(combustivel, fatores_combustivel["Gasolina 95"])

    perfis_intake = {
        "Plenum OEM": {"tq": 1.000, "hp": 1.000},
        "ITBs": {"tq": 0.985, "hp": 1.055},
        "Dual-Plenum": {"tq": 1.040, "hp": 1.020},
        "Velocity Stacks": {"tq": 0.960, "hp": 1.075},
        "Cold Air Intake": {"tq": 1.015, "hp": 1.030},
    }
    p_int = perfis_intake.get(intake_type, perfis_intake["Plenum OEM"])

    perfis_intake_mat = {
        "Alumínio Fundido": {"tq": 1.000, "hp": 1.000},
        "Plástico ABS": {"tq": 1.008, "hp": 1.005},
        "Alumínio Billet": {"tq": 1.005, "hp": 1.020},
        "Fibra de Carbono": {"tq": 1.020, "hp": 1.035},
        "Magnésio": {"tq": 1.010, "hp": 1.025},
        "Titânio": {"tq": 1.005, "hp": 1.030},
    }
    p_imat = perfis_intake_mat.get(intake_material, perfis_intake_mat["Alumínio Fundido"])

    perfis_gearbox = {
        "Manual": {"tq": 1.000, "hp": 1.000},
        "Gated Manual": {"tq": 1.005, "hp": 1.012},
        "Manual 6V": {"tq": 1.000, "hp": 1.000},
        "Manual 5V": {"tq": 1.005, "hp": 1.005},
        "Sequencial": {"tq": 1.010, "hp": 1.025},
        "Sequencial 6V": {"tq": 1.010, "hp": 1.025},
        "DCT": {"tq": 0.995, "hp": 1.015},
        "DCT 7V": {"tq": 0.995, "hp": 1.015},
        "Automática": {"tq": 1.015, "hp": 0.975},
        "Automática 8V": {"tq": 1.015, "hp": 0.975},
        "E-CVT": {"tq": 1.045, "hp": 1.035},
    }
    p_gb = perfis_gearbox.get(gearbox_type, perfis_gearbox["Manual"])
    gb_speeds = max(4, min(9, int(gearbox_speeds or 6)))
    gb_spd_hp = 1.0 if gearbox_type == "E-CVT" else (1.0 + (gb_speeds - 6) * 0.004)

    perfis_clutch = {
        "Monodisco Orgânica": {"tq": 1.000, "hp": 1.000},
        "Cerâmica Racing": {"tq": 1.012, "hp": 1.012},
        "Duplo Disco Aço": {"tq": 1.010, "hp": 1.018},
        "Carbono Multi-Disco": {"tq": 1.000, "hp": 1.028},
        "Conversor de Binário": {"tq": 1.020, "hp": 0.978},
    }
    p_cl = perfis_clutch.get(clutch_type, perfis_clutch["Monodisco Orgânica"])

    perfis_exhaust = {
        "OEM Catalisador": {"tq": 1.000, "hp": 1.000},
        "Sport Cat-Back": {"tq": 1.010, "hp": 1.025},
        "Inconel 4-1": {"tq": 1.015, "hp": 1.045},
        "Titânio Valvetronic": {"tq": 1.020, "hp": 1.038},
        "Straight Pipe": {"tq": 0.990, "hp": 1.055},
    }
    p_exh = perfis_exhaust.get(exhaust_type, perfis_exhaust["OEM Catalisador"])

    perfis_junction = {
        "Sem União": {"tq": 1.000, "hp": 1.000},
        "X-Pipe": {"tq": 1.005, "hp": 1.022},
        "H-Pipe": {"tq": 1.018, "hp": 1.005},
        "Y-Pipe": {"tq": 1.012, "hp": 1.010},
        "Coletor Merge": {"tq": 1.008, "hp": 1.018},
    }
    supports_junc = formato_valido in ("B", "VR", "V", "W")
    exh_junc_eff = exhaust_junction if supports_junc else "Sem União"
    p_junc = perfis_junction.get(exh_junc_eff, perfis_junction["X-Pipe" if supports_junc else "Sem União"])

    try:
        exh_d = float(str(exhaust_diameter).lower().replace("mm", "").strip())
    except (TypeError, ValueError):
        exh_d = 63.0
    exh_d = max(35.0, min(140.0, exh_d))
    d_delta = (exh_d - 63.0) / 63.0
    p_ediam = {
        "tq": max(0.96, min(1.03, 1.0 - 0.024 * d_delta)),
        "hp": max(0.92, min(1.06, 1.0 + 0.055 * (1.0 - math.exp(-d_delta * 1.4)))),
    }

    is_wankel = formato_valido == "WANKEL"
    is_2t = (not is_wankel) and (ciclo == "2T")
    eff_valve_type = "Reed Valve" if is_2t else valve_type
    is_freevalve = (not is_2t) and (camshaft == "Freevalve" or eff_valve_type == "Freevalve")
    perfis_cam = {
        "DOHC": {"tq": 1.00, "hp": 1.00},
        "SOHC": {"tq": 1.01, "hp": 0.96},
        "OHV": {"tq": 1.04, "hp": 0.91},
        "Freevalve": {"tq": 1.06, "hp": 1.10},
    }
    p_cam = (
        {"tq": 1.00, "hp": 1.00}
        if (is_wankel or is_2t)
        else (perfis_cam["Freevalve"] if is_freevalve else perfis_cam.get(camshaft, perfis_cam["DOHC"]))
    )

    perfis_valvulas = {
        "Molas": {"tq": 1.00, "hp": 1.00, "tol": 0.0},
        "VVT": {"tq": 1.03, "hp": 1.03, "tol": 0.5},
        "Desmodrómico": {"tq": 1.01, "hp": 1.05, "tol": 2.0},
        "Pneumático": {"tq": 1.00, "hp": 1.08, "tol": 4.0},
        "Freevalve": {"tq": 1.00, "hp": 1.00, "tol": 4.5},
        "Reed Valve": {"tq": 1.00, "hp": 1.00, "tol": 3.5},
    }
    p_val = perfis_valvulas["Freevalve"] if is_freevalve else perfis_valvulas.get(eff_valve_type, perfis_valvulas["Molas"])

    perfis_mat = {
        "Alumínio": {"hp": 1.00, "tol": 0.5},
        "Ferro Fundido": {"hp": 1.00, "tol": -0.5},
        "Alumínio Billet": {"hp": 1.02, "tol": 3.0},
        "Forged": {"hp": 1.01, "tol": 2.5},
        "Forged Heavy": {"hp": 0.99, "tol": 1.5},
        "Billet": {"hp": 1.03, "tol": 3.8},
        "Magnésio": {"hp": 1.01, "tol": 1.5},
        "Titanium": {"hp": 1.02, "tol": 4.5},
        "Titanium Billet": {"hp": 1.04, "tol": 6.0},
        "Titanium Forged": {"hp": 1.03, "tol": 5.5},
    }
    p_mat = perfis_mat.get(material, perfis_mat["Alumínio"])

    perfis_pistao = {
        "Alumínio": {"tq": 1.00, "hp": 1.00, "tol": 0.0, "cr_tol": 0.0},
        "Forged": {"tq": 1.01, "hp": 1.02, "tol": 2.5, "cr_tol": 1.0},
        "Forged Heavy": {"tq": 1.03, "hp": 0.98, "tol": 1.5, "cr_tol": 3.0},
        "Titânio": {"tq": 1.00, "hp": 1.05, "tol": 5.0, "cr_tol": 2.0},
    }
    p_pis = perfis_pistao.get(piston_material, perfis_pistao["Alumínio"])

    perfis_flywheel = {
        "Monomassa Aço": {"tq": 1.000, "hp": 1.000, "tol": 0.0},
        "Dupla Massa": {"tq": 1.015, "hp": 0.985, "tol": -0.8},
        "Aligeirado Cromoly": {"tq": 1.000, "hp": 1.015, "tol": 1.0},
        "Alumínio Billet": {"tq": 0.995, "hp": 1.022, "tol": 1.5},
        "Carbono Multi-Disco": {"tq": 0.990, "hp": 1.032, "tol": 2.5},
    }
    p_fw = perfis_flywheel.get(flywheel, perfis_flywheel["Monomassa Aço"])

    perfis_damper = {
        "Elastómero OEM": {"tq": 1.000, "hp": 1.000, "tol": 0.0},
        "Fluido Viscoso": {"tq": 1.005, "hp": 1.010, "tol": 2.0},
        "ATI Super Damper": {"tq": 1.005, "hp": 1.020, "tol": 3.5},
        "Polia Sólida": {"tq": 1.000, "hp": 1.006, "tol": -2.5},
    }
    p_dmp = perfis_damper.get(damper, perfis_damper["Elastómero OEM"])
    ideal_damper_kg = calcular_peso_ideal_damper(
        bore=bore,
        stroke=stroke,
        max_rpm=max_rpm,
        combustivel=combustivel,
        ciclo=ciclo,
        num_cilindros=num_cilindros,
        admissao=admissao_valida,
        formato=formato_valido,
        piston_material=piston_material,
        turbo_bar=turbo_b,
        sc_bar=sc_b,
    )
    damper_w = ideal_damper_kg if (damper_weight is None or float(damper_weight) <= 0) else max(0.1, min(2000.0, float(damper_weight)))
    w_ratio = damper_w / max(0.5, ideal_damper_kg)
    w_hp = (
        max(0.95, 1.0 - (0.70 - w_ratio) * 0.06)
        if w_ratio < 0.70
        else (max(0.72, 1.0 - math.log1p(max(0.0, damper_w - ideal_damper_kg * 1.4)) * 0.030) if damper_w > ideal_damper_kg * 1.4 else 1.00)
    )
    w_tq = (
        max(0.84, 1.0 - math.log1p(max(0.0, damper_w - ideal_damper_kg * 2.0)) * 0.018)
        if damper_w > ideal_damper_kg * 2.0
        else 1.00
    )
    if 0.75 <= w_ratio <= 1.35:
        w_tol = 0.4
    elif w_ratio < 0.75:
        w_tol = -min(3.0, (0.75 - w_ratio) * 5.0)
    elif damper_w > ideal_damper_kg * 1.8:
        w_tol = -min(3.5, math.log1p(max(0.0, damper_w - ideal_damper_kg * 1.8)) * 0.55)
    else:
        w_tol = 0.0

    n_val = 2 if int(num_valvulas) == 2 else 4
    val_tq = 1.00 if (is_wankel or is_2t) else (1.02 if n_val == 2 else 1.00)
    val_hp = 1.00 if (is_wankel or is_2t) else (0.93 if n_val == 2 else 1.00)
    if is_wankel:
        p_cam = {"tq": 1.00, "hp": 1.00}
        p_val = {"tq": 1.00, "hp": 1.00, "tol": 6.0}

    # 1. Cilindrada em Litros
    cilindrada_unit_cc = (math.pi / 4.0) * ((bore / 10.0) ** 2) * (stroke / 10.0)
    if is_wankel:
        cilindrada_litros = (cilindrada_unit_cc * 1.308 * num_cilindros) / 1000.0
    else:
        cilindrada_litros = (cilindrada_unit_cc * num_cilindros) / 1000.0

    # 2. Binário estimado (Nm) e Potência estimada (kW) considerando todos os parâmetros
    fator_cr = 1.0 + max(-0.25, min(0.35, (cr - 10.0) * 0.025))
    fator_ciclo_tq = 1.42 if is_wankel else (1.25 if ciclo == "2T" else 1.00)
    torque_nm = int(round(
        cilindrada_litros
        * 105.0
        * fator_cr
        * perfil_comb["torque"]
        * fator_ciclo_tq
        * adm_mb
        * tcfg_tq
        * p_cam["tq"]
        * p_val["tq"]
        * val_tq
        * p_pis["tq"]
        * p_fw["tq"]
        * p_dmp["tq"]
        * w_tq
        * p_int["tq"]
        * p_imat["tq"]
        * p_gb["tq"]
        * p_cl["tq"]
        * p_exh["tq"]
        * p_junc["tq"]
        * p_ediam["tq"]
        * p_rad["tq"]
    ))

    fator_rpm_potencia = 0.93 if is_wankel else (0.88 if ciclo == "4T" else 0.94)
    potencia_cv = (
        ((torque_nm * max_rpm * fator_rpm_potencia) / 7121.0)
        * (adm_mp / adm_mb)
        * (tcfg_hp / tcfg_tq)
        * (perfil_comb["power"] / perfil_comb["torque"])
        * (p_cam["hp"] / p_cam["tq"])
        * (p_val["hp"] / p_val["tq"])
        * (val_hp / val_tq)
        * p_mat["hp"]
        * (p_pis["hp"] / p_pis["tq"])
        * (p_fw["hp"] / p_fw["tq"])
        * (p_dmp["hp"] / p_dmp["tq"])
        * (w_hp / w_tq)
        * (p_int["hp"] / p_int["tq"])
        * (p_imat["hp"] / p_imat["tq"])
        * (p_gb["hp"] / p_gb["tq"])
        * gb_spd_hp
        * (p_cl["hp"] / p_cl["tq"])
        * (p_exh["hp"] / p_exh["tq"])
        * (p_junc["hp"] / p_junc["tq"])
        * (p_ediam["hp"] / p_ediam["tq"])
        * (p_rad["hp"] / p_rad["tq"])
        * 1.01387
    )
    potencia_kw = int(round(potencia_cv * 0.73549875))

    # 3. Validação da velocidade média do pistão / rotor e taxa de compressão (máximo 30.0 m/s)
    if is_wankel:
        velocidade_pistao_mps = (2.0 * (stroke / 1000.0) * (max_rpm / 3.0) * 1.55) / 60.0
    else:
        velocidade_pistao_mps = (2.0 * (stroke / 1000.0) * max_rpm) / 60.0
    limite_vm = min(30.0, 25.0 + p_mat["tol"] + p_val["tol"] + p_pis["tol"] + p_fw["tol"] + p_dmp["tol"] + w_tol)
    limite_cr = perfil_comb["cr_lim"] + p_pis["cr_tol"] + p_rad["cr_tol"]
    motivos_alerta = []
    if velocidade_pistao_mps > limite_vm:
        motivos_alerta.append(f"Vel. média do pistão elevada ({velocidade_pistao_mps:.1f} m/s > {limite_vm:.1f} m/s)")
    if cr > limite_cr:
        motivos_alerta.append(f"Taxa de compressão > {limite_cr:.1f}:1")
    alerta_rpm = len(motivos_alerta) > 0

    adm_desc = f"{admissao_valida} {t_cfg}" if has_multi_turbo else admissao_valida

    return {
        "tipo_motor": f"{formato_valido}{num_cilindros} · {adm_desc} ({ciclo})",
        "cilindrada_litros": f"{cilindrada_litros:.2f} L",
        "pressao_bar": pressao_str,
        "torque_nm": f"{torque_nm} Nm",
        "potencia_kw": f"{potencia_kw} kW",
        "torque_nm_val": torque_nm,
        "potencia_kw_val": potencia_kw,
        "velocidade_pistao_mps": round(velocidade_pistao_mps, 2),
        "limite_vm": round(limite_vm, 1),
        "limite_cr": round(limite_cr, 1),
        "alerta_rpm": alerta_rpm,
        "motivos_alerta": motivos_alerta,
        "damper_ideal_kg": ideal_damper_kg,
    }


def widget_3_modular(
    num_cilindros: int = 4,
    admissao: str = "Atmosférico",
    formato: str = "I",
) -> str:
    """
    Barra inferior de largura total com as Configurações do Motor organizadas em
    3 secções (Bloco & Geometria, Distribuição & Válvulas, Admissão & Combustão).
    """
    formato_clean = str(formato).upper() if str(formato).upper() in FORMATOS_MOTOR else "I"
    num_cilindros = clamp_cilindros_formato(formato_clean, num_cilindros)
    dados_iniciais = processar_combustao(
        num_cilindros=num_cilindros,
        admissao=admissao,
        formato=formato_clean,
    )
    classe_rpm = "input-cyber input-alerta" if dados_iniciais["alerta_rpm"] else "input-cyber"
    texto_alerta = " | ".join(dados_iniciais["motivos_alerta"])

    opcoes_cilindros = FORMAT_CYL_OPTIONS.get(formato_clean, [3, 4, 5, 6])
    unit_cyl_label = "Rotores" if formato_clean == "WANKEL" else "Cilindros"
    options_fmt_html = "\n".join(
        f'<option value="{cod}" {"selected" if cod == formato_clean else ""}>{rotulo}</option>'
        for cod, rotulo in FORMATOS_MOTOR.items()
    )
    options_cyl_html = "\n".join(
        f'<option value="{c}" {"selected" if c == num_cilindros else ""}>{c} {unit_cyl_label}</option>'
        for c in opcoes_cilindros
    )
    options_adm_html = "\n".join(
        f'<option value="{a}" {"selected" if a == admissao else ""}>{a}</option>'
        for a in PERFIS_ADMISSAO.keys()
    )
    has_turbo = admissao in ("Turbo", "Biturbo", "Quad Turbo", "Twincharge")
    has_multi_turbo = admissao in ("Biturbo", "Quad Turbo")
    has_sc = admissao in ("Supercompressor", "Twincharge")
    turbo_init = PERFIS_ADMISSAO.get(admissao, {}).get("turbo_bar", 0.0) if has_turbo else 0.0
    sc_init = PERFIS_ADMISSAO.get(admissao, {}).get("sc_bar", 0.0) if has_sc else 0.0

    return f"""
        <section class="widget-card widget-configs config-bar-inferior" id="widget-3">
            <div class="widget-header config-bar-header">
                <span class="ficha-titulo" id="cfg-page-title">1 · BLOCO &amp; GEOMETRIA</span>
                <div class="config-header-right">
                    <div id="rpm-alerta-msg" class="rpm-alerta-msg">{texto_alerta}</div>
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

            <!-- Página 1: Bloco & Geometria -->
            <div class="config-page ativo" id="cfg-page-0" data-page="0">
                <div class="config-page-grid grid-cols-7">
                    <div class="campo-grupo">
                        <label for="select-formato" id="lbl-formato">FORMATO</label>
                        <select id="select-formato" class="input-cyber">
                            {options_fmt_html}
                        </select>
                    </div>
                    <div class="campo-grupo">
                        <label for="select-cilindros" id="lbl-cilindros">N.º DE CILINDROS</label>
                        <select id="select-cilindros" class="input-cyber">
                            {options_cyl_html}
                        </select>
                    </div>
                    <div class="campo-grupo">
                        <label for="input-bore" id="lbl-bore">DIÂMETRO (mm)</label>
                        <input type="number" id="input-bore" class="input-cyber" value="86.0" step="0.5" min="20" max="200">
                    </div>
                    <div class="campo-grupo">
                        <label for="input-stroke" id="lbl-stroke">CURSO (mm)</label>
                        <input type="number" id="input-stroke" class="input-cyber" value="86.0" step="0.5" min="20" max="200">
                    </div>
                    <div class="campo-grupo">
                        <label for="select-v-angle" id="lbl-v-angle">ÂNGULO EM V</label>
                        <select id="select-v-angle" class="input-cyber" {"disabled" if formato_clean not in ("V", "W") else ""}>
                            <option value="60" selected>60° (Apertado)</option>
                            <option value="90">90° (Aberto)</option>
                        </select>
                    </div>
                    <div class="campo-grupo">
                        <label for="select-material" id="lbl-material">MATERIAL DO MOTOR</label>
                        <select id="select-material" class="input-cyber">
                            <option value="Alumínio" selected>Alumínio</option>
                            <option value="Ferro Fundido">Ferro Fundido</option>
                            <option value="Alumínio Billet">Alumínio Billet</option>
                            <option value="Billet">Billet (Maquinado)</option>
                            <option value="Forged">Forged (Forjado)</option>
                            <option value="Forged Heavy">Forged Heavy</option>
                            <option value="Magnésio">Magnésio</option>
                            <option value="Titanium">Titânio</option>
                            <option value="Titanium Billet">Titânio Billet</option>
                            <option value="Titanium Forged">Titânio Forged</option>
                        </select>
                    </div>
                    <div class="campo-grupo">
                        <label for="select-piston-material" id="lbl-piston-material">MATERIAL DO PISTÃO</label>
                        <select id="select-piston-material" class="input-cyber">
                            <option value="Alumínio" selected>Alumínio</option>
                            <option value="Forged">Forged</option>
                            <option value="Forged Heavy">Forged Heavy</option>
                            <option value="Titânio">Titânio</option>
                        </select>
                    </div>
                </div>
            </div>

            <!-- Página 2: Distribuição, Válvulas, Volante & Damper -->
            <div class="config-page" id="cfg-page-1" data-page="1">
                <div class="config-page-grid grid-cols-7">
                    <div class="campo-grupo">
                        <label for="select-camshaft" id="lbl-camshaft">CAMSHAFT</label>
                        <select id="select-camshaft" class="input-cyber">
                            <option value="DOHC" selected>DOHC (Dupla)</option>
                            <option value="SOHC">SOHC (Simples)</option>
                            <option value="OHV">OHV (Varetas)</option>
                            <option value="Freevalve">Freevalve (Sem Cames)</option>
                        </select>
                    </div>
                    <div class="campo-grupo">
                        <label for="select-valve-type" id="lbl-valve-type">TIPO DE VÁLVULAS</label>
                        <select id="select-valve-type" class="input-cyber">
                            <option value="Molas" selected>Molas Helicoidais</option>
                            <option value="VVT">VVT (Variável)</option>
                            <option value="Desmodrómico">Desmodrómico</option>
                            <option value="Pneumático">Pneumático</option>
                            <option value="Freevalve">Freevalve (Eletropneumático)</option>
                        </select>
                    </div>
                    <div class="campo-grupo">
                        <label for="select-valves" id="lbl-valves">VÁLVULAS / CIL.</label>
                        <select id="select-valves" class="input-cyber">
                            <option value="4" selected>4 Válvulas</option>
                            <option value="2">2 Válvulas</option>
                        </select>
                    </div>
                    <div class="campo-grupo">
                        <label for="select-ciclo" id="lbl-ciclo">CICLO (2T / 4T)</label>
                        <select id="select-ciclo" class="input-cyber">
                            <option value="4T" selected>4T</option>
                            <option value="2T">2T</option>
                        </select>
                    </div>
                    <div class="campo-grupo">
                        <label for="select-flywheel" id="lbl-flywheel">VOLANTE (FLYWHEEL)</label>
                        <select id="select-flywheel" class="input-cyber">
                            <option value="Monomassa Aço" selected>Monomassa (Aço)</option>
                            <option value="Dupla Massa">Dupla Massa (DMF)</option>
                            <option value="Aligeirado Cromoly">Aligeirado (Cromoly)</option>
                            <option value="Alumínio Billet">Alumínio Billet</option>
                            <option value="Carbono Multi-Disco">Carbono Multi-Disco</option>
                        </select>
                    </div>
                    <div class="campo-grupo">
                        <label for="select-damper" id="lbl-damper">HARMONIC DAMPER</label>
                        <select id="select-damper" class="input-cyber">
                            <option value="Elastómero OEM" selected>Elastómero OEM</option>
                            <option value="Fluido Viscoso">Fluido Viscoso (Fluidampr)</option>
                            <option value="ATI Super Damper">ATI Super Damper</option>
                            <option value="Polia Sólida">Polia Sólida (Sem Damper)</option>
                        </select>
                    </div>
                    <div class="campo-grupo">
                        <label for="input-damper-weight" id="lbl-damper-weight">PESO DO DAMPER (kg)</label>
                        <div class="damper-weight-row">
                            <input type="number" id="input-damper-weight" class="input-cyber" value="{dados_iniciais['damper_ideal_kg']:.1f}" step="0.1" min="0.1" max="2000" aria-label="Peso do harmonic damper em kg (máximo 2000 kg)">
                            <button type="button" class="btn-damper-ideal" id="btn-damper-ideal" title="Peso ideal sugerido para este motor (máx. 2000 kg) · Clique para aplicar">Ideal: {dados_iniciais['damper_ideal_kg']:.1f} kg</button>
                        </div>
                    </div>
                </div>
            </div>

            <!-- Página 3: Admissão & Combustão -->
            <div class="config-page" id="cfg-page-2" data-page="2">
                <div class="config-page-grid grid-cols-5-intake">
                    <div class="campo-grupo">
                        <label for="select-admissao" id="lbl-admissao">TIPO DE ADMISSÃO</label>
                        <select id="select-admissao" class="input-cyber">
                            {options_adm_html}
                        </select>
                    </div>
                    <div class="campo-grupo">
                        <label for="select-turbo-config" id="lbl-turbo-config">MULTI-TURBO</label>
                        <select id="select-turbo-config" class="input-cyber" {"" if has_multi_turbo else "disabled"}>
                            <option value="Paralelo" selected>Paralelo</option>
                            <option value="Sequencial">Sequencial</option>
                        </select>
                    </div>
                    <div class="campo-grupo">
                        <label for="select-intake-type" id="lbl-intake-type">TIPO DE INTAKE</label>
                        <select id="select-intake-type" class="input-cyber">
                            <option value="Plenum OEM" selected>Plenum OEM</option>
                            <option value="ITBs">Corpos Individuais (ITBs)</option>
                            <option value="Dual-Plenum">Coletor Dual-Plenum</option>
                            <option value="Velocity Stacks">Velocity Stacks (Trombetas)</option>
                            <option value="Cold Air Intake">Cold Air Intake (CAI)</option>
                        </select>
                    </div>
                    <div class="campo-grupo">
                        <label for="select-intake-material" id="lbl-intake-material">MATERIAL DA INTAKE</label>
                        <select id="select-intake-material" class="input-cyber">
                            <option value="Alumínio Fundido" selected>Alumínio Fundido</option>
                            <option value="Plástico ABS">Plástico ABS / Compósito</option>
                            <option value="Alumínio Billet">Alumínio Billet</option>
                            <option value="Fibra de Carbono">Fibra de Carbono</option>
                            <option value="Magnésio">Magnésio</option>
                            <option value="Titânio">Titânio</option>
                        </select>
                    </div>
                    <div class="campo-grupo">
                        <label for="input-turbo-boost" id="lbl-turbo-boost">PRESSÃO TURBO (bar)</label>
                        <input type="number" id="input-turbo-boost" class="input-cyber" value="{turbo_init:.1f}" step="0.1" min="0.1" max="6.0" {"" if has_turbo else "disabled"}>
                    </div>
                    <div class="campo-grupo">
                        <label for="input-sc-boost" id="lbl-sc-boost">PRESSÃO SUPERCHARGER (bar)</label>
                        <input type="number" id="input-sc-boost" class="input-cyber" value="{sc_init:.1f}" step="0.1" min="0.1" max="4.0" {"" if has_sc else "disabled"}>
                    </div>
                    <div class="campo-grupo">
                        <label for="select-radiator-type" id="lbl-radiator-type">TIPO DE RADIADOR</label>
                        <select id="select-radiator-type" class="input-cyber" {"" if has_turbo else "disabled"}>
                            <option value="OEM Alumínio" selected>Alumínio OEM (Tube &amp; Fin)</option>
                            <option value="Duplo Núcleo">Duplo Núcleo (Bar &amp; Plate)</option>
                            <option value="Triple-Pass Racing">Triple-Pass Racing (Ventoinhas)</option>
                            <option value="Cobre / Latão">Cobre / Latão (Clássico)</option>
                            <option value="Água-Ar (Charge Cooler)">Água-Ar (Charge Cooler)</option>
                        </select>
                    </div>
                    <div class="campo-grupo">
                        <label for="select-combustivel" id="lbl-combustivel">COMBUSTÍVEL</label>
                        <select id="select-combustivel" class="input-cyber">
                            <option value="Gasolina 91">Gasolina 91 RON (Normal)</option>
                            <option value="Gasolina 95" selected>Gasolina 95 RON (91 AKI)</option>
                            <option value="Gasolina 98">Gasolina 98 RON (93 AKI)</option>
                            <option value="Gasolina 102">Gasolina 102 RON (Corrida)</option>
                            <option value="Gasolina 110">Gasolina 110 RON (Avgas/Race)</option>
                            <option value="Etanol (E85)">Etanol E85 (~108 RON)</option>
                            <option value="Metanol">Metanol (~115 RON)</option>
                            <option value="Nitrometano">Nitrometano (Top Fuel)</option>
                            <option value="Diesel">Diesel (Gasóleo)</option>
                            <option value="Biodiesel">Biodiesel</option>
                        </select>
                    </div>
                    <div class="campo-grupo">
                        <label for="input-cr" id="lbl-cr">COMPRESSÃO (:1)</label>
                        <input type="number" id="input-cr" class="input-cyber" value="10.5" step="0.1" min="4" max="25">
                    </div>
                    <div class="campo-grupo">
                        <label for="input-rpm" id="lbl-rpm">ROTAÇÃO MÁX. (RPM)</label>
                        <input type="number" id="input-rpm" class="{classe_rpm}" value="7500" step="100" min="1000" max="25000">
                    </div>
                </div>
            </div>

            <!-- Página 4 (Sempre Última Página): Dados do Motor + Dyno Curves à direita -->
            <div class="config-page" id="cfg-page-3" data-page="3">
                <div class="summary-stats-grid">
                    <div class="summary-pill summary-arch">
                        <span id="lbl-sum-arch">ARQUITETURA</span>
                        <strong id="sum-arch-val">{formato_clean}{num_cilindros} · DOHC · 4V</strong>
                        <small id="sum-arch-sub">4T · Compressão 10.5:1</small>
                    </div>
                    <div class="summary-pill">
                        <span id="lbl-sum-disp">CILINDRADA</span>
                        <strong id="sum-disp-val">2.00 L</strong>
                        <small id="sum-geo-sub">86×86 mm · 7500 RPM</small>
                    </div>
                    <div class="summary-pill dyno-est-power">
                        <span id="lbl-est-power">POTÊNCIA EST.</span>
                        <strong id="dyno-est-power-val">{dados_iniciais["potencia_kw"]}</strong>
                        <small id="dyno-est-power-rpm">@ 7500 RPM</small>
                    </div>
                    <div class="summary-pill dyno-est-torque">
                        <span id="lbl-est-torque">BINÁRIO EST.</span>
                        <strong id="dyno-est-torque-val">{dados_iniciais["torque_nm"]}</strong>
                        <small id="dyno-est-torque-rpm">@ 5200 RPM</small>
                    </div>
                    <div class="summary-pill">
                        <span id="lbl-sum-adm">ADMISSÃO &amp; PRESSÃO</span>
                        <strong id="sum-adm-val">{admissao}</strong>
                        <small id="sum-adm-sub">{dados_iniciais["pressao_bar"]} · Plenum OEM (Alum. Fundido)</small>
                    </div>
                    <div class="summary-pill">
                        <span id="lbl-sum-build">BLOCO &amp; COMBUSTÍVEL</span>
                        <strong id="sum-build-val">Alumínio</strong>
                        <small id="sum-build-sub">Pistão: Alumínio · Gasolina 95 RON · Monomassa · Damper OEM</small>
                    </div>
                </div>
            </div>
        </section>
    """


# ==============================================================================
# MONTAGEM DO PAINEL WEB (HTML + CSS INLINE SIMPLES)
# ==============================================================================
def gerar_dashboard_html(
    num_cilindros: int = 4,
    admissao: str = "Atmosférico",
    formato: str = "I",
) -> str:
    """
    Junta o palco 3D de background, Dyno Curves à direita e a barra inferior
    de Configurações do Motor em 3 secções numa página HTML bilíngue (PT/EN).
    """
    dados_iniciais = processar_combustao(
        num_cilindros=num_cilindros,
        admissao=admissao,
        formato=formato,
    )
    w1 = widget_motor_inline(num_cilindros, formato, admissao)
    w3 = widget_3_modular(num_cilindros, admissao, formato)
    w_dyno = widget_dyno_modular(dados_iniciais["potencia_kw"], dados_iniciais["torque_nm"])
    formato_clean = str(formato).upper() if str(formato).upper() in FORMATOS_MOTOR else "I"
    adm_clean = admissao if admissao in PERFIS_ADMISSAO else "Atmosférico"

    return f"""<!DOCTYPE html>
<html lang="pt">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Custom Engine</title>
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

        /* Linha Superior: Barra pequena de Transmissão & Escape à esquerda + Controlos 3D à direita */
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

        .damper-weight-row {{
            display: flex;
            align-items: stretch;
            gap: 5px;
            width: 100%;
        }}

        .damper-weight-row input[type="number"] {{
            flex: 1 1 54px;
            min-width: 54px;
            width: 0;
        }}

        .btn-damper-ideal {{
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

        .btn-damper-ideal.warn {{
            background: rgba(212, 155, 75, 0.16);
            border-color: rgba(212, 155, 75, 0.55);
            color: #fde68a;
        }}

        .btn-damper-ideal.alert {{
            background: rgba(220, 38, 38, 0.18);
            border-color: rgba(239, 68, 68, 0.62);
            color: #fca5a5;
        }}

        .btn-damper-ideal:hover {{
            background: var(--btn-hover-grad);
            border-color: #ef4444;
            color: #ffffff;
            box-shadow: 0 4px 12px -4px rgba(220, 38, 38, 0.55);
        }}

        .btn-damper-ideal:focus-visible {{
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
                <nav class="dashboard-topbar topbar-subsystems" aria-label="Caixa de Velocidades e Escape">
                    <button type="button" class="btn-3d-ctrl" id="btn-top-engine" style="display:none;" title="Voltar ao modelo 3D do Motor">← Motor</button>
                    <button type="button" class="btn-3d-ctrl" id="btn-top-gearbox" aria-expanded="false" title="Ver modelo separado da Caixa de Velocidades 3D">Caixa de Velocidades</button>
                    <button type="button" class="btn-3d-ctrl" id="btn-top-exhaust" aria-expanded="false" title="Ver percurso dos gases e Escape 3D">Escape</button>
                    <button type="button" class="btn-3d-ctrl" id="btn-top-all" aria-pressed="false" title="Ver Motor, Caixa de Velocidades e Escape juntos em 3D">Ver Tudo Junto</button>
                </nav>

                <div class="subsystem-popover" id="popover-gearbox" role="region" aria-label="Caixa de Velocidades">
                    <div class="subsystem-popover-header">
                        <span class="ficha-titulo" id="gb-panel-title">CAIXA DE VELOCIDADES</span>
                        <button type="button" class="btn-popover-close" id="btn-close-gearbox" aria-label="Fechar">×</button>
                    </div>
                    <div class="grid-2-col">
                        <div class="campo-grupo">
                            <label for="select-gearbox-type" id="lbl-gb-type">TIPO DE CAIXA</label>
                            <select id="select-gearbox-type" class="input-cyber">
                                <option value="Manual" selected>Manual (Sincronizada)</option>
                                <option value="Gated Manual">Manual Gated (Grelha H)</option>
                                <option value="Sequencial">Sequencial (Dog-Box)</option>
                                <option value="DCT">Dupla Embraiagem (DCT)</option>
                                <option value="Automática">Automática (Epicíclica)</option>
                                <option value="E-CVT">E-CVT (Híbrido Planetário)</option>
                            </select>
                        </div>
                        <div class="campo-grupo">
                            <label for="select-gearbox-speeds" id="lbl-gb-speeds">N.º DE MUDANÇAS</label>
                            <select id="select-gearbox-speeds" class="input-cyber">
                                <option value="4">4 Mudanças</option>
                                <option value="5">5 Mudanças</option>
                                <option value="6" selected>6 Mudanças</option>
                                <option value="7">7 Mudanças</option>
                                <option value="8">8 Mudanças</option>
                                <option value="9">9 Mudanças</option>
                            </select>
                        </div>
                        <div class="campo-grupo">
                            <label for="select-clutch-type" id="lbl-clutch-type">TIPO DE EMBRAIAGEM</label>
                            <select id="select-clutch-type" class="input-cyber">
                                <option value="Monodisco Orgânica" selected>Monodisco Orgânica</option>
                                <option value="Cerâmica Racing">Cerâmica (Racing)</option>
                                <option value="Duplo Disco Aço">Duplo Disco Aço</option>
                                <option value="Carbono Multi-Disco">Carbono Multi-Disco</option>
                                <option value="Conversor de Binário">Conversor de Binário</option>
                            </select>
                        </div>
                        <div class="campo-grupo">
                            <label for="select-final-drive" id="lbl-gb-final">RELAÇÃO FINAL</label>
                            <select id="select-final-drive" class="input-cyber">
                                <option value="2.92">2.92:1 (Longa GT)</option>
                                <option value="3.42">3.42:1 (Equilibrada)</option>
                                <option value="3.73" selected>3.73:1 (Desportiva)</option>
                                <option value="4.10">4.10:1 (Curta Track)</option>
                                <option value="4.56">4.56:1 (Drag / Rally)</option>
                            </select>
                        </div>
                    </div>
                    <div class="subsystem-footer-row">
                        <span class="subsystem-readout-pill" id="gearbox-summary-info">Manual · 6V · Monodisco</span>
                        <button type="button" class="btn-3d-ctrl" id="btn-gb-back-engine">Ver Motor</button>
                    </div>
                </div>

                <div class="subsystem-popover" id="popover-exhaust" role="region" aria-label="Sistema de Escape">
                    <div class="subsystem-popover-header">
                        <span class="ficha-titulo" id="exh-panel-title">PERCURSO &amp; ESCAPE</span>
                        <button type="button" class="btn-popover-close" id="btn-close-exhaust" aria-label="Fechar">×</button>
                    </div>
                    <div class="grid-2-col">
                        <div class="campo-grupo">
                            <label for="select-exhaust-type" id="lbl-exh-type">TIPO DE ESCAPE</label>
                            <select id="select-exhaust-type" class="input-cyber">
                                <option value="OEM Catalisador" selected>OEM c/ Catalisador</option>
                                <option value="Sport Cat-Back">Sport Cat-Back</option>
                                <option value="Inconel 4-1">Inconel Competição 4-1</option>
                                <option value="Titânio Valvetronic">Titânio Valvetronic</option>
                                <option value="Straight Pipe">Linha Direta (Straight)</option>
                            </select>
                        </div>
                        <div class="campo-grupo">
                            <label for="select-exhaust-tips" id="lbl-exh-tips">SAÍDA / PONTEIRAS</label>
                            <select id="select-exhaust-tips" class="input-cyber">
                                <option value="Simples">Simples</option>
                                <option value="Dupla" selected>Dupla</option>
                                <option value="Quádrupla">Quádrupla</option>
                            </select>
                        </div>
                        <div class="campo-grupo campo-span-2">
                            <label for="select-exhaust-junction" id="lbl-exh-junction">UNIÃO / JUNÇÃO DO ESCAPE</label>
                            <select id="select-exhaust-junction" class="input-cyber">
                                <option value="X-Pipe" selected>X-Pipe Junction (Cruzado)</option>
                                <option value="H-Pipe">H-Pipe (Tubo Compensador)</option>
                                <option value="Y-Pipe">Y-Pipe (Junção 2-em-1)</option>
                                <option value="Coletor Merge">Coletor Merge (Cone Venturi)</option>
                                <option value="Sem União">Direto / Dual Independente</option>
                            </select>
                        </div>
                        <div class="campo-grupo campo-span-2">
                            <label for="input-exhaust-diameter" id="lbl-exh-diam">DIÂMETRO DO TUBO (mm)</label>
                            <div class="diam-control-row">
                                <input type="range" id="range-exhaust-diameter" min="35" max="140" step="1" value="63" aria-label="Tamanho do tubo de escape em milímetros">
                                <input type="number" id="input-exhaust-diameter" class="input-cyber" min="35" max="140" step="1" value="63">
                            </div>
                        </div>
                    </div>
                    <div class="subsystem-footer-row">
                        <span class="subsystem-readout-pill" id="exhaust-sound-note">Pressão de retorno padrão · 63 mm</span>
                        <button type="button" class="btn-3d-ctrl" id="btn-exh-back-engine">Ver Motor</button>
                    </div>
                </div>
            </div>

            <header class="dashboard-topbar">
                <div class="topbar-right">
                    <span class="widget-badge badge-live" id="motor-3d-badge">{formato_clean}{num_cilindros} · {adm_clean.upper()}</span>
                    <button type="button" class="btn-3d-ctrl ativo" id="btn-3d-cutaway" aria-pressed="true" title="Alternar vista de corte transparente">Vista Corte</button>
                    <button type="button" class="btn-3d-ctrl" id="btn-3d-autorotate" aria-pressed="false" title="Rodar o modelo automaticamente">Auto-Rodar</button>
                    <button type="button" class="btn-3d-ctrl" id="btn-3d-reset" title="Repor ângulo inicial da câmara">Repor Vista</button>
                    <button type="button" class="btn-3d-ctrl btn-lang-toggle" id="btn-lang-toggle" aria-pressed="false" title="Mudar idioma (Português / English)">PT → EN</button>
                </div>
            </header>
        </div>

        <main class="dashboard-container dyno-hidden" id="dashboard-main">
            <!-- Lado Esquerdo: Área aberta para visualizar/mover o motor no background + Botões Ligar/Desligar e Acelerar -->



{w1}
            <!-- Lado Direito: Dyno Curves (visível apenas na última página) -->
            <div class="panels-right-col" id="panels-right-col">
                <!-- Dyno Curves (Potência e Binário) -->



{w_dyno}
    
            </div>
        </main>

        <!-- Barra inferior compacta paginada (1: Bloco, 2: Válvulas, 3: Admissão, 4: Dados + Dyno) -->



{w3}
    
    </div>

    <script>
        const selectFormato = document.getElementById('select-formato');
        const selectCilindros = document.getElementById('select-cilindros');
        const selectAdmissao = document.getElementById('select-admissao');
        const motorNumCilindros = document.getElementById('motor-num-cilindros');
        const motor3dBadge = document.getElementById('motor-3d-badge');
        const motor3dSpec = document.getElementById('motor-3d-spec');

        const inputBore = document.getElementById('input-bore');
        const inputStroke = document.getElementById('input-stroke');
        const inputCr = document.getElementById('input-cr');
        const inputRpm = document.getElementById('input-rpm');
        const selectCombustivel = document.getElementById('select-combustivel');
        const selectCiclo = document.getElementById('select-ciclo');
        const selectVAngle = document.getElementById('select-v-angle');
        const selectMaterial = document.getElementById('select-material');
        const selectPistonMaterial = document.getElementById('select-piston-material');
        const selectCamshaft = document.getElementById('select-camshaft');
        const selectValveType = document.getElementById('select-valve-type');
        const selectValves = document.getElementById('select-valves');
        const selectFlywheel = document.getElementById('select-flywheel');
        const selectDamper = document.getElementById('select-damper');
        const inputDamperWeight = document.getElementById('input-damper-weight');
        const btnDamperIdeal = document.getElementById('btn-damper-ideal');
        const selectTurboConfig = document.getElementById('select-turbo-config');
        const selectIntakeType = document.getElementById('select-intake-type');
        const selectIntakeMaterial = document.getElementById('select-intake-material');
        const selectRadiatorType = document.getElementById('select-radiator-type');
        const btnTopEngine = document.getElementById('btn-top-engine');
        const btnTopGearbox = document.getElementById('btn-top-gearbox');
        const btnTopExhaust = document.getElementById('btn-top-exhaust');
        const btnTopAll = document.getElementById('btn-top-all');
        const popoverGearbox = document.getElementById('popover-gearbox');
        const popoverExhaust = document.getElementById('popover-exhaust');
        const btnCloseGearbox = document.getElementById('btn-close-gearbox');
        const btnCloseExhaust = document.getElementById('btn-close-exhaust');
        const btnGbBackEngine = document.getElementById('btn-gb-back-engine');
        const btnExhBackEngine = document.getElementById('btn-exh-back-engine');
        const selectGearboxType = document.getElementById('select-gearbox-type');
        const selectGearboxSpeeds = document.getElementById('select-gearbox-speeds');
        const selectClutchType = document.getElementById('select-clutch-type');
        const selectFinalDrive = document.getElementById('select-final-drive');
        const gearboxSummaryInfo = document.getElementById('gearbox-summary-info');
        const selectExhaustType = document.getElementById('select-exhaust-type');
        const selectExhaustTips = document.getElementById('select-exhaust-tips');
        const selectExhaustJunction = document.getElementById('select-exhaust-junction');
        const EXHAUST_JUNCTION_FORMATS = ['B', 'VR', 'V', 'W'];
        let savedDualExhaustJunction = 'X-Pipe';
        const FOUR_STROKE_VALVE_TYPES = ['Molas', 'VVT', 'Desmodrómico', 'Pneumático', 'Freevalve'];
        let savedPistonCycle = '4T';
        let saved4tCamshaft = 'DOHC';
        let saved4tValveType = 'Molas';
        let saved4tNumValves = '4';
        const rangeExhaustDiameter = document.getElementById('range-exhaust-diameter');
        const inputExhaustDiameter = document.getElementById('input-exhaust-diameter');
        const exhaustSoundNote = document.getElementById('exhaust-sound-note');
        let viewMode = 'engine';
        let activeTopPopover = null;
        const inputTurboBoost = document.getElementById('input-turbo-boost');
        const inputScBoost = document.getElementById('input-sc-boost');
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
                cutawayOff: 'Bloco Sólido',
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
                telCyl: 'CILINDROS',
                telRotors: 'ROTORES',
                telGeo: 'GEOMETRIA',
                dynoTitle: 'DYNO CURVES',
                estPower: 'POTÊNCIA EST.',
                estTorque: 'BINÁRIO EST.',
                powerWord: 'Potência',
                torqueWord: 'Binário',
                engineOff: 'Motor desligado',
                cursorPrefix: 'Cursor',
                liveBadge: 'TEMPO REAL',
                pageTitles: [
                    '1 · BLOCO & GEOMETRIA',
                    '2 · DISTRIBUIÇÃO & VÁLVULAS',
                    '3 · ADMISSÃO & COMBUSTÃO',
                    '4 · DADOS DO MOTOR & DYNO'
                ],
                pagePrevTitle: 'Página anterior',
                pageNextTitle: 'Próxima página',
                topEngine: '← Motor',
                topEngineTitle: 'Voltar ao modelo 3D do Motor',
                topGearbox: 'Caixa de Velocidades',
                topGearboxTitle: 'Ver modelo separado da Caixa de Velocidades 3D',
                topExhaust: 'Escape',
                topExhaustTitle: 'Ver percurso dos gases e Escape 3D',
                topAll: 'Ver Tudo Junto',
                topAllTitle: 'Ver Motor, Caixa de Velocidades e Escape juntos em 3D',
                viewEngineBtn: 'Ver Motor',
                gbPanelTitle: 'CAIXA DE VELOCIDADES',
                lblGbType: 'TIPO DE CAIXA',
                lblGbSpeeds: 'N.º DE MUDANÇAS',
                lblClutchType: 'TIPO DE EMBRAIAGEM',
                lblGbFinal: 'RELAÇÃO FINAL',
                exhPanelTitle: 'PERCURSO & ESCAPE',
                lblExhType: 'TIPO DE ESCAPE',
                lblExhTips: 'SAÍDA / PONTEIRAS',
                lblExhJunction: 'UNIÃO / JUNÇÃO (B · VR · V · W)',
                exhJuncTitle: 'Disponível para motores Boxer (B), VR, V e W',
                exhSingleBankLabel: 'Bancada única',
                lblExhDiam: 'DIÂMETRO DO TUBO (mm)',
                gbTypeOpts: {{
                    'Manual': 'Manual (Sincronizada)',
                    'Gated Manual': 'Manual Gated (Grelha H)',
                    'Sequencial': 'Sequencial (Dog-Box)',
                    'DCT': 'Dupla Embraiagem (DCT)',
                    'Automática': 'Automática (Epicíclica)',
                    'E-CVT': 'E-CVT (Híbrido Planetário)'
                }},
                gbSteplessLabel: 'Contínua',
                gbSteplessShort: 'Cont.',
                gbSpeedsEcvtTitle: 'E-CVT planetária tem variação contínua (sem mudanças fixas)',
                gbSpeedOpts: {{
                    '4': '4 Mudanças',
                    '5': '5 Mudanças',
                    '6': '6 Mudanças',
                    '7': '7 Mudanças',
                    '8': '8 Mudanças',
                    '9': '9 Mudanças'
                }},
                clutchOpts: {{
                    'Monodisco Orgânica': 'Monodisco Orgânica',
                    'Cerâmica Racing': 'Cerâmica (Racing)',
                    'Duplo Disco Aço': 'Duplo Disco Aço',
                    'Carbono Multi-Disco': 'Carbono Multi-Disco',
                    'Conversor de Binário': 'Conversor de Binário'
                }},
                clutchShort: {{
                    'Monodisco Orgânica': 'Monodisco',
                    'Cerâmica Racing': 'Cerâmica',
                    'Duplo Disco Aço': 'Duplo Disco',
                    'Carbono Multi-Disco': 'Carbono',
                    'Conversor de Binário': 'Conversor'
                }},
                finalDriveOpts: {{
                    '2.92': '2.92:1 (Longa GT)',
                    '3.42': '3.42:1 (Equilibrada)',
                    '3.73': '3.73:1 (Desportiva)',
                    '4.10': '4.10:1 (Curta Track)',
                    '4.56': '4.56:1 (Drag / Rally)'
                }},
                exhTypeOpts: {{
                    'OEM Catalisador': 'OEM c/ Catalisador',
                    'Sport Cat-Back': 'Sport Cat-Back',
                    'Inconel 4-1': 'Inconel Competição 4-1',
                    'Titânio Valvetronic': 'Titânio Valvetronic',
                    'Straight Pipe': 'Linha Direta (Straight)'
                }},
                exhTipsOpts: {{
                    'Simples': 'Simples',
                    'Dupla': 'Dupla',
                    'Quádrupla': 'Quádrupla'
                }},
                exhJunctionOpts: {{
                    'X-Pipe': 'X-Pipe Junction (Cruzado)',
                    'H-Pipe': 'H-Pipe (Tubo Compensador)',
                    'Y-Pipe': 'Y-Pipe (Junção 2-em-1)',
                    'Coletor Merge': 'Coletor Merge (Cone Venturi)',
                    'Sem União': 'Direto / Dual Independente'
                }},
                exhJunctionShort: {{
                    'X-Pipe': 'X-Pipe',
                    'H-Pipe': 'H-Pipe',
                    'Y-Pipe': 'Y-Pipe 2-1',
                    'Coletor Merge': 'Merge Cone',
                    'Sem União': 'Direto'
                }},
                exhFlowNotes: {{
                    'OEM Catalisador': 'Fluxo OEM c/ catalisador',
                    'Sport Cat-Back': '+2.5% fluxo desportivo',
                    'Inconel 4-1': '+4.5% competição Inconel',
                    'Titânio Valvetronic': '+3.8% válvula ativa',
                    'Straight Pipe': '+5.5% fluxo livre + pops'
                }},
                lblSumArch: 'ARQUITETURA',
                lblSumDisp: 'CILINDRADA',
                lblSumAdm: 'ADMISSÃO & PRESSÃO',
                lblSumBuild: 'BLOCO & COMBUSTÍVEL',
                rotaryWord: 'Rotativo',
                compShort: 'Comp.',
                pistonWord: 'Pistão',
                rotorMatWord: 'Rotor',
                lblFormato: 'FORMATO',
                lblCilindros: 'N.º DE CILINDROS',
                lblRotors: 'N.º DE ROTORES',
                lblBore: 'DIÂMETRO (mm)',
                lblStroke: 'CURSO (mm)',
                lblVAngle: 'ÂNGULO EM V',
                lblMaterial: 'MATERIAL DO MOTOR',
                lblPistonMaterial: 'MATERIAL DO PISTÃO',
                lblRotorMaterial: 'MATERIAL DO ROTOR',
                lblCamshaft: 'CAMSHAFT',
                lblValveType: 'TIPO DE VÁLVULAS',
                lblValves: 'VÁLVULAS / CIL.',
                lblCiclo: 'CICLO (2T / 4T)',
                lblFlywheel: 'VOLANTE (FLYWHEEL)',
                lblDamper: 'HARMONIC DAMPER',
                lblDamperWeight: 'PESO DO DAMPER (kg)',
                damperWeightAria: 'Peso do harmonic damper em quilogramas (máximo 2000 kg)',
                damperIdealPrefix: 'Ideal',
                damperIdealTitle: (motorTag, kg, statusTxt) => `Sugestão para ${{motorTag}}: ${{kg}} kg (${{statusTxt}} · máx. 2000 kg) — clique para aplicar`,
                damperStatusOk: 'peso equilibrado',
                damperStatusLight: 'leve demais para este motor',
                damperStatusHeavy: 'acima do ideal',
                lblAdmissao: 'TIPO DE ADMISSÃO',
                lblTurboConfig: 'MULTI-TURBO',
                lblIntakeType: 'TIPO DE INTAKE',
                lblIntakeMaterial: 'MATERIAL DA INTAKE',
                lblRadiatorType: 'TIPO DE RADIADOR',
                lblCombustivel: 'COMBUSTÍVEL',
                lblTurboBoost: 'PRESSÃO TURBO (bar)',
                lblScBoost: 'PRESSÃO SUPERCHARGER (bar)',
                lblCr: 'COMPRESSÃO (:1)',
                lblRpm: 'ROTAÇÃO MÁX. (RPM)',
                cylUnit: 'Cilindros',
                rotorUnit: 'Rotores',
                valvesUnit: 'Válvulas',
                fmtOpts: {{ I: 'I (Em Linha)', V: 'V (Em V)', VR: 'VR (V Estreito)', W: 'W (Em W)', B: 'B (Boxer)', WANKEL: 'Wankel (Rotativo)' }},
                vOpts: {{ '60': '60° (Apertado)', '90': '90° (Aberto)' }},
                matOpts: {{
                    'Alumínio': 'Alumínio',
                    'Ferro Fundido': 'Ferro Fundido',
                    'Alumínio Billet': 'Alumínio Billet',
                    'Billet': 'Billet (Maquinado)',
                    'Forged': 'Forged (Forjado)',
                    'Forged Heavy': 'Forged Heavy',
                    'Magnésio': 'Magnésio',
                    'Titanium': 'Titânio',
                    'Titanium Billet': 'Titânio Billet',
                    'Titanium Forged': 'Titânio Forged'
                }},
                pistonMatOpts: {{
                    'Alumínio': 'Alumínio',
                    'Forged': 'Forged',
                    'Forged Heavy': 'Forged Heavy',
                    'Titânio': 'Titânio'
                }},
                camOpts: {{ 'DOHC': 'DOHC (Dupla)', 'SOHC': 'SOHC (Simples)', 'OHV': 'OHV (Varetas)', 'Freevalve': 'Freevalve (Sem Cames)' }},
                vTypeOpts: {{ 'Molas': 'Molas Helicoidais', 'VVT': 'VVT (Variável)', 'Desmodrómico': 'Desmodrómico', 'Pneumático': 'Pneumático', 'Freevalve': 'Freevalve (Eletropneumático)', 'Reed Valve': 'Reed Valve (Lâminas)' }},
                wankelCycleTitle: 'Motores Wankel operam sempre em ciclo de 4 tempos (4T)',
                reedLockedTitle: 'Motores de 2 tempos utilizam exclusivamente admissão por Reed Valve',
                twoStrokeNoCamTitle: 'Motores 2T com Reed Valve não utilizam árvore de cames nem válvulas de cabeça',
                flywheelOpts: {{
                    'Monomassa Aço': 'Monomassa (Aço)',
                    'Dupla Massa': 'Dupla Massa (DMF)',
                    'Aligeirado Cromoly': 'Aligeirado (Cromoly)',
                    'Alumínio Billet': 'Alumínio Billet',
                    'Carbono Multi-Disco': 'Carbono Multi-Disco'
                }},
                flywheelShort: {{
                    'Monomassa Aço': 'Monomassa',
                    'Dupla Massa': 'DMF',
                    'Aligeirado Cromoly': 'Cromoly',
                    'Alumínio Billet': 'Alum. Billet',
                    'Carbono Multi-Disco': 'Carbono'
                }},
                damperOpts: {{
                    'Elastómero OEM': 'Elastómero OEM',
                    'Fluido Viscoso': 'Fluido Viscoso (Fluidampr)',
                    'ATI Super Damper': 'ATI Super Damper',
                    'Polia Sólida': 'Polia Sólida (Sem Damper)'
                }},
                damperShort: {{
                    'Elastómero OEM': 'Damper OEM',
                    'Fluido Viscoso': 'Fluidampr',
                    'ATI Super Damper': 'ATI Damper',
                    'Polia Sólida': 'Sem Damper'
                }},
                admOpts: {{ 'Atmosférico': 'Atmosférico', 'Turbo': 'Turbo', 'Supercompressor': 'Supercompressor', 'Biturbo': 'Biturbo', 'Quad Turbo': 'Quad Turbo', 'Twincharge': 'Twincharge' }},
                turboCfgOpts: {{ 'Paralelo': 'Paralelo', 'Sequencial': 'Sequencial' }},
                intakeTypeOpts: {{
                    'Plenum OEM': 'Plenum OEM',
                    'ITBs': 'Corpos Individuais (ITBs)',
                    'Dual-Plenum': 'Coletor Dual-Plenum',
                    'Velocity Stacks': 'Velocity Stacks (Trombetas)',
                    'Cold Air Intake': 'Cold Air Intake (CAI)'
                }},
                intakeTypeShort: {{
                    'Plenum OEM': 'Plenum OEM',
                    'ITBs': 'ITBs',
                    'Dual-Plenum': 'Dual-Plenum',
                    'Velocity Stacks': 'Vel. Stacks',
                    'Cold Air Intake': 'CAI'
                }},
                intakeMatOpts: {{
                    'Alumínio Fundido': 'Alumínio Fundido',
                    'Plástico ABS': 'Plástico ABS / Compósito',
                    'Alumínio Billet': 'Alumínio Billet',
                    'Fibra de Carbono': 'Fibra de Carbono',
                    'Magnésio': 'Magnésio',
                    'Titânio': 'Titânio'
                }},
                intakeMatShort: {{
                    'Alumínio Fundido': 'Alum. Fundido',
                    'Plástico ABS': 'Plástico ABS',
                    'Alumínio Billet': 'Billet',
                    'Fibra de Carbono': 'Carbono',
                    'Magnésio': 'Magnésio',
                    'Titânio': 'Titânio'
                }},
                radiatorLockedTitle: 'Disponível quando equipado com radiador/intercooler (Turbo, Biturbo, Quad Turbo ou Twincharge)',
                radiatorOpts: {{
                    'OEM Alumínio': 'Alumínio OEM (Tube & Fin)',
                    'Duplo Núcleo': 'Duplo Núcleo (Bar & Plate)',
                    'Triple-Pass Racing': 'Triple-Pass Racing (Ventoinhas)',
                    'Cobre / Latão': 'Cobre / Latão (Clássico)',
                    'Água-Ar (Charge Cooler)': 'Água-Ar (Charge Cooler)'
                }},
                radiatorShort: {{
                    'OEM Alumínio': 'Rad. OEM',
                    'Duplo Núcleo': 'Duplo Núcleo',
                    'Triple-Pass Racing': 'Triple-Pass',
                    'Cobre / Latão': 'Cobre/Latão',
                    'Água-Ar (Charge Cooler)': 'Água-Ar'
                }},
                fuelOpts: {{
                    'Gasolina 91': 'Gasolina 91 RON (Normal)',
                    'Gasolina 95': 'Gasolina 95 RON (91 AKI)',
                    'Gasolina 98': 'Gasolina 98 RON (93 AKI)',
                    'Gasolina 102': 'Gasolina 102 RON (Corrida)',
                    'Gasolina 110': 'Gasolina 110 RON (Avgas/Race)',
                    'Etanol (E85)': 'Etanol E85 (~108 RON)',
                    'Metanol': 'Metanol (~115 RON)',
                    'Nitrometano': 'Nitrometano (Top Fuel)',
                    'Diesel': 'Diesel (Gasóleo)',
                    'Biodiesel': 'Biodiesel'
                }},
                warnPiston: (v, lim) => `Vel. média do pistão elevada (${{v}} m/s > ${{lim}} m/s)`,
                warnCr: lim => `Taxa de compressão > ${{lim}}:1`
            }},
            en: {{
                cutawayOn: 'Cutaway View',
                cutawayOff: 'Solid Block',
                cutawayTitle: 'Toggle transparent cutaway view',
                autoRotate: 'Auto-Rotate',
                autoRotateTitle: 'Rotate the model automatically',
                resetView: 'Reset View',
                resetViewTitle: 'Reset initial camera angle',
                langBtn: 'EN → PT',
                langBtnTitle: 'Switch language (Português / English)',
                hint: 'Drag background: orbit · Scroll: zoom · Right-click: pan',
                startEngine: 'Start Engine',
                stopEngine: 'Stop Engine',
                throttleLabel: 'THROTTLE',
                throttleTitle: 'Throttle position (0% – 100%) · Drag or hold Spacebar for 100%',
                throttleAria: 'Throttle position percentage',
                slowMo: 'Slow Mo',
                slowMoTitle: 'Toggle slow motion: 1x -> 2x -> 5x -> 10x -> Off',
                unitBtnTitle: 'Switch units between kW / Nm and hp / lb-ft',
                telRpm: 'CURRENT RPM',
                telCyl: 'CYLINDERS',
                telRotors: 'ROTORS',
                telGeo: 'GEOMETRY',
                dynoTitle: 'DYNO CURVES',
                estPower: 'EST. POWER',
                estTorque: 'EST. TORQUE',
                powerWord: 'Power',
                torqueWord: 'Torque',
                engineOff: 'Engine off',
                cursorPrefix: 'Cursor',
                liveBadge: 'REAL TIME',
                pageTitles: [
                    '1 · BLOCK & GEOMETRY',
                    '2 · VALVETRAIN & CYCLE',
                    '3 · INDUCTION & COMBUSTION',
                    '4 · ENGINE DATA & DYNO'
                ],
                pagePrevTitle: 'Previous page',
                pageNextTitle: 'Next page',
                topEngine: '← Engine',
                topEngineTitle: 'Return to 3D Engine model',
                topGearbox: 'Gearbox',
                topGearboxTitle: 'View standalone 3D Gearbox model',
                topExhaust: 'Exhaust',
                topExhaustTitle: 'View standalone Exhaust Gas Path & 3D Exhaust',
                topAll: 'View All Together',
                topAllTitle: 'View Engine, Gearbox and Exhaust assembled together in 3D',
                viewEngineBtn: 'View Engine',
                gbPanelTitle: 'GEARBOX & CLUTCH',
                lblGbType: 'GEARBOX TYPE',
                lblGbSpeeds: 'NUMBER OF GEARS',
                lblClutchType: 'CLUTCH TYPE',
                lblGbFinal: 'FINAL DRIVE',
                exhPanelTitle: 'EXHAUST GAS PATH',
                lblExhType: 'EXHAUST TYPE',
                lblExhTips: 'TIPS / OUTLET',
                lblExhJunction: 'EXHAUST JUNCTION (B · VR · V · W)',
                exhJuncTitle: 'Available only for Boxer (B), VR, V, and W engines',
                exhSingleBankLabel: 'Single bank',
                lblExhDiam: 'PIPE DIAMETER (mm)',
                gbTypeOpts: {{
                    'Manual': 'Manual (Synchromesh)',
                    'Gated Manual': 'Gated Manual (Open-Gate H)',
                    'Sequencial': 'Sequential (Dog-Box)',
                    'DCT': 'Dual-Clutch (DCT)',
                    'Automática': 'Automatic (Planetary)',
                    'E-CVT': 'E-CVT (Planetary Hybrid)'
                }},
                gbSteplessLabel: 'Stepless',
                gbSteplessShort: 'Stepless',
                gbSpeedsEcvtTitle: 'Planetary E-CVT is continuously variable (no fixed gears)',
                gbSpeedOpts: {{
                    '4': '4-Speed',
                    '5': '5-Speed',
                    '6': '6-Speed',
                    '7': '7-Speed',
                    '8': '8-Speed',
                    '9': '9-Speed'
                }},
                clutchOpts: {{
                    'Monodisco Orgânica': 'Single-Disc Organic',
                    'Cerâmica Racing': 'Sintered Ceramic Paddle',
                    'Duplo Disco Aço': 'Twin-Plate Steel',
                    'Carbono Multi-Disco': 'Carbon Multi-Plate',
                    'Conversor de Binário': 'Torque Converter'
                }},
                clutchShort: {{
                    'Monodisco Orgânica': 'Single-Disc',
                    'Cerâmica Racing': 'Ceramic',
                    'Duplo Disco Aço': 'Twin-Plate',
                    'Carbono Multi-Disco': 'Carbon Multi',
                    'Conversor de Binário': 'Torque Conv.'
                }},
                finalDriveOpts: {{
                    '2.92': '2.92:1 (Long GT)',
                    '3.42': '3.42:1 (Balanced)',
                    '3.73': '3.73:1 (Sport)',
                    '4.10': '4.10:1 (Short Track)',
                    '4.56': '4.56:1 (Drag / Rally)'
                }},
                exhTypeOpts: {{
                    'OEM Catalisador': 'OEM Catalytic',
                    'Sport Cat-Back': 'Sport Cat-Back',
                    'Inconel 4-1': 'Inconel 4-1 Race',
                    'Titânio Valvetronic': 'Titanium Valvetronic',
                    'Straight Pipe': 'Straight Pipe (Decat)'
                }},
                exhTipsOpts: {{
                    'Simples': 'Single',
                    'Dupla': 'Dual',
                    'Quádrupla': 'Quad'
                }},
                exhJunctionOpts: {{
                    'X-Pipe': 'X-Pipe Junction (Scavenging)',
                    'H-Pipe': 'H-Pipe (Balance Tube)',
                    'Y-Pipe': 'Y-Pipe (2-into-1 Merge)',
                    'Coletor Merge': 'Merge Collector (Venturi Cone)',
                    'Sem União': 'True Dual (No Crossover)'
                }},
                exhJunctionShort: {{
                    'X-Pipe': 'X-Pipe',
                    'H-Pipe': 'H-Pipe',
                    'Y-Pipe': 'Y-Pipe 2-1',
                    'Coletor Merge': 'Merge Cone',
                    'Sem União': 'No Merge'
                }},
                exhFlowNotes: {{
                    'OEM Catalisador': 'OEM catalytic flow',
                    'Sport Cat-Back': '+2.5% sport high-flow',
                    'Inconel 4-1': '+4.5% Inconel race flow',
                    'Titânio Valvetronic': '+3.8% active valve',
                    'Straight Pipe': '+5.5% open flow + pops'
                }},
                lblSumArch: 'ARCHITECTURE',
                lblSumDisp: 'DISPLACEMENT',
                lblSumAdm: 'INDUCTION & BOOST',
                lblSumBuild: 'MATERIALS & FUEL',
                rotaryWord: 'Rotary',
                compShort: 'CR',
                pistonWord: 'Piston',
                rotorMatWord: 'Rotor',
                lblFormato: 'ENGINE FORMAT',
                lblCilindros: 'CYLINDERS',
                lblRotors: 'ROTORS',
                lblBore: 'BORE (mm)',
                lblStroke: 'STROKE (mm)',
                lblVAngle: 'V-ANGLE',
                lblMaterial: 'BLOCK MATERIAL',
                lblPistonMaterial: 'PISTON MATERIAL',
                lblRotorMaterial: 'ROTOR MATERIAL',
                lblCamshaft: 'CAMSHAFT',
                lblValveType: 'VALVE TYPE',
                lblValves: 'VALVES / CYL.',
                lblCiclo: 'CYCLE (2T / 4T)',
                lblFlywheel: 'FLYWHEEL',
                lblDamper: 'HARMONIC DAMPER',
                lblDamperWeight: 'DAMPER WEIGHT (kg)',
                damperWeightAria: 'Harmonic damper weight in kilograms (max 2000 kg)',
                damperIdealPrefix: 'Ideal',
                damperIdealTitle: (motorTag, kg, statusTxt) => `Suggested for ${{motorTag}}: ${{kg}} kg (${{statusTxt}} · max 2000 kg) — click to apply`,
                damperStatusOk: 'balanced weight',
                damperStatusLight: 'too light for this engine',
                damperStatusHeavy: 'heavier than ideal',
                lblAdmissao: 'INDUCTION',
                lblTurboConfig: 'TURBO LAYOUT',
                lblIntakeType: 'INTAKE TYPE',
                lblIntakeMaterial: 'INTAKE MATERIAL',
                lblRadiatorType: 'RADIATOR TYPE',
                lblCombustivel: 'FUEL',
                lblTurboBoost: 'TURBO BOOST (bar)',
                lblScBoost: 'SUPERCHARGER BOOST (bar)',
                lblCr: 'COMPRESSION (:1)',
                lblRpm: 'MAX RPM',
                cylUnit: 'Cylinders',
                rotorUnit: 'Rotors',
                valvesUnit: 'Valves',
                fmtOpts: {{ I: 'I (Inline)', V: 'V (V-Type)', VR: 'VR (Narrow V)', W: 'W (W-Type)', B: 'B (Boxer Flat)', WANKEL: 'Wankel (Rotary)' }},
                vOpts: {{ '60': '60° (Narrow)', '90': '90° (Wide)' }},
                matOpts: {{
                    'Alumínio': 'Aluminum',
                    'Ferro Fundido': 'Cast Iron',
                    'Alumínio Billet': 'Billet Aluminum',
                    'Billet': 'Billet Steel',
                    'Forged': 'Forged',
                    'Forged Heavy': 'Forged Heavy',
                    'Magnésio': 'Magnesium',
                    'Titanium': 'Titanium',
                    'Titanium Billet': 'Titanium Billet',
                    'Titanium Forged': 'Titanium Forged'
                }},
                pistonMatOpts: {{
                    'Alumínio': 'Aluminum',
                    'Forged': 'Forged',
                    'Forged Heavy': 'Forged Heavy',
                    'Titânio': 'Titanium'
                }},
                camOpts: {{ 'DOHC': 'DOHC (Dual Cam)', 'SOHC': 'SOHC (Single Cam)', 'OHV': 'OHV (Pushrod)', 'Freevalve': 'Freevalve (Camless)' }},
                vTypeOpts: {{ 'Molas': 'Coil Springs', 'VVT': 'VVT (Variable)', 'Desmodrómico': 'Desmodromic', 'Pneumático': 'Pneumatic', 'Freevalve': 'Freevalve (Electro-Pneumatic)', 'Reed Valve': 'Reed Valve' }},
                wankelCycleTitle: 'Wankel rotary engines always operate on a 4-stroke cycle (4T)',
                reedLockedTitle: '2-stroke engines use fixed Reed Valve induction (4-stroke valves removed)',
                twoStrokeNoCamTitle: '2-stroke Reed Valve engines do not use camshafts or poppet valves',
                flywheelOpts: {{
                    'Monomassa Aço': 'Single-Mass (Steel)',
                    'Dupla Massa': 'Dual-Mass (DMF)',
                    'Aligeirado Cromoly': 'Lightweight Chromoly',
                    'Alumínio Billet': 'Billet Aluminum',
                    'Carbono Multi-Disco': 'Carbon Multi-Plate'
                }},
                flywheelShort: {{
                    'Monomassa Aço': 'Single-Mass',
                    'Dupla Massa': 'DMF',
                    'Aligeirado Cromoly': 'Chromoly',
                    'Alumínio Billet': 'Billet Alu',
                    'Carbono Multi-Disco': 'Carbon'
                }},
                damperOpts: {{
                    'Elastómero OEM': 'OEM Elastomer',
                    'Fluido Viscoso': 'Viscous Fluid (Fluidampr)',
                    'ATI Super Damper': 'ATI Super Damper',
                    'Polia Sólida': 'Solid Pulley (Undamped)'
                }},
                damperShort: {{
                    'Elastómero OEM': 'OEM Damper',
                    'Fluido Viscoso': 'Fluidampr',
                    'ATI Super Damper': 'ATI Damper',
                    'Polia Sólida': 'No Damper'
                }},
                admOpts: {{ 'Atmosférico': 'Nat. Aspirated', 'Turbo': 'Turbocharged', 'Supercompressor': 'Supercharged', 'Biturbo': 'Twin-Turbo', 'Quad Turbo': 'Quad-Turbo', 'Twincharge': 'Twincharged' }},
                turboCfgOpts: {{ 'Paralelo': 'Parallel', 'Sequencial': 'Sequential' }},
                intakeTypeOpts: {{
                    'Plenum OEM': 'OEM Plenum',
                    'ITBs': 'Individual Throttle Bodies (ITBs)',
                    'Dual-Plenum': 'Dual-Plenum Resonance (VIS)',
                    'Velocity Stacks': 'Open Velocity Stacks',
                    'Cold Air Intake': 'Cold Air Intake (CAI)'
                }},
                intakeTypeShort: {{
                    'Plenum OEM': 'OEM Plenum',
                    'ITBs': 'ITBs',
                    'Dual-Plenum': 'Dual-Plenum',
                    'Velocity Stacks': 'Vel. Stacks',
                    'Cold Air Intake': 'CAI'
                }},
                intakeMatOpts: {{
                    'Alumínio Fundido': 'Cast Aluminum',
                    'Plástico ABS': 'ABS / Composite Nylon',
                    'Alumínio Billet': 'Billet Aluminum',
                    'Fibra de Carbono': 'Carbon Fiber',
                    'Magnésio': 'Cast Magnesium',
                    'Titânio': 'Titanium'
                }},
                intakeMatShort: {{
                    'Alumínio Fundido': 'Cast Alu.',
                    'Plástico ABS': 'ABS Plastic',
                    'Alumínio Billet': 'Billet Alu.',
                    'Fibra de Carbono': 'Carbon',
                    'Magnésio': 'Magnesium',
                    'Titânio': 'Titanium'
                }},
                radiatorLockedTitle: 'Available when equipped with a front intercooler/radiator (Turbo, Twin-Turbo, Quad-Turbo, or Twincharged)',
                radiatorOpts: {{
                    'OEM Alumínio': 'OEM Aluminum (Tube & Fin)',
                    'Duplo Núcleo': 'Dual-Core Bar & Plate',
                    'Triple-Pass Racing': 'Triple-Pass Racing (Dual Fans)',
                    'Cobre / Latão': 'Copper / Brass (Heavy-Duty)',
                    'Água-Ar (Charge Cooler)': 'Water-to-Air Charge Cooler'
                }},
                radiatorShort: {{
                    'OEM Alumínio': 'OEM Rad.',
                    'Duplo Núcleo': 'Dual-Core',
                    'Triple-Pass Racing': 'Triple-Pass',
                    'Cobre / Latão': 'Copper/Brass',
                    'Água-Ar (Charge Cooler)': 'Water-to-Air'
                }},
                fuelOpts: {{
                    'Gasolina 91': 'Gasoline 91 RON (87 AKI)',
                    'Gasolina 95': 'Gasoline 95 RON (91 AKI)',
                    'Gasolina 98': 'Gasoline 98 RON (93 AKI)',
                    'Gasolina 102': 'Gasoline 102 RON (Race)',
                    'Gasolina 110': 'Gasoline 110 RON (Leaded Race)',
                    'Etanol (E85)': 'Ethanol E85 (~108 RON)',
                    'Metanol': 'Methanol (~115 RON)',
                    'Nitrometano': 'Nitromethane (Top Fuel)',
                    'Diesel': 'Diesel',
                    'Biodiesel': 'Biodiesel'
                }},
                warnPiston: (v, lim) => `High mean piston speed (${{v}} m/s > ${{lim}} m/s)`,
                warnCr: lim => `Compression ratio > ${{lim}}:1`
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
            idleRpm: 950,
            maxRpm: 7500,
            inertiaFactor: 1.0,
            rotInertia: 0.15,
            slowMo: 1,
            unitMode: 'metric',
            dynoPoints: [],
            peakPowerKw: 146,
            peakPowerRpm: 6800,
            peakTorqueNm: 212,
            peakTorqueRpm: 5100,
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
            if (dynoEstTorqueRpm) dynoEstTorqueRpm.textContent = `@ ${{engineSim.peakTorqueRpm}} RPM`;
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
                }} else {{
                    const refRpm = engineSim.hoverRpm !== null ? engineSim.hoverRpm : engineSim.currentRpm;
                    const s = sampleDynoAtRpm(refRpm);
                    dynoLiveReadout.textContent = `${{Math.round(refRpm)}} RPM · ${{formatPowerStr(s.powerKw)}} · ${{formatTorqueStr(s.torqueNm)}}`;
                }}
            }}
            drawDynoChart();
        }}

        const FORMAT_CYL_LIMITS = {{
            'I': [3, 4, 5, 6],
            'VR': [3, 4, 5, 6],
            'V': [4, 6, 8, 10, 12, 16],
            'W': [4, 6, 8, 10, 12, 16],
            'B': [4, 6, 8],
            'WANKEL': [1, 2, 3, 4]
        }};

        const DEFAULT_BOOST_BY_ADM = {{
            'Atmosférico': {{ turbo: 0.0, sc: 0.0 }},
            'Turbo': {{ turbo: 1.5, sc: 0.0 }},
            'Supercompressor': {{ turbo: 0.0, sc: 0.8 }},
            'Biturbo': {{ turbo: 2.0, sc: 0.0 }},
            'Quad Turbo': {{ turbo: 2.5, sc: 0.0 }},
            'Twincharge': {{ turbo: 1.5, sc: 0.8 }}
        }};

        const FORMAT_CYCLE_LIMITS = {{
            'I': ['4T', '2T'],
            'VR': ['4T', '2T'],
            'V': ['4T', '2T'],
            'W': ['4T', '2T'],
            'B': ['4T', '2T'],
            'WANKEL': ['4T']
        }};

        function syncCycleAndValvetrainUI() {{
            const t = I18N[currentLang];
            const fmt = (selectFormato && FORMAT_CYL_LIMITS[selectFormato.value]) ? selectFormato.value : 'I';
            const isWankel = fmt === 'WANKEL';
            const allowedCycles = FORMAT_CYCLE_LIMITS[fmt] || ['4T', '2T'];

            if (selectCiclo) {{
                const curCiclo = selectCiclo.value;
                if (!selectCiclo.disabled && (curCiclo === '4T' || curCiclo === '2T')) {{
                    savedPistonCycle = curCiclo;
                }}
                const targetCiclo = isWankel
                    ? '4T'
                    : (selectCiclo.disabled ? savedPistonCycle : (allowedCycles.includes(curCiclo) ? curCiclo : allowedCycles[0]));
                const curOpts = Array.from(selectCiclo.options).map(o => o.value);
                if (curOpts.length !== allowedCycles.length || allowedCycles.some((c, idx) => curOpts[idx] !== c)) {{
                    selectCiclo.innerHTML = allowedCycles.map(c => `<option value="${{c}}">${{c}}</option>`).join('');
                }}
                selectCiclo.value = allowedCycles.includes(targetCiclo) ? targetCiclo : allowedCycles[0];
                selectCiclo.disabled = isWankel || allowedCycles.length <= 1;
                selectCiclo.title = isWankel ? (t.wankelCycleTitle || '') : '';
                if (!isWankel) savedPistonCycle = selectCiclo.value;
            }}

            const effCiclo = isWankel ? '4T' : (selectCiclo ? (selectCiclo.value || '4T') : '4T');
            const is2T = !isWankel && effCiclo === '2T';
            const has4tOptions = selectValveType
                ? (selectValveType.options.length === FOUR_STROKE_VALVE_TYPES.length && Array.from(selectValveType.options).every((o, i) => o.value === FOUR_STROKE_VALVE_TYPES[i]))
                : false;

            if (!isWankel && !is2T && has4tOptions) {{
                if (selectCamshaft && !selectCamshaft.disabled) saved4tCamshaft = selectCamshaft.value || 'DOHC';
                if (selectValveType && !selectValveType.disabled && FOUR_STROKE_VALVE_TYPES.includes(selectValveType.value)) {{
                    saved4tValveType = selectValveType.value;
                }}
                if (selectValves && !selectValves.disabled) saved4tNumValves = selectValves.value || '4';
            }}

            if (is2T) {{
                if (has4tOptions) {{
                    if (selectCamshaft) saved4tCamshaft = selectCamshaft.value || 'DOHC';
                    if (selectValveType && FOUR_STROKE_VALVE_TYPES.includes(selectValveType.value)) {{
                        saved4tValveType = selectValveType.value;
                    }}
                    if (selectValves) saved4tNumValves = selectValves.value || '4';
                }}
                if (selectValveType) {{
                    const reedLabel = (t.vTypeOpts && t.vTypeOpts['Reed Valve']) ? t.vTypeOpts['Reed Valve'] : 'Reed Valve';
                    selectValveType.innerHTML = `<option value="Reed Valve">${{reedLabel}}</option>`;
                    selectValveType.value = 'Reed Valve';
                    selectValveType.disabled = true;
                    selectValveType.title = t.reedLockedTitle || '';
                }}
                if (selectCamshaft) {{
                    selectCamshaft.disabled = true;
                    selectCamshaft.title = t.twoStrokeNoCamTitle || '';
                }}
                if (selectValves) {{
                    selectValves.disabled = true;
                    selectValves.title = t.twoStrokeNoCamTitle || '';
                }}
            }} else {{
                if (selectValveType) {{
                    if (!has4tOptions) {{
                        selectValveType.innerHTML = FOUR_STROKE_VALVE_TYPES
                            .map(v => `<option value="${{v}}">${{(t.vTypeOpts && t.vTypeOpts[v]) ? t.vTypeOpts[v] : v}}</option>`)
                            .join('');
                        const restoreV = FOUR_STROKE_VALVE_TYPES.includes(saved4tValveType) ? saved4tValveType : 'Molas';
                        selectValveType.value = restoreV;
                    }}
                    selectValveType.disabled = isWankel;
                    selectValveType.title = '';
                }}
                if (selectCamshaft) {{
                    if (!has4tOptions && saved4tCamshaft) selectCamshaft.value = saved4tCamshaft;
                    selectCamshaft.disabled = isWankel;
                    selectCamshaft.title = '';
                }}
                if (selectValves) {{
                    if (!has4tOptions && saved4tNumValves) selectValves.value = saved4tNumValves;
                    selectValves.disabled = isWankel;
                    selectValves.title = '';
                }}
            }}
        }}

        function syncCylinderOptionsForFormat() {{
            if (!selectFormato || !selectCilindros) return;
            const fmt = FORMAT_CYL_LIMITS[selectFormato.value] ? selectFormato.value : 'I';
            const allowed = FORMAT_CYL_LIMITS[fmt];
            const cur = parseInt(selectCilindros.value, 10) || 4;
            let chosen = allowed[0];
            if (allowed.includes(cur)) {{
                chosen = cur;
            }} else {{
                chosen = allowed.reduce((best, cand) => (Math.abs(cand - cur) < Math.abs(best - cur) ? cand : best), allowed[0]);
            }}
            const t = I18N[currentLang];
            const isWankel = fmt === 'WANKEL';
            const unitTxt = isWankel ? t.rotorUnit : t.cylUnit;
            selectCilindros.innerHTML = allowed.map(c => `<option value="${{c}}">${{c}} ${{unitTxt}}</option>`).join('');
            selectCilindros.value = String(chosen);

            const lblCyl = document.getElementById('lbl-cilindros');
            if (lblCyl) lblCyl.textContent = isWankel ? t.lblRotors : t.lblCilindros;
            const lblTelCyl = document.getElementById('lbl-tel-cyl');
            if (lblTelCyl) lblTelCyl.textContent = isWankel ? t.telRotors : t.telCyl;
            const lblPisMat = document.getElementById('lbl-piston-material');
            if (lblPisMat) lblPisMat.textContent = isWankel ? t.lblRotorMaterial : t.lblPistonMaterial;

            if (selectVAngle) selectVAngle.disabled = (fmt !== 'V' && fmt !== 'W');
            syncCycleAndValvetrainUI();
        }}

        function syncBoostControls(resetToDefaults = false) {{
            if (!selectAdmissao) return;
            const adm = selectAdmissao.value || 'Atmosférico';
            const hasTurbo = ['Turbo', 'Biturbo', 'Quad Turbo', 'Twincharge'].includes(adm);
            const hasMultiTurbo = adm === 'Biturbo' || adm === 'Quad Turbo';
            const hasSc = ['Supercompressor', 'Twincharge'].includes(adm);
            const defs = DEFAULT_BOOST_BY_ADM[adm] || DEFAULT_BOOST_BY_ADM['Atmosférico'];
            const t = I18N[currentLang];
            if (selectTurboConfig) {{
                selectTurboConfig.disabled = !hasMultiTurbo;
            }}
            if (selectRadiatorType) {{
                selectRadiatorType.disabled = !hasTurbo;
                selectRadiatorType.title = !hasTurbo ? (t.radiatorLockedTitle || '') : '';
            }}
            if (inputTurboBoost) {{
                inputTurboBoost.disabled = !hasTurbo;
                if (!hasTurbo) {{
                    inputTurboBoost.value = '0.0';
                }} else if (resetToDefaults || parseFloat(inputTurboBoost.value) <= 0) {{
                    inputTurboBoost.value = defs.turbo.toFixed(1);
                }}
            }}
            if (inputScBoost) {{
                inputScBoost.disabled = !hasSc;
                if (!hasSc) {{
                    inputScBoost.value = '0.0';
                }} else if (resetToDefaults || parseFloat(inputScBoost.value) <= 0) {{
                    inputScBoost.value = defs.sc.toFixed(1);
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
            setTxt('lbl-formato', t.lblFormato);
            setTxt('lbl-bore', t.lblBore);
            setTxt('lbl-stroke', t.lblStroke);
            setTxt('lbl-v-angle', t.lblVAngle);
            setTxt('lbl-material', t.lblMaterial);
            setTxt('lbl-camshaft', t.lblCamshaft);
            setTxt('lbl-valve-type', t.lblValveType);
            setTxt('lbl-valves', t.lblValves);
            setTxt('lbl-ciclo', t.lblCiclo);
            setTxt('lbl-flywheel', t.lblFlywheel);
            setTxt('lbl-damper', t.lblDamper);
            setTxt('lbl-damper-weight', t.lblDamperWeight);
            if (inputDamperWeight) inputDamperWeight.setAttribute('aria-label', t.damperWeightAria);
            setTxt('lbl-admissao', t.lblAdmissao);
            setTxt('lbl-turbo-config', t.lblTurboConfig);
            setTxt('lbl-intake-type', t.lblIntakeType);
            setTxt('lbl-intake-material', t.lblIntakeMaterial);
            setTxt('lbl-radiator-type', t.lblRadiatorType);
            setTxt('lbl-combustivel', t.lblCombustivel);
            setTxt('lbl-turbo-boost', t.lblTurboBoost);
            setTxt('lbl-sc-boost', t.lblScBoost);
            setTxt('lbl-cr', t.lblCr);
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
            if (btnSlowMo) {{
                btnSlowMo.title = t.slowMoTitle;
            }}
            if (btnSlowMoLabel) {{
                btnSlowMoLabel.textContent = engineSim.slowMo > 1 ? `${{t.slowMo}} ${{engineSim.slowMo}}x` : t.slowMo;
            }}
            const mapOpts = (sel, dict) => {{
                if (!sel || !dict) return;
                Array.from(sel.options).forEach(opt => {{ if (dict[opt.value]) opt.textContent = dict[opt.value]; }});
            }};
            mapOpts(selectFormato, t.fmtOpts);
            mapOpts(selectVAngle, t.vOpts);
            mapOpts(selectMaterial, t.matOpts);
            mapOpts(selectPistonMaterial, t.pistonMatOpts);
            mapOpts(selectCamshaft, t.camOpts);
            mapOpts(selectValveType, t.vTypeOpts);
            mapOpts(selectFlywheel, t.flywheelOpts);
            mapOpts(selectDamper, t.damperOpts);
            mapOpts(selectAdmissao, t.admOpts);
            mapOpts(selectTurboConfig, t.turboCfgOpts);
            mapOpts(selectIntakeType, t.intakeTypeOpts);
            mapOpts(selectIntakeMaterial, t.intakeMatOpts);
            mapOpts(selectRadiatorType, t.radiatorOpts);
            mapOpts(selectCombustivel, t.fuelOpts);
            mapOpts(selectGearboxType, t.gbTypeOpts);
            mapOpts(selectGearboxSpeeds, t.gbSpeedOpts);
            mapOpts(selectClutchType, t.clutchOpts);
            mapOpts(selectFinalDrive, t.finalDriveOpts);
            mapOpts(selectExhaustType, t.exhTypeOpts);
            mapOpts(selectExhaustTips, t.exhTipsOpts);
            mapOpts(selectExhaustJunction, t.exhJunctionOpts);
            setTxt('gb-panel-title', t.gbPanelTitle);
            setTxt('lbl-gb-type', t.lblGbType);
            setTxt('lbl-gb-speeds', t.lblGbSpeeds);
            setTxt('lbl-clutch-type', t.lblClutchType);
            setTxt('lbl-gb-final', t.lblGbFinal);
            setTxt('exh-panel-title', t.exhPanelTitle);
            setTxt('lbl-exh-type', t.lblExhType);
            setTxt('lbl-exh-tips', t.lblExhTips);
            setTxt('lbl-exh-junction', t.lblExhJunction);
            if (selectExhaustJunction) selectExhaustJunction.title = t.exhJuncTitle;
            setTxt('lbl-exh-diam', t.lblExhDiam);
            setTxt('btn-top-engine', t.topEngine);
            setTxt('btn-top-all', t.topAll);
            setTxt('btn-gb-back-engine', t.viewEngineBtn);
            setTxt('btn-exh-back-engine', t.viewEngineBtn);
            if (btnTopEngine) btnTopEngine.title = t.topEngineTitle;
            if (btnTopGearbox) btnTopGearbox.title = t.topGearboxTitle;
            if (btnTopExhaust) btnTopExhaust.title = t.topExhaustTitle;
            if (btnTopAll) btnTopAll.title = t.topAllTitle;
            syncSubsystemUI();
            syncBoostControls(false);
            syncCylinderOptionsForFormat();
            if (selectValves) {{
                Array.from(selectValves.options).forEach(opt => {{ opt.textContent = `${{opt.value}} ${{t.valvesUnit}}`; }});
            }}

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

        function computeIdealDamperKg(params) {{
            const isWankel = params.formato === 'WANKEL';
            const cyl = Math.max(1, parseInt(params.cilindros, 10) || 4);
            const bore = Math.max(10.0, Number(params.bore) || 86.0);
            const stroke = Math.max(10.0, Number(params.stroke) || 86.0);
            const unitCc = (Math.PI / 4.0) * Math.pow(bore / 10.0, 2) * (stroke / 10.0);
            const litros = (unitCc * (isWankel ? 1.308 : 1.0) * cyl) / 1000.0;
            const baseMass = 1.25 + Math.pow(Math.max(0.3, litros), 0.72) * 1.10;
            let fmtMult = 1.00;
            if (isWankel) fmtMult = 0.42;
            else if (params.formato === 'B') fmtMult = 0.82;
            else if (params.formato === 'VR') fmtMult = 0.94;
            else if (params.formato === 'V') fmtMult = cyl >= 10 ? 1.06 : 0.98;
            else if (params.formato === 'W') fmtMult = 1.22;
            else if (params.formato === 'I') fmtMult = cyl >= 5 ? 1.12 : (cyl === 3 ? 1.04 : 1.00);
            const comb = params.combustivel || 'Gasolina 95';
            const isDiesel = comb === 'Diesel' || comb === 'Biodiesel';
            let fuelMult = 1.00;
            if (isDiesel) fuelMult = 1.38;
            else if (comb === 'Nitrometano') fuelMult = 1.34;
            else if (['Etanol (E85)', 'Metanol', 'Gasolina 102', 'Gasolina 110'].includes(comb)) fuelMult = 1.06;
            const cycleMult = (!isWankel && params.ciclo === '2T') ? 0.90 : 1.00;
            const boostTotal = Math.max(0, Number(params.turbo_bar) || 0) + Math.max(0, Number(params.sc_bar) || 0);
            const boostMult = 1.0 + Math.min(0.45, boostTotal * 0.08);
            const maxR = Math.max(1500, Number(params.max_rpm) || 7500);
            const rpmMult = Math.max(0.75, Math.min(1.16, 1.06 - (maxR - 6500) * 0.000022));
            const pisIdealMap = {{ 'Alumínio': 1.00, 'Forged': 1.06, 'Forged Heavy': 1.15, 'Titânio': 0.88 }};
            const pisMult = isWankel ? 0.92 : (pisIdealMap[params.piston_material] || 1.00);
            const rawIdeal = baseMass * fmtMult * fuelMult * cycleMult * boostMult * rpmMult * pisMult;
            return Math.round(Math.max(0.5, Math.min(2000.0, rawIdeal)) * 10) / 10;
        }}

        function computeDamperWeightStats(params) {{
            const idealKg = computeIdealDamperKg(params);
            const rawW = Number(params.damper_weight);
            const damperW = (Number.isFinite(rawW) && rawW > 0) ? Math.max(0.1, Math.min(2000.0, rawW)) : idealKg;
            const wRatio = damperW / Math.max(0.5, idealKg);
            const wIn = damperW >= idealKg
                ? (1.0 + (damperW - idealKg) * 0.045)
                : Math.max(0.72, 1.0 - (1.0 - wRatio) * 0.25);
            const wHp = wRatio < 0.70
                ? Math.max(0.95, 1.0 - (0.70 - wRatio) * 0.06)
                : (damperW > idealKg * 1.4
                    ? Math.max(0.72, 1.0 - Math.log1p(Math.max(0.0, damperW - idealKg * 1.4)) * 0.030)
                    : 1.00);
            const wTq = damperW > idealKg * 2.0
                ? Math.max(0.84, 1.0 - Math.log1p(Math.max(0.0, damperW - idealKg * 2.0)) * 0.018)
                : 1.00;
            let wTol = 0.0;
            let status = 'ok';
            if (wRatio >= 0.75 && wRatio <= 1.35) {{
                wTol = 0.4;
                status = 'ok';
            }} else if (wRatio < 0.75) {{
                wTol = -Math.min(3.0, (0.75 - wRatio) * 5.0);
                status = wRatio < 0.50 ? 'alert' : 'warn';
            }} else {{
                wTol = damperW > idealKg * 1.8
                    ? -Math.min(3.5, Math.log1p(Math.max(0.0, damperW - idealKg * 1.8)) * 0.55)
                    : 0.0;
                status = wRatio > 2.2 ? 'alert' : 'warn';
            }}
            return {{ idealKg, damperW, wRatio, wIn, wHp, wTq, wTol, status }};
        }}

        function syncDamperSuggestionUI(params) {{
            const p = params || readEnginePayload();
            const stats = computeDamperWeightStats(p);
            engineSim.damperIdealKg = stats.idealKg;
            if (!btnDamperIdeal) return;
            const t = I18N[currentLang];
            const unitCc = (Math.PI / 4.0) * Math.pow(Math.max(10, p.bore) / 10.0, 2) * (Math.max(10, p.stroke) / 10.0);
            const isWankel = p.formato === 'WANKEL';
            const litros = ((unitCc * (isWankel ? 1.308 : 1.0) * p.cilindros) / 1000.0).toFixed(1);
            const motorTag = `${{p.formato}}${{p.cilindros}} · ${{litros}} L · ${{p.combustivel}}`;
            const statusTxt = stats.status === 'ok'
                ? t.damperStatusOk
                : (stats.wRatio < 0.75 ? t.damperStatusLight : t.damperStatusHeavy);
            const idealStr = stats.idealKg.toFixed(1);
            btnDamperIdeal.textContent = `${{t.damperIdealPrefix}}: ${{idealStr}} kg`;
            btnDamperIdeal.title = t.damperIdealTitle(motorTag, idealStr, statusTxt);
            btnDamperIdeal.dataset.idealKg = idealStr;
            btnDamperIdeal.classList.remove('warn', 'alert');
            if (stats.status === 'warn' || stats.status === 'alert') {{
                btnDamperIdeal.classList.add(stats.status);
            }}
        }}

        function computeDynoData(params) {{
            const fatoresComb = {{
                'Gasolina 91': {{ tq: 0.96, hp: 0.95 }},
                'Gasolina 95': {{ tq: 1.00, hp: 1.00 }},
                'Gasolina': {{ tq: 1.00, hp: 1.00 }},
                'Gasolina 98': {{ tq: 1.03, hp: 1.04 }},
                'Gasolina 102': {{ tq: 1.06, hp: 1.08 }},
                'Gasolina 110': {{ tq: 1.09, hp: 1.12 }},
                'Etanol (E85)': {{ tq: 1.10, hp: 1.11 }},
                'Metanol': {{ tq: 1.14, hp: 1.15 }},
                'Nitrometano': {{ tq: 1.45, hp: 1.52 }},
                'Diesel': {{ tq: 1.14, hp: 0.78 }},
                'Biodiesel': {{ tq: 1.10, hp: 0.75 }}
            }};
            const intTypeMap = {{
                'Plenum OEM': {{ tq: 1.000, hp: 1.000, lowEnd: 0.00, topEnd: 0.00 }},
                'ITBs': {{ tq: 0.985, hp: 1.055, lowEnd: -0.05, topEnd: 0.09 }},
                'Dual-Plenum': {{ tq: 1.040, hp: 1.020, lowEnd: 0.06, topEnd: 0.02 }},
                'Velocity Stacks': {{ tq: 0.960, hp: 1.075, lowEnd: -0.08, topEnd: 0.12 }},
                'Cold Air Intake': {{ tq: 1.015, hp: 1.030, lowEnd: 0.02, topEnd: 0.04 }}
            }};
            const intMatMap = {{
                'Alumínio Fundido': {{ tq: 1.000, hp: 1.000 }},
                'Plástico ABS': {{ tq: 1.008, hp: 1.005 }},
                'Alumínio Billet': {{ tq: 1.005, hp: 1.020 }},
                'Fibra de Carbono': {{ tq: 1.020, hp: 1.035 }},
                'Magnésio': {{ tq: 1.010, hp: 1.025 }},
                'Titânio': {{ tq: 1.005, hp: 1.030 }}
            }};
            const admKey = ['Atmosférico', 'Turbo', 'Supercompressor', 'Biturbo', 'Quad Turbo', 'Twincharge'].includes(params.admissao)
                ? params.admissao
                : 'Atmosférico';
            const turboBar = Math.max(0, Math.min(6, Number(params.turbo_bar) || 0));
            const scBar = Math.max(0, Math.min(4, Number(params.sc_bar) || 0));
            const hasMultiTurbo = admKey === 'Biturbo' || admKey === 'Quad Turbo';
            const turboCfg = (hasMultiTurbo && params.turbo_config === 'Sequencial') ? 'Sequencial' : 'Paralelo';
            const tcfgTq = (hasMultiTurbo && turboCfg === 'Sequencial') ? 1.025 : 1.00;
            const tcfgHp = (hasMultiTurbo && turboCfg === 'Sequencial') ? 0.985 : 1.00;
            let admMb = 1.0, admMp = 1.0;
            if (admKey === 'Turbo') {{
                admMb = 1.0 + turboBar * 0.40;
                admMp = 1.0 + turboBar * 0.367;
            }} else if (admKey === 'Supercompressor') {{
                admMb = 1.0 + scBar * 0.5625;
                admMp = 1.0 + scBar * 0.4375;
            }} else if (admKey === 'Biturbo') {{
                admMb = 1.0 + turboBar * 0.425;
                admMp = 1.0 + turboBar * 0.40;
            }} else if (admKey === 'Quad Turbo') {{
                admMb = 1.0 + turboBar * 0.44;
                admMp = 1.0 + turboBar * 0.43;
            }} else if (admKey === 'Twincharge') {{
                const effB = turboBar + scBar * 0.70;
                admMb = 1.0 + effB * 0.46;
                admMp = 1.0 + effB * 0.435;
            }}

            const perfilComb = fatoresComb[params.combustivel] || fatoresComb['Gasolina 95'];
            const pInt = intTypeMap[params.intake_type] || intTypeMap['Plenum OEM'];
            const pIMat = intMatMap[params.intake_material] || intMatMap['Alumínio Fundido'];
            const isDiesel = params.combustivel === 'Diesel' || params.combustivel === 'Biodiesel';
            const isWankel = params.formato === 'WANKEL';
            const effCiclo = isWankel ? '4T' : (params.ciclo === '2T' ? '2T' : '4T');
            const is2T = !isWankel && effCiclo === '2T';
            const effValveType = is2T ? 'Reed Valve' : params.valve_type;
            const isFreevalve = !isWankel && !is2T && (params.camshaft === 'Freevalve' || effValveType === 'Freevalve');

            const unitCc = (Math.PI / 4.0) * Math.pow(params.bore / 10.0, 2) * (params.stroke / 10.0);
            const litros = isWankel
                ? (unitCc * 1.308 * params.cilindros) / 1000.0
                : (unitCc * params.cilindros) / 1000.0;
            const camMap = {{
                'DOHC': {{ tq: 1.00, hp: 1.00 }},
                'SOHC': {{ tq: 1.01, hp: 0.96 }},
                'OHV': {{ tq: 1.04, hp: 0.91 }},
                'Freevalve': {{ tq: 1.06, hp: 1.10 }}
            }};
            const valMap = {{
                'Molas': {{ tq: 1.00, hp: 1.00 }},
                'VVT': {{ tq: 1.03, hp: 1.03 }},
                'Desmodrómico': {{ tq: 1.01, hp: 1.05 }},
                'Pneumático': {{ tq: 1.00, hp: 1.08 }},
                'Freevalve': {{ tq: 1.00, hp: 1.00 }},
                'Reed Valve': {{ tq: 1.00, hp: 1.00 }}
            }};
            const matHpMap = {{
                'Alumínio': 1.00, 'Ferro Fundido': 1.00, 'Alumínio Billet': 1.02,
                'Forged': 1.01, 'Forged Heavy': 0.99, 'Billet': 1.03,
                'Magnésio': 1.01, 'Titanium': 1.02, 'Titanium Billet': 1.04, 'Titanium Forged': 1.03
            }};
            const pisMap = {{
                'Alumínio': {{ tq: 1.00, hp: 1.00 }},
                'Forged': {{ tq: 1.01, hp: 1.02 }},
                'Forged Heavy': {{ tq: 1.03, hp: 0.98 }},
                'Titânio': {{ tq: 1.00, hp: 1.05 }}
            }};
            const fwMap = {{
                'Monomassa Aço': {{ tq: 1.000, hp: 1.000, in: 1.00 }},
                'Dupla Massa': {{ tq: 1.015, hp: 0.985, in: 1.38 }},
                'Aligeirado Cromoly': {{ tq: 1.000, hp: 1.015, in: 0.70 }},
                'Alumínio Billet': {{ tq: 0.995, hp: 1.022, in: 0.58 }},
                'Carbono Multi-Disco': {{ tq: 0.990, hp: 1.032, in: 0.42 }}
            }};
            const dmpMap = {{
                'Elastómero OEM': {{ tq: 1.000, hp: 1.000, in: 1.00 }},
                'Fluido Viscoso': {{ tq: 1.005, hp: 1.010, in: 1.04 }},
                'ATI Super Damper': {{ tq: 1.005, hp: 1.020, in: 0.85 }},
                'Polia Sólida': {{ tq: 1.000, hp: 1.006, in: 0.80 }}
            }};
            const gbMap = {{
                'Manual':     {{ tq: 1.000, hp: 1.000, in: 1.00 }},
                'Gated Manual': {{ tq: 1.005, hp: 1.012, in: 0.90 }},
                'Manual 6V':  {{ tq: 1.000, hp: 1.000, in: 1.00 }},
                'Manual 5V':  {{ tq: 1.005, hp: 1.005, in: 0.98 }},
                'Sequencial': {{ tq: 1.010, hp: 1.025, in: 0.78 }},
                'Sequencial 6V': {{ tq: 1.010, hp: 1.025, in: 0.78 }},
                'DCT':        {{ tq: 0.995, hp: 1.015, in: 0.88 }},
                'DCT 7V':     {{ tq: 0.995, hp: 1.015, in: 0.88 }},
                'Automática': {{ tq: 1.015, hp: 0.975, in: 1.15 }},
                'Automática 8V': {{ tq: 1.015, hp: 0.975, in: 1.15 }},
                'E-CVT':      {{ tq: 1.045, hp: 1.035, in: 0.72 }}
            }};
            const clutchMap = {{
                'Monodisco Orgânica':   {{ tq: 1.000, hp: 1.000, in: 1.00 }},
                'Cerâmica Racing':      {{ tq: 1.012, hp: 1.012, in: 0.84 }},
                'Duplo Disco Aço':      {{ tq: 1.010, hp: 1.018, in: 0.76 }},
                'Carbono Multi-Disco':  {{ tq: 1.000, hp: 1.028, in: 0.56 }},
                'Conversor de Binário': {{ tq: 1.020, hp: 0.978, in: 1.30 }}
            }};
            const exhMap = {{
                'OEM Catalisador':     {{ tq: 1.000, hp: 1.000 }},
                'Sport Cat-Back':      {{ tq: 1.010, hp: 1.025 }},
                'Inconel 4-1':         {{ tq: 1.015, hp: 1.045 }},
                'Titânio Valvetronic': {{ tq: 1.020, hp: 1.038 }},
                'Straight Pipe':       {{ tq: 0.990, hp: 1.055 }}
            }};
            const juncMap = {{
                'Sem União':     {{ tq: 1.000, hp: 1.000 }},
                'X-Pipe':        {{ tq: 1.005, hp: 1.022 }},
                'H-Pipe':        {{ tq: 1.018, hp: 1.005 }},
                'Y-Pipe':        {{ tq: 1.012, hp: 1.010 }},
                'Coletor Merge': {{ tq: 1.008, hp: 1.018 }}
            }};
            const hasRadiator = ['Turbo', 'Biturbo', 'Quad Turbo', 'Twincharge'].includes(admKey);
            const radMap = {{
                'OEM Alumínio':            {{ tq: 1.000, hp: 1.000 }},
                'Duplo Núcleo':            {{ tq: 1.020, hp: 1.030 }},
                'Triple-Pass Racing':      {{ tq: 1.030, hp: 1.055 }},
                'Cobre / Latão':           {{ tq: 1.015, hp: 1.022 }},
                'Água-Ar (Charge Cooler)': {{ tq: 1.040, hp: 1.045 }}
            }};
            const pRad = hasRadiator ? (radMap[params.radiator_type] || radMap['OEM Alumínio']) : {{ tq: 1.000, hp: 1.000 }};
            const pCam = (isWankel || is2T) ? {{ tq: 1.00, hp: 1.00 }} : (isFreevalve ? camMap['Freevalve'] : (camMap[params.camshaft] || camMap['DOHC']));
            const pVal = isWankel ? {{ tq: 1.00, hp: 1.00 }} : (isFreevalve ? valMap['Freevalve'] : (valMap[effValveType] || valMap['Molas']));
            const pMatHp = matHpMap[params.material] || 1.00;
            const pPis = pisMap[params.piston_material] || pisMap['Alumínio'];
            const pFw = fwMap[params.flywheel] || fwMap['Monomassa Aço'];
            const pDmp = dmpMap[params.damper] || dmpMap['Elastómero OEM'];
            const pGb = gbMap[params.gearbox_type] || gbMap['Manual'];
            const gbSpds = Math.max(4, Math.min(9, parseInt(params.gearbox_speeds, 10) || 6));
            const gbSpdHp = params.gearbox_type === 'E-CVT' ? 1.0 : (1.0 + (gbSpds - 6) * 0.004);
            const pCl = clutchMap[params.clutch_type] || clutchMap['Monodisco Orgânica'];
            const pExh = exhMap[params.exhaust_type] || exhMap['OEM Catalisador'];
            const supportsExhJunc = EXHAUST_JUNCTION_FORMATS.includes(params.formato);
            const pJunc = supportsExhJunc ? (juncMap[params.exhaust_junction] || juncMap['X-Pipe']) : juncMap['Sem União'];
            const exhD = Math.max(35, Math.min(140, Number(params.exhaust_diameter) || 63));
            const dDelta = (exhD - 63.0) / 63.0;
            const pEDiam = {{
                tq: Math.max(0.96, Math.min(1.03, 1.0 - 0.024 * dDelta)),
                hp: Math.max(0.92, Math.min(1.06, 1.0 + 0.055 * (1.0 - Math.exp(-dDelta * 1.4))))
            }};
            const dmpStats = computeDamperWeightStats(params);
            engineSim.damperIdealKg = dmpStats.idealKg;
            engineSim.inertiaFactor = pFw.in * pDmp.in * pGb.in * pCl.in * dmpStats.wIn;
            const nVal = parseInt(params.num_valvulas, 10) === 2 ? 2 : 4;
            const valTq = (isWankel || is2T) ? 1.00 : (nVal === 2 ? 1.02 : 1.00);
            const valHp = (isWankel || is2T) ? 1.00 : (nVal === 2 ? 0.93 : 1.00);

            const fatorCr = 1.0 + Math.max(-0.25, Math.min(0.35, (params.compression_ratio - 10.0) * 0.025));
            const fatorCicloTq = isWankel ? 1.42 : (effCiclo === '2T' ? 1.25 : 1.00);
            const peakTorqueNm = Math.round(litros * 105.0 * fatorCr * perfilComb.tq * fatorCicloTq * admMb * tcfgTq * pCam.tq * pVal.tq * valTq * pPis.tq * pFw.tq * pDmp.tq * dmpStats.wTq * pInt.tq * pIMat.tq * pGb.tq * pCl.tq * pExh.tq * pJunc.tq * pEDiam.tq * pRad.tq);
            const fatorRpmHp = isWankel ? 0.93 : (effCiclo === '4T' ? 0.88 : 0.94);
            const peakPowerCv = ((peakTorqueNm * params.max_rpm * fatorRpmHp) / 7121.0) * (admMp / admMb) * (tcfgHp / tcfgTq) * (perfilComb.hp / perfilComb.tq) * (pCam.hp / pCam.tq) * (pVal.hp / pVal.tq) * (valHp / valTq) * pMatHp * (pPis.hp / pPis.tq) * (pFw.hp / pFw.tq) * (pDmp.hp / pDmp.tq) * (dmpStats.wHp / dmpStats.wTq) * (pInt.hp / pInt.tq) * (pIMat.hp / pIMat.tq) * (pGb.hp / pGb.tq) * gbSpdHp * (pCl.hp / pCl.tq) * (pExh.hp / pExh.tq) * (pJunc.hp / pJunc.tq) * (pEDiam.hp / pEDiam.tq) * (pRad.hp / pRad.tq) * 1.01387;
            const peakPowerKw = Math.round(peakPowerCv * 0.73549875);

            const maxRpm = Math.max(1500, params.max_rpm);
            const startRpm = Math.min(1000, Math.round(maxRpm * 0.15));
            const steps = 48;
            const strokeRatio = Math.max(0.75, Math.min(1.25, params.stroke / Math.max(1, params.bore)));
            const lowEndBias = (strokeRatio - 1.0) * 0.14 + (isDiesel ? 0.12 : 0.0) + (!isWankel && !is2T && params.camshaft === 'OHV' ? 0.04 : 0.0) + (!isWankel && !is2T && effValveType === 'VVT' ? 0.05 : 0.0) + (isFreevalve ? 0.06 : 0.0) + (!isWankel && !is2T && nVal === 2 ? 0.04 : 0.0) + pInt.lowEnd;
            const topFallScale = Math.max(0.60, 1.0 - pInt.topEnd * 2.5);

            const raw = [];
            let maxRawT = 1e-6;
            for (let i = 0; i <= steps; i++) {{
                const rpm = startRpm + (maxRpm - startRpm) * (i / steps);
                const u = rpm / maxRpm;
                let tShape = 1.0;

                if (admKey === 'Atmosférico') {{
                    const rise = Math.sin(Math.min(1, u / (isDiesel ? 0.48 : 0.70)) * (Math.PI * 0.5));
                    const drop = Math.max(0, u - (isDiesel ? 0.58 : (isWankel ? 0.78 : 0.72))) * (isDiesel ? 0.76 : (isWankel ? 0.42 : 0.56)) * topFallScale;
                    tShape = (0.70 + lowEndBias) + 0.30 * rise - drop;
                }} else if (admKey === 'Turbo') {{
                    const spoolRpm = Math.min(maxRpm * (isDiesel ? 0.34 : 0.44), (isDiesel ? 2000 : 2700) + turboBar * 240);
                    const spool = smoothstep(spoolRpm * 0.42, spoolRpm * 1.05, rpm);
                    tShape = ((isDiesel ? 0.56 : 0.46) + (isDiesel ? 0.44 : 0.54) * spool) * (1.0 - Math.max(0, u - (isDiesel ? 0.62 : 0.78)) * (isDiesel ? 0.78 : 0.54) * topFallScale);
                }} else if (admKey === 'Biturbo') {{
                    const spoolRpm = Math.min(maxRpm * (isDiesel ? 0.30 : 0.40), (isDiesel ? 1850 : 2500) + turboBar * 180);
                    if (turboCfg === 'Sequencial') {{
                        const s1 = smoothstep(spoolRpm * 0.18, spoolRpm * 0.62, rpm);
                        const s2 = smoothstep(maxRpm * 0.36, maxRpm * 0.62, rpm);
                        tShape = ((isDiesel ? 0.68 : 0.60) + (isDiesel ? 0.24 : 0.30) * s1 + (isDiesel ? 0.08 : 0.10) * s2) * (1.0 - Math.max(0, u - (isDiesel ? 0.68 : 0.80)) * (isDiesel ? 0.68 : 0.48) * topFallScale);
                    }} else {{
                        const spool = smoothstep(spoolRpm * 0.40, spoolRpm * 1.02, rpm);
                        tShape = ((isDiesel ? 0.60 : 0.50) + (isDiesel ? 0.40 : 0.50) * spool) * (1.0 - Math.max(0, u - (isDiesel ? 0.68 : 0.82)) * (isDiesel ? 0.62 : 0.42) * topFallScale);
                    }}
                }} else if (admKey === 'Quad Turbo') {{
                    const spoolRpm = Math.min(maxRpm * (isDiesel ? 0.28 : 0.38), (isDiesel ? 1750 : 2400) + turboBar * 160);
                    if (turboCfg === 'Sequencial') {{
                        const s1 = smoothstep(spoolRpm * 0.16, spoolRpm * 0.56, rpm);
                        const s2 = smoothstep(maxRpm * 0.38, maxRpm * 0.64, rpm);
                        tShape = ((isDiesel ? 0.70 : 0.62) + (isDiesel ? 0.22 : 0.28) * s1 + (isDiesel ? 0.08 : 0.10) * s2) * (1.0 - Math.max(0, u - (isDiesel ? 0.70 : 0.82)) * (isDiesel ? 0.60 : 0.40) * topFallScale);
                    }} else {{
                        const spool = smoothstep(spoolRpm * 0.36, spoolRpm * 0.98, rpm);
                        tShape = ((isDiesel ? 0.62 : 0.52) + (isDiesel ? 0.38 : 0.48) * spool) * (1.0 - Math.max(0, u - (isDiesel ? 0.72 : 0.86)) * (isDiesel ? 0.54 : 0.32) * topFallScale);
                    }}
                }} else if (admKey === 'Supercompressor') {{
                    const rise = Math.sin(Math.min(1, u / 0.62) * (Math.PI * 0.5));
                    tShape = (0.83 + lowEndBias * 0.5) + 0.17 * rise - Math.max(0, u - (isDiesel ? 0.60 : 0.72)) * (isDiesel ? 0.72 : 0.50) * topFallScale;
                }} else {{
                    // Twincharge: compressor em baixa + turbo em alta
                    tShape = 0.86 + 0.14 * smoothstep(0.16, 0.54, u) - Math.max(0, u - (isDiesel ? 0.70 : 0.84)) * (isDiesel ? 0.60 : 0.38) * topFallScale;
                }}

                tShape = Math.max(0.25, tShape);
                if (tShape > maxRawT) maxRawT = tShape;
                raw.push({{ rpm, tShape }});
            }}

            let maxRawP = 1e-6;
            const pts = raw.map(item => {{
                const torqueNm = (item.tShape / maxRawT) * peakTorqueNm;
                const pRaw = torqueNm * item.rpm;
                if (pRaw > maxRawP) maxRawP = pRaw;
                return {{ rpm: item.rpm, torqueNm, pRaw }};
            }});

            let bestP = {{ val: 0, rpm: maxRpm }};
            let bestT = {{ val: 0, rpm: startRpm }};
            const points = pts.map(p => {{
                const powerKw = (p.pRaw / maxRawP) * peakPowerKw;
                if (powerKw >= bestP.val) bestP = {{ val: powerKw, rpm: p.rpm }};
                if (p.torqueNm >= bestT.val) bestT = {{ val: p.torqueNm, rpm: p.rpm }};
                return {{ rpm: p.rpm, torqueNm: p.torqueNm, powerKw }};
            }});

            const pisInMap = {{ 'Alumínio': 1.00, 'Forged': 1.08, 'Forged Heavy': 1.24, 'Titânio': 0.82 }};
            const pisInertia = isWankel ? 0.92 : (pisInMap[params.piston_material] || 1.00);
            engineSim.rotInertia = Math.max(0.055, (0.088 + Math.max(0.4, litros) * 0.032) * pisInertia * Math.max(0.32, Math.min(14.0, engineSim.inertiaFactor || 1.0)));
            engineSim.maxRpm = maxRpm;
            engineSim.idleRpm = Math.min(1150, Math.max(750, Math.round(maxRpm * 0.13)));
            engineSim.dynoPoints = points;
            engineSim.peakPowerKw = peakPowerKw;
            engineSim.peakPowerRpm = Math.round(bestP.rpm);
            engineSim.peakTorqueNm = peakTorqueNm;
            engineSim.peakTorqueRpm = Math.round(bestT.rpm);

            syncUnitDisplays();
            updateRpmRedlineVisual(engineSim.currentRpm);
        }}

        function sampleDynoAtRpm(rpm) {{
            const pts = engineSim.dynoPoints;
            if (!pts.length) return {{ powerKw: 0, torqueNm: 0 }};
            if (rpm <= pts[0].rpm) {{
                const ratio = Math.max(0, rpm / Math.max(1, pts[0].rpm));
                return {{ powerKw: pts[0].powerKw * ratio, torqueNm: pts[0].torqueNm * (0.45 + 0.55 * ratio) }};
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
                padL: compact ? 33 : 40,
                padR: compact ? 33 : 40,
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

            // Grelha do dinamómetro + rótulos das unidades no topo dos eixos
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

            // Eixo X simplificado (×1000 RPM: 1K -> 1, 2K -> 2...)
            let stepRpm = maxRpm > 16000 ? 4000 : (maxRpm > 9000 ? 2000 : 1000);
            if (compact && pw < 215) {{
                stepRpm = maxRpm > 14000 ? 4000 : (maxRpm > 6500 ? 2000 : 1000);
            }}
            const firstTick = Math.max(stepRpm, Math.ceil(minRpm / stepRpm) * stepRpm);
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
                    cilindros: 4,
                    formato: 'I',
                    admissao: 'Atmosférico',
                    bore: 86.0,
                    stroke: 86.0,
                    maxRpm: 7500,
                    ciclo: '4T',
                    combustivel: 'Gasolina 95',
                    vAngle: '60',
                    material: 'Alumínio',
                    pistonMaterial: 'Alumínio',
                    camshaft: 'DOHC',
                    valveType: 'Molas',
                    numValvulas: 4,
                    turboConfig: 'Paralelo',
                    intakeType: 'Plenum OEM',
                    intakeMaterial: 'Alumínio Fundido',
                    flywheel: 'Monomassa Aço',
                    damper: 'Elastómero OEM',
                    damperWeight: 3.2,
                    viewMode: 'engine',
                    gearboxType: 'Manual',
                    gearboxSpeeds: 6,
                    clutchType: 'Monodisco Orgânica',
                    finalDrive: 3.73,
                    exhaustType: 'OEM Catalisador',
                    exhaustTips: 'Dupla',
                    exhaustJunction: 'X-Pipe',
                    exhaustDiameter: 63,
                    radiatorType: 'OEM Alumínio',
                    turboBar: 0.0,
                    scBar: 0.0
                }};

                this.exhaustTips = [];
                this.exhaustGasPaths = [];
                this.gasFlowPhase = 0;

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
                this.dynamicCyls = [];
                this.dynamicWankel = [];
                this.dynamicRotors = [];
                this.dynamicCams = [];
                this.dynamicValves = [];
                this.exhaustTips = [];

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

                        // Microtextura procedimental: maquinagem CNC longitudinal vs fundição granular
                        float latheGrain = sin(vWorldPos.x * 115.0 + vWorldPos.z * 28.0) * 0.5 + 0.5;
                        float castNoise = fract(sin(dot(floor(vWorldPos * 90.0), vec3(12.9898, 78.233, 37.719))) * 43758.5453);
                        float microTex = mix((castNoise - 0.5) * 0.055, (latheGrain - 0.5) * 0.042, step(0.56, uSpec.x));
                        vec3 baseCol = clamp(uColor.rgb * (1.0 + microTex), 0.0, 1.0);

                        // Oclusão espacial sutil no cárter/inferior e cavidades voltadas para baixo
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

                        // Reflexo de estúdio simulado no vetor R (softbox superior + rebote inferior)
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
                    camLobe: this.makeMesh(this.buildCamLobeData(32)),
                    gear: this.makeMesh(this.buildGearData(20, 0.88, 1.04)),
                    torus: this.makeMesh(this.buildTorusData(32, 16, 0.42)),
                    sphere: this.makeMesh(this.buildSphereData(12, 16)),
                    spring: this.makeMesh(this.buildHelixSpringData(4.0, 36, 6)),
                    crankWeb: this.makeMesh(this.buildCrankWebData(36)),
                    impeller: this.makeMesh(this.buildImpellerData(7)),
                    wankelHousing: this.makeMesh(this.buildWankelHousingData(54)),
                    wankelRotor: this.makeMesh(this.buildWankelRotorData(36))
                }};
            }}

            buildCamLobeData(segs) {{
                const pos = [], norm = [], idx = [];
                const radAt = (a) => 0.27 + 0.23 * Math.pow(Math.max(0, -Math.cos(a)), 2.2);
                for (let i = 0; i < segs; i++) {{
                    const a0 = (i / segs) * Math.PI * 2;
                    const a1 = ((i + 1) / segs) * Math.PI * 2;
                    const r0 = radAt(a0), r1 = radAt(a1);
                    const y0 = Math.cos(a0) * r0, z0 = Math.sin(a0) * r0;
                    const y1 = Math.cos(a1) * r1, z1 = Math.sin(a1) * r1;
                    const ny0 = z1 - z0, nz0 = -(y1 - y0);
                    const nl = Math.hypot(ny0, nz0) || 1;
                    const ny = ny0 / nl, nz = nz0 / nl;
                    const l0 = [-0.5, y0, z0], l1 = [-0.5, y1, z1], r1p = [0.5, y1, z1], r0p = [0.5, y0, z0];
                    pos.push(...l0, ...l1, ...r1p, ...l0, ...r1p, ...r0p);
                    for (let k = 0; k < 6; k++) norm.push(0, ny, nz);
                    pos.push(0.5, 0, 0, ...r0p, ...r1p);
                    for (let k = 0; k < 3; k++) norm.push(1, 0, 0);
                    pos.push(-0.5, 0, 0, ...l1, ...l0);
                    for (let k = 0; k < 3; k++) norm.push(-1, 0, 0);
                }}
                for (let i = 0; i < pos.length / 3; i++) idx.push(i);
                return {{ pos, norm, idx }};
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

            buildWankelHousingData(segs) {{
                const pos = [], norm = [], idx = [];
                const R = 1.0, e = 0.16;
                const Ro = 1.19, eo = 0.13;
                const epi = (t, rBase, eAmt) => [
                    rBase * Math.cos(t) + eAmt * Math.cos(3 * t),
                    rBase * Math.sin(t) + eAmt * Math.sin(3 * t)
                ];
                for (let i = 0; i < segs; i++) {{
                    const t0 = (i / segs) * Math.PI * 2;
                    const t1 = ((i + 1) / segs) * Math.PI * 2;
                    const [iy0, iz0] = epi(t0, R, e);
                    const [iy1, iz1] = epi(t1, R, e);
                    const [oy0, oz0] = epi(t0, Ro, eo);
                    const [oy1, oz1] = epi(t1, Ro, eo);

                    const onLen = Math.hypot(oz1 - oz0, oy1 - oy0) || 1;
                    const ony = (oz1 - oz0) / onLen, onz = -(oy1 - oy0) / onLen;
                    const inLen = Math.hypot(iz1 - iz0, iy1 - iy0) || 1;
                    const iny = -(iz1 - iz0) / inLen, inz = (iy1 - iy0) / inLen;

                    // Parede externa epitrocoidal
                    const o0L = [-0.5, oy0, oz0], o1L = [-0.5, oy1, oz1], o1R = [0.5, oy1, oz1], o0R = [0.5, oy0, oz0];
                    pos.push(...o0L, ...o1L, ...o1R, ...o0L, ...o1R, ...o0R);
                    for (let k = 0; k < 6; k++) norm.push(0, ony, onz);

                    // Câmara interna (normal aponta para dentro)
                    const i0L = [-0.5, iy0, iz0], i1L = [-0.5, iy1, iz1], i1R = [0.5, iy1, iz1], i0R = [0.5, iy0, iz0];
                    pos.push(...i0L, ...i1R, ...i1L, ...i0L, ...i0R, ...i1R);
                    for (let k = 0; k < 6; k++) norm.push(0, iny, inz);

                    // Coroa lateral direita (+X)
                    pos.push(...i0R, ...o0R, ...o1R, ...i0R, ...o1R, ...i1R);
                    for (let k = 0; k < 6; k++) norm.push(1, 0, 0);

                    // Coroa lateral esquerda (-X)
                    pos.push(...i0L, ...o1L, ...o0L, ...i0L, ...i1L, ...o1L);
                    for (let k = 0; k < 6; k++) norm.push(-1, 0, 0);
                }}
                for (let i = 0; i < pos.length / 3; i++) idx.push(i);
                return {{ pos, norm, idx }};
            }}

            buildWankelRotorData(segs) {{
                const pos = [], norm = [], idx = [];
                const perSide = Math.max(6, Math.round(segs / 3));
                const pts = [];
                for (let k = 0; k < 3; k++) {{
                    const a0 = (k / 3) * Math.PI * 2;
                    const a1 = ((k + 1) / 3) * Math.PI * 2;
                    const ay0 = Math.cos(a0), az0 = Math.sin(a0);
                    const ay1 = Math.cos(a1), az1 = Math.sin(a1);
                    const midA = (a0 + a1) * 0.5;
                    const outY = Math.cos(midA), outZ = Math.sin(midA);
                    for (let s = 0; s < perSide; s++) {{
                        const u = s / perSide;
                        // Flanco convexo com cavidade central de combustão (bathtub pocket)
                        const bulge = 0.13 * Math.sin(Math.PI * u) - 0.042 * Math.pow(Math.max(0, Math.sin(Math.PI * u)), 6);
                        const py = (1 - u) * ay0 + u * ay1 + outY * bulge;
                        const pz = (1 - u) * az0 + u * az1 + outZ * bulge;
                        pts.push([py, pz]);
                    }}
                }}
                for (let i = 0; i < pts.length; i++) {{
                    const [y0, z0] = pts[i];
                    const [y1, z1] = pts[(i + 1) % pts.length];
                    const nLen = Math.hypot(z1 - z0, y1 - y0) || 1;
                    const ny = (z1 - z0) / nLen, nz = -(y1 - y0) / nLen;
                    const l0 = [-0.5, y0, z0], l1 = [-0.5, y1, z1], r1p = [0.5, y1, z1], r0p = [0.5, y0, z0];
                    pos.push(...l0, ...l1, ...r1p, ...l0, ...r1p, ...r0p);
                    for (let k = 0; k < 6; k++) norm.push(0, ny, nz);
                    pos.push(0.5, 0, 0, ...r0p, ...r1p);
                    for (let k = 0; k < 3; k++) norm.push(1, 0, 0);
                    pos.push(-0.5, 0, 0, ...l1, ...l0);
                    for (let k = 0; k < 3; k++) norm.push(-1, 0, 0);
                }}
                for (let i = 0; i < pos.length / 3; i++) idx.push(i);
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

            buildCrankWebData(segs = 36) {{
                const pos = [], norm = [], idx = [];
                const radAt = (a) => {{
                    const dPin = Math.abs(Math.atan2(Math.sin(a), Math.cos(a)));
                    const dCw  = Math.abs(Math.atan2(Math.sin(a - Math.PI), Math.cos(a - Math.PI)));
                    if (dPin < 0.36) return 1.24 - dPin * 1.15;
                    if (dCw < 1.18) {{
                        const u = dCw / 1.18;
                        return 0.44 + 0.84 * Math.pow(Math.cos(u * Math.PI * 0.5), 0.55);
                    }}
                    return 0.42;
                }};
                for (let i = 0; i < segs; i++) {{
                    const a0 = (i / segs) * Math.PI * 2;
                    const a1 = ((i + 1) / segs) * Math.PI * 2;
                    const r0 = radAt(a0), r1 = radAt(a1);
                    const y0 = Math.cos(a0) * r0, z0 = Math.sin(a0) * r0;
                    const y1 = Math.cos(a1) * r1, z1 = Math.sin(a1) * r1;
                    const nl = Math.hypot(z1 - z0, y1 - y0) || 1;
                    const ny = (z1 - z0) / nl, nz = -(y1 - y0) / nl;
                    const l0 = [-0.5, y0, z0], l1 = [-0.5, y1, z1], r1p = [0.5, y1, z1], r0p = [0.5, y0, z0];
                    pos.push(...l0, ...l1, ...r1p, ...l0, ...r1p, ...r0p);
                    for (let k = 0; k < 6; k++) norm.push(0, ny, nz);
                    pos.push(0.5, 0, 0, ...r0p, ...r1p);
                    for (let k = 0; k < 3; k++) norm.push(1, 0, 0);
                    pos.push(-0.5, 0, 0, ...l1, ...l0);
                    for (let k = 0; k < 3; k++) norm.push(-1, 0, 0);
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

            addCoilPackAndDetails(x, y, z, tiltAngle, isDiesel = false) {{
                const cosA = Math.cos(tiltAngle), sinA = Math.sin(tiltAngle);
                const dBase = y;
                if (isDiesel) {{
                    const C_INJ = [0.76, 0.62, 0.28, 1.0];
                    const C_CAP = [0.22, 0.25, 0.30, 1.0];
                    this.addPart(this.staticOpaque, 'cyl', this.matTRS(x, dBase * cosA, z + dBase * sinA, tiltAngle, 0, 0, 0.044, 0.16, 0.044), C_INJ, [0.75, 58]);
                    const dTop = y + 0.10;
                    this.addPart(this.staticOpaque, 'bevelBox', this.matTRS(x, dTop * cosA, z + dTop * sinA, tiltAngle, 0, 0, 0.095, 0.06, 0.11), C_CAP, [0.45, 34]);
                    // Linha metálica de alta pressão Common Rail para cada injetor
                    const dSide = y + 0.04;
                    this.addPart(this.staticOpaque, 'cyl', this.matTRS(x, dSide * cosA - 0.06 * sinA, z + dSide * sinA + 0.06 * cosA, tiltAngle + 0.6, 0, 0, 0.018, 0.14, 0.018), [0.80, 0.84, 0.88, 1.0], [0.8, 64]);
                }} else {{
                    const C_COIL = [0.68, 0.22, 0.22, 1.0];
                    const C_BOOT = [0.18, 0.20, 0.24, 1.0];
                    this.addPart(this.staticOpaque, 'cyl', this.matTRS(x, dBase * cosA, z + dBase * sinA, tiltAngle, 0, 0, 0.055, 0.13, 0.055), C_BOOT, [0.3, 18]);
                    const dTop = y + 0.08;
                    this.addPart(this.staticOpaque, 'bevelBox', this.matTRS(x, dTop * cosA, z + dTop * sinA, tiltAngle, 0, 0, 0.12, 0.075, 0.14), C_COIL, [0.58, 44]);
                    this.addPart(this.staticOpaque, 'bevelBox', this.matTRS(x, (dTop + 0.045) * cosA, z + (dTop + 0.045) * sinA, tiltAngle, 0, 0, 0.06, 0.025, 0.08), C_BOOT, [0.4, 24]);
                }}
            }}

            addReedValveCage(px, py, pz, orientation = 'z+', scale = 1.0, tiltAngle = 0) {{
                const s = Math.max(0.65, Math.min(1.4, scale));
                const C_FLANGE = [0.76, 0.80, 0.86, 1.0];
                const C_PETAL  = [0.13, 0.15, 0.19, 1.0];
                const C_STOP   = [0.68, 0.72, 0.78, 1.0];
                const C_BOLT   = [0.84, 0.64, 0.24, 1.0];

                if (orientation === 'y+') {{
                    // Admissão vertical superior (Boxer): V-block aponta para baixo no pórtico
                    this.addPart(this.staticOpaque, 'bevelBox', this.matTRS(px, py, pz, 0, 0, 0, 0.145 * s, 0.042 * s, 0.125 * s), C_FLANGE, [0.72, 56]);
                    for (const bx of [-0.055 * s, 0.055 * s]) {{
                        for (const bz of [-0.045 * s, 0.045 * s]) {{
                            this.addPart(this.staticOpaque, 'hex', this.matTRS(px + bx, py + 0.024 * s, pz + bz, 0, 0, 0, 0.015 * s, 0.018 * s, 0.015 * s), C_BOLT, [0.80, 62]);
                        }}
                    }}
                    for (const side of [-1, 1]) {{
                        this.addPart(this.staticOpaque, 'box', this.matTRS(px, py - 0.045 * s, pz + side * 0.022 * s, side * 0.36, 0, 0, 0.105 * s, 0.068 * s, 0.014 * s), C_PETAL, [0.28, 18]);
                        this.addPart(this.staticOpaque, 'box', this.matTRS(px, py - 0.045 * s, pz + side * 0.030 * s, side * 0.36, 0, 0, 0.095 * s, 0.054 * s, 0.008 * s), C_STOP, [0.76, 58]);
                    }}
                }} else if (orientation === 'v') {{
                    // Admissão inclinada pelo ângulo de bancada V / W
                    this.addPart(this.staticOpaque, 'bevelBox', this.matTRS(px, py, pz, tiltAngle, 0, 0, 0.140 * s, 0.042 * s, 0.120 * s), C_FLANGE, [0.72, 56]);
                    this.addPart(this.staticOpaque, 'hex', this.matTRS(px - 0.052 * s, py + 0.018 * s, pz, tiltAngle, 0, 0, 0.015 * s, 0.018 * s, 0.015 * s), C_BOLT, [0.80, 62]);
                    this.addPart(this.staticOpaque, 'hex', this.matTRS(px + 0.052 * s, py + 0.018 * s, pz, tiltAngle, 0, 0, 0.015 * s, 0.018 * s, 0.015 * s), C_BOLT, [0.80, 62]);
                    for (const side of [-1, 1]) {{
                        this.addPart(this.staticOpaque, 'box', this.matTRS(px, py - 0.032 * s, pz + side * 0.020 * s, tiltAngle + side * 0.36, 0, 0, 0.098 * s, 0.060 * s, 0.014 * s), C_PETAL, [0.28, 18]);
                        this.addPart(this.staticOpaque, 'box', this.matTRS(px, py - 0.032 * s, pz + side * 0.028 * s, tiltAngle + side * 0.36, 0, 0, 0.088 * s, 0.048 * s, 0.008 * s), C_STOP, [0.76, 58]);
                    }}
                }} else {{
                    // Admissão lateral (+Z em I / VR): flange vertical + bloco de lâminas em V
                    this.addPart(this.staticOpaque, 'bevelBox', this.matTRS(px, py, pz, 0, 0, 0, 0.155 * s, 0.130 * s, 0.044 * s), C_FLANGE, [0.72, 56]);
                    for (const bx of [-0.058 * s, 0.058 * s]) {{
                        for (const by of [-0.046 * s, 0.046 * s]) {{
                            this.addPart(this.staticOpaque, 'hex', this.matTRS(px + bx, py + by, pz + 0.025 * s, Math.PI * 0.5, 0, 0, 0.015 * s, 0.018 * s, 0.015 * s), C_BOLT, [0.80, 62]);
                        }}
                    }}
                    for (const side of [-1, 1]) {{
                        this.addPart(this.staticOpaque, 'box', this.matTRS(px, py + side * 0.024 * s, pz + 0.050 * s, -side * 0.38, 0, 0, 0.112 * s, 0.014 * s, 0.072 * s), C_PETAL, [0.28, 18]);
                        this.addPart(this.staticOpaque, 'box', this.matTRS(px, py + side * 0.032 * s, pz + 0.050 * s, -side * 0.38, 0, 0, 0.100 * s, 0.008 * s, 0.058 * s), C_STOP, [0.76, 58]);
                    }}
                }}
            }}

            addStarterMotor(x, y, z) {{
                const C_BODY = [0.24, 0.27, 0.33, 1.0];
                const C_CAP  = [0.54, 0.58, 0.64, 1.0];
                this.addPart(this.staticOpaque, 'cyl', this.matTRS(x, y, z, 0, 0, Math.PI * 0.5, 0.15, 0.44, 0.15), C_BODY, [0.5, 38]);
                this.addPart(this.staticOpaque, 'cyl', this.matTRS(x - 0.04, y + 0.16, z, 0, 0, Math.PI * 0.5, 0.085, 0.28, 0.085), C_CAP, [0.6, 48]);
                this.addPart(this.staticOpaque, 'cyl', this.matTRS(x + 0.24, y, z, 0, 0, Math.PI * 0.5, 0.11, 0.08, 0.11), C_CAP, [0.65, 52]);
            }}

            addThrottleBody(x, y, z) {{
                const C_TB = [0.68, 0.72, 0.78, 1.0];
                const C_TPS = [0.16, 0.18, 0.22, 1.0];
                this.addPart(this.staticOpaque, 'cyl', this.matTRS(x, y, z, 0, 0, Math.PI * 0.5, 0.15, 0.14, 0.15), C_TB, [0.72, 60]);
                this.addPart(this.staticOpaque, 'box', this.matTRS(x, y + 0.13, z + 0.08, 0, 0, 0, 0.09, 0.09, 0.07), C_TPS, [0.35, 22]);
                this.addPart(this.staticOpaque, 'cyl', this.matTRS(x, y, z - 0.16, Math.PI * 0.5, 0, 0, 0.045, 0.07, 0.045), [0.76, 0.62, 0.28, 1.0], [0.7, 56]);
            }}

            addTurboUnit(cx, cy, cz, scale, flipZ = 1, stage = 'all') {{
                const s = scale;
                const C_COMP = [0.78, 0.82, 0.87, 1.0];
                const C_TURB = [0.50, 0.36, 0.28, 1.0];
                const C_CART = [0.34, 0.38, 0.44, 1.0];
                const C_HUB  = stage === 'primary'
                    ? [0.80, 0.58, 0.22, 1.0]
                    : (stage === 'secondary' ? [0.74, 0.24, 0.26, 1.0] : [0.24, 0.41, 0.60, 1.0]);
                const C_BLADE = [0.90, 0.93, 0.96, 1.0];
                const C_WASTE = stage === 'primary' ? [0.80, 0.62, 0.26, 1.0] : [0.58, 0.62, 0.68, 1.0];

                // Center bearing housing (CHRA) + linha AN malha de aço + V-bands
                this.addPart(this.staticOpaque, 'cyl', this.matTRS(cx, cy, cz, 0, 0, Math.PI * 0.5, 0.14 * s, 0.32 * s, 0.14 * s), C_CART, [0.55, 40]);
                this.addPart(this.staticOpaque, 'hex', this.matTRS(cx, cy + 0.16 * s, cz, 0, 0, 0, 0.044 * s, 0.10 * s, 0.044 * s), [0.20, 0.46, 0.78, 1.0], [0.74, 58]);
                this.addPipe(this.staticOpaque, [[cx, cy + 0.21 * s, cz], [cx, cy + 0.30 * s, cz + 0.18 * s * flipZ], [cx, cy + 0.12 * s, cz + 0.34 * s * flipZ]], 0.015 * s, C_COMP, [0.80, 64]);
                this.addPart(this.staticOpaque, 'cyl', this.matTRS(cx, cy - 0.16 * s, cz, 0, 0, 0, 0.042 * s, 0.12 * s, 0.042 * s), C_CART, [0.5, 36]);
                this.addPart(this.staticOpaque, 'cyl', this.matTRS(cx - 0.09 * s, cy, cz, 0, 0, Math.PI * 0.5, 0.21 * s, 0.03 * s, 0.21 * s), stage === 'primary' ? C_WASTE : C_COMP, [0.78, 64]);
                this.addPart(this.staticOpaque, 'cyl', this.matTRS(cx + 0.09 * s, cy, cz, 0, 0, Math.PI * 0.5, 0.19 * s, 0.03 * s, 0.19 * s), C_WASTE, [0.68, 54]);
                // Compressor snail + intake bellmouth + blow-off valve (BOV)
                this.addPart(this.staticOpaque, 'torus', this.matTRS(cx - 0.17 * s, cy, cz, 0, Math.PI * 0.5, 0, 0.25 * s, 0.25 * s, 0.25 * s), C_COMP, [0.78, 68]);
                this.addPart(this.staticOpaque, 'cyl', this.matTRS(cx - 0.25 * s, cy, cz, 0, 0, Math.PI * 0.5, 0.19 * s, 0.15 * s, 0.19 * s), C_COMP, [0.72, 60]);
                this.addPart(this.staticOpaque, 'cone', this.matTRS(cx - 0.34 * s, cy, cz, 0, 0, Math.PI * 0.5, 0.22 * s, 0.09 * s, 0.22 * s), C_COMP, [0.78, 66]);
                this.addPart(this.staticOpaque, 'cyl', this.matTRS(cx - 0.17 * s, cy + 0.26 * s, cz - 0.14 * s * flipZ, 0, 0, 0, 0.065 * s, 0.14 * s, 0.065 * s), [0.72, 0.24, 0.24, 1.0], [0.68, 54]);
                // Turbine snail + heat-tinted downpipe + lambda O2 sensor
                this.addPart(this.staticOpaque, 'torus', this.matTRS(cx + 0.17 * s, cy, cz, 0, Math.PI * 0.5, 0, 0.22 * s, 0.22 * s, 0.22 * s), C_TURB, [0.40, 28]);
                this.addPart(this.staticOpaque, 'cyl', this.matTRS(cx + 0.26 * s, cy, cz, 0, 0, Math.PI * 0.5, 0.15 * s, 0.16 * s, 0.15 * s), C_TURB, [0.35, 24]);
                this.addPipe(this.staticOpaque, [[cx + 0.33 * s, cy, cz], [cx + 0.62 * s, cy - 0.08 * s, cz], [cx + 0.78 * s, cy - 0.36 * s, cz]], 0.115 * s, C_TURB, [0.44, 34]);
                this.addPart(this.staticOpaque, 'cyl', this.matTRS(cx + 0.55 * s, cy + 0.05 * s, cz, -0.35, 0, -0.35, 0.028 * s, 0.14 * s, 0.028 * s), C_WASTE, [0.7, 56]);
                // Wastegate actuator canister + rod
                this.addPart(this.staticOpaque, 'cyl', this.matTRS(cx - 0.04 * s, cy + 0.26 * s, cz + 0.16 * s * flipZ, 0, 0, Math.PI * 0.5, 0.08 * s, 0.16 * s, 0.08 * s), C_WASTE, [0.6, 48]);
                this.addPart(this.staticOpaque, 'cyl', this.matTRS(cx + 0.10 * s, cy + 0.21 * s, cz + 0.10 * s * flipZ, 0.3, 0, Math.PI * 0.5, 0.018 * s, 0.24 * s, 0.018 * s), C_COMP, [0.7, 56]);

                this.dynamicRotors.push({{
                    type: 'impeller',
                    stage: stage || 'all',
                    symmetry: 7,
                    cx: cx - 0.35 * s, cy, cz,
                    r: 0.148 * s,
                    speedMult: 2.2,
                    colorHub: C_HUB,
                    colorBlade: C_BLADE
                }});

                return {{
                    inlet: [cx - 0.36 * s, cy, cz],
                    compOut: [cx - 0.17 * s, cy + 0.25 * s, cz],
                    turbOut: [cx + 0.34 * s, cy, cz],
                    downpipeOut: [cx + 0.78 * s, cy - 0.36 * s, cz],
                    chra: [cx, cy, cz]
                }};
            }}

            samplePolyline(pts, u) {{
                if (!pts || pts.length === 0) return [0, 0, 0];
                if (pts.length === 1) return pts[0];
                const t = Math.max(0, Math.min(1, u)) * (pts.length - 1);
                const idx = Math.min(pts.length - 2, Math.floor(t));
                const f = t - idx;
                const a = pts[idx], b = pts[idx + 1];
                return [a[0] + (b[0] - a[0]) * f, a[1] + (b[1] - a[1]) * f, a[2] + (b[2] - a[2]) * f];
            }}

            addGearboxModel(xFront, bellR = 0.68) {{
                const gbType = this.config.gearboxType || 'Manual';
                const speeds = Math.max(4, Math.min(9, parseInt(this.config.gearboxSpeeds, 10) || 6));
                const clutchType = this.config.clutchType || 'Monodisco Orgânica';
                const finalDrive = Number(this.config.finalDrive) || 3.73;

                const styles = {{
                    'Manual':       {{ caseCol: [0.50, 0.54, 0.60, 1.0], ribCol: [0.36, 0.40, 0.47, 1.0], turretCol: [0.24, 0.27, 0.33, 1.0], spec: [0.48, 38] }},
                    'Gated Manual': {{ caseCol: [0.56, 0.60, 0.68, 1.0], ribCol: [0.80, 0.64, 0.24, 1.0], turretCol: [0.76, 0.80, 0.86, 1.0], spec: [0.74, 58] }},
                    'Sequencial':   {{ caseCol: [0.24, 0.27, 0.33, 1.0], ribCol: [0.76, 0.22, 0.22, 1.0], turretCol: [0.78, 0.60, 0.24, 1.0], spec: [0.68, 56] }},
                    'DCT':          {{ caseCol: [0.40, 0.45, 0.52, 1.0], ribCol: [0.72, 0.58, 0.26, 1.0], turretCol: [0.18, 0.22, 0.28, 1.0], spec: [0.58, 46] }},
                    'Automática':   {{ caseCol: [0.34, 0.37, 0.43, 1.0], ribCol: [0.48, 0.52, 0.58, 1.0], turretCol: [0.16, 0.18, 0.22, 1.0], spec: [0.46, 36] }},
                    'E-CVT':        {{ caseCol: [0.68, 0.75, 0.84, 1.0], ribCol: [0.90, 0.44, 0.12, 1.0], turretCol: [0.16, 0.56, 0.78, 1.0], spec: [0.76, 62] }}
                }};
                const st = styles[gbType] || styles['Manual'];
                const isEcvt = gbType === 'E-CVT';

                const extraLen = isEcvt ? 0.16 : (speeds - 6) * 0.14;
                const caseLen = 1.24 + extraLen;
                const xBell = xFront + 0.34;
                const xCase = xFront + 0.72 + caseLen * 0.5;
                const xTail = xCase + caseLen * 0.5 + 0.22;

                // Cloche da embraiagem translúcida + flange de aperto + atuador hidráulico
                this.addPart(this.staticTrans, 'cone', this.matTRS(xBell, 0, 0, 0, 0, -Math.PI * 0.5, bellR, 0.62, bellR), st.caseCol, st.spec);
                this.addPart(this.staticOpaque, 'cyl', this.matTRS(xFront + 0.04, 0, 0, 0, 0, Math.PI * 0.5, bellR * 1.03, 0.045, bellR * 1.03), st.ribCol, [0.64, 50]);
                for (let b = 0; b < 8; b++) {{
                    const ba = (b * Math.PI * 2) / 8;
                    this.addPart(this.staticOpaque, 'hex', this.matTRS(xFront + 0.01, Math.cos(ba) * (bellR * 0.91), Math.sin(ba) * (bellR * 0.91), ba, 0, Math.PI * 0.5, 0.032, 0.04, 0.032), [0.82, 0.86, 0.92, 1.0], [0.8, 62]);
                }}
                const slaveZ = bellR * 0.76;
                this.addPart(this.staticOpaque, 'cyl', this.matTRS(xBell + 0.12, -0.14, slaveZ, 0, 0, Math.PI * 0.5, 0.055, 0.26, 0.055), [0.72, 0.76, 0.82, 1.0], [0.7, 56]);
                this.addPipe(this.staticOpaque, [[xBell + 0.12, -0.06, bellR * 0.80], [xBell + 0.12, 0.22, bellR * 0.85], [xBell + 0.38, 0.30, bellR * 0.62]], 0.018, [0.78, 0.60, 0.24, 1.0], [0.78, 62]);

                // Embraiagem rotativa exposta consoante o Tipo de Embraiagem selecionado
                this.dynamicRotors.push({{
                    type: 'clutchAssembly',
                    clutchStyle: clutchType,
                    symmetry: 6,
                    cx: xFront + 0.24, cy: 0, cz: 0,
                    r: Math.min(0.48, bellR * 0.72), thick: 0.14,
                    speedMult: 1.0
                }});

                // Carcaça principal da caixa (cutaway) + nervuras estruturais + cárter inferior
                this.addPart(this.staticTrans, 'bevelBox', this.matTRS(xCase, -0.12, 0, 0, 0, 0, caseLen, 0.78, 0.72), st.caseCol, st.spec);
                const ribCount = isEcvt ? 6 : Math.max(4, speeds - 1);
                for (let rk = 0; rk < ribCount; rk++) {{
                    const rx = xCase - caseLen * 0.40 + (rk / (ribCount - 1)) * (caseLen * 0.80);
                    this.addPart(this.staticOpaque, 'box', this.matTRS(rx, -0.52, 0, 0, 0, 0, 0.036, 0.05, 0.70), st.ribCol, [0.55, 42]);
                }}
                this.addPart(this.staticOpaque, 'hex', this.matTRS(xCase + 0.14, -0.55, 0, 0, 0, 0, 0.038, 0.04, 0.038), [0.84, 0.64, 0.24, 1.0], [0.78, 60]);

                if (gbType === 'E-CVT') {{
                    // Inversor de potência (PCU) superior + cabos laranja High-Voltage para MG1/MG2
                    const C_HV = [0.92, 0.40, 0.08, 1.0];
                    this.addPart(this.staticOpaque, 'bevelBox', this.matTRS(xCase, 0.34, 0, 0, 0, 0, caseLen * 0.68, 0.14, 0.52), [0.72, 0.78, 0.86, 1.0], [0.78, 64]);
                    this.addPart(this.staticOpaque, 'bevelBox', this.matTRS(xCase, 0.42, 0, 0, 0, 0, caseLen * 0.56, 0.04, 0.38), st.turretCol, [0.68, 54]);
                    this.addPipe(this.staticOpaque, [[xCase - 0.28, 0.34, 0.28], [xCase - 0.28, 0.18, 0.39], [xCase - 0.36, 0.04, 0.32]], 0.028, C_HV, [0.38, 28]);
                    this.addPipe(this.staticOpaque, [[xCase + 0.28, 0.34, 0.28], [xCase + 0.28, 0.18, 0.39], [xCase + 0.36, 0.04, 0.32]], 0.028, C_HV, [0.38, 28]);
                }} else if (gbType === 'Automática') {{
                    this.addPart(this.staticOpaque, 'bevelBox', this.matTRS(xCase, -0.54, 0, 0, 0, 0, caseLen * 0.92, 0.11, 0.64), st.turretCol, [0.35, 22]);
                    this.addPipe(this.staticOpaque, [[xCase - 0.34, -0.26, 0.38], [xCase - 0.34, -0.02, 0.45], [xCase + 0.34, -0.02, 0.45], [xCase + 0.34, -0.26, 0.38]], 0.022, [0.80, 0.62, 0.24, 1.0], [0.78, 60]);
                    this.addPart(this.staticOpaque, 'cyl', this.matTRS(xCase + 0.20, 0.30, 0, 0, 0, 0, 0.12, 0.10, 0.12), [0.22, 0.25, 0.30, 1.0], [0.55, 40]);
                }} else if (gbType === 'Sequencial') {{
                    this.addPart(this.staticOpaque, 'bevelBox', this.matTRS(xCase, 0.32, 0, 0, 0, 0, caseLen * 0.72, 0.14, 0.32), [0.74, 0.22, 0.22, 1.0], [0.68, 54]);
                    this.addPart(this.staticOpaque, 'cyl', this.matTRS(xCase, 0.44, 0, 0, 0, Math.PI * 0.5, 0.075, caseLen * 0.58, 0.075), st.turretCol, [0.78, 62]);
                    this.addPipe(this.staticOpaque, [[xCase - 0.32, 0.44, 0.18], [xCase + 0.35, 0.44, 0.18]], 0.024, [0.84, 0.88, 0.92, 1.0], [0.82, 66]);
                }} else if (gbType === 'DCT') {{
                    this.addPart(this.staticOpaque, 'bevelBox', this.matTRS(xCase, 0.31, 0, 0, 0, 0, caseLen * 0.68, 0.12, 0.40), st.ribCol, [0.66, 52]);
                    this.addPart(this.staticOpaque, 'bevelBox', this.matTRS(xCase - 0.05, -0.10, -0.40, 0, 0, 0, 0.54, 0.32, 0.11), st.ribCol, [0.72, 56]);
                    this.addPart(this.staticOpaque, 'cyl', this.matTRS(xCase - 0.05, 0.14, -0.40, 0, 0, 0, 0.045, 0.16, 0.045), [0.20, 0.23, 0.28, 1.0], [0.5, 36]);
                }} else if (gbType === 'Gated Manual') {{
                    // Torre aberta estilo Gated Manual: placa maquinada em H com canais marcados e punho metálico esférico
                    const gX = xCase + 0.14;
                    this.addPart(this.staticOpaque, 'bevelBox', this.matTRS(gX, 0.31, 0, 0, 0, 0, 0.42, 0.15, 0.34), [0.22, 0.25, 0.31, 1.0], [0.58, 44]);
                    this.addPart(this.staticOpaque, 'bevelBox', this.matTRS(gX, 0.44, 0, 0, 0, 0, 0.44, 0.036, 0.38), [0.84, 0.88, 0.94, 1.0], [0.86, 72]);
                    for (const sx of [-0.17, 0.17]) {{
                        for (const sz of [-0.14, 0.14]) {{
                            this.addPart(this.staticOpaque, 'hex', this.matTRS(gX + sx, 0.415, sz, 0, 0, 0, 0.018, 0.08, 0.018), st.ribCol, [0.78, 60]);
                        }}
                    }}
                    for (const gz of [-0.10, 0.0, 0.10]) {{
                        this.addPart(this.staticOpaque, 'box', this.matTRS(gX, 0.460, gz, 0, 0, 0, 0.26, 0.014, 0.026), [0.06, 0.07, 0.10, 1.0], [0.15, 10]);
                    }}
                    this.addPart(this.staticOpaque, 'box', this.matTRS(gX, 0.460, 0, 0, 0, 0, 0.034, 0.014, 0.226), [0.06, 0.07, 0.10, 1.0], [0.15, 10]);
                    this.addPart(this.staticOpaque, 'cyl', this.matTRS(gX + 0.05, 0.55, -0.05, -0.14, 0, -0.18, 0.026, 0.22, 0.026), [0.90, 0.94, 0.98, 1.0], [0.88, 74]);
                    this.addPart(this.staticOpaque, 'sphere', this.matTRS(gX + 0.07, 0.66, -0.07, 0, 0, 0, 0.072, 0.072, 0.072), [0.92, 0.95, 0.99, 1.0], [0.90, 76]);
                    this.addPipe(this.staticOpaque, [[gX - 0.16, 0.34, 0.18], [xCase - 0.20, 0.26, 0.26], [xCase - 0.20, 0.06, 0.32]], 0.020, st.ribCol, [0.76, 60]);
                }} else {{
                    this.addPart(this.staticOpaque, 'bevelBox', this.matTRS(xCase + 0.16, 0.31, 0, 0, 0, 0, 0.36, 0.16, 0.28), st.turretCol, [0.60, 48]);
                    this.addPart(this.staticOpaque, 'cyl', this.matTRS(xCase + 0.16, 0.45, 0, 0.26, 0, 0, 0.036, 0.24, 0.036), [0.84, 0.88, 0.92, 1.0], [0.8, 64]);
                    this.addPart(this.staticOpaque, 'sphere', this.matTRS(xCase + 0.16, 0.56, 0.06, 0, 0, 0, 0.068, 0.068, 0.068), [0.74, 0.22, 0.22, 1.0], [0.65, 52]);
                }}

                // Veios internos + Power-Split Planetário E-CVT ou N pares de carretos dentados (4 a 9 mudanças)
                this.addPart(this.staticOpaque, 'cyl', this.matTRS(xFront + 0.64 + caseLen * 0.45, 0.02, 0, 0, 0, Math.PI * 0.5, 0.055, caseLen + 0.66, 0.055), [0.74, 0.78, 0.84, 1.0], [0.78, 64]);
                this.addPart(this.staticOpaque, 'cyl', this.matTRS(xCase, -0.27, 0, 0, 0, Math.PI * 0.5, 0.048, caseLen * 0.90, 0.048), [0.62, 0.66, 0.72, 1.0], [0.72, 58]);

                const xStartG = xCase - caseLen * 0.38;
                const xEndG = xCase + caseLen * 0.38;
                if (isEcvt) {{
                    // Motor-Gerador MG1 (Gerador + arranque híbrido)
                    const xMg1 = xCase - caseLen * 0.29;
                    const C_STATOR = [0.22, 0.26, 0.33, 1.0];
                    const C_COPPER = [0.82, 0.42, 0.16, 1.0];
                    this.addPart(this.staticOpaque, 'torus', this.matTRS(xMg1, 0.02, 0, 0, Math.PI * 0.5, 0, 0.23, 0.23, 0.23), C_STATOR, [0.55, 42]);
                    this.addPart(this.staticOpaque, 'torus', this.matTRS(xMg1 - 0.06, 0.02, 0, 0, Math.PI * 0.5, 0, 0.19, 0.19, 0.19), C_COPPER, [0.74, 58]);
                    this.dynamicRotors.push({{ type: 'gearboxGear', symmetry: 16, cx: xMg1, cy: 0.02, cz: 0, r: 0.165, thick: 0.105, speedMult: -1.35, colorRim: [0.18, 0.62, 0.84, 1.0] }});

                    // Conjunto Planetário Divisor de Potência (Power-Split Device)
                    const xPsd = xCase;
                    this.addPart(this.staticTrans, 'torus', this.matTRS(xPsd, 0.02, 0, 0, Math.PI * 0.5, 0, 0.245, 0.245, 0.245), [0.74, 0.78, 0.84, 1.0], [0.72, 56]);
                    this.dynamicRotors.push({{ type: 'gearboxGear', symmetry: 18, cx: xPsd, cy: 0.02, cz: 0, r: 0.102, thick: 0.068, speedMult: 1.0, colorRim: [0.84, 0.68, 0.28, 1.0] }});
                    for (let pi = 0; pi < 3; pi++) {{
                        const pa = (pi * Math.PI * 2) / 3;
                        this.dynamicRotors.push({{
                            type: 'gearboxGear', symmetry: 14,
                            cx: xPsd, cy: 0.02 + Math.cos(pa) * 0.168, cz: Math.sin(pa) * 0.168,
                            r: 0.062, thick: 0.064, speedMult: -1.65,
                            colorRim: [0.64, 0.70, 0.78, 1.0]
                        }});
                    }}

                    // Motor-Gerador MG2 (Tração elétrica de binário elevado + redução)
                    const xMg2 = xCase + caseLen * 0.28;
                    this.addPart(this.staticOpaque, 'torus', this.matTRS(xMg2, 0.02, 0, 0, Math.PI * 0.5, 0, 0.26, 0.26, 0.26), C_STATOR, [0.55, 42]);
                    this.addPart(this.staticOpaque, 'torus', this.matTRS(xMg2 - 0.07, 0.02, 0, 0, Math.PI * 0.5, 0, 0.22, 0.22, 0.22), C_COPPER, [0.74, 58]);
                    this.addPart(this.staticOpaque, 'torus', this.matTRS(xMg2 + 0.07, 0.02, 0, 0, Math.PI * 0.5, 0, 0.22, 0.22, 0.22), C_COPPER, [0.74, 58]);
                    this.dynamicRotors.push({{ type: 'gearboxGear', symmetry: 20, cx: xMg2, cy: 0.02, cz: 0, r: 0.205, thick: 0.145, speedMult: 0.90, colorRim: [0.20, 0.66, 0.88, 1.0] }});
                    this.dynamicRotors.push({{ type: 'gearboxGear', symmetry: 18, cx: xMg2, cy: -0.27, cz: 0, r: 0.125, thick: 0.070, speedMult: -1.25, colorRim: [0.54, 0.59, 0.66, 1.0] }});
                }} else {{
                    for (let gi = 0; gi < speeds; gi++) {{
                        const frac = speeds > 1 ? gi / (speeds - 1) : 0.5;
                        const gx = xStartG + frac * (xEndG - xStartG);
                        const topR = 0.085 + frac * 0.120;
                        const botR = 0.290 - topR;
                        const gCol = (gi % 2 === 0) ? [0.66, 0.71, 0.78, 1.0] : [0.54, 0.59, 0.66, 1.0];
                        this.dynamicRotors.push({{ type: 'gearboxGear', symmetry: 20, cx: gx, cy: 0.02, cz: 0, r: topR, thick: 0.058, speedMult: 1.0, colorRim: gCol }});
                        this.dynamicRotors.push({{ type: 'gearboxGear', symmetry: 20, cx: gx, cy: -0.27, cz: 0, r: botR, thick: 0.058, speedMult: -0.78, colorRim: [0.48, 0.53, 0.60, 1.0] }});
                        if (gi < speeds - 1) {{
                            const synX = gx + ((xEndG - xStartG) / (speeds - 1)) * 0.5;
                            this.addPart(this.staticOpaque, 'cyl', this.matTRS(synX, 0.02, 0, 0, 0, Math.PI * 0.5, 0.088, 0.022, 0.088), [0.84, 0.64, 0.24, 1.0], [0.80, 62]);
                        }}
                    }}
                    // Carreto de marcha-atrás lateral
                    this.dynamicRotors.push({{ type: 'gearboxGear', symmetry: 20, cx: xStartG, cy: -0.13, cz: 0.23, r: 0.084, thick: 0.055, speedMult: -0.95, colorRim: [0.76, 0.58, 0.26, 1.0] }});
                }}

                // Coroa do diferencial traseiro (proporcional à relação final) + cauda + veio de saída
                const ringR = Math.max(0.24, Math.min(0.36, 0.22 + (finalDrive - 2.9) * 0.06));
                this.dynamicRotors.push({{ type: 'gearboxGear', symmetry: 20, cx: xCase + caseLen * 0.44, cy: -0.24, cz: 0.14, r: ringR, thick: 0.075, speedMult: 1.0 / Math.max(1.5, finalDrive), colorRim: [0.78, 0.62, 0.28, 1.0] }});
                this.addPart(this.staticOpaque, 'cone', this.matTRS(xTail, 0.02, 0, 0, 0, -Math.PI * 0.5, 0.28, 0.44, 0.28), st.caseCol, st.spec);
                this.dynamicRotors.push({{
                    type: 'driveshaft',
                    symmetry: 4,
                    cx: xTail + 0.30, cy: 0.02, cz: 0,
                    r: 0.13, thick: 0.32,
                    speedMult: 0.85,
                    colorRim: [0.78, 0.82, 0.88, 1.0],
                    colorHub: st.ribCol
                }});

                return {{ xTailEnd: xTail + 0.46, caseLen, xCase }};
            }}

            getExhaustParams() {{
                const exType = this.config.exhaustType || 'OEM Catalisador';
                const tipsMode = this.config.exhaustTips || 'Dupla';
                const exJunc = this.config.exhaustJunction || 'X-Pipe';
                const diamMm = Math.max(35, Math.min(140, Number(this.config.exhaustDiameter) || 63));
                const pipeR = (diamMm / 63.0) * 0.082;
                const styles = {{
                    'OEM Catalisador':     {{ col: [0.54, 0.57, 0.62, 1.0], spec: [0.52, 40], catCol: [0.38, 0.41, 0.46, 1.0], mufCol: [0.48, 0.51, 0.56, 1.0], tipCol: [0.78, 0.82, 0.88, 1.0], hasCat: true, hasMuf: true, valved: false }},
                    'Sport Cat-Back':      {{ col: [0.72, 0.76, 0.82, 1.0], spec: [0.78, 62], catCol: [0.64, 0.68, 0.74, 1.0], mufCol: [0.74, 0.78, 0.84, 1.0], tipCol: [0.86, 0.90, 0.94, 1.0], hasCat: true, hasMuf: true, valved: false }},
                    'Inconel 4-1':         {{ col: [0.76, 0.60, 0.34, 1.0], spec: [0.76, 60], catCol: [0.68, 0.52, 0.28, 1.0], mufCol: [0.72, 0.56, 0.32, 1.0], tipCol: [0.82, 0.68, 0.42, 1.0], hasCat: false, hasMuf: true, valved: false }},
                    'Titânio Valvetronic': {{ col: [0.64, 0.62, 0.58, 1.0], spec: [0.78, 64], catCol: [0.58, 0.56, 0.54, 1.0], mufCol: [0.52, 0.56, 0.74, 1.0], tipCol: [0.34, 0.44, 0.86, 1.0], hasCat: true, hasMuf: true, valved: true }},
                    'Straight Pipe':       {{ col: [0.70, 0.62, 0.52, 1.0], spec: [0.72, 56], catCol: [0.62, 0.54, 0.44, 1.0], mufCol: [0.58, 0.48, 0.40, 1.0], tipCol: [0.36, 0.46, 0.86, 1.0], hasCat: false, hasMuf: false, valved: false }}
                }};
                return {{ exType, tipsMode, exJunc, diamMm, pipeR, st: styles[exType] || styles['OEM Catalisador'] }};
            }}

            addExhaustDownstreamSystem({{ lanesZ, yLine, xStartPipe, xMid, xJunc, xCat, xMuf, xTip, pathItems, st, pipeR, exType, tipsMode, exJunc = 'X-Pipe', placeCatBeforeJunc = false }}) {{
                const hasDualLanes = lanesZ.length >= 2;
                const zMid = hasDualLanes ? (lanesZ[0] + lanesZ[1]) * 0.5 : lanesZ[0];
                const isMergedJunc = exJunc === 'Y-Pipe' || exJunc === 'Coletor Merge';
                const outLanesZ = (hasDualLanes && isMergedJunc) ? [zMid] : lanesZ;
                const trunkR = (hasDualLanes && isMergedJunc) ? pipeR * 1.18 : pipeR;
                const jX = (xJunc !== undefined && xJunc !== null) ? xJunc : ((xMid + xCat) * 0.5);
                const splitJunction = hasDualLanes && exJunc !== 'H-Pipe' && exJunc !== 'Sem União';
                const preEnd = splitJunction ? (jX - 0.24) : (jX + 0.02);
                const postStart = splitJunction ? (jX + 0.24) : (jX + 0.02);

                const drawCatAt = (lzCat, rCatBase) => {{
                    const catR = Math.max(0.14, rCatBase * 1.90);
                    this.addPart(this.staticTrans, 'cyl', this.matTRS(xCat, yLine, lzCat, 0, 0, Math.PI * 0.5, catR, 0.46, catR), st.catCol, [0.58, 44]);
                    this.addPart(this.staticOpaque, 'cyl', this.matTRS(xCat, yLine, lzCat, 0, 0, Math.PI * 0.5, catR * 0.78, 0.34, catR * 0.78), [0.76, 0.54, 0.26, 1.0], [0.30, 18]);
                    this.addPart(this.staticOpaque, 'hex', this.matTRS(xCat - 0.20, yLine + catR * 1.02, lzCat, 0, 0, 0, 0.026, 0.09, 0.026), [0.82, 0.64, 0.24, 1.0], [0.78, 62]);
                }};

                // Troço a montante (coletor -> fole flexível -> junção)
                for (let bi = 0; bi < lanesZ.length; bi++) {{
                    const lz = lanesZ[bi];
                    const startPt = (xStartPipe && xStartPipe[bi]) ? xStartPipe[bi] : [xMid - 0.30, yLine, lz];
                    const pipePts = [startPt];
                    if (Math.abs(startPt[0] - xMid) > 0.45) {{
                        pipePts.push([Math.min(startPt[0] + 0.24, xMid - 0.22), yLine, lz]);
                    }}
                    pipePts.push([xMid - 0.14, yLine, lz], [xMid, yLine, lz], [preEnd, yLine, lz]);
                    this.addPipe(this.staticOpaque, pipePts, pipeR, st.col, st.spec);
                    this.addPart(this.staticOpaque, 'cyl', this.matTRS(xMid - 0.08, yLine, lz, 0, 0, Math.PI * 0.5, pipeR * 1.30, 0.18, pipeR * 1.30), [0.34, 0.37, 0.43, 1.0], [0.4, 28]);
                    this.addPart(this.staticOpaque, 'cyl', this.matTRS(xMid + 0.10, yLine, lz, 0, 0, Math.PI * 0.5, pipeR * 1.24, 0.04, pipeR * 1.24), [0.86, 0.89, 0.94, 1.0], [0.82, 68]);
                    if (st.hasCat && placeCatBeforeJunc) {{
                        drawCatAt(lz, pipeR);
                    }}
                }}

                // Geometria da forma de união / junção (X-Pipe, H-Pipe, Y-Pipe, Coletor Merge, Sem União)
                if (hasDualLanes) {{
                    const zL = lanesZ[0], zR = lanesZ[1];
                    if (exJunc === 'X-Pipe') {{
                        this.addPipe(this.staticOpaque, [[preEnd, yLine, zL], [jX, yLine, zMid], [postStart, yLine, zR]], pipeR * 0.94, st.col, st.spec);
                        this.addPipe(this.staticOpaque, [[preEnd, yLine, zR], [jX, yLine, zMid], [postStart, yLine, zL]], pipeR * 0.94, st.col, st.spec);
                        this.addPart(this.staticOpaque, 'bevelBox', this.matTRS(jX, yLine, zMid, 0, 0, 0, 0.24, pipeR * 2.15, Math.min(0.42, Math.abs(zR - zL) * 0.46)), st.catCol, [0.74, 56]);
                        this.addPart(this.staticOpaque, 'hex', this.matTRS(jX, yLine + pipeR * 1.18, zMid, 0, 0, 0, 0.024, 0.05, 0.024), [0.82, 0.64, 0.24, 1.0], [0.78, 60]);
                    }} else if (exJunc === 'H-Pipe') {{
                        this.addPipe(this.staticOpaque, [[jX, yLine, zL], [jX, yLine, zR]], pipeR * 0.84, st.col, st.spec, [], false);
                        for (const lz of lanesZ) {{
                            this.addPart(this.staticOpaque, 'cyl', this.matTRS(jX, yLine, lz, 0, 0, Math.PI * 0.5, pipeR * 1.26, 0.14, pipeR * 1.26), st.catCol, [0.72, 54]);
                        }}
                        this.addPart(this.staticOpaque, 'cyl', this.matTRS(jX, yLine, zMid, Math.PI * 0.5, 0, 0, pipeR * 1.08, 0.06, pipeR * 1.08), [0.84, 0.88, 0.92, 1.0], [0.80, 64]);
                    }} else if (exJunc === 'Y-Pipe') {{
                        this.addPipe(this.staticOpaque, [[preEnd, yLine, zL], [jX - 0.06, yLine, (zL + zMid) * 0.5], [jX + 0.10, yLine, zMid]], pipeR * 0.96, st.col, st.spec);
                        this.addPipe(this.staticOpaque, [[preEnd, yLine, zR], [jX - 0.06, yLine, (zR + zMid) * 0.5], [jX + 0.10, yLine, zMid]], pipeR * 0.96, st.col, st.spec);
                        this.addPart(this.staticOpaque, 'cone', this.matTRS(jX + 0.12, yLine, zMid, 0, 0, -Math.PI * 0.5, trunkR * 1.34, 0.28, trunkR * 1.34), st.catCol, st.spec);
                        this.addPart(this.staticOpaque, 'cyl', this.matTRS(postStart, yLine, zMid, 0, 0, Math.PI * 0.5, trunkR * 1.22, 0.05, trunkR * 1.22), [0.86, 0.89, 0.94, 1.0], [0.82, 68]);
                    }} else if (exJunc === 'Coletor Merge') {{
                        this.addPipe(this.staticOpaque, [[preEnd, yLine, zL], [jX - 0.05, yLine, zMid]], pipeR * 0.95, st.col, st.spec);
                        this.addPipe(this.staticOpaque, [[preEnd, yLine, zR], [jX - 0.05, yLine, zMid]], pipeR * 0.95, st.col, st.spec);
                        this.addPart(this.staticOpaque, 'bevelBox', this.matTRS(jX - 0.08, yLine, zMid, 0, 0, 0, 0.16, pipeR * 2.2, Math.abs(zR - zL) * 0.65), [0.28, 0.32, 0.38, 1.0], [0.64, 48]);
                        this.addPart(this.staticOpaque, 'cone', this.matTRS(jX + 0.08, yLine, zMid, 0, 0, -Math.PI * 0.5, trunkR * 1.56, 0.30, trunkR * 1.56), [0.76, 0.58, 0.28, 1.0], [0.74, 58]);
                        this.addPart(this.staticOpaque, 'cyl', this.matTRS(postStart, yLine, zMid, 0, 0, Math.PI * 0.5, trunkR * 1.25, 0.05, trunkR * 1.25), [0.86, 0.89, 0.94, 1.0], [0.82, 68]);
                    }}
                }} else if (exJunc === 'Coletor Merge' || exJunc === 'Y-Pipe') {{
                    this.addPart(this.staticOpaque, 'cone', this.matTRS(jX, yLine, lanesZ[0], 0, 0, -Math.PI * 0.5, pipeR * 1.65, 0.28, pipeR * 1.65), [0.76, 0.58, 0.28, 1.0], [0.74, 58]);
                    this.addPart(this.staticOpaque, 'cyl', this.matTRS(jX + 0.15, yLine, lanesZ[0], 0, 0, Math.PI * 0.5, pipeR * 1.28, 0.05, pipeR * 1.28), [0.86, 0.89, 0.94, 1.0], [0.82, 68]);
                }}

                // Troço a jusante (junção -> catalisador opcional -> panela -> ponteiras)
                for (let oi = 0; oi < outLanesZ.length; oi++) {{
                    const lzOut = outLanesZ[oi];
                    this.addPipe(this.staticOpaque, [[postStart, yLine, lzOut], [xTip - 0.06, yLine, lzOut]], trunkR, st.col, st.spec);
                    if (st.hasCat && !placeCatBeforeJunc) {{
                        drawCatAt(lzOut, trunkR);
                    }}
                    if (st.hasMuf) {{
                        const mufR = Math.max(0.15, trunkR * 1.75);
                        const mufLen = exType === 'Inconel 4-1' ? 0.42 : 0.56;
                        this.addPart(this.staticTrans, 'bevelBox', this.matTRS(xMuf, yLine, lzOut, 0, 0, 0, mufLen, mufR * 1.45, mufR * 1.90), st.mufCol, st.spec);
                        this.addPart(this.staticOpaque, 'cyl', this.matTRS(xMuf, yLine, lzOut, 0, 0, Math.PI * 0.5, trunkR * 0.88, mufLen * 0.92, trunkR * 0.88), [0.78, 0.82, 0.88, 1.0], [0.65, 52]);
                        this.addPart(this.staticOpaque, 'box', this.matTRS(xMuf - 0.09, yLine, lzOut, 0, 0, 0, 0.024, mufR * 1.32, mufR * 1.70), st.col, [0.5, 36]);
                        this.addPart(this.staticOpaque, 'box', this.matTRS(xMuf + 0.09, yLine, lzOut, 0, 0, 0, 0.024, mufR * 1.32, mufR * 1.70), st.col, [0.5, 36]);
                        if (st.valved) {{
                            this.addPart(this.staticOpaque, 'cyl', this.matTRS(xMuf + 0.16, yLine + mufR * 1.05, lzOut, 0, 0, 0, 0.056, 0.12, 0.056), [0.84, 0.64, 0.24, 1.0], [0.78, 62]);
                            this.addPipe(this.staticOpaque, [[xMuf - 0.34, yLine, lzOut], [xMuf, yLine, lzOut + (lzOut <= 0 ? -mufR * 1.12 : mufR * 1.12)], [xTip - 0.28, yLine, lzOut]], trunkR * 0.72, st.tipCol, [0.80, 64]);
                        }}
                    }}
                }}

                const hasOutDual = outLanesZ.length >= 2;
                const tipPositions = [];
                if (tipsMode === 'Simples') {{
                    const cZ = hasOutDual ? (outLanesZ[0] + outLanesZ[1]) * 0.5 : outLanesZ[0];
                    if (hasOutDual) {{
                        this.addPipe(this.staticOpaque, [[xTip - 0.42, yLine, outLanesZ[0]], [xTip - 0.10, yLine, cZ]], trunkR * 0.92, st.col, st.spec);
                        this.addPipe(this.staticOpaque, [[xTip - 0.42, yLine, outLanesZ[1]], [xTip - 0.10, yLine, cZ]], trunkR * 0.92, st.col, st.spec);
                    }}
                    tipPositions.push({{ lz: outLanesZ[0], tz: cZ }});
                }} else if (tipsMode === 'Dupla') {{
                    if (hasOutDual) {{
                        tipPositions.push({{ lz: outLanesZ[0], tz: outLanesZ[0] }}, {{ lz: outLanesZ[1], tz: outLanesZ[1] }});
                    }} else {{
                        for (const s of [-1, 1]) {{
                            const tz = outLanesZ[0] + s * Math.max(0.14, pipeR * 1.38);
                            this.addPipe(this.staticOpaque, [[xTip - 0.30, yLine, outLanesZ[0]], [xTip - 0.08, yLine, tz]], pipeR * 0.85, st.col, st.spec);
                            tipPositions.push({{ lz: outLanesZ[0], tz }});
                        }}
                    }}
                }} else {{
                    if (hasOutDual) {{
                        for (const bZ of outLanesZ) {{
                            const off = Math.max(0.11, pipeR * 1.28);
                            for (const s of [-1, 1]) {{
                                const tz = bZ + s * off;
                                this.addPipe(this.staticOpaque, [[xTip - 0.30, yLine, bZ], [xTip - 0.08, yLine, tz]], pipeR * 0.82, st.col, st.spec);
                                tipPositions.push({{ lz: bZ, tz }});
                            }}
                        }}
                    }} else {{
                        const stepZ = Math.max(0.13, pipeR * 1.50);
                        for (let qi = -1.5; qi <= 1.5; qi += 1.0) {{
                            const tz = outLanesZ[0] + qi * stepZ;
                            this.addPipe(this.staticOpaque, [[xTip - 0.32, yLine, outLanesZ[0]], [xTip - 0.08, yLine, tz]], pipeR * 0.78, st.col, st.spec);
                            tipPositions.push({{ lz: outLanesZ[0], tz }});
                        }}
                    }}
                }}

                const tipR = pipeR * 1.24;
                for (const tp of tipPositions) {{
                    this.addPart(this.staticOpaque, 'cyl', this.matTRS(xTip + 0.08, yLine, tp.tz, 0, 0, Math.PI * 0.5, tipR, 0.32, tipR), st.tipCol, [0.85, 72]);
                    this.addPart(this.staticOpaque, 'cyl', this.matTRS(xTip + 0.25, yLine, tp.tz, 0, 0, Math.PI * 0.5, tipR * 0.82, 0.02, tipR * 0.82), [0.06, 0.07, 0.09, 1.0], [0.1, 8]);
                    this.exhaustTips.push({{ x: xTip + 0.26, y: yLine, z: tp.tz, r: tipR * 0.90, hot: exType === 'Straight Pipe' || exType === 'Inconel 4-1' || exType === 'Titânio Valvetronic' }});
                }}

                for (let pi = 0; pi < pathItems.length; pi++) {{
                    const pItem = pathItems[pi];
                    let postLz = pItem.lz;
                    const jPts = [];
                    if (hasDualLanes && exJunc === 'X-Pipe') {{
                        const otherLz = pItem.lz === lanesZ[0] ? lanesZ[1] : lanesZ[0];
                        jPts.push([preEnd, yLine, pItem.lz], [jX, yLine, zMid], [postStart, yLine, otherLz]);
                        postLz = otherLz;
                    }} else if (hasDualLanes && isMergedJunc) {{
                        jPts.push([preEnd, yLine, pItem.lz], [jX + 0.08, yLine, zMid]);
                        postLz = zMid;
                    }} else {{
                        jPts.push([jX, yLine, pItem.lz]);
                    }}
                    const matchTips = tipPositions.filter(tp => tp.lz === postLz);
                    const chosenTip = matchTips.length ? matchTips[pi % matchTips.length] : tipPositions[pi % tipPositions.length];
                    const midAndCat = placeCatBeforeJunc
                        ? [[xMid, yLine, pItem.lz], [xCat, yLine, pItem.lz], ...jPts]
                        : [[xMid, yLine, pItem.lz], ...jPts, [xCat, yLine, postLz]];
                    const fullPath = [
                        ...pItem.prefixPts,
                        ...midAndCat,
                        [xMuf, yLine, postLz],
                        [xTip - 0.12, yLine, chosenTip.tz],
                        [xTip + 0.32, yLine, chosenTip.tz]
                    ];
                    this.exhaustGasPaths.push({{ pts: fullPath, phaseOff: pi / Math.max(1, pathItems.length), r: Math.max(0.030, pipeR * 0.54) }});
                }}
            }}

            buildStandaloneGearboxScene() {{
                this.sceneCenterX = 0;
                const isEcvt = this.config.gearboxType === 'E-CVT';
                const speeds = Math.max(4, Math.min(9, parseInt(this.config.gearboxSpeeds, 10) || 6));
                const extraLen = isEcvt ? 0.16 : (speeds - 6) * 0.14;
                this.addGearboxModel(-1.45 - extraLen * 0.3, 0.68);
                this.baseDist = 5.4 + (isEcvt ? 0.15 : Math.max(0, speeds - 6) * 0.25);
            }}

            buildStandaloneExhaustScene() {{
                this.sceneCenterX = 0;
                const n = Math.max(1, Math.min(16, parseInt(this.config.cilindros, 10) || 4));
                const fmt = ['I', 'V', 'VR', 'W', 'B', 'WANKEL'].includes(this.config.formato) ? this.config.formato : 'I';
                const supportsJunc = EXHAUST_JUNCTION_FORMATS.includes(fmt);
                const {{ exType, tipsMode, exJunc, pipeR, st }} = this.getExhaustParams();
                const effJunc = supportsJunc ? exJunc : 'Sem União';
                const runnerR = Math.max(0.036, Math.min(0.095, pipeR * 0.66));

                const useDualHeaders = supportsJunc;
                const lanesZ = useDualHeaders ? [-0.46, 0.46] : [0.0];
                const portCounts = useDualHeaders
                    ? [Math.max(1, Math.min(5, Math.ceil(n / 2))), Math.max(1, Math.min(5, Math.floor(n / 2)))]
                    : [Math.min(6, n)];
                const xPortStart = -1.78, xPortEnd = -1.04;
                const xCol = -0.82, xMid = -0.44, xJunc = 0.00, xCat = 0.54, xMuf = 1.14, xTip = 1.80;
                const yLine = -0.06;
                const pathItems = [];
                const xStartPipe = [];

                for (let bi = 0; bi < lanesZ.length; bi++) {{
                    const lz = lanesZ[bi];
                    const collPt = [xCol, yLine, lz];
                    xStartPipe.push(collPt);
                    const pCount = portCounts[bi];

                    for (let pi = 0; pi < pCount; pi++) {{
                        const frac = pCount > 1 ? pi / (pCount - 1) : 0.5;
                        const px = xPortStart + frac * (xPortEnd - xPortStart);
                        const py = 0.24;
                        const pz = useDualHeaders ? (lz * 1.15) : ((pi % 2 === 0 ? -0.10 : 0.10));
                        this.addPart(this.staticTrans, 'cyl', this.matTRS(px, py + 0.14, pz, 0, 0, 0, 0.10, 0.26, 0.10), [0.56, 0.60, 0.66, 1.0], [0.46, 36]);
                        this.addPart(this.staticOpaque, 'cyl', this.matTRS(px, py + 0.04, pz, 0, 0, 0, 0.072, 0.025, 0.072), [0.95, 0.46, 0.18, 1.0], [0.7, 50]);
                        this.addPart(this.staticOpaque, 'cyl', this.matTRS(px, py + 0.17, pz, 0, 0, 0, 0.016, 0.22, 0.016), [0.80, 0.84, 0.88, 1.0], [0.8, 64]);
                        this.addPart(this.staticOpaque, 'box', this.matTRS(px, py, pz, 0, 0, 0, 0.13, 0.036, 0.14), st.col, st.spec);

                        const midRun = [px + 0.18, 0.08 + (pi % 2) * 0.05, lz * (1.12 + 0.08 * (1 - frac))];
                        this.addPipe(this.staticOpaque, [[px, py, pz], midRun, collPt], runnerR, st.col, st.spec);
                        pathItems.push({{ lz, prefixPts: [[px, py, pz], midRun, collPt] }});
                    }}

                    this.addPart(this.staticOpaque, 'cone', this.matTRS(xCol + 0.08, yLine, lz, 0, 0, -Math.PI * 0.5, runnerR * 1.85, 0.22, runnerR * 1.85), st.catCol, st.spec);
                }}

                this.addExhaustDownstreamSystem({{ lanesZ, yLine, xStartPipe, xMid, xJunc, xCat, xMuf, xTip, pathItems, st, pipeR, exType, tipsMode, exJunc: effJunc, placeCatBeforeJunc: false }});
                this.baseDist = 5.4;
            }}

            addSequentialCrossover(pA, pB, dropY = -0.14, rad = 0.052) {{
                const mx = (pA[0] + pB[0]) * 0.5;
                const my = (pA[1] + pB[1]) * 0.5 + dropY;
                const mz = (pA[2] + pB[2]) * 0.5;
                this.addPipe(this.staticOpaque, [pA, [mx, my, mz], pB], rad, [0.76, 0.54, 0.22, 1.0], [0.62, 48]);
                // Válvula de derivação sequencial (flapper + atuador)
                this.addPart(this.staticOpaque, 'cyl', this.matTRS(mx, my + 0.08, mz, 0, 0, 0, rad * 1.65, 0.14, rad * 1.65), [0.80, 0.62, 0.24, 1.0], [0.74, 58]);
                this.addPart(this.staticOpaque, 'box', this.matTRS(mx, my, mz, 0, 0, 0, rad * 2.2, rad * 2.2, rad * 2.2), [0.22, 0.25, 0.30, 1.0], [0.55, 40]);
            }}

            getIntakeAppearance(matName) {{
                const map = {{
                    'Alumínio Fundido': {{ col: [0.54, 0.58, 0.64, 1.0], runner: [0.60, 0.64, 0.70, 1.0], spec: [0.46, 34], rSpec: [0.50, 38], accent: [0.70, 0.74, 0.80, 1.0], isCarbon: false, isTitanium: false }},
                    'Plástico ABS':     {{ col: [0.16, 0.18, 0.22, 1.0], runner: [0.22, 0.24, 0.29, 1.0], spec: [0.22, 16], rSpec: [0.24, 18], accent: [0.44, 0.48, 0.54, 1.0], isCarbon: false, isTitanium: false }},
                    'Alumínio Billet':  {{ col: [0.78, 0.83, 0.90, 1.0], runner: [0.70, 0.75, 0.82, 1.0], spec: [0.85, 72], rSpec: [0.78, 64], accent: [0.92, 0.95, 0.99, 1.0], isCarbon: false, isTitanium: false }},
                    'Fibra de Carbono': {{ col: [0.13, 0.15, 0.19, 1.0], runner: [0.19, 0.21, 0.26, 1.0], spec: [0.68, 58], rSpec: [0.58, 46], accent: [0.78, 0.62, 0.22, 1.0], isCarbon: true,  isTitanium: false }},
                    'Magnésio':         {{ col: [0.62, 0.54, 0.43, 1.0], runner: [0.56, 0.49, 0.40, 1.0], spec: [0.50, 38], rSpec: [0.50, 38], accent: [0.78, 0.68, 0.54, 1.0], isCarbon: false, isTitanium: false }},
                    'Titânio':          {{ col: [0.64, 0.61, 0.56, 1.0], runner: [0.60, 0.58, 0.66, 1.0], spec: [0.76, 62], rSpec: [0.74, 58], accent: [0.38, 0.48, 0.78, 1.0], isCarbon: false, isTitanium: true }}
                }};
                return map[matName] || map['Alumínio Fundido'];
            }}

            addPlenumRibsAndFinish(x, y, z, plenumW, radY, radZ, isCyl, app) {{
                const ribCol = (app.isCarbon || app.isTitanium) ? app.accent : app.runner;
                const ribSpec = app.isTitanium ? [0.82, 68] : app.rSpec;
                for (let r = -2; r <= 2; r++) {{
                    const rx = x + r * (plenumW * 0.18);
                    if (isCyl) {{
                        this.addPart(this.staticOpaque, 'cyl', this.matTRS(rx, y, z, 0, 0, Math.PI * 0.5, radY * 1.07, 0.032, radZ * 1.07), ribCol, ribSpec);
                    }} else {{
                        this.addPart(this.staticOpaque, 'bevelBox', this.matTRS(rx, y, z, 0, 0, 0, 0.036, radY * 1.07, radZ * 1.05), ribCol, ribSpec);
                    }}
                }}
                if (app.isCarbon && !isCyl) {{
                    this.addPart(this.staticOpaque, 'box', this.matTRS(x, y - radY * 0.48, z, 0, 0, 0, plenumW * 0.96, 0.022, radZ * 0.92), [0.82, 0.64, 0.22, 1.0], [0.78, 62]);
                }}
            }}

            addVelocityTrumpet(tx, ty, tz, tiltX, tiltZ, radScale, app, tall = false) {{
                const bodyR = 0.078 * radScale;
                const bodyH = (tall ? 0.16 : 0.12) * radScale;
                const bellH = (tall ? 0.15 : 0.11) * radScale;
                const bellR = (tall ? 0.135 : 0.115) * radScale;
                const ux = -Math.sin(tiltZ);
                const uy = Math.cos(tiltX) * Math.cos(tiltZ);
                const uz = Math.sin(tiltX) * Math.cos(tiltZ);
                this.addPart(this.staticOpaque, 'cyl', this.matTRS(tx, ty, tz, tiltX, 0, tiltZ, bodyR, bodyH, bodyR), app.col, app.spec);
                this.addPart(this.staticOpaque, 'cyl', this.matTRS(tx + ux * bodyH * 0.38, ty + uy * bodyH * 0.38, tz + uz * bodyH * 0.38, tiltX, 0, tiltZ, bodyR * 1.20, 0.026, bodyR * 1.20), [0.76, 0.62, 0.26, 1.0], [0.76, 60]);
                const bellDist = bodyH * 0.5 + bellH * 0.48;
                const bx = tx + ux * bellDist, by = ty + uy * bellDist, bz = tz + uz * bellDist;
                this.addPart(this.staticOpaque, 'cone', this.matTRS(bx, by, bz, tiltX + Math.PI, 0, -tiltZ, bellR, bellH, bellR), app.runner, app.rSpec);
                const rimDist = bodyH * 0.5 + bellH * 0.96;
                const mx = tx + ux * rimDist, my = ty + uy * rimDist, mz = tz + uz * rimDist;
                this.addPart(this.staticOpaque, 'torus', this.matTRS(mx, my, mz, tiltX + Math.PI * 0.5, 0, tiltZ, bellR * 0.78, bellR * 0.78, bellR * 0.78), app.accent, [0.84, 68]);
                this.addPart(this.staticOpaque, 'cyl', this.matTRS(mx, my, mz, tiltX, 0, tiltZ, bellR * 0.76, 0.012, bellR * 0.76), [0.16, 0.18, 0.22, 1.0], [0.22, 16]);
            }}

            addIntakeFeedEnd(x, y, z, dirX, isBoosted, isCAI, app) {{
                if (isBoosted) {{
                    this.addPart(this.staticOpaque, 'cyl', this.matTRS(x, y, z, 0, 0, Math.PI * 0.5, 0.125, 0.14, 0.125), app.accent, app.spec);
                    return;
                }}
                this.addThrottleBody(x + dirX * 0.04, y, z);
                if (isCAI) {{
                    const boxX = x + dirX * 0.62;
                    this.addPipe(this.staticOpaque, [[x + dirX * 0.02, y, z], [x + dirX * 0.26, y + 0.05, z + 0.08], [boxX - dirX * 0.12, y + 0.02, z + 0.10]], 0.124, app.runner, app.rSpec, [0]);
                    this.addPart(this.staticTrans, 'bevelBox', this.matTRS(boxX + dirX * 0.08, y + 0.02, z + 0.10, 0, 0, 0, 0.56, 0.56, 0.56), app.col, app.spec);
                    this.addPart(this.staticOpaque, 'bevelBox', this.matTRS(boxX + dirX * 0.08, y - 0.24, z + 0.10, 0, 0, 0, 0.58, 0.06, 0.58), app.accent, app.rSpec);
                    this.addConeFilter(boxX + dirX * 0.08, y + 0.02, z + 0.10, dirX);
                }} else {{
                    this.addPipe(this.staticOpaque, [[x, y, z], [x + dirX * 0.42, y, z]], 0.11, app.runner, app.rSpec, [0]);
                    this.addConeFilter(x + dirX * 0.62, y, z, dirX);
                }}
            }}

            addSideIntakeAssembly({{ halfLenX, py, pz, plenumW, runnersX, feedDirX, isBoosted, intType, app, boreScale }}) {{
                const feedX = feedDirX < 0 ? -halfLenX * 0.94 : halfLenX * 0.94;
                if (intType === 'ITBs' || intType === 'Velocity Stacks') {{
                    const isStacks = intType === 'Velocity Stacks';
                    for (const rx of runnersX) {{
                        if (isStacks) {{
                            this.addVelocityTrumpet(rx, py + 0.10, pz + 0.04, 0.24, 0, boreScale * 1.05, app, true);
                        }} else {{
                            this.addVelocityTrumpet(rx, py + 0.05, pz + 0.02, 0.42, 0, boreScale * 0.95, app, false);
                        }}
                    }}
                    if (!isStacks) {{
                        this.addPart(this.staticOpaque, 'cyl', this.matTRS(0, py + 0.06, pz + 0.06, 0, 0, Math.PI * 0.5, 0.020, plenumW * 0.94, 0.020), [0.84, 0.88, 0.92, 1.0], [0.82, 66]);
                        this.addPart(this.staticOpaque, 'cyl', this.matTRS(feedDirX * plenumW * 0.48, py + 0.06, pz + 0.06, 0, 0, Math.PI * 0.5, 0.048, 0.024, 0.048), [0.76, 0.58, 0.22, 1.0], [0.74, 58]);
                    }}
                    if (isBoosted) {{
                        this.addPart(this.staticTrans, 'bevelBox', this.matTRS(0, py + 0.10, pz + 0.06, 0, 0, 0, plenumW * 1.04, 0.34, 0.42), app.col, app.spec);
                        this.addPart(this.staticOpaque, 'cyl', this.matTRS(feedX, py, pz, 0, 0, Math.PI * 0.5, 0.125, 0.14, 0.125), app.accent, app.spec);
                    }}
                    return;
                }}
                if (intType === 'Dual-Plenum') {{
                    const zA = pz - 0.04, zB = pz + 0.22;
                    this.addPart(this.staticOpaque, 'cyl', this.matTRS(0, py, zA, 0, 0, Math.PI * 0.5, 0.14, plenumW, 0.14), app.col, app.spec);
                    this.addPart(this.staticOpaque, 'cyl', this.matTRS(0, py + 0.06, zB, 0, 0, Math.PI * 0.5, 0.13, plenumW * 0.92, 0.13), app.col, app.spec);
                    for (const bx of [-plenumW * 0.30, 0, plenumW * 0.30]) {{
                        this.addPipe(this.staticOpaque, [[bx, py, zA], [bx, py + 0.06, zB]], 0.056, app.runner, app.rSpec);
                    }}
                    this.addPart(this.staticOpaque, 'cyl', this.matTRS(feedDirX * plenumW * 0.44, py + 0.20, zB, 0, 0, 0, 0.062, 0.09, 0.062), app.accent, app.rSpec);
                    this.addPipe(this.staticOpaque, [[feedX, py, zA], [feedX, py + 0.06, zB]], 0.095, app.runner, app.rSpec);
                    this.addIntakeFeedEnd(feedX, py, pz, feedDirX, isBoosted, false, app);
                    return;
                }}
                if (intType === 'Cold Air Intake') {{
                    this.addPart(this.staticOpaque, 'bevelBox', this.matTRS(0, py + 0.02, pz + 0.02, 0, 0, 0, plenumW, 0.30, 0.36), app.col, app.spec);
                    this.addPlenumRibsAndFinish(0, py + 0.02, pz + 0.02, plenumW, 0.30, 0.36, false, app);
                    this.addIntakeFeedEnd(feedX, py, pz, feedDirX, isBoosted, true, app);
                    return;
                }}
                // Plenum OEM (default)
                this.addPart(this.staticOpaque, 'cyl', this.matTRS(0, py, pz, 0, 0, Math.PI * 0.5, 0.19, plenumW, 0.19), app.col, app.spec);
                this.addPlenumRibsAndFinish(0, py, pz, plenumW, 0.19, 0.19, true, app);
                this.addIntakeFeedEnd(feedX, py, pz, feedDirX, isBoosted, false, app);
            }}

            addValleyIntakeAssembly({{ halfLenX, topY, plenumW, cylSpecs, isBoosted, intType, app, boreScale }}) {{
                const feedX = isBoosted ? -halfLenX * 0.90 : halfLenX * 0.94;
                const feedDirX = isBoosted ? -1 : 1;
                if (intType === 'ITBs' || intType === 'Velocity Stacks') {{
                    const isStacks = intType === 'Velocity Stacks';
                    for (const c of cylSpecs) {{
                        const s = c.bank >= 0 ? 1 : -1;
                        const zOff = s * 0.16;
                        const tilt = s * (isStacks ? 0.16 : 0.24);
                        this.addVelocityTrumpet(c.x, topY - 0.04, zOff, tilt, 0, boreScale * (isStacks ? 1.02 : 0.92), app, isStacks);
                    }}
                    if (!isStacks) {{
                        for (const s of [-1, 1]) {{
                            this.addPart(this.staticOpaque, 'cyl', this.matTRS(0, topY + 0.02, s * 0.21, 0, 0, Math.PI * 0.5, 0.018, plenumW * 0.92, 0.018), [0.84, 0.88, 0.92, 1.0], [0.82, 66]);
                        }}
                    }}
                    if (isBoosted) {{
                        this.addPart(this.staticTrans, 'bevelBox', this.matTRS(0, topY + 0.06, 0, 0, 0, 0, plenumW * 1.04, 0.30, 0.56), app.col, app.spec);
                        this.addPart(this.staticOpaque, 'cyl', this.matTRS(feedX, topY, 0, 0, 0, Math.PI * 0.5, 0.125, 0.14, 0.125), app.accent, app.spec);
                    }}
                    return;
                }}
                if (intType === 'Dual-Plenum') {{
                    for (const s of [-1, 1]) {{
                        this.addPart(this.staticOpaque, 'cyl', this.matTRS(0, topY, s * 0.17, 0, 0, Math.PI * 0.5, 0.145, plenumW, 0.145), app.col, app.spec);
                    }}
                    for (const bx of [-plenumW * 0.34, 0, plenumW * 0.34]) {{
                        this.addPipe(this.staticOpaque, [[bx, topY, -0.17], [bx, topY + 0.06, 0], [bx, topY, 0.17]], 0.062, app.runner, app.rSpec);
                    }}
                    this.addPart(this.staticOpaque, 'cyl', this.matTRS(0, topY + 0.14, 0, 0, 0, 0, 0.068, 0.10, 0.068), app.accent, app.rSpec);
                    this.addPipe(this.staticOpaque, [[feedX, topY, -0.17], [feedX, topY, 0], [feedX, topY, 0.17]], 0.10, app.runner, app.rSpec);
                    this.addIntakeFeedEnd(feedX, topY, 0, feedDirX, isBoosted, false, app);
                    return;
                }}
                if (intType === 'Cold Air Intake') {{
                    this.addPart(this.staticOpaque, 'bevelBox', this.matTRS(0, topY, 0, 0, 0, 0, plenumW, 0.24, 0.58), app.col, app.spec);
                    this.addPlenumRibsAndFinish(0, topY, 0, plenumW, 0.24, 0.58, false, app);
                    this.addIntakeFeedEnd(feedX, topY, 0, feedDirX, isBoosted, true, app);
                    return;
                }}
                // Plenum OEM
                this.addPart(this.staticOpaque, 'bevelBox', this.matTRS(0, topY, 0, 0, 0, 0, plenumW, 0.27, 0.52), app.col, app.spec);
                this.addPlenumRibsAndFinish(0, topY, 0, plenumW, 0.27, 0.52, false, app);
                this.addIntakeFeedEnd(feedX, topY, 0, feedDirX, isBoosted, false, app);
            }}

            addSuperchargerUnit(x, y, z, lenX, widthZ, pulleyX, app = null, intType = 'Plenum OEM') {{
                const C_BODY = app ? app.col : [0.35, 0.40, 0.47, 1.0];
                const C_RIB  = app ? app.accent : [0.60, 0.65, 0.72, 1.0];
                const C_SNOUT = app ? app.runner : [0.68, 0.73, 0.79, 1.0];
                const sp = app ? app.spec : [0.55, 44];
                const C_BELT = [0.15, 0.17, 0.20, 1.0];

                this.addPart(this.staticOpaque, 'bevelBox', this.matTRS(x, y - 0.18, z, 0, 0, 0, lenX * 1.06, 0.08, widthZ * 1.08), app ? app.runner : C_BODY, sp);
                this.addPart(this.staticOpaque, 'bevelBox', this.matTRS(x, y, z, 0, 0, 0, lenX, 0.42, widthZ), C_BODY, sp);
                this.addPart(this.staticOpaque, 'cyl', this.matTRS(x, y + 0.08, z - widthZ * 0.22, 0, 0, Math.PI * 0.5, 0.18, lenX * 0.98, 0.18), C_RIB, [0.68, 58]);
                this.addPart(this.staticOpaque, 'cyl', this.matTRS(x, y + 0.08, z + widthZ * 0.22, 0, 0, Math.PI * 0.5, 0.18, lenX * 0.98, 0.18), C_RIB, [0.68, 58]);
                for (let k = -3; k <= 3; k++) {{
                    this.addPart(this.staticOpaque, 'bevelBox', this.matTRS(x + k * (lenX * 0.13), y + 0.25, z, 0, 0, 0, 0.045, 0.055, widthZ * 0.94), C_RIB, [0.62, 50]);
                }}
                if (intType === 'ITBs' || intType === 'Velocity Stacks') {{
                    this.addPart(this.staticOpaque, 'bevelBox', this.matTRS(x, y + 0.36, z, 0, 0, 0, lenX * 0.58, 0.20, widthZ * 0.72), C_RIB, [0.80, 66]);
                    for (const bOff of [-widthZ * 0.18, widthZ * 0.18]) {{
                        this.addPart(this.staticOpaque, 'cyl', this.matTRS(x + lenX * 0.31, y + 0.36, z + bOff, 0, 0, Math.PI * 0.5, 0.095, 0.08, 0.095), [0.76, 0.22, 0.22, 1.0], [0.65, 52]);
                    }}
                }} else if (intType === 'Dual-Plenum') {{
                    this.addPart(this.staticOpaque, 'cyl', this.matTRS(x, y + 0.30, z + widthZ * 0.34, 0, 0, Math.PI * 0.5, 0.065, lenX * 0.62, 0.065), C_RIB, [0.72, 58]);
                }}
                const snoutLen = Math.max(0.25, (x - lenX * 0.5) - pulleyX);
                const snoutCx = pulleyX + snoutLen * 0.5;
                this.addPart(this.staticOpaque, 'cyl', this.matTRS(snoutCx, y, z, 0, 0, Math.PI * 0.5, 0.098, snoutLen + 0.14, 0.098), C_SNOUT, [0.72, 62]);
                this.addPart(this.staticOpaque, 'bevelBox', this.matTRS(x - lenX * 0.5, y, z, 0, 0, 0, 0.07, 0.30, 0.32), C_RIB, [0.65, 52]);
                this.addPart(this.staticOpaque, 'cyl', this.matTRS(x + lenX * 0.2, y + 0.10, z + widthZ * 0.55, Math.PI * 0.5, 0, 0, 0.07, 0.16, 0.07), C_SNOUT, [0.6, 48]);

                this.dynamicRotors.push({{
                    type: 'pulley',
                    cx: pulleyX - 0.04, cy: y, cz: z,
                    r: 0.21, thick: 0.095, speedMult: 1.5,
                    colorRim: [0.62, 0.44, 0.20, 1.0],
                    colorHub: [0.80, 0.84, 0.88, 1.0]
                }});
                const px = pulleyX - 0.04;
                this.addPipe(this.staticOpaque, [
                    [px, y, z - 0.18],
                    [px, 0, -0.25],
                    [px, -0.25, 0],
                    [px, 0, 0.25],
                    [px, y, z + 0.18],
                    [px, y + 0.19, z],
                    [px, y, z - 0.18]
                ], 0.030, C_BELT, [0.15, 10]);
            }}

            addConeFilter(cx, cy, cz, dirX = -1) {{
                const rotZ = dirX < 0 ? Math.PI * 0.5 : -Math.PI * 0.5;
                this.addPart(this.staticOpaque, 'cone', this.matTRS(cx, cy, cz, 0, 0, rotZ, 0.25, 0.40, 0.25), [0.58, 0.22, 0.22, 1.0], [0.22, 14]);
                for (let r = -1; r <= 1; r++) {{
                    this.addPart(this.staticOpaque, 'cyl', this.matTRS(cx + r * 0.08, cy, cz, 0, 0, rotZ, 0.215 - r * dirX * 0.025, 0.015, 0.215 - r * dirX * 0.025), [0.35, 0.14, 0.14, 1.0], [0.15, 10]);
                }}
                this.addPart(this.staticOpaque, 'cyl', this.matTRS(cx + dirX * 0.21, cy, cz, 0, 0, rotZ, 0.15, 0.055, 0.15), [0.78, 0.82, 0.87, 1.0], [0.76, 64]);
                this.addPart(this.staticOpaque, 'cyl', this.matTRS(cx - dirX * 0.20, cy, cz, 0, 0, rotZ, 0.255, 0.04, 0.255), [0.72, 0.76, 0.82, 1.0], [0.7, 56]);
            }}

            addIntercooler(cx, cy, cz, wX, hY, dZ) {{
                const rType = this.config.radiatorType || 'OEM Alumínio';
                const isDual = rType === 'Duplo Núcleo';
                const isRace = rType === 'Triple-Pass Racing';
                const isCopper = rType === 'Cobre / Latão';
                const isWater = rType === 'Água-Ar (Charge Cooler)';

                const coreW = isRace ? wX * 1.56 : (isDual ? wX * 1.42 : (isWater ? wX * 1.18 : wX));
                const coreH = isRace ? hY * 1.12 : (isDual ? hY * 1.08 : (isWater ? hY * 0.90 : hY));
                const coreD = isRace ? dZ * 1.08 : (isWater ? dZ * 0.88 : dZ);

                const C_CORE = isCopper ? [0.72, 0.42, 0.20, 1.0]
                             : (isWater ? [0.18, 0.22, 0.28, 1.0]
                             : (isRace ? [0.80, 0.84, 0.90, 1.0] : [0.74, 0.78, 0.84, 1.0]));
                const C_TANK = isCopper ? [0.78, 0.58, 0.24, 1.0]
                             : (isWater ? [0.24, 0.28, 0.35, 1.0]
                             : (isRace ? [0.68, 0.73, 0.80, 1.0] : [0.42, 0.47, 0.54, 1.0]));
                const C_FIN  = isCopper ? [0.46, 0.26, 0.14, 1.0]
                             : (isWater ? [0.28, 0.34, 0.42, 1.0] : [0.48, 0.52, 0.58, 1.0]);
                const coreSpec = isCopper ? [0.78, 60] : (isRace ? [0.82, 66] : [0.65, 50]);
                const tankSpec = isCopper ? [0.80, 62] : (isRace ? [0.84, 68] : [0.54, 44]);

                // Núcleo e depósitos laterais adaptados ao tipo de radiador
                this.addPart(this.staticOpaque, 'bevelBox', this.matTRS(cx, cy, cz, 0, 0, 0, coreW, coreH, coreD * 0.76), C_CORE, coreSpec);
                this.addPart(this.staticOpaque, 'bevelBox', this.matTRS(cx, cy, cz - coreD * 0.48, 0, 0, 0, coreW * 1.08, coreH * 1.04, coreD * 0.20), C_TANK, tankSpec);
                this.addPart(this.staticOpaque, 'bevelBox', this.matTRS(cx, cy, cz + coreD * 0.48, 0, 0, 0, coreW * 1.08, coreH * 1.04, coreD * 0.20), C_TANK, tankSpec);

                const finSpan = (isDual || isRace) ? 5 : 3;
                const finStep = 1.0 / (finSpan * 2.15);
                for (let k = -finSpan; k <= finSpan; k++) {{
                    this.addPart(this.staticOpaque, 'box', this.matTRS(cx, cy + k * (coreH * finStep), cz, 0, 0, 0, coreW * 1.05, isDual || isRace ? 0.015 : 0.020, coreD * 0.73), C_FIN, [0.4, 24]);
                }}
                this.addPart(this.staticOpaque, 'bevelBox', this.matTRS(cx, cy + coreH * 0.54, cz - coreD * 0.3, 0, 0, 0, coreW * 0.62, 0.06, 0.08), C_TANK, [0.5, 36]);
                this.addPart(this.staticOpaque, 'bevelBox', this.matTRS(cx, cy + coreH * 0.54, cz + coreD * 0.3, 0, 0, 0, coreW * 0.62, 0.06, 0.08), C_TANK, [0.5, 36]);

                if (isDual) {{
                    this.addPart(this.staticOpaque, 'box', this.matTRS(cx, cy + coreH * 0.51, cz, 0, 0, 0, coreW * 0.28, 0.028, coreD * 0.92), [0.76, 0.80, 0.86, 1.0], [0.78, 62]);
                }} else if (isRace) {{
                    // Triple-Pass Racing: deflectores nos tanques, tampões AN e ventoinhas duplas traseiras
                    for (const zS of [-1, 1]) {{
                        const fz = cz + zS * (coreD * 0.22);
                        const fx = cx + coreW * 0.54;
                        const fR = Math.min(coreH * 0.42, coreD * 0.19);
                        this.addPart(this.staticOpaque, 'box', this.matTRS(cx, cy + (zS * coreH * 0.16), cz + zS * coreD * 0.56, 0, 0, 0, coreW * 1.12, 0.025, 0.06), [0.86, 0.26, 0.20, 1.0], [0.76, 60]);
                        this.addPart(this.staticOpaque, 'cyl', this.matTRS(cx, cy + coreH * 0.57, cz + zS * coreD * 0.44, 0, 0, 0, 0.045, 0.055, 0.045), zS < 0 ? [0.84, 0.24, 0.22, 1.0] : [0.22, 0.52, 0.88, 1.0], [0.80, 62]);
                        this.addPart(this.staticOpaque, 'torus', this.matTRS(fx, cy, fz, 0, Math.PI * 0.5, 0, fR, fR, 0.036), [0.16, 0.19, 0.24, 1.0], [0.42, 28]);
                        this.dynamicRotors.push({{
                            type: 'impeller',
                            cx: fx + 0.01,
                            cy: cy,
                            cz: fz,
                            r: fR * 0.92,
                            speedMult: zS * 1.35,
                            symmetry: 7,
                            colorHub: [0.82, 0.26, 0.22, 1.0],
                            colorBlade: [0.24, 0.28, 0.34, 1.0]
                        }});
                    }}
                }} else if (isCopper) {{
                    this.addPart(this.staticOpaque, 'cyl', this.matTRS(cx, cy - coreH * 0.48, cz + coreD * 0.46, 0, 0, 0, 0.028, 0.08, 0.028), [0.86, 0.68, 0.26, 1.0], [0.82, 64]);
                    this.addPart(this.staticOpaque, 'cyl', this.matTRS(cx, cy + coreH * 0.57, cz, 0, 0, 0, 0.055, 0.045, 0.055), [0.84, 0.64, 0.24, 1.0], [0.82, 66]);
                }} else if (isWater) {{
                    // Água-Ar: bomba de água elétrica + vaso expansor + conexões AN azuis
                    const C_AN = [0.20, 0.52, 0.88, 1.0];
                    const C_FIT = [0.84, 0.64, 0.24, 1.0];
                    this.addPart(this.staticOpaque, 'cyl', this.matTRS(cx, cy + coreH * 0.62, cz - coreD * 0.16, 0, 0, Math.PI * 0.5, 0.068, 0.18, 0.068), [0.22, 0.26, 0.32, 1.0], [0.64, 48]);
                    this.addPart(this.staticOpaque, 'cyl', this.matTRS(cx, cy + coreH * 0.60, cz + coreD * 0.22, 0, 0, 0, 0.065, 0.12, 0.065), C_AN, [0.76, 60]);
                    this.addPipe(this.staticOpaque, [
                        [cx, cy + coreH * 0.60, cz - coreD * 0.16],
                        [cx + 0.12, cy + coreH * 0.60, cz + coreD * 0.04],
                        [cx, cy + coreH * 0.60, cz + coreD * 0.22]
                    ], 0.024, C_AN, [0.72, 56], [], true);
                    for (const zS of [-1, 1]) {{
                        this.addPart(this.staticOpaque, 'hex', this.matTRS(cx + coreW * 0.42, cy - coreH * 0.22, cz + zS * coreD * 0.44, 0, 0, Math.PI * 0.5, 0.035, 0.06, 0.035), C_FIT, [0.82, 64]);
                    }}
                }}
            }}

            addFreevalveBank(cylSpecs, xValOffs, deckDist, cylR, halfLenX) {{
                const C_ACT  = [0.18, 0.48, 0.78, 1.0];
                const C_SOL  = [0.15, 0.18, 0.24, 1.0];
                const C_FIT  = [0.84, 0.65, 0.25, 1.0];
                const C_RAIL = [0.68, 0.75, 0.84, 1.0];
                const banks = new Map();
                for (const c of cylSpecs) {{
                    const cosA = Math.cos(c.angle), sinA = Math.sin(c.angle);
                    const latY = -sinA, latZ = cosA;
                    if (!banks.has(c.bank)) banks.set(c.bank, c.angle);
                    for (const xOff of xValOffs) {{
                        for (const sideSign of [-1, 1]) {{
                            const latOff = sideSign * (cylR * 0.34);
                            const tilt = c.angle + sideSign * 0.08;
                            const dBody = deckDist + 0.34;
                            const dCap  = deckDist + 0.45;
                            const dFit  = deckDist + 0.49;
                            this.addPart(this.staticOpaque, 'cyl', this.matTRS(c.x + xOff, dBody * cosA + latOff * latY, c.zOff + dBody * sinA + latOff * latZ, tilt, 0, 0, 0.044, 0.20, 0.044), C_ACT, [0.72, 58]);
                            this.addPart(this.staticOpaque, 'box', this.matTRS(c.x + xOff, dCap * cosA + latOff * latY, c.zOff + dCap * sinA + latOff * latZ, tilt, 0, 0, 0.088, 0.048, 0.088), C_SOL, [0.35, 22]);
                            this.addPart(this.staticOpaque, 'hex', this.matTRS(c.x + xOff, dFit * cosA + latOff * latY, c.zOff + dFit * sinA + latOff * latZ, tilt, 0, 0, 0.022, 0.028, 0.022), C_FIT, [0.78, 60]);
                        }}
                    }}
                }}
                for (const [, bAng] of banks.entries()) {{
                    const bCos = Math.cos(bAng), bSin = Math.sin(bAng);
                    const latY = -bSin, latZ = bCos;
                    const rDist = deckDist + 0.49;
                    for (const sideSign of [-1, 1]) {{
                        const lOff = sideSign * (cylR * 0.40);
                        this.addPart(
                            this.staticOpaque,
                            'cyl',
                            this.matTRS(0, rDist * bCos + lOff * latY, rDist * bSin + lOff * latZ, 0, 0, Math.PI * 0.5, 0.024, halfLenX * 1.92, 0.024),
                            C_RAIL,
                            [0.78, 62]
                        );
                    }}
                }}
            }}

            rebuildScene() {{
                this.staticOpaque = [];
                this.staticTrans = [];
                this.dynamicCyls = [];
                this.dynamicWankel = [];
                this.dynamicRotors = [];
                this.dynamicCams = [];
                this.dynamicValves = [];
                this.exhaustTips = [];
                this.exhaustGasPaths = [];
                this.sceneCenterX = 0;
                const viewMode = this.config.viewMode || 'engine';
                if (viewMode === 'gearbox') {{
                    this.buildStandaloneGearboxScene();
                    return;
                }}
                if (viewMode === 'exhaust') {{
                    this.buildStandaloneExhaustScene();
                    return;
                }}

                const n = Math.max(1, Math.min(16, parseInt(this.config.cilindros, 10) || 4));
                const fmt = ['I', 'V', 'VR', 'W', 'B', 'WANKEL'].includes(this.config.formato) ? this.config.formato : 'I';
                const adm = this.config.admissao || 'Atmosférico';
                const intType = this.config.intakeType || 'Plenum OEM';
                const intMat = this.config.intakeMaterial || 'Alumínio Fundido';
                const intApp = this.getIntakeAppearance(intMat);
                const isDiesel = this.config.combustivel === 'Diesel' || this.config.combustivel === 'Biodiesel';
                const vAngOpt = this.config.vAngle === '90' ? '90' : '60';
                const matOpt = this.config.material || 'Alumínio';
                const pMatOpt = this.config.pistonMaterial || 'Alumínio';
                const camMode = ['DOHC', 'SOHC', 'OHV', 'Freevalve'].includes(this.config.camshaft) ? this.config.camshaft : 'DOHC';
                const vType = this.config.valveType || 'Molas';
                const is2Stroke = fmt !== 'WANKEL' && this.config.ciclo === '2T';
                const isFreevalve = fmt !== 'WANKEL' && !is2Stroke && (camMode === 'Freevalve' || vType === 'Freevalve');
                const valvesCount = parseInt(this.config.numValvulas, 10) === 2 ? 2 : 4;
                const hasMultiTurbo = adm === 'Biturbo' || adm === 'Quad Turbo';
                const turboCfg = (hasMultiTurbo && this.config.turboConfig === 'Sequencial') ? 'Sequencial' : 'Paralelo';
                const fwType = this.config.flywheel || 'Monomassa Aço';
                const dmpType = this.config.damper || 'Elastómero OEM';
                const turboBar = Math.max(0, Number(this.config.turboBar) || 0);
                const turboImpMult = 1.0 + Math.min(2.0, turboBar * 0.25);

                const boreScale = Math.max(0.72, Math.min(1.32, (this.config.bore || 86) / 86.0));
                const strokeScale = Math.max(0.72, Math.min(1.32, (this.config.stroke || 86) / 86.0));

                const cylR = 0.30 * boreScale;
                const crankR = 0.20 * strokeScale;
                const rodLen = 0.66 * strokeScale;
                const pistonH = 0.32 * boreScale;
                const cylLen = crankR * 2.0 + pistonH + 0.18;
                const deckDist = rodLen + crankR + pistonH * 0.55 + 0.05;

                const matPalettes = {{
                    'Alumínio':        {{ blk: [0.60, 0.65, 0.72, 1.0], hd: [0.40, 0.45, 0.52, 1.0], sp: [0.48, 36] }},
                    'Ferro Fundido':   {{ blk: [0.28, 0.30, 0.35, 1.0], hd: [0.24, 0.26, 0.31, 1.0], sp: [0.24, 18] }},
                    'Alumínio Billet': {{ blk: [0.74, 0.79, 0.86, 1.0], hd: [0.56, 0.62, 0.70, 1.0], sp: [0.78, 64] }},
                    'Forged':          {{ blk: [0.46, 0.50, 0.57, 1.0], hd: [0.35, 0.39, 0.46, 1.0], sp: [0.58, 44] }},
                    'Forged Heavy':    {{ blk: [0.34, 0.36, 0.40, 1.0], hd: [0.27, 0.29, 0.33, 1.0], sp: [0.46, 32] }},
                    'Billet':          {{ blk: [0.80, 0.84, 0.90, 1.0], hd: [0.62, 0.67, 0.74, 1.0], sp: [0.86, 76] }},
                    'Magnésio':        {{ blk: [0.50, 0.45, 0.39, 1.0], hd: [0.38, 0.35, 0.31, 1.0], sp: [0.42, 30] }},
                    'Titanium':        {{ blk: [0.62, 0.60, 0.58, 1.0], hd: [0.48, 0.47, 0.46, 1.0], sp: [0.70, 56] }},
                    'Titanium Billet': {{ blk: [0.70, 0.68, 0.65, 1.0], hd: [0.56, 0.55, 0.53, 1.0], sp: [0.88, 78] }},
                    'Titanium Forged': {{ blk: [0.54, 0.51, 0.52, 1.0], hd: [0.42, 0.40, 0.42, 1.0], sp: [0.66, 50] }}
                }};
                const matP = matPalettes[matOpt] || matPalettes['Alumínio'];
                const C_BLOCK   = matP.blk;
                const C_HEAD    = matP.hd;
                const BLK_SPEC  = matP.sp;
                const pistonPalettes = {{
                    'Alumínio':     {{ pis: [0.84, 0.87, 0.91, 1.0], rod: [0.46, 0.50, 0.56, 1.0] }},
                    'Forged':       {{ pis: [0.76, 0.80, 0.86, 1.0], rod: [0.52, 0.56, 0.62, 1.0] }},
                    'Forged Heavy': {{ pis: [0.48, 0.51, 0.56, 1.0], rod: [0.34, 0.37, 0.42, 1.0] }},
                    'Titânio':      {{ pis: [0.72, 0.67, 0.60, 1.0], rod: [0.64, 0.59, 0.52, 1.0] }}
                }};
                const pisP = pistonPalettes[pMatOpt] || pistonPalettes['Alumínio'];
                const C_HOSE    = [0.09, 0.11, 0.15, 1.0];
                const C_BRASS   = [0.82, 0.63, 0.24, 1.0];
                const C_DIP     = [0.92, 0.72, 0.10, 1.0];
                const C_VALVE   = [0.24, 0.30, 0.38, 1.0];
                const C_SUMP    = [0.22, 0.24, 0.29, 1.0];
                const C_LINER   = [0.50, 0.54, 0.60, 1.0];
                const C_PISTON  = pisP.pis;
                const C_RING    = [0.20, 0.23, 0.28, 1.0];
                const C_ROD     = pisP.rod;
                const C_CRANK   = [0.34, 0.37, 0.42, 1.0];
                const C_INTAKE  = intApp.col;
                const C_RUNNER  = intApp.runner;
                const C_EXHAUST = [0.58, 0.43, 0.32, 1.0];
                const C_PIPE    = [0.70, 0.74, 0.80, 1.0];
                const C_BELT    = [0.16, 0.18, 0.21, 1.0];
                const C_RAIL    = isDiesel ? [0.78, 0.65, 0.30, 1.0] : [0.68, 0.24, 0.24, 1.0];
                const C_ALT     = [0.52, 0.56, 0.62, 1.0];
                const C_FILTER  = [0.22, 0.35, 0.52, 1.0];
                const C_BOLT    = [0.76, 0.80, 0.85, 1.0];

                const firingPhases4 = [0, Math.PI, Math.PI, 0];
                const firingPhases6 = [0, (4 * Math.PI) / 3, (2 * Math.PI) / 3, (2 * Math.PI) / 3, (4 * Math.PI) / 3, 0];
                const getPhase = (idx, count) => {{
                    if (count === 4) return firingPhases4[idx];
                    if (count === 6) return firingPhases6[idx];
                    if (count === 3) return (idx * 2 * Math.PI) / 3;
                    if (count === 5) return ((idx * 2) % 5) * (2 * Math.PI / 5);
                    return ((idx * 3) % Math.max(1, count)) * ((2 * Math.PI) / Math.max(1, count));
                }};

                const cylSpecs = [];
                let halfLenX = 1.2;
                let maxSpanZ = 1.0;
                let exhaustAnchors = [];

                if (fmt === 'I' || fmt === 'VR') {{
                    const isVR = fmt === 'VR';
                    const stepX = isVR ? cylR * 1.65 : cylR * 2.38;
                    const startX = -((n - 1) * stepX) / 2;
                    halfLenX = Math.max(0.85, (n * stepX) * 0.5 + cylR * 0.45);
                    maxSpanZ = isVR ? cylR * 2.1 : cylR * 1.5;

                    for (let i = 0; i < n; i++) {{
                        const x = startX + i * stepX;
                        const sign = (i % 2 === 0) ? -1 : 1;
                        const angle = isVR ? sign * 0.19 : 0;
                        cylSpecs.push({{ x, zOff: 0, angle, phase: getPhase(i, n), bank: 0 }});
                    }}

                    const blockW = halfLenX * 2.04;
                    const blockZ = isVR ? cylR * 3.8 : cylR * 2.5;
                    // Cárter detalhado chanfrado + aletas de arrefecimento + parafusos do cárter + bujão em latão
                    this.addPart(this.staticOpaque, 'bevelBox', this.matTRS(0, -crankR - 0.14, 0, 0, 0, 0, blockW * 1.04, 0.10, blockZ * 1.04), C_SUMP, [0.44, 28]);
                    this.addPart(this.staticOpaque, 'bevelBox', this.matTRS(0, -crankR - 0.30, 0, 0, 0, 0, blockW * 0.96, 0.28, blockZ * 0.90), C_SUMP, [0.38, 22]);
                    this.addPart(this.staticOpaque, 'hex', this.matTRS(halfLenX * 0.60, -crankR - 0.43, 0, 0, 0, 0, 0.052, 0.05, 0.052), [0.80, 0.64, 0.28, 1.0], [0.74, 56]);
                    for (let f = -2; f <= 2; f++) {{
                        this.addPart(this.staticOpaque, 'bevelBox', this.matTRS(0, -crankR - 0.45, f * (blockZ * 0.16), 0, 0, 0, blockW * 0.88, 0.03, 0.03), C_BLOCK, [0.5, 32]);
                    }}

                    // Bloco esculpido chanfrado, saia do cárter, bosses dos cilindros e capas de mancal
                    const blockY = deckDist * 0.46;
                    const blockH = deckDist * 0.92;
                    const skirtBot = -crankR - 0.10;
                    const skirtH = 0.04 - skirtBot;
                    const skirtZ = Math.max(blockZ * 1.02, crankR * 2.55);
                    this.addPart(this.staticTrans, 'bevelBox', this.matTRS(0, blockY, 0, 0, 0, 0, blockW, blockH, blockZ * 0.94), C_BLOCK, BLK_SPEC);
                    this.addPart(this.staticTrans, 'bevelBox', this.matTRS(0, skirtBot + skirtH * 0.5, 0, 0, 0, 0, blockW * 1.01, skirtH, skirtZ), C_BLOCK, BLK_SPEC);
                    this.addPart(this.staticTrans, 'bevelBox', this.matTRS(halfLenX + 0.03, skirtBot + skirtH * 0.5, 0, 0, 0, 0, 0.06, skirtH, skirtZ * 0.98), C_BLOCK, BLK_SPEC);
                    // Nervuras laterais + relas de latão + bosses dos cilindros
                    for (const ribSide of [-1, 1]) {{
                        for (let rIdx = 0; rIdx < n; rIdx++) {{
                            const rx = cylSpecs[rIdx].x;
                            this.addPart(this.staticOpaque, 'bevelBox', this.matTRS(rx, blockY, ribSide * (blockZ * 0.49), 0, 0, 0, 0.044, blockH * 0.80, 0.040), C_BLOCK, BLK_SPEC);
                            this.addPart(this.staticOpaque, 'hex', this.matTRS(rx, deckDist + 0.415, ribSide * (blockZ * 0.34), 0, 0, 0, 0.032, 0.024, 0.032), C_BOLT, [0.78, 60]);
                            this.addPart(this.staticOpaque, 'hex', this.matTRS(rx, -crankR - 0.105, ribSide * (blockZ * 0.50), 0, 0, 0, 0.022, 0.036, 0.022), C_BOLT, [0.80, 62]);
                        }}
                    }}
                    // Termóstato frontal + mangueiras do radiador com abraçadeiras em inox
                    const thermX = -halfLenX - 0.18;
                    this.addPart(this.staticOpaque, 'cyl', this.matTRS(thermX, deckDist + 0.08, blockZ * 0.32, 0, 0, Math.PI * 0.5, 0.085, 0.15, 0.085), C_HEAD, [0.55, 38]);
                    this.addPart(this.staticOpaque, 'hex', this.matTRS(thermX - 0.06, deckDist + 0.14, blockZ * 0.32, 0, 0, 0, 0.028, 0.03, 0.028), C_BOLT, [0.8, 60]);
                    this.addPipe(this.staticOpaque, [[thermX - 0.06, deckDist + 0.08, blockZ * 0.32], [thermX - 0.24, deckDist + 0.06, blockZ * 0.48], [thermX - 0.34, deckDist - 0.10, blockZ * 0.56]], 0.048, C_HOSE, [0.16, 12]);
                    this.addPart(this.staticOpaque, 'cyl', this.matTRS(thermX - 0.11, deckDist + 0.07, blockZ * 0.37, 0, -0.68, Math.PI * 0.5, 0.056, 0.030, 0.056), C_PIPE, [0.82, 64]);
                    // Vareta de nível de óleo com pega amarela
                    this.addPipe(this.staticOpaque, [[halfLenX * 0.28, -0.22, blockZ * 0.54], [halfLenX * 0.34, deckDist * 0.48, blockZ * 0.62], [halfLenX * 0.36, deckDist + 0.16, blockZ * 0.58]], 0.015, C_PIPE, [0.75, 58]);
                    this.addPart(this.staticOpaque, 'torus', this.matTRS(halfLenX * 0.36, deckDist + 0.23, blockZ * 0.58, 0, 0, 0, 0.058, 0.058, 0.058), C_DIP, [0.42, 32]);
                    if (adm !== 'Atmosférico' && adm !== 'Supercompressor') {{
                        this.addPipe(this.staticOpaque, [[halfLenX * 0.12, 0.06, -blockZ * 0.54], [halfLenX * 0.04, deckDist * 0.52, -blockZ * 0.72], [-halfLenX * 0.18, deckDist * 0.54, -blockZ * 0.78]], 0.012, C_PIPE, [0.84, 66]);
                    }}
                    this.addPart(this.staticOpaque, 'bevelBox', this.matTRS(0, blockY - 0.10, blockZ * 0.48, 0, 0, 0, blockW * 0.96, 0.048, 0.050), C_BLOCK, [0.5, 32]);
                    this.addPart(this.staticOpaque, 'bevelBox', this.matTRS(0, blockY - 0.10, -blockZ * 0.48, 0, 0, 0, blockW * 0.96, 0.048, 0.050), C_BLOCK, [0.5, 32]);
                    for (let i = 0; i < n; i++) {{
                        const cx = cylSpecs[i].x;
                        const angC = cylSpecs[i].angle;
                        this.addPart(this.staticTrans, 'cyl', this.matTRS(cx, blockY, 0, angC, 0, 0, cylR * 1.15, blockH * 0.92, cylR * 1.15), C_BLOCK, BLK_SPEC);
                        this.addPart(this.staticOpaque, 'cyl', this.matTRS(cx, blockY, blockZ * 0.48, Math.PI * 0.5, 0, 0, 0.075, 0.032, 0.075), C_BRASS, [0.74, 58]);
                        this.addPart(this.staticOpaque, 'cyl', this.matTRS(cx, blockY, -blockZ * 0.48, Math.PI * 0.5, 0, 0, 0.075, 0.032, 0.075), C_BRASS, [0.74, 58]);
                        this.addPart(this.staticOpaque, 'bevelBox', this.matTRS(cx, -0.05, 0, 0, 0, 0, 0.12, 0.24, 0.28), C_CRANK, [0.48, 34]);
                    }}
                    // Filtro de óleo + sensor de pressão + motor de arranque traseiro
                    this.addPart(this.staticOpaque, 'cyl', this.matTRS(-halfLenX * 0.32, -0.06, blockZ * 0.64, 0.65, 0, 0, 0.12, 0.28, 0.12), C_FILTER, [0.55, 44]);
                    this.addPart(this.staticOpaque, 'cyl', this.matTRS(-halfLenX * 0.05, 0.08, blockZ * 0.55, Math.PI * 0.5, 0, 0, 0.032, 0.08, 0.032), C_BRASS, [0.74, 58]);
                    this.addStarterMotor(halfLenX * 0.62, -0.06, blockZ * 0.56 + 0.16);

                    // Cabeça + tampa de válvulas esculpida em dois túneis (DOHC) / torre central + respiro PCV (ou cabeça 2T sem válvulas)
                    this.addPart(this.staticTrans, 'bevelBox', this.matTRS(0, deckDist + 0.16, 0, 0, 0, 0, blockW * 1.01, 0.28, blockZ * 1.04), C_HEAD, [0.46, 36]);
                    if (is2Stroke) {{
                        this.addPart(this.staticOpaque, 'bevelBox', this.matTRS(0, deckDist + 0.30, 0, 0, 0, 0, blockW * 1.00, 0.06, blockZ * 0.96), C_HEAD, [0.56, 44]);
                        for (let i = 0; i < n; i++) {{
                            const cx = cylSpecs[i].x;
                            this.addPart(this.staticOpaque, 'bevelBox', this.matTRS(cx, deckDist + 0.34, 0, 0, 0, 0, 0.04, 0.045, blockZ * 0.90), C_BOLT, [0.70, 52]);
                            this.addCoilPackAndDetails(cx, deckDist + 0.36, 0, 0, isDiesel);
                        }}
                    }} else {{
                        this.addPart(this.staticOpaque, 'bevelBox', this.matTRS(0, deckDist + 0.36, 0, 0, 0, 0, blockW * 1.02, 0.11, blockZ * 1.02), C_VALVE, [0.58, 50]);
                        if (!isFreevalve && camMode === 'DOHC') {{
                            this.addPart(this.staticOpaque, 'bevelBox', this.matTRS(0, deckDist + 0.43, -blockZ * 0.26, 0, 0, 0, blockW * 0.99, 0.08, blockZ * 0.34), C_VALVE, [0.62, 54]);
                            this.addPart(this.staticOpaque, 'bevelBox', this.matTRS(0, deckDist + 0.43,  blockZ * 0.26, 0, 0, 0, blockW * 0.99, 0.08, blockZ * 0.34), C_VALVE, [0.62, 54]);
                        }} else if (!isFreevalve) {{
                            this.addPart(this.staticOpaque, 'bevelBox', this.matTRS(0, deckDist + 0.43, 0, 0, 0, 0, blockW * 0.98, 0.075, blockZ * 0.62), C_VALVE, [0.60, 52]);
                        }}
                        this.addPart(this.staticOpaque, 'bevelBox', this.matTRS(0, deckDist + 0.47, -blockZ * 0.26, 0, 0, 0, blockW * 0.90, 0.025, 0.055), C_BOLT, [0.74, 58]);
                        this.addPart(this.staticOpaque, 'bevelBox', this.matTRS(0, deckDist + 0.47,  blockZ * 0.26, 0, 0, 0, blockW * 0.90, 0.025, 0.055), C_BOLT, [0.74, 58]);
                        this.addPart(this.staticOpaque, 'cyl', this.matTRS(-halfLenX * 0.70, deckDist + 0.48, 0.12, 0, 0, 0, 0.092, 0.055, 0.092), C_BOLT, [0.78, 62]);
                    }}

                    // Distribuição DOHC / SOHC / OHV / Freevalve (ou 2T Reed Valve sem árvore de cames)
                    const camZIn = blockZ * 0.22;
                    const camZEx = -blockZ * 0.22;
                    const tx = -halfLenX - 0.24;
                    if (!is2Stroke) {{
                        this.addPart(this.staticOpaque, 'box', this.matTRS(0, deckDist + 0.46, 0.14, 0, 0, 0, blockW * 0.88, 0.04, 0.045), C_BELT, [0.25, 16]);
                    }}
                    if (is2Stroke) {{
                        // Motor 2T utiliza Reed Valve na admissão — sem árvores de cames nem polias de distribuição
                    }} else if (isFreevalve) {{
                        for (let i = 0; i < n; i++) {{
                            const c = cylSpecs[i];
                            this.addCoilPackAndDetails(c.x, deckDist + 0.45, 0, 0, isDiesel);
                        }}
                    }} else if (camMode === 'DOHC') {{
                        this.addPart(this.staticOpaque, 'cyl', this.matTRS(0, deckDist + 0.22, camZIn, 0, 0, Math.PI * 0.5, 0.046, blockW * 1.03, 0.046), C_CRANK, [0.65, 52]);
                        this.addPart(this.staticOpaque, 'cyl', this.matTRS(0, deckDist + 0.22, camZEx, 0, 0, Math.PI * 0.5, 0.046, blockW * 1.03, 0.046), C_CRANK, [0.65, 52]);
                        for (let i = 0; i < n; i++) {{
                            const c = cylSpecs[i];
                            this.dynamicCams.push({{ x: c.x, y: deckDist + 0.22, z: camZIn, phase: c.phase * 0.5 }});
                            this.dynamicCams.push({{ x: c.x, y: deckDist + 0.22, z: camZEx, phase: c.phase * 0.5 + 2.1 }});
                            this.addCoilPackAndDetails(c.x, deckDist + 0.45, 0, 0, isDiesel);
                            this.addPart(this.staticOpaque, 'box', this.matTRS(c.x + stepX * 0.45, deckDist + 0.23, 0, 0, 0, 0, 0.07, 0.08, blockZ * 0.62), C_HEAD, [0.5, 36]);
                        }}
                        const vvtColor = vType === 'VVT' ? [0.76, 0.60, 0.24, 1.0] : [0.26, 0.44, 0.64, 1.0];
                        this.dynamicRotors.push({{ type: 'pulley', cx: tx, cy: deckDist + 0.22, cz: camZEx, r: 0.21, thick: 0.075, speedMult: this.config.ciclo === '2T' ? 1.0 : 0.5, colorRim: [0.36, 0.41, 0.48, 1.0], colorHub: vvtColor }});
                        this.dynamicRotors.push({{ type: 'pulley', cx: tx, cy: deckDist + 0.22, cz: camZIn, r: 0.21, thick: 0.075, speedMult: this.config.ciclo === '2T' ? 1.0 : 0.5, colorRim: [0.36, 0.41, 0.48, 1.0], colorHub: vvtColor }});
                    }} else if (camMode === 'SOHC') {{
                        this.addPart(this.staticOpaque, 'cyl', this.matTRS(0, deckDist + 0.23, 0, 0, 0, Math.PI * 0.5, 0.055, blockW * 1.03, 0.055), C_CRANK, [0.65, 52]);
                        for (let i = 0; i < n; i++) {{
                            const c = cylSpecs[i];
                            this.dynamicCams.push({{ x: c.x, y: deckDist + 0.23, z: 0, phase: c.phase * 0.5 }});
                            this.addCoilPackAndDetails(c.x, deckDist + 0.45, 0, 0, isDiesel);
                            this.addPart(this.staticOpaque, 'box', this.matTRS(c.x + stepX * 0.45, deckDist + 0.23, 0, 0, 0, 0, 0.07, 0.08, blockZ * 0.46), C_HEAD, [0.5, 36]);
                        }}
                        const vvtColor = vType === 'VVT' ? [0.76, 0.60, 0.24, 1.0] : [0.26, 0.44, 0.64, 1.0];
                        this.dynamicRotors.push({{ type: 'pulley', cx: tx, cy: deckDist + 0.23, cz: 0, r: 0.25, thick: 0.08, speedMult: this.config.ciclo === '2T' ? 1.0 : 0.5, colorRim: [0.36, 0.41, 0.48, 1.0], colorHub: vvtColor }});
                    }} else {{
                        // OHV (Cam-in-block + Pushrod tubes + Rocker shaft)
                        const ohvY = deckDist * 0.36;
                        const ohvZ = blockZ * 0.28;
                        this.addPart(this.staticOpaque, 'cyl', this.matTRS(0, ohvY, ohvZ, 0, 0, Math.PI * 0.5, 0.052, blockW * 1.02, 0.052), C_CRANK, [0.65, 52]);
                        this.addPart(this.staticOpaque, 'cyl', this.matTRS(0, deckDist + 0.24, 0, 0, 0, Math.PI * 0.5, 0.036, blockW * 0.94, 0.036), C_BOLT, [0.7, 56]);
                        for (let i = 0; i < n; i++) {{
                            const c = cylSpecs[i];
                            this.dynamicCams.push({{ x: c.x, y: ohvY, z: ohvZ, phase: c.phase * 0.5 }});
                            this.addPipe(this.staticOpaque, [[c.x - 0.05, ohvY, ohvZ], [c.x - 0.05, deckDist + 0.23, ohvZ * 0.5]], 0.022, C_PIPE, [0.75, 58]);
                            this.addPipe(this.staticOpaque, [[c.x + 0.05, ohvY, ohvZ], [c.x + 0.05, deckDist + 0.23, -ohvZ * 0.3]], 0.022, C_PIPE, [0.75, 58]);
                            this.addCoilPackAndDetails(c.x, deckDist + 0.45, 0, 0, isDiesel);
                        }}
                        this.dynamicRotors.push({{ type: 'pulley', cx: tx, cy: ohvY, cz: ohvZ, r: 0.20, thick: 0.075, speedMult: this.config.ciclo === '2T' ? 1.0 : 0.5, colorRim: [0.36, 0.41, 0.48, 1.0], colorHub: [0.72, 0.48, 0.26, 1.0] }});
                    }}
                    // Bomba de água / polia tensora + bomba alta pressão (Diesel)
                    const wpY = deckDist * 0.52;
                    this.addPart(this.staticOpaque, 'cyl', this.matTRS(-halfLenX * 0.85, wpY, -blockZ * 0.22, 0, 0, Math.PI * 0.5, 0.15, 0.22, 0.15), C_HEAD, [0.55, 44]);
                    this.dynamicRotors.push({{
                        type: 'pulley', cx: tx, cy: wpY, cz: -blockZ * 0.22,
                        r: 0.13, thick: 0.07, speedMult: 1.35,
                        colorRim: [0.46, 0.50, 0.56, 1.0], colorHub: [0.68, 0.72, 0.78, 1.0]
                    }});
                    if (isDiesel) {{
                        this.addPart(this.staticOpaque, 'box', this.matTRS(-halfLenX * 0.66, deckDist * 0.74, blockZ * 0.55, 0, 0, 0, 0.24, 0.22, 0.20), [0.54, 0.58, 0.64, 1.0], [0.6, 46]);
                    }}
                    // Alternador lateral + polia do alternador
                    const altZ = blockZ * 0.56 + 0.16;
                    const altY = 0.26;
                    this.addPart(this.staticOpaque, 'cyl', this.matTRS(-halfLenX * 0.62, altY, altZ, 0, 0, Math.PI * 0.5, 0.18, 0.34, 0.18), C_ALT, [0.6, 48]);
                    this.dynamicRotors.push({{
                        type: 'pulley', cx: tx, cy: altY, cz: altZ,
                        r: 0.12, thick: 0.07, speedMult: 1.8,
                        colorRim: [0.46, 0.50, 0.56, 1.0], colorHub: [0.76, 0.80, 0.86, 1.0]
                    }});
                    if (is2Stroke || isFreevalve) {{
                        this.addPipe(this.staticOpaque, [
                            [tx, 0, -0.25],
                            [tx, wpY, -blockZ * 0.22 - 0.12],
                            [tx, wpY + 0.10, -blockZ * 0.22],
                            [tx, altY + 0.08, altZ],
                            [tx, altY - 0.08, altZ],
                            [tx, -0.25, 0],
                            [tx, 0, -0.25]
                        ], 0.026, C_BELT, [0.15, 10]);
                    }} else if (camMode === 'DOHC') {{
                        this.addPipe(this.staticOpaque, [
                            [tx, 0, -0.25],
                            [tx, wpY, -blockZ * 0.22 - 0.12],
                            [tx, deckDist + 0.22, camZEx - 0.18],
                            [tx, deckDist + 0.42, camZEx],
                            [tx, deckDist + 0.42, camZIn],
                            [tx, deckDist + 0.22, camZIn + 0.18],
                            [tx, altY + 0.06, altZ + 0.08],
                            [tx, altY - 0.08, altZ],
                            [tx, -0.25, 0],
                            [tx, 0, -0.25]
                        ], 0.028, C_BELT, [0.15, 10]);
                    }} else if (camMode === 'SOHC') {{
                        this.addPipe(this.staticOpaque, [
                            [tx, 0, -0.25],
                            [tx, wpY, -blockZ * 0.22 - 0.12],
                            [tx, deckDist + 0.23, -0.23],
                            [tx, deckDist + 0.47, 0],
                            [tx, deckDist + 0.23, 0.23],
                            [tx, altY + 0.06, altZ + 0.08],
                            [tx, altY - 0.08, altZ],
                            [tx, -0.25, 0],
                            [tx, 0, -0.25]
                        ], 0.028, C_BELT, [0.15, 10]);
                    }} else {{
                        const ohvY = deckDist * 0.36;
                        const ohvZ = blockZ * 0.28;
                        this.addPipe(this.staticOpaque, [
                            [tx, 0, -0.25],
                            [tx, wpY, -blockZ * 0.22 - 0.12],
                            [tx, ohvY + 0.18, ohvZ],
                            [tx, altY + 0.06, altZ + 0.08],
                            [tx, altY - 0.08, altZ],
                            [tx, -0.25, 0],
                            [tx, 0, -0.25]
                        ], 0.028, C_BELT, [0.15, 10]);
                    }}

                    // Admissão, rampa de injeção, injetores e coletores de escape com flanges
                    const intZ = blockZ * 0.5 + 0.48;
                    const exhZ = -(blockZ * 0.5 + 0.46);
                    const portY = deckDist + 0.15;

                    for (let i = 0; i < n; i++) {{
                        const cx = cylSpecs[i].x;
                        if (is2Stroke) {{
                            this.addReedValveCage(cx, portY + 0.02, blockZ * 0.50, 'z+', boreScale, 0);
                        }}
                        this.addPipe(this.staticOpaque, [
                            [cx, portY, blockZ * 0.45],
                            [cx, portY + 0.11, intZ * 0.84],
                            [cx, portY + 0.02, intZ]
                        ], 0.072 * boreScale, C_RUNNER, intApp.rSpec);
                        // Injetor de combustível
                        this.addPart(this.staticOpaque, 'cyl', this.matTRS(cx, portY + 0.16, blockZ * 0.58, -0.45, 0, 0, 0.028, 0.14, 0.028), C_BOLT, [0.6, 48]);
                        // Escape com flange
                        this.addPart(this.staticOpaque, 'box', this.matTRS(cx, portY, -blockZ * 0.50, 0, 0, 0, 0.16, 0.14, 0.05), C_EXHAUST, [0.45, 32]);
                        this.addPipe(this.staticOpaque, [
                            [cx, portY, -blockZ * 0.48],
                            [cx, portY - 0.08, exhZ * 0.88],
                            [cx, portY - 0.42, exhZ]
                        ], 0.068 * boreScale, C_EXHAUST, [0.4, 28]);
                    }}
                    // Rampa de injeção (Fuel rail)
                    this.addPart(this.staticOpaque, 'cyl', this.matTRS(0, portY + 0.23, blockZ * 0.62, 0, 0, Math.PI * 0.5, 0.042, halfLenX * 1.85, 0.042), C_RAIL, [0.65, 52]);
                    // Coletor de escape + cone de união + tubo de saída
                    this.addPart(this.staticOpaque, 'cyl', this.matTRS(0, portY - 0.44, exhZ, 0, 0, Math.PI * 0.5, 0.115, halfLenX * 1.92, 0.115), C_EXHAUST, [0.4, 28]);
                    this.addPart(this.staticOpaque, 'cone', this.matTRS(halfLenX * 0.96, portY - 0.44, exhZ, 0, 0, -Math.PI * 0.5, 0.145, 0.18, 0.145), C_EXHAUST, [0.48, 36]);
                    this.addPipe(this.staticOpaque, [[halfLenX * 1.02, portY - 0.44, exhZ], [halfLenX + 0.38, portY - 0.58, exhZ], [halfLenX + 0.65, -0.15, exhZ * 0.9]], 0.10, C_EXHAUST, [0.4, 28]);
                    if (isVR && viewMode === 'all' && (adm === 'Atmosférico' || adm === 'Supercompressor')) {{
                        this.addPipe(this.staticOpaque, [[halfLenX * 0.65, portY - 0.44, exhZ], [halfLenX + 0.30, -0.36, -0.88], [halfLenX + 0.65, -0.36, -0.88]], 0.085, C_EXHAUST, [0.4, 28]);
                        exhaustAnchors = [
                            [halfLenX + 0.65, -0.36, -0.88],
                            [halfLenX + 0.65, -0.15, exhZ * 0.9]
                        ];
                    }} else {{
                        exhaustAnchors = [[halfLenX + 0.65, -0.15, exhZ * 0.9]];
                    }}

                    const plenumW = halfLenX * 1.88;
                    const runnersX = cylSpecs.map(c => c.x);
                    if (adm === 'Atmosférico') {{
                        this.addSideIntakeAssembly({{ halfLenX, py: portY + 0.02, pz: intZ + 0.10, plenumW, runnersX, feedDirX: -1, isBoosted: false, intType, app: intApp, boreScale }});
                    }} else if (adm === 'Turbo') {{
                        this.addSideIntakeAssembly({{ halfLenX, py: portY + 0.02, pz: intZ + 0.10, plenumW, runnersX, feedDirX: -1, isBoosted: true, intType, app: intApp, boreScale }});
                        const t = this.addTurboUnit(-0.1, portY - 0.45, exhZ - 0.44, 1.05, -1);
                        exhaustAnchors = [t.downpipeOut];
                        const icX = -halfLenX - 1.15;
                        this.addIntercooler(icX, 0.05, 0, 0.24, 0.72, 1.25);
                        this.addPipe(this.staticOpaque, [t.compOut, [t.compOut[0] - 0.25, 0.25, exhZ - 0.45], [icX, 0.15, -0.58]], 0.075, C_PIPE, [0.62, 52], [0, 1]);
                        this.addPipe(this.staticOpaque, [[icX, 0.15, 0.58], [icX + 0.3, portY + 0.02, intZ + 0.10], [-halfLenX * 0.94, portY + 0.02, intZ + 0.10]], 0.08, C_PIPE, [0.62, 52], [0, 1]);
                    }} else if (adm === 'Supercompressor') {{
                        this.addSuperchargerUnit(0, deckDist + 0.68, 0.05, halfLenX * 1.55, 0.58, -halfLenX - 0.24, intApp, intType);
                        this.addPipe(this.staticOpaque, [[halfLenX * 0.78, deckDist + 0.68, 0.05], [halfLenX + 0.28, deckDist + 0.68, 0.05]], 0.11, C_PIPE, [0.62, 52], [0]);
                        if (intType === 'Cold Air Intake') {{
                            this.addPart(this.staticTrans, 'bevelBox', this.matTRS(halfLenX + 0.50, deckDist + 0.68, 0.05, 0, 0, 0, 0.54, 0.54, 0.54), intApp.col, intApp.spec);
                        }}
                        this.addConeFilter(halfLenX + 0.50, deckDist + 0.68, 0.05, 1);
                    }} else if (adm === 'Biturbo') {{
                        this.addSideIntakeAssembly({{ halfLenX, py: portY + 0.02, pz: intZ + 0.10, plenumW, runnersX, feedDirX: -1, isBoosted: true, intType, app: intApp, boreScale }});
                        const isSeq = turboCfg === 'Sequencial';
                        const t1 = this.addTurboUnit(-halfLenX * 0.45, portY - 0.45, exhZ - 0.44, isSeq ? 0.78 : 0.92, -1, isSeq ? 'primary' : 'all');
                        const t2 = this.addTurboUnit(halfLenX * 0.45, portY - 0.45, exhZ - 0.44, isSeq ? 1.12 : 0.92, -1, isSeq ? 'secondary' : 'all');
                        exhaustAnchors = [t2.downpipeOut];
                        const icX = -halfLenX - 1.15;
                        this.addIntercooler(icX, 0.05, 0, 0.24, 0.74, 1.35);
                        if (isSeq) {{
                            this.addSequentialCrossover(t1.turbOut, [t2.chra[0] - 0.12, t2.chra[1], t2.chra[2] + 0.08], -0.14, 0.056);
                            this.addPipe(this.staticOpaque, [t1.compOut, [icX + 0.35, 0.18, exhZ - 0.35], [icX, 0.15, -0.62]], 0.064, C_PIPE, [0.62, 52], [0, 1]);
                            this.addPipe(this.staticOpaque, [t2.compOut, [t1.compOut[0], 0.32, exhZ - 0.56], [icX, 0.25, -0.62]], 0.072, C_PIPE, [0.62, 52], [0, 1]);
                        }} else {{
                            this.addPipe(this.staticOpaque, [t1.compOut, [icX + 0.35, 0.18, exhZ - 0.35], [icX, 0.15, -0.62]], 0.068, C_PIPE, [0.62, 52], [0, 1]);
                            this.addPipe(this.staticOpaque, [t2.compOut, [t1.compOut[0], 0.35, exhZ - 0.55], [icX, 0.25, -0.62]], 0.064, C_PIPE, [0.62, 52], [0, 1]);
                        }}
                        this.addPipe(this.staticOpaque, [[icX, 0.15, 0.62], [icX + 0.3, portY + 0.02, intZ + 0.10], [-halfLenX * 0.94, portY + 0.02, intZ + 0.10]], 0.082, C_PIPE, [0.62, 52], [0, 1]);
                    }} else if (adm === 'Quad Turbo') {{
                        this.addSideIntakeAssembly({{ halfLenX, py: portY + 0.02, pz: intZ + 0.10, plenumW, runnersX, feedDirX: -1, isBoosted: true, intType, app: intApp, boreScale }});
                        const icX = -halfLenX - 1.18;
                        this.addIntercooler(icX, 0.05, 0, 0.26, 0.78, 1.48);
                        const isSeq = turboCfg === 'Sequencial';
                        const qXs = [-0.72 * halfLenX, -0.24 * halfLenX, 0.24 * halfLenX, 0.72 * halfLenX];
                        const qUnits = [];
                        for (let qi = 0; qi < qXs.length; qi++) {{
                            const stg = isSeq ? (qi % 2 === 0 ? 'primary' : 'secondary') : 'all';
                            const qScale = isSeq ? (qi % 2 === 0 ? 0.60 : 0.86) : 0.72;
                            const qt = this.addTurboUnit(qXs[qi], portY - 0.45, exhZ - 0.42, qScale, -1, stg);
                            qUnits.push(qt);
                            this.addPipe(this.staticOpaque, [qt.compOut, [icX + 0.36, 0.15 + qi * 0.05, exhZ - 0.46], [icX, 0.15 + qi * 0.04, -0.64]], 0.048, C_PIPE, [0.62, 52], [0, 1]);
                        }}
                        exhaustAnchors = [qUnits[3].downpipeOut];
                        if (isSeq) {{
                            this.addSequentialCrossover(qUnits[0].turbOut, qUnits[1].chra, -0.10, 0.040);
                            this.addSequentialCrossover(qUnits[2].turbOut, qUnits[3].chra, -0.10, 0.040);
                        }}
                        this.addPipe(this.staticOpaque, [[icX, 0.15, 0.64], [icX + 0.3, portY + 0.02, intZ + 0.10], [-halfLenX * 0.94, portY + 0.02, intZ + 0.10]], 0.088, C_PIPE, [0.62, 52], [0, 1]);
                    }} else {{
                        this.addSuperchargerUnit(0, deckDist + 0.68, 0.05, halfLenX * 1.55, 0.58, -halfLenX - 0.24, intApp, intType);
                        const t = this.addTurboUnit(0.15, portY - 0.45, exhZ - 0.44, 1.0, -1);
                        exhaustAnchors = [t.downpipeOut];
                        const icX = -halfLenX - 1.15;
                        this.addIntercooler(icX, 0.05, 0, 0.24, 0.72, 1.25);
                        this.addPipe(this.staticOpaque, [t.compOut, [icX + 0.4, 0.22, exhZ - 0.42], [icX, 0.15, -0.58]], 0.072, C_PIPE, [0.62, 52], [0, 1]);
                        this.addPipe(this.staticOpaque, [[icX, 0.15, 0.58], [icX + 0.25, deckDist + 0.68, 0.65], [halfLenX * 0.85, deckDist + 0.68, 0.65], [halfLenX * 0.85, deckDist + 0.68, 0.05], [halfLenX * 0.76, deckDist + 0.68, 0.05]], 0.076, C_PIPE, [0.62, 52], [0, 2]);
                    }}
                }} else if (fmt === 'B') {{
                    const nBankA = Math.ceil(n / 2);
                    const nBankB = Math.floor(n / 2);
                    const cols = Math.max(1, nBankA, nBankB);
                    const stepX = cylR * 2.45;
                    const startX = -((cols - 1) * stepX) / 2;
                    halfLenX = Math.max(0.88, (cols * stepX) * 0.5 + cylR * 0.55);
                    maxSpanZ = deckDist + 0.78;

                    for (let i = 0; i < nBankA; i++) {{
                        const x = startX + i * stepX - stepX * 0.14;
                        cylSpecs.push({{ x, zOff: 0, angle: -Math.PI * 0.5, phase: getPhase(i, nBankA), bank: -1 }});
                    }}
                    for (let i = 0; i < nBankB; i++) {{
                        const x = startX + i * stepX + stepX * 0.14;
                        cylSpecs.push({{ x, zOff: 0, angle: Math.PI * 0.5, phase: getPhase(i, nBankB) + Math.PI, bank: 1 }});
                    }}

                    const blockW = halfLenX * 2.04;
                    const bankH = cylR * 2.35;
                    const crankCaseZ = crankR * 2.6;

                    // Cárter central horizontal reforçado + cárter de óleo inferior + aletas + filtro frontal superior
                    const bCaseZ = Math.max(crankCaseZ, crankR * 2.65);
                    this.addPart(this.staticTrans, 'bevelBox', this.matTRS(0, -0.02, 0, 0, 0, 0, blockW * 1.01, bankH * 1.06, bCaseZ), C_BLOCK, BLK_SPEC);
                    this.addPart(this.staticOpaque, 'bevelBox', this.matTRS(0, bankH * 0.50, 0, 0, 0, 0, blockW * 0.96, 0.08, bCaseZ * 0.94), C_HEAD, [0.46, 36]);
                    this.addPart(this.staticOpaque, 'bevelBox', this.matTRS(0, -bankH * 0.54, 0, 0, 0, 0, blockW * 0.98, 0.11, bCaseZ * 1.08), C_SUMP, [0.4, 24]);
                    this.addPart(this.staticOpaque, 'bevelBox', this.matTRS(0, -bankH * 0.70, 0, 0, 0, 0, blockW * 0.88, 0.24, bCaseZ * 0.92), C_SUMP, [0.35, 20]);
                    for (let f = -2; f <= 2; f++) {{
                        this.addPart(this.staticOpaque, 'bevelBox', this.matTRS(0, -bankH * 0.83, f * 0.11, 0, 0, 0, blockW * 0.80, 0.03, 0.03), C_BLOCK, [0.5, 32]);
                    }}
                    this.addPart(this.staticOpaque, 'cyl', this.matTRS(-halfLenX * 0.62, bankH * 0.56, bCaseZ * 0.42, 0.2, 0, 0, 0.11, 0.24, 0.11), C_FILTER, [0.55, 44]);

                    // Bancadas horizontais opostas (-Z e +Z)
                    const vvtColorB = vType === 'VVT' ? [0.76, 0.60, 0.24, 1.0] : [0.26, 0.44, 0.64, 1.0];
                    for (const side of [-1, 1]) {{
                        const ang = side * Math.PI * 0.5;
                        const blockMidZ = side * deckDist * 0.48;
                        this.addPart(this.staticTrans, 'bevelBox', this.matTRS(0, 0, blockMidZ, ang, 0, 0, blockW, deckDist * 0.88, bankH * 0.94), C_BLOCK, BLK_SPEC);
                        this.addPart(this.staticTrans, 'bevelBox', this.matTRS(0, 0, side * (deckDist + 0.14), ang, 0, 0, blockW * 1.01, 0.26, bankH * 1.04), C_HEAD, [0.45, 36]);
                        for (const boltSide of [-1, 1]) {{
                            for (const c of cylSpecs) {{
                                this.addPart(this.staticOpaque, 'hex', this.matTRS(c.x, boltSide * bankH * 0.36, side * (deckDist + 0.39), ang, 0, 0, 0.028, 0.022, 0.028), C_BOLT, [0.78, 60]);
                            }}
                        }}
                        this.addPart(this.staticOpaque, 'bevelBox', this.matTRS(0, 0, side * (deckDist + 0.35), ang, 0, 0, blockW * 1.02, 0.11, bankH * 1.02), C_VALVE, [0.58, 50]);
                        if (!is2Stroke && !isFreevalve && camMode === 'DOHC') {{
                            for (const cyOff of [-bankH * 0.26, bankH * 0.26]) {{
                                this.addPart(this.staticOpaque, 'bevelBox', this.matTRS(0, cyOff, side * (deckDist + 0.42), ang, 0, 0, blockW * 0.98, 0.075, bankH * 0.34), C_VALVE, [0.62, 54]);
                            }}
                        }}
                        this.addPart(this.staticOpaque, 'bevelBox', this.matTRS(0, 0, side * (deckDist + 0.425), ang, 0, 0, blockW * 0.90, 0.03, bankH * 0.26), C_BOLT, [0.7, 54]);

                        const camZ = side * (deckDist + 0.20);
                        if (is2Stroke || isFreevalve) {{
                            // 2T Reed Valve / Freevalve: sem árvore de cames na bancada
                        }} else if (camMode === 'DOHC') {{
                            for (const cyOff of [-0.11, 0.11]) {{
                                this.addPart(this.staticOpaque, 'cyl', this.matTRS(0, cyOff, camZ, 0, 0, Math.PI * 0.5, 0.044, blockW * 1.03, 0.044), C_CRANK, [0.65, 52]);
                                this.dynamicRotors.push({{ type: 'pulley', cx: -halfLenX - 0.24, cy: cyOff, cz: camZ, r: 0.16, thick: 0.07, speedMult: this.config.ciclo === '2T' ? 1.0 : 0.5, colorRim: [0.36, 0.41, 0.48, 1.0], colorHub: vvtColorB }});
                            }}
                        }} else if (camMode === 'SOHC') {{
                            this.addPart(this.staticOpaque, 'cyl', this.matTRS(0, 0, camZ, 0, 0, Math.PI * 0.5, 0.052, blockW * 1.03, 0.052), C_CRANK, [0.65, 52]);
                            this.dynamicRotors.push({{ type: 'pulley', cx: -halfLenX - 0.24, cy: 0, cz: camZ, r: 0.22, thick: 0.08, speedMult: this.config.ciclo === '2T' ? 1.0 : 0.5, colorRim: [0.36, 0.41, 0.48, 1.0], colorHub: vvtColorB }});
                        }} else {{
                            this.addPart(this.staticOpaque, 'cyl', this.matTRS(0, 0, camZ, 0, 0, Math.PI * 0.5, 0.036, blockW * 0.94, 0.036), C_BOLT, [0.7, 54]);
                        }}
                    }}
                    // Bocal superior de enchimento de óleo Boxer + ponte frontal de refrigeração
                    this.addPart(this.staticOpaque, 'cyl', this.matTRS(-halfLenX * 0.38, bankH * 0.54, -0.18, 0.18, 0, 0, 0.068, 0.16, 0.056), C_HOSE, [0.22, 16]);
                    this.addPart(this.staticOpaque, 'hex', this.matTRS(-halfLenX * 0.38, bankH * 0.63, -0.20, 0.18, 0, 0, 0.078, 0.036, 0.078), C_DIP, [0.42, 32]);
                    this.addPipe(this.staticOpaque, [[-halfLenX - 0.06, -0.16, -deckDist - 0.10], [-halfLenX - 0.06, -0.28, 0], [-halfLenX - 0.06, -0.16, deckDist + 0.10]], 0.042, C_PIPE, [0.78, 60]);
                    if (!is2Stroke && !isFreevalve && camMode === 'OHV') {{
                        this.addPart(this.staticOpaque, 'cyl', this.matTRS(0, 0.24, 0, 0, 0, Math.PI * 0.5, 0.052, blockW * 1.02, 0.052), C_CRANK, [0.65, 52]);
                        this.dynamicRotors.push({{ type: 'pulley', cx: -halfLenX - 0.24, cy: 0.24, cz: 0, r: 0.18, thick: 0.07, speedMult: this.config.ciclo === '2T' ? 1.0 : 0.5, colorRim: [0.36, 0.41, 0.48, 1.0], colorHub: [0.72, 0.48, 0.26, 1.0] }});
                    }}

                    // Motor de arranque traseiro + capas de mancal + cames/varetas + bobinas/injetores Boxer
                    this.addStarterMotor(halfLenX * 0.62, bankH * 0.48 + 0.14, 0.24);
                    for (const c of cylSpecs) {{
                        if (!is2Stroke && !isFreevalve) {{
                            if (camMode === 'OHV') {{
                                this.dynamicCams.push({{ x: c.x, y: 0.24, z: 0, phase: c.phase * 0.5 }});
                                this.addPipe(this.staticOpaque, [[c.x, 0.24, 0], [c.x, 0, (deckDist + 0.20) * Math.sin(c.angle)]], 0.020, C_PIPE, [0.75, 58]);
                            }} else if (camMode === 'DOHC') {{
                                const camD = deckDist + 0.20;
                                this.dynamicCams.push({{ x: c.x, y: -0.11, z: camD * Math.sin(c.angle), phase: c.phase * 0.5 }});
                                this.dynamicCams.push({{ x: c.x, y:  0.11, z: camD * Math.sin(c.angle), phase: c.phase * 0.5 + 2.1 }});
                            }} else {{
                                const camD = deckDist + 0.20;
                                this.dynamicCams.push({{ x: c.x, y: 0, z: camD * Math.sin(c.angle), phase: c.phase * 0.5 }});
                            }}
                        }}
                        this.addCoilPackAndDetails(c.x, deckDist + 0.43, 0, c.angle, isDiesel);
                        this.addPart(this.staticOpaque, 'box', this.matTRS(c.x, -0.05, 0, 0, 0, 0, 0.11, 0.22, 0.26), C_CRANK, [0.48, 34]);
                    }}

                    // Correia dentada horizontal Boxer + alternador superior
                    const tx = -halfLenX - 0.24;
                    const camZOut = deckDist + 0.20;
                    const altY = bankH * 0.56 + 0.12;
                    this.addPart(this.staticOpaque, 'cyl', this.matTRS(-halfLenX * 0.55, altY, -0.18, 0, 0, Math.PI * 0.5, 0.16, 0.30, 0.16), C_ALT, [0.6, 48]);
                    this.dynamicRotors.push({{
                        type: 'pulley',
                        cx: tx, cy: altY, cz: -0.18,
                        r: 0.11, thick: 0.07, speedMult: 1.8,
                        colorRim: [0.46, 0.50, 0.56, 1.0],
                        colorHub: [0.76, 0.80, 0.86, 1.0]
                    }});
                    if (is2Stroke || isFreevalve) {{
                        this.addPipe(this.staticOpaque, [
                            [tx, -0.24, 0],
                            [tx, 0, -0.24],
                            [tx, altY + 0.07, -0.18],
                            [tx, 0, 0.24],
                            [tx, -0.24, 0]
                        ], 0.026, C_BELT, [0.15, 10]);
                    }} else if (camMode === 'OHV') {{
                        this.addPipe(this.staticOpaque, [
                            [tx, -0.24, 0],
                            [tx, 0.24, -0.16],
                            [tx, altY + 0.07, -0.18],
                            [tx, 0.24, 0.16],
                            [tx, -0.24, 0]
                        ], 0.028, C_BELT, [0.15, 10]);
                    }} else {{
                        this.addPipe(this.staticOpaque, [
                            [tx, -0.24, 0],
                            [tx, -0.18, -camZOut],
                            [tx, 0, -camZOut - 0.20],
                            [tx, 0.18, -camZOut],
                            [tx, altY + 0.07, -0.18],
                            [tx, 0.20, camZOut],
                            [tx, 0, camZOut + 0.20],
                            [tx, -0.18, camZOut],
                            [tx, -0.24, 0]
                        ], 0.028, C_BELT, [0.15, 10]);
                    }}

                    // Escapes inferiores Boxer (sob as cabeças)
                    const exhY = -bankH * 0.55 - 0.34;
                    const exhZOut = deckDist * 0.72;
                    for (const c of cylSpecs) {{
                        const portZ = c.bank * (deckDist + 0.10);
                        this.addPipe(this.staticOpaque, [
                            [c.x, -bankH * 0.46, portZ],
                            [c.x, exhY + 0.08, c.bank * (exhZOut + 0.14)],
                            [c.x, exhY, c.bank * exhZOut]
                        ], 0.062 * boreScale, C_EXHAUST, [0.4, 28]);
                    }}
                    this.addPart(this.staticOpaque, 'cyl', this.matTRS(0, exhY, -exhZOut, 0, 0, Math.PI * 0.5, 0.105, halfLenX * 1.9, 0.105), C_EXHAUST, [0.4, 28]);
                    this.addPart(this.staticOpaque, 'cyl', this.matTRS(0, exhY,  exhZOut, 0, 0, Math.PI * 0.5, 0.105, halfLenX * 1.9, 0.105), C_EXHAUST, [0.4, 28]);
                    if (viewMode === 'all' && (adm === 'Atmosférico' || adm === 'Supercompressor')) {{
                        exhaustAnchors = [[halfLenX * 0.90, exhY, -exhZOut], [halfLenX * 0.90, exhY, exhZOut]];
                    }} else {{
                        this.addPipe(this.staticOpaque, [
                            [halfLenX * 0.90, exhY, -exhZOut],
                            [halfLenX + 0.35, exhY - 0.05, 0],
                            [halfLenX * 0.90, exhY, exhZOut]
                        ], 0.095, C_EXHAUST, [0.4, 28]);
                        exhaustAnchors = [[halfLenX + 0.35, exhY - 0.05, 0]];
                    }}

                    // Admissão superior aranha (spider) + rampas de injeção
                    const intTopY = bankH * 0.52 + 0.46;
                    const plenumW = halfLenX * 1.82;
                    for (const c of cylSpecs) {{
                        const portZ = c.bank * (deckDist + 0.06);
                        if (is2Stroke) {{
                            this.addReedValveCage(c.x, bankH * 0.45, portZ, 'y+', boreScale, 0);
                        }}
                        this.addPipe(this.staticOpaque, [
                            [c.x, bankH * 0.45, portZ],
                            [c.x, intTopY - 0.08, c.bank * (deckDist * 0.48)],
                            [c.x, intTopY, 0]
                        ], 0.064 * boreScale, C_RUNNER, intApp.rSpec);
                    }}
                    this.addPart(this.staticOpaque, 'cyl', this.matTRS(0, bankH * 0.52 + 0.08, -deckDist * 0.78, 0, 0, Math.PI * 0.5, 0.036, plenumW * 0.94, 0.036), C_RAIL, [0.65, 52]);
                    this.addPart(this.staticOpaque, 'cyl', this.matTRS(0, bankH * 0.52 + 0.08,  deckDist * 0.78, 0, 0, Math.PI * 0.5, 0.036, plenumW * 0.94, 0.036), C_RAIL, [0.65, 52]);

                    if (adm === 'Atmosférico') {{
                        this.addValleyIntakeAssembly({{ halfLenX, topY: intTopY + 0.12, plenumW, cylSpecs, isBoosted: false, intType, app: intApp, boreScale }});
                    }} else if (adm === 'Turbo') {{
                        this.addValleyIntakeAssembly({{ halfLenX, topY: intTopY + 0.12, plenumW, cylSpecs, isBoosted: true, intType, app: intApp, boreScale }});
                        const t = this.addTurboUnit(0, exhY - 0.04, -exhZOut - 0.36, 1.02, -1);
                        exhaustAnchors = [t.downpipeOut];
                        const icX = -halfLenX - 1.18;
                        this.addIntercooler(icX, 0.08, 0, 0.24, 0.72, 1.38);
                        this.addPipe(this.staticOpaque, [t.compOut, [icX + 0.35, 0.12, -exhZOut - 0.28], [icX, 0.12, -0.62]], 0.076, C_PIPE, [0.62, 52], [0, 1]);
                        this.addPipe(this.staticOpaque, [[icX, 0.12, 0.62], [icX + 0.30, intTopY + 0.12, 0.36], [-halfLenX * 0.90, intTopY + 0.12, 0]], 0.082, C_PIPE, [0.62, 52], [0, 1]);
                    }} else if (adm === 'Supercompressor') {{
                        this.addSuperchargerUnit(0, intTopY + 0.28, 0, halfLenX * 1.55, 0.62, -halfLenX - 0.24, intApp, intType);
                        this.addPipe(this.staticOpaque, [[halfLenX * 0.78, intTopY + 0.28, 0], [halfLenX + 0.30, intTopY + 0.28, 0]], 0.11, C_PIPE, [0.62, 52], [0]);
                        if (intType === 'Cold Air Intake') {{
                            this.addPart(this.staticTrans, 'bevelBox', this.matTRS(halfLenX + 0.52, intTopY + 0.28, 0, 0, 0, 0, 0.54, 0.54, 0.54), intApp.col, intApp.spec);
                        }}
                        this.addConeFilter(halfLenX + 0.52, intTopY + 0.28, 0, 1);
                    }} else if (adm === 'Biturbo') {{
                        this.addValleyIntakeAssembly({{ halfLenX, topY: intTopY + 0.12, plenumW, cylSpecs, isBoosted: true, intType, app: intApp, boreScale }});
                        const isSeq = turboCfg === 'Sequencial';
                        const tL = this.addTurboUnit(0, exhY - 0.04, -exhZOut - 0.34, isSeq ? 0.80 : 0.94, -1, isSeq ? 'primary' : 'all');
                        const tR = this.addTurboUnit(0, exhY - 0.04,  exhZOut + 0.34, isSeq ? 1.12 : 0.94,  1, isSeq ? 'secondary' : 'all');
                        exhaustAnchors = [tL.downpipeOut, tR.downpipeOut];
                        const icX = -halfLenX - 1.18;
                        this.addIntercooler(icX, 0.08, 0, 0.24, 0.74, 1.48);
                        if (isSeq) {{
                            this.addSequentialCrossover(tL.turbOut, tR.chra, -0.26, 0.054);
                        }}
                        this.addPipe(this.staticOpaque, [tL.compOut, [icX + 0.32, 0.12, -exhZOut - 0.20], [icX, 0.12, -0.68]], 0.070, C_PIPE, [0.62, 52], [0, 1]);
                        this.addPipe(this.staticOpaque, [tR.compOut, [icX + 0.32, 0.12,  exhZOut + 0.20], [icX, 0.12,  0.68]], 0.070, C_PIPE, [0.62, 52], [0, 1]);
                        this.addPipe(this.staticOpaque, [[icX, 0.26, 0], [-halfLenX * 0.90, intTopY + 0.12, 0]], 0.085, C_PIPE, [0.62, 52], [0]);
                    }} else if (adm === 'Quad Turbo') {{
                        this.addValleyIntakeAssembly({{ halfLenX, topY: intTopY + 0.12, plenumW, cylSpecs, isBoosted: true, intType, app: intApp, boreScale }});
                        const icX = -halfLenX - 1.18;
                        this.addIntercooler(icX, 0.08, 0, 0.26, 0.78, 1.56);
                        const isSeq = turboCfg === 'Sequencial';
                        const qPos = [-halfLenX * 0.46, halfLenX * 0.46];
                        const lPair = [], rPair = [];
                        for (let qi = 0; qi < 2; qi++) {{
                            const qx = qPos[qi];
                            const stg = isSeq ? (qi === 0 ? 'primary' : 'secondary') : 'all';
                            const qScale = isSeq ? (qi === 0 ? 0.62 : 0.88) : 0.74;
                            const tL = this.addTurboUnit(qx, exhY - 0.04, -exhZOut - 0.34, qScale, -1, stg);
                            const tR = this.addTurboUnit(qx, exhY - 0.04,  exhZOut + 0.34, qScale,  1, stg);
                            lPair.push(tL); rPair.push(tR);
                            this.addPipe(this.staticOpaque, [tL.compOut, [icX + 0.34, 0.12, -exhZOut - 0.24], [icX, 0.12, -0.72]], 0.052, C_PIPE, [0.62, 52], [0, 1]);
                            this.addPipe(this.staticOpaque, [tR.compOut, [icX + 0.34, 0.12,  exhZOut + 0.24], [icX, 0.12,  0.72]], 0.052, C_PIPE, [0.62, 52], [0, 1]);
                        }}
                        exhaustAnchors = [lPair[1].downpipeOut, rPair[1].downpipeOut];
                        if (isSeq) {{
                            this.addSequentialCrossover(lPair[0].turbOut, lPair[1].chra, -0.10, 0.042);
                            this.addSequentialCrossover(rPair[0].turbOut, rPair[1].chra, -0.10, 0.042);
                        }}
                        this.addPipe(this.staticOpaque, [[icX, 0.26, 0], [-halfLenX * 0.90, intTopY + 0.12, 0]], 0.088, C_PIPE, [0.62, 52], [0]);
                    }} else {{
                        this.addSuperchargerUnit(0, intTopY + 0.28, 0, halfLenX * 1.55, 0.62, -halfLenX - 0.24, intApp, intType);
                        const t = this.addTurboUnit(0, exhY - 0.04, -exhZOut - 0.36, 0.96, -1);
                        exhaustAnchors = [t.downpipeOut];
                        const icX = -halfLenX - 1.18;
                        this.addIntercooler(icX, 0.08, 0, 0.24, 0.72, 1.38);
                        this.addPipe(this.staticOpaque, [t.compOut, [icX + 0.35, 0.12, -exhZOut - 0.26], [icX, 0.12, -0.62]], 0.072, C_PIPE, [0.62, 52], [0, 1]);
                        this.addPipe(this.staticOpaque, [[icX, 0.12, 0.62], [icX + 0.28, intTopY + 0.28, 0.72], [halfLenX * 0.88, intTopY + 0.28, 0.72], [halfLenX * 0.88, intTopY + 0.28, 0], [halfLenX * 0.78, intTopY + 0.28, 0]], 0.076, C_PIPE, [0.62, 52], [0, 2]);
                    }}
                }} else if (fmt === 'V' || fmt === 'W') {{
                    const isW = fmt === 'W';
                    const nBankA = Math.ceil(n / 2);
                    const nBankB = Math.floor(n / 2);
                    const cols = Math.max(1, nBankA, nBankB);
                    const stepX = isW ? cylR * 1.65 : cylR * 2.40;
                    const startX = -((cols - 1) * stepX) / 2;
                    halfLenX = Math.max(0.88, (cols * stepX) * 0.5 + cylR * 0.55);
                    const baseBankAng = isW ? (vAngOpt === '90' ? 0.80 : 0.62) : (vAngOpt === '90' ? Math.PI * 0.25 : Math.PI / 6.0);
                    maxSpanZ = vAngOpt === '90' ? 1.85 : 1.55;

                    for (let i = 0; i < nBankA; i++) {{
                        const x = startX + i * stepX - stepX * 0.12;
                        const subAng = isW ? ((i % 2 === 0 ? -1 : 1) * 0.19) : 0;
                        cylSpecs.push({{ x, zOff: 0, angle: -baseBankAng + subAng, phase: getPhase(i, nBankA), bank: -1 }});
                    }}
                    for (let i = 0; i < nBankB; i++) {{
                        const x = startX + i * stepX + stepX * 0.12;
                        const subAng = isW ? ((i % 2 === 0 ? -1 : 1) * 0.19) : 0;
                        cylSpecs.push({{ x, zOff: 0, angle: baseBankAng + subAng, phase: getPhase(i, nBankB) + 0.78, bank: 1 }});
                    }}

                    const blockW = halfLenX * 2.04;
                    const bankZWidth = isW ? cylR * 3.6 : cylR * 2.3;
                    const bankMidDist = deckDist * 0.48;
                    const bankH = deckDist * 0.88;

                    // Cárter detalhado chanfrado + saia do bloco + tampa central do vale + filtro
                    const skirtBotV = -crankR - 0.10;
                    const vCaseH = 0.28 - skirtBotV;
                    const vCaseZ = Math.max(cylR * 2.85, crankR * 2.55);
                    this.addPart(this.staticOpaque, 'bevelBox', this.matTRS(0, -crankR - 0.14, 0, 0, 0, 0, blockW * 1.03, 0.10, vCaseZ * 1.04), C_SUMP, [0.44, 28]);
                    this.addPart(this.staticOpaque, 'bevelBox', this.matTRS(0, -crankR - 0.30, 0, 0, 0, 0, blockW * 0.96, 0.28, vCaseZ * 0.92), C_SUMP, [0.38, 22]);
                    for (let f = -2; f <= 2; f++) {{
                        this.addPart(this.staticOpaque, 'bevelBox', this.matTRS(0, -crankR - 0.45, f * 0.14, 0, 0, 0, blockW * 0.88, 0.03, 0.03), C_BLOCK, [0.5, 32]);
                    }}
                    this.addPart(this.staticTrans, 'bevelBox', this.matTRS(0, skirtBotV + vCaseH * 0.5, 0, 0, 0, 0, blockW * 1.01, vCaseH, vCaseZ), C_BLOCK, BLK_SPEC);
                    this.addPart(this.staticOpaque, 'bevelBox', this.matTRS(0, deckDist * 0.52, 0, 0, 0, 0, blockW * 0.98, 0.08, Math.max(0.32, cylR * 1.1)), C_HEAD, [0.46, 36]);
                    this.addPart(this.staticOpaque, 'cyl', this.matTRS(-halfLenX * 0.45, -0.05, cylR * 1.38, 0.7, 0, 0, 0.12, 0.26, 0.12), C_FILTER, [0.55, 44]);
                    this.addStarterMotor(halfLenX * 0.62, -0.14, cylR * 1.48);

                    for (const side of [-1, 1]) {{
                        const ang = side * baseBankAng;
                        const sinA = Math.sin(ang), cosA = Math.cos(ang);
                        this.addPart(this.staticTrans, 'bevelBox', this.matTRS(0, bankMidDist * cosA, bankMidDist * sinA, ang, 0, 0, blockW, bankH, bankZWidth * 0.94), C_BLOCK, BLK_SPEC);
                        const outerSideZ = ang >= 0 ? bankZWidth * 0.50 : -bankZWidth * 0.50;
                        const bankCylSpecs = cylSpecs.filter(c => c.bank === side);
                        for (const c of bankCylSpecs) {{
                            const rx = c.x;
                            const ribY = bankMidDist * cosA - outerSideZ * sinA;
                            const ribZ = bankMidDist * sinA + outerSideZ * cosA;
                            this.addPart(this.staticOpaque, 'bevelBox', this.matTRS(rx, ribY, ribZ, ang, 0, 0, 0.042, bankH * 0.74, 0.038), C_BLOCK, BLK_SPEC);
                            this.addPart(this.staticOpaque, 'cyl', this.matTRS(rx, ribY, ribZ, ang + Math.PI * 0.5, 0, 0, 0.068, 0.032, 0.068), C_BRASS, [0.74, 58]);
                            const boltD = deckDist + 0.39;
                            const boltY = boltD * cosA - (outerSideZ * 0.65) * sinA;
                            const boltZ = boltD * sinA + (outerSideZ * 0.65) * cosA;
                            this.addPart(this.staticOpaque, 'hex', this.matTRS(rx, boltY, boltZ, ang, 0, 0, 0.030, 0.022, 0.030), C_BOLT, [0.78, 60]);
                        }}
                        const headD = deckDist + 0.14;
                        this.addPart(this.staticTrans, 'bevelBox', this.matTRS(0, headD * cosA, headD * sinA, ang, 0, 0, blockW * 1.01, 0.26, bankZWidth * 1.03), C_HEAD, [0.45, 36]);
                        const vcD = deckDist + 0.35;
                        this.addPart(this.staticOpaque, 'bevelBox', this.matTRS(0, vcD * cosA, vcD * sinA, ang, 0, 0, blockW * 1.02, 0.11, bankZWidth * 1.02), C_VALVE, [0.58, 50]);
                        if (!is2Stroke && !isFreevalve && camMode === 'DOHC') {{
                            const camRidgeD = deckDist + 0.415;
                            for (const off of [-bankZWidth * 0.25, bankZWidth * 0.25]) {{
                                this.addPart(this.staticOpaque, 'bevelBox', this.matTRS(0, camRidgeD * cosA - off * sinA, camRidgeD * sinA + off * cosA, ang, 0, 0, blockW * 0.98, 0.072, bankZWidth * 0.34), C_VALVE, [0.62, 54]);
                            }}
                        }}
                        const ribD = deckDist + 0.425;
                        this.addPart(this.staticOpaque, 'bevelBox', this.matTRS(0, ribD * cosA, ribD * sinA, ang, 0, 0, blockW * 0.90, 0.03, bankZWidth * 0.28), C_BOLT, [0.7, 54]);

                        const vvtColor = vType === 'VVT' ? [0.76, 0.60, 0.24, 1.0] : [0.26, 0.44, 0.64, 1.0];
                        if (is2Stroke || isFreevalve) {{
                            // 2T Reed Valve / Freevalve: sem árvore de cames na cabeça
                        }} else if (camMode === 'DOHC') {{
                            const camD = deckDist + 0.20;
                            for (const off of [-0.11, 0.11]) {{
                                const camY = camD * cosA - off * sinA, camZ = camD * sinA + off * cosA;
                                this.addPart(this.staticOpaque, 'cyl', this.matTRS(0, camY, camZ, 0, 0, Math.PI * 0.5, 0.044, blockW * 1.03, 0.044), C_CRANK, [0.65, 52]);
                                this.dynamicRotors.push({{ type: 'pulley', cx: -halfLenX - 0.24, cy: camY, cz: camZ, r: 0.17, thick: 0.07, speedMult: this.config.ciclo === '2T' ? 1.0 : 0.5, colorRim: [0.36, 0.41, 0.48, 1.0], colorHub: vvtColor }});
                            }}
                        }} else if (camMode === 'SOHC') {{
                            const camD = deckDist + 0.20;
                            const camY = camD * cosA, camZ = camD * sinA;
                            this.addPart(this.staticOpaque, 'cyl', this.matTRS(0, camY, camZ, 0, 0, Math.PI * 0.5, 0.052, blockW * 1.03, 0.052), C_CRANK, [0.65, 52]);
                            this.dynamicRotors.push({{ type: 'pulley', cx: -halfLenX - 0.24, cy: camY, cz: camZ, r: 0.22, thick: 0.08, speedMult: this.config.ciclo === '2T' ? 1.0 : 0.5, colorRim: [0.36, 0.41, 0.48, 1.0], colorHub: vvtColor }});
                        }} else {{
                            // OHV pushrod rocker shaft on head
                            const rD = deckDist + 0.22;
                            this.addPart(this.staticOpaque, 'cyl', this.matTRS(0, rD * cosA, rD * sinA, 0, 0, Math.PI * 0.5, 0.036, blockW * 0.94, 0.036), C_BOLT, [0.7, 54]);
                        }}
                    }}
                    // Ponte dianteira de refrigeração no vale em V + tubo termóstato
                    const vCrossX = -halfLenX - 0.06;
                    const vCrossY = deckDist * 0.76;
                    this.addPipe(this.staticOpaque, [[vCrossX, vCrossY, -0.44], [vCrossX, vCrossY + 0.04, 0], [vCrossX, vCrossY, 0.44]], 0.042, C_PIPE, [0.78, 60]);
                    this.addPart(this.staticOpaque, 'cyl', this.matTRS(vCrossX - 0.08, vCrossY + 0.05, 0, 0, 0, Math.PI * 0.5, 0.068, 0.14, 0.068), C_HEAD, [0.55, 38]);
                    if (!is2Stroke && !isFreevalve && camMode === 'OHV') {{
                        const valleyCamY = 0.26;
                        this.addPart(this.staticOpaque, 'cyl', this.matTRS(0, valleyCamY, 0, 0, 0, Math.PI * 0.5, 0.055, blockW * 1.02, 0.055), C_CRANK, [0.65, 52]);
                        this.dynamicRotors.push({{ type: 'pulley', cx: -halfLenX - 0.24, cy: valleyCamY, cz: 0, r: 0.20, thick: 0.075, speedMult: this.config.ciclo === '2T' ? 1.0 : 0.5, colorRim: [0.36, 0.41, 0.48, 1.0], colorHub: [0.72, 0.48, 0.26, 1.0] }});
                    }}
                    // Bobinas/injetores + cames + varetas OHV + capas de mancal em cada cilindro
                    for (const c of cylSpecs) {{
                        if (!is2Stroke && !isFreevalve) {{
                            if (camMode === 'OHV') {{
                                this.dynamicCams.push({{ x: c.x, y: 0.26, z: 0, phase: c.phase * 0.5 }});
                                const pTopD = deckDist + 0.20;
                                this.addPipe(this.staticOpaque, [[c.x, 0.26, 0], [c.x, pTopD * Math.cos(c.angle), pTopD * Math.sin(c.angle)]], 0.020, C_PIPE, [0.75, 58]);
                            }} else if (camMode === 'DOHC') {{
                                const camD = deckDist + 0.20;
                                const bAng = c.bank * baseBankAng;
                                const bCos = Math.cos(bAng), bSin = Math.sin(bAng);
                                this.dynamicCams.push({{ x: c.x, y: camD * bCos - (-0.11) * bSin, z: camD * bSin + (-0.11) * bCos, phase: c.phase * 0.5 }});
                                this.dynamicCams.push({{ x: c.x, y: camD * bCos - (0.11) * bSin, z: camD * bSin + (0.11) * bCos, phase: c.phase * 0.5 + 2.1 }});
                            }} else {{
                                const camD = deckDist + 0.20;
                                const bAng = c.bank * baseBankAng;
                                this.dynamicCams.push({{ x: c.x, y: camD * Math.cos(bAng), z: camD * Math.sin(bAng), phase: c.phase * 0.5 }});
                            }}
                        }}
                        this.addCoilPackAndDetails(c.x, deckDist + 0.43, 0, c.angle, isDiesel);
                        this.addPart(this.staticOpaque, 'box', this.matTRS(c.x, -0.05, 0, 0, 0, 0, 0.11, 0.22, 0.26), C_CRANK, [0.48, 34]);
                    }}

                    const camD = deckDist + 0.20;
                    const camY = camD * Math.cos(baseBankAng);
                    const camZ = camD * Math.sin(baseBankAng);
                    const tx = -halfLenX - 0.24;
                    if (is2Stroke || isFreevalve) {{
                        this.addPart(this.staticOpaque, 'cyl', this.matTRS(-halfLenX * 0.60, 0.34, 0.34, 0, 0, Math.PI * 0.5, 0.14, 0.28, 0.14), C_ALT, [0.6, 48]);
                        this.dynamicRotors.push({{ type: 'pulley', cx: tx, cy: 0.34, cz: 0.34, r: 0.11, thick: 0.07, speedMult: 1.8, colorRim: [0.46, 0.50, 0.56, 1.0], colorHub: [0.76, 0.80, 0.86, 1.0] }});
                        this.addPipe(this.staticOpaque, [
                            [tx, -0.25, 0],
                            [tx, 0, -0.24],
                            [tx, 0.34, 0.34],
                            [tx, 0, 0.24],
                            [tx, -0.25, 0]
                        ], 0.026, C_BELT, [0.15, 10]);
                    }} else if (camMode === 'OHV') {{
                        this.addPipe(this.staticOpaque, [
                            [tx, -0.25, 0],
                            [tx, 0, -0.22],
                            [tx, 0.26, -0.18],
                            [tx, 0.44, 0],
                            [tx, 0.26, 0.18],
                            [tx, 0, 0.22],
                            [tx, -0.25, 0]
                        ], 0.028, C_BELT, [0.15, 10]);
                    }} else {{
                        this.addPipe(this.staticOpaque, [
                            [tx, -0.25, 0],
                            [tx, 0, -0.24],
                            [tx, camY, -camZ - 0.18],
                            [tx, camY + 0.20, -camZ],
                            [tx, camY + 0.20, camZ],
                            [tx, camY, camZ + 0.18],
                            [tx, 0, 0.24],
                            [tx, -0.25, 0]
                        ], 0.028, C_BELT, [0.15, 10]);
                    }}

                    const exhD = deckDist + 0.10;
                    const exhY = exhD * Math.cos(baseBankAng) - 0.22;
                    const exhZOut = exhD * Math.sin(baseBankAng) + 0.66;
                    for (const c of cylSpecs) {{
                        const s = c.bank;
                        const portY = (deckDist + 0.12) * Math.cos(c.angle);
                        const portZ = (deckDist + 0.12) * Math.sin(c.angle) + s * (bankZWidth * 0.42);
                        this.addPipe(this.staticOpaque, [
                            [c.x, portY, portZ],
                            [c.x, exhY + 0.05, s * (exhZOut - 0.10)],
                            [c.x, exhY - 0.18, s * exhZOut]
                        ], 0.062 * boreScale, C_EXHAUST, [0.4, 28]);
                    }}
                    this.addPart(this.staticOpaque, 'cyl', this.matTRS(0, exhY - 0.20, -exhZOut, 0, 0, Math.PI * 0.5, 0.105, halfLenX * 1.9, 0.105), C_EXHAUST, [0.4, 28]);
                    this.addPart(this.staticOpaque, 'cyl', this.matTRS(0, exhY - 0.20,  exhZOut, 0, 0, Math.PI * 0.5, 0.105, halfLenX * 1.9, 0.105), C_EXHAUST, [0.4, 28]);
                    exhaustAnchors = [[halfLenX * 0.94, exhY - 0.20, -exhZOut], [halfLenX * 0.94, exhY - 0.20, exhZOut]];

                    const valleyY = deckDist * 0.85 + 0.16;
                    const plenumW = halfLenX * 1.82;
                    for (const c of cylSpecs) {{
                        const portY = (deckDist + 0.08) * Math.cos(c.angle);
                        const portZ = (deckDist + 0.08) * Math.sin(c.angle) - c.bank * (bankZWidth * 0.35);
                        if (is2Stroke) {{
                            this.addReedValveCage(c.x, portY + 0.02, portZ, 'v', boreScale, c.angle);
                        }}
                        this.addPipe(this.staticOpaque, [[c.x, valleyY, 0], [c.x, portY, portZ]], 0.064 * boreScale, C_RUNNER, intApp.rSpec);
                    }}
                    // Rampas de injeção no vale central
                    this.addPart(this.staticOpaque, 'cyl', this.matTRS(0, valleyY + 0.06, -0.32, 0, 0, Math.PI * 0.5, 0.036, plenumW * 0.94, 0.036), C_RAIL, [0.65, 52]);
                    this.addPart(this.staticOpaque, 'cyl', this.matTRS(0, valleyY + 0.06,  0.32, 0, 0, Math.PI * 0.5, 0.036, plenumW * 0.94, 0.036), C_RAIL, [0.65, 52]);

                    if (adm === 'Atmosférico') {{
                        this.addValleyIntakeAssembly({{ halfLenX, topY: valleyY + 0.14, plenumW, cylSpecs, isBoosted: false, intType, app: intApp, boreScale }});
                    }} else if (adm === 'Turbo') {{
                        this.addValleyIntakeAssembly({{ halfLenX, topY: valleyY + 0.14, plenumW, cylSpecs, isBoosted: true, intType, app: intApp, boreScale }});
                        const t = this.addTurboUnit(0, exhY - 0.20, -exhZOut - 0.42, 1.05, -1);
                        exhaustAnchors = [
                            [t.downpipeOut[0], t.downpipeOut[1], -exhZOut - 0.42],
                            [halfLenX * 0.94, exhY - 0.20, exhZOut]
                        ];
                        const icX = -halfLenX - 1.18;
                        this.addIntercooler(icX, 0.06, 0, 0.24, 0.74, 1.45);
                        this.addPipe(this.staticOpaque, [t.compOut, [icX + 0.35, 0.20, -exhZOut - 0.35], [icX, 0.15, -0.68]], 0.078, C_PIPE, [0.62, 52], [0, 1]);
                        this.addPipe(this.staticOpaque, [[icX, 0.15, 0.68], [icX + 0.32, valleyY + 0.14, 0.40], [-halfLenX * 0.90, valleyY + 0.14, 0]], 0.082, C_PIPE, [0.62, 52], [0, 1]);
                    }} else if (adm === 'Supercompressor') {{
                        this.addSuperchargerUnit(0, valleyY + 0.30, 0, halfLenX * 1.55, 0.62, -halfLenX - 0.24, intApp, intType);
                        this.addPipe(this.staticOpaque, [[halfLenX * 0.78, valleyY + 0.30, 0], [halfLenX + 0.30, valleyY + 0.30, 0]], 0.11, C_PIPE, [0.62, 52], [0]);
                        if (intType === 'Cold Air Intake') {{
                            this.addPart(this.staticTrans, 'bevelBox', this.matTRS(halfLenX + 0.52, valleyY + 0.30, 0, 0, 0, 0, 0.54, 0.54, 0.54), intApp.col, intApp.spec);
                        }}
                        this.addConeFilter(halfLenX + 0.52, valleyY + 0.30, 0, 1);
                    }} else if (adm === 'Biturbo') {{
                        this.addValleyIntakeAssembly({{ halfLenX, topY: valleyY + 0.14, plenumW, cylSpecs, isBoosted: true, intType, app: intApp, boreScale }});
                        const isSeq = turboCfg === 'Sequencial';
                        const tL = this.addTurboUnit(-0.1, exhY - 0.20, -exhZOut - 0.40, isSeq ? 0.80 : 0.96, -1, isSeq ? 'primary' : 'all');
                        const tR = this.addTurboUnit(-0.1, exhY - 0.20,  exhZOut + 0.40, isSeq ? 1.15 : 0.96,  1, isSeq ? 'secondary' : 'all');
                        exhaustAnchors = [tL.downpipeOut, tR.downpipeOut];
                        const icX = -halfLenX - 1.18;
                        this.addIntercooler(icX, 0.06, 0, 0.24, 0.76, 1.55);
                        if (isSeq) {{
                            this.addSequentialCrossover(tL.turbOut, tR.chra, -0.28, 0.056);
                        }}
                        this.addPipe(this.staticOpaque, [tL.compOut, [icX + 0.30, 0.18, -exhZOut - 0.2], [icX, 0.15, -0.72]], 0.07, C_PIPE, [0.62, 52], [0, 1]);
                        this.addPipe(this.staticOpaque, [tR.compOut, [icX + 0.30, 0.18,  exhZOut + 0.2], [icX, 0.15,  0.72]], 0.07, C_PIPE, [0.62, 52], [0, 1]);
                        this.addPipe(this.staticOpaque, [[icX, 0.30, 0], [-halfLenX * 0.90, valleyY + 0.14, 0]], 0.085, C_PIPE, [0.62, 52], [0]);
                    }} else if (adm === 'Quad Turbo') {{
                        this.addValleyIntakeAssembly({{ halfLenX, topY: valleyY + 0.14, plenumW, cylSpecs, isBoosted: true, intType, app: intApp, boreScale }});
                        const icX = -halfLenX - 1.18;
                        this.addIntercooler(icX, 0.06, 0, 0.26, 0.80, 1.62);
                        const isSeq = turboCfg === 'Sequencial';
                        const qPos = [-halfLenX * 0.46, halfLenX * 0.46];
                        const lPair = [], rPair = [];
                        for (let qi = 0; qi < 2; qi++) {{
                            const qx = qPos[qi];
                            const stg = isSeq ? (qi === 0 ? 'primary' : 'secondary') : 'all';
                            const qScale = isSeq ? (qi === 0 ? 0.64 : 0.90) : 0.76;
                            const tL = this.addTurboUnit(qx, exhY - 0.20, -exhZOut - 0.40, qScale, -1, stg);
                            const tR = this.addTurboUnit(qx, exhY - 0.20,  exhZOut + 0.40, qScale,  1, stg);
                            lPair.push(tL); rPair.push(tR);
                            this.addPipe(this.staticOpaque, [tL.compOut, [icX + 0.32, 0.18, -exhZOut - 0.22], [icX, 0.15, -0.74]], 0.052, C_PIPE, [0.62, 52], [0, 1]);
                            this.addPipe(this.staticOpaque, [tR.compOut, [icX + 0.32, 0.18,  exhZOut + 0.22], [icX, 0.15,  0.74]], 0.052, C_PIPE, [0.62, 52], [0, 1]);
                        }}
                        exhaustAnchors = [lPair[1].downpipeOut, rPair[1].downpipeOut];
                        if (isSeq) {{
                            this.addSequentialCrossover(lPair[0].turbOut, lPair[1].chra, -0.10, 0.044);
                            this.addSequentialCrossover(rPair[0].turbOut, rPair[1].chra, -0.10, 0.044);
                        }}
                        this.addPipe(this.staticOpaque, [[icX, 0.30, 0], [-halfLenX * 0.90, valleyY + 0.14, 0]], 0.088, C_PIPE, [0.62, 52], [0]);
                    }} else {{
                        this.addSuperchargerUnit(0, valleyY + 0.30, 0, halfLenX * 1.55, 0.62, -halfLenX - 0.24, intApp, intType);
                        const t = this.addTurboUnit(0, exhY - 0.20, -exhZOut - 0.40, 0.98, -1);
                        exhaustAnchors = [
                            t.downpipeOut,
                            [halfLenX * 0.94, exhY - 0.20, exhZOut]
                        ];
                        const icX = -halfLenX - 1.18;
                        this.addIntercooler(icX, 0.06, 0, 0.24, 0.74, 1.45);
                        this.addPipe(this.staticOpaque, [t.compOut, [icX + 0.35, 0.20, -exhZOut - 0.3], [icX, 0.15, -0.68]], 0.072, C_PIPE, [0.62, 52], [0, 1]);
                        this.addPipe(this.staticOpaque, [[icX, 0.15, 0.68], [icX + 0.30, valleyY + 0.30, 0.78], [halfLenX * 0.88, valleyY + 0.30, 0.78], [halfLenX * 0.88, valleyY + 0.30, 0], [halfLenX * 0.78, valleyY + 0.30, 0]], 0.076, C_PIPE, [0.62, 52], [0, 2]);
                    }}
                }} else {{
                    // Motor Wankel Rotativo (1 a 4 rotores epitrocoidais)
                    const nRotors = Math.max(1, Math.min(4, n));
                    const wScale = Math.max(0.75, Math.min(1.26, ((this.config.bore || 86) + (this.config.stroke || 86)) / 172.0));
                    const rotorR = 1.05 * wScale;
                    const housingW = 0.44 * wScale;
                    const ironW = 0.14 * wScale;
                    const pitchX = housingW + ironW;
                    halfLenX = Math.max(0.78, (nRotors * pitchX + ironW) * 0.5 + 0.10);
                    maxSpanZ = 1.48 * wScale;

                    const wPhases = nRotors === 1
                        ? [0]
                        : (nRotors === 2 ? [0, Math.PI] : (nRotors === 3 ? [0, (2 * Math.PI) / 3, (4 * Math.PI) / 3] : [0, Math.PI, Math.PI * 0.5, Math.PI * 1.5]));
                    const startRx = -((nRotors - 1) * pitchX) * 0.5;
                    const stackW = nRotors * pitchX + ironW;

                    // Placas laterais e intermédias (Irons) + pernos axiais + carcaças epitrocoidais com aletas + rotores
                    for (let i = 0; i <= nRotors; i++) {{
                        const px = startRx - pitchX * 0.5 + i * pitchX;
                        const isEnd = (i === 0 || i === nRotors);
                        const targetPlate = isEnd ? this.staticOpaque : this.staticTrans;
                        this.addPart(targetPlate, 'bevelBox', this.matTRS(px, 0, 0, 0, 0, 0, ironW, 2.38 * rotorR, 2.02 * rotorR), isEnd ? C_HEAD : C_BLOCK, BLK_SPEC);
                        this.addPart(targetPlate, 'cyl', this.matTRS(px, 1.04 * rotorR, 0, 0, 0, Math.PI * 0.5, 0.92 * rotorR, ironW * 0.98, 0.92 * rotorR), isEnd ? C_HEAD : C_BLOCK, BLK_SPEC);
                        this.addPart(targetPlate, 'cyl', this.matTRS(px, -1.04 * rotorR, 0, 0, 0, Math.PI * 0.5, 0.92 * rotorR, ironW * 0.98, 0.92 * rotorR), isEnd ? C_HEAD : C_BLOCK, BLK_SPEC);
                    }}
                    // Pernos de tensão perimetrais a unir todo o bloco Wankel
                    for (let tb = 0; tb < 10; tb++) {{
                        const ta = (tb / 10) * Math.PI * 2 + 0.15;
                        const tby = (1.14 * Math.cos(ta) + 0.11 * Math.cos(3 * ta)) * rotorR;
                        const tbz = (1.14 * Math.sin(ta) + 0.11 * Math.sin(3 * ta)) * rotorR;
                        this.addPart(this.staticOpaque, 'cyl', this.matTRS(0, tby, tbz, 0, 0, Math.PI * 0.5, 0.022, stackW * 1.04, 0.022), C_BOLT, [0.78, 62]);
                    }}

                    for (let rIdx = 0; rIdx < nRotors; rIdx++) {{
                        const rx = startRx + rIdx * pitchX;
                        this.addPart(this.staticTrans, 'wankelHousing', this.matTRS(rx, 0, 0, 0, 0, 0, housingW, rotorR, rotorR), C_BLOCK, BLK_SPEC);
                        for (let fin = -1; fin <= 1; fin++) {{
                            this.addPart(this.staticOpaque, 'bevelBox', this.matTRS(rx + fin * (housingW * 0.28), 1.24 * rotorR, 0, 0, 0, 0, 0.028, 0.12, 1.38 * rotorR), C_BLOCK, BLK_SPEC);
                        }}
                        // Velas Leading & Trailing no lado +Z (câmara de combustão) + cabos HT
                        for (const spY of [-0.20 * rotorR, 0.20 * rotorR]) {{
                            this.addPart(this.staticOpaque, 'cyl', this.matTRS(rx, spY, 1.02 * rotorR, Math.PI * 0.5, 0, 0, 0.042, 0.16, 0.042), C_BOLT, [0.76, 60]);
                            this.addPart(this.staticOpaque, 'cyl', this.matTRS(rx, spY, 1.13 * rotorR, Math.PI * 0.5, 0, 0, 0.052, 0.10, 0.052), [0.72, 0.22, 0.22, 1.0], [0.55, 42]);
                            this.addPipe(this.staticOpaque, [[rx, spY, 1.15 * rotorR], [rx, 0.90 * rotorR, 1.22 * rotorR], [rx, 1.26 * rotorR, 0.65 * rotorR]], 0.018, [0.16, 0.18, 0.22, 1.0], [0.22, 16]);
                        }}
                        this.dynamicWankel.push({{
                            x: rx,
                            phase: wPhases[rIdx],
                            ecc: 0.16 * rotorR,
                            rotorR: rotorR * 0.99,
                            rotorW: housingW * 0.88,
                            cRotor: C_PISTON,
                            cSeal: C_RING,
                            cGear: C_BRASS,
                            cShaft: C_CRANK
                        }});
                    }}

                    // Cárter sólido inferior + aletas + cobertura superior sólida epitrocoidal
                    const sumpY = -1.30 * rotorR;
                    this.addPart(this.staticTrans, 'bevelBox', this.matTRS(0, sumpY + 0.12, 0, 0, 0, 0, stackW * 0.98, 0.26, 1.72 * rotorR), C_BLOCK, BLK_SPEC);
                    this.addPart(this.staticOpaque, 'bevelBox', this.matTRS(0, sumpY - 0.06, 0, 0, 0, 0, stackW * 1.02, 0.12, 1.85 * rotorR), C_SUMP, [0.44, 28]);
                    this.addPart(this.staticOpaque, 'bevelBox', this.matTRS(0, sumpY - 0.22, 0, 0, 0, 0, stackW * 0.94, 0.24, 1.65 * rotorR), C_SUMP, [0.38, 22]);
                    for (let f = -2; f <= 2; f++) {{
                        this.addPart(this.staticOpaque, 'bevelBox', this.matTRS(0, sumpY - 0.35, f * 0.18 * rotorR, 0, 0, 0, stackW * 0.86, 0.03, 0.03), C_BLOCK, [0.5, 32]);
                    }}
                    this.addPart(this.staticOpaque, 'bevelBox', this.matTRS(0, 1.32 * rotorR, 0, 0, 0, 0, stackW * 0.96, 0.12, 1.24 * rotorR), C_VALVE, [0.58, 50]);
                    this.addPart(this.staticOpaque, 'cyl', this.matTRS(-halfLenX * 0.65, 1.41 * rotorR, 0.16, 0, 0, 0, 0.088, 0.06, 0.088), C_BOLT, [0.72, 54]);
                    this.addPart(this.staticOpaque, 'cyl', this.matTRS(-halfLenX * 0.35, -0.35 * rotorR, 1.18 * rotorR, 0.45, 0, 0, 0.11, 0.24, 0.11), C_FILTER, [0.55, 44]);
                    this.addStarterMotor(halfLenX * 0.56, -0.78 * rotorR, 1.04 * rotorR);

                    // Alternador, bomba de água e correia frontal Wankel
                    const tx = -halfLenX - 0.24;
                    const altY = 0.85 * rotorR;
                    const altZ = 0.86 * rotorR;
                    const wpY = 0.42 * rotorR;
                    const wpZ = -0.82 * rotorR;
                    this.addPart(this.staticOpaque, 'cyl', this.matTRS(-halfLenX * 0.52, altY, altZ, 0, 0, Math.PI * 0.5, 0.17, 0.32, 0.17), C_ALT, [0.6, 48]);
                    this.addPart(this.staticOpaque, 'cyl', this.matTRS(-halfLenX * 0.65, wpY, wpZ, 0, 0, Math.PI * 0.5, 0.14, 0.22, 0.14), C_HEAD, [0.55, 44]);
                    this.dynamicRotors.push({{ type: 'pulley', cx: tx, cy: altY, cz: altZ, r: 0.12, thick: 0.07, speedMult: 1.8, colorRim: [0.46, 0.50, 0.56, 1.0], colorHub: [0.76, 0.80, 0.86, 1.0] }});
                    this.dynamicRotors.push({{ type: 'pulley', cx: tx, cy: wpY, cz: wpZ, r: 0.13, thick: 0.07, speedMult: 1.35, colorRim: [0.46, 0.50, 0.56, 1.0], colorHub: [0.68, 0.72, 0.78, 1.0] }});
                    this.addPipe(this.staticOpaque, [
                        [tx, -0.25, 0],
                        [tx, wpY, wpZ - 0.12],
                        [tx, altY + 0.08, altZ],
                        [tx, altY - 0.08, altZ],
                        [tx, -0.25, 0]
                    ], 0.026, C_BELT, [0.15, 10]);

                    // Coletores de escape (-Z inferior), runners de admissão (topo / -Z superior) e rampa de injeção
                    const exhY = -0.56 * rotorR;
                    const exhZ = -1.24 * rotorR;
                    const intY = 1.54 * rotorR;
                    const intZ = 0.20 * rotorR;
                    const plenW = Math.max(0.85, stackW * 0.92);
                    const rotorRunnersX = [];
                    for (let rIdx = 0; rIdx < nRotors; rIdx++) {{
                        const rx = startRx + rIdx * pitchX;
                        rotorRunnersX.push(rx);
                        this.addPipe(this.staticOpaque, [[rx, -0.35 * rotorR, -0.98 * rotorR], [rx, exhY, exhZ]], 0.088 * wScale, C_EXHAUST, [0.4, 28]);
                        this.addPipe(this.staticOpaque, [[rx, 0.48 * rotorR, -0.96 * rotorR], [rx, 1.15 * rotorR, -0.82 * rotorR], [rx, intY, intZ]], 0.082 * wScale, C_RUNNER, intApp.rSpec);
                        this.addPart(this.staticOpaque, 'cyl', this.matTRS(rx, 0.95 * rotorR, -0.58 * rotorR, -0.45, 0, 0, 0.030, 0.14, 0.030), C_BOLT, [0.6, 48]);
                    }}
                    this.addPart(this.staticOpaque, 'cyl', this.matTRS(0, exhY, exhZ, 0, 0, Math.PI * 0.5, 0.12, plenW, 0.12), C_EXHAUST, [0.4, 28]);
                    this.addPart(this.staticOpaque, 'cyl', this.matTRS(0, 1.04 * rotorR, -0.54 * rotorR, 0, 0, Math.PI * 0.5, 0.040, plenW, 0.040), C_RAIL, [0.65, 52]);
                    this.addPipe(this.staticOpaque, [[halfLenX * 0.88, exhY, exhZ], [halfLenX + 0.42, exhY - 0.12, exhZ]], 0.105, C_EXHAUST, [0.4, 28]);
                    exhaustAnchors = [[halfLenX + 0.42, exhY - 0.12, exhZ]];

                    if (adm === 'Atmosférico') {{
                        this.addSideIntakeAssembly({{ halfLenX, py: intY, pz: intZ, plenumW: plenW, runnersX: rotorRunnersX, feedDirX: -1, isBoosted: false, intType, app: intApp, boreScale: wScale }});
                    }} else if (adm === 'Turbo') {{
                        this.addSideIntakeAssembly({{ halfLenX, py: intY, pz: intZ, plenumW: plenW, runnersX: rotorRunnersX, feedDirX: -1, isBoosted: true, intType, app: intApp, boreScale: wScale }});
                        const t = this.addTurboUnit(0, exhY, exhZ - 0.42, 1.08, -1);
                        exhaustAnchors = [t.downpipeOut];
                        const icX = -halfLenX - 1.18;
                        this.addIntercooler(icX, 0.06, 0, 0.24, 0.74, 1.38);
                        this.addPipe(this.staticOpaque, [t.compOut, [icX + 0.34, 0.16, exhZ - 0.35], [icX, 0.15, -0.62]], 0.078, C_PIPE, [0.62, 52], [0, 1]);
                        this.addPipe(this.staticOpaque, [[icX, 0.15, 0.62], [icX + 0.32, intY, intZ], [-halfLenX * 0.90, intY, intZ]], 0.082, C_PIPE, [0.62, 52], [0, 1]);
                    }} else if (adm === 'Supercompressor') {{
                        this.addSuperchargerUnit(0, intY + 0.24, intZ, Math.max(0.95, plenW * 0.85), 0.58, -halfLenX - 0.24, intApp, intType);
                        this.addPipe(this.staticOpaque, [[plenW * 0.46, intY + 0.24, intZ], [halfLenX + 0.30, intY + 0.24, intZ]], 0.11, C_PIPE, [0.62, 52], [0]);
                        if (intType === 'Cold Air Intake') {{
                            this.addPart(this.staticTrans, 'bevelBox', this.matTRS(halfLenX + 0.52, intY + 0.24, intZ, 0, 0, 0, 0.54, 0.54, 0.54), intApp.col, intApp.spec);
                        }}
                        this.addConeFilter(halfLenX + 0.52, intY + 0.24, intZ, 1);
                    }} else if (adm === 'Biturbo') {{
                        this.addSideIntakeAssembly({{ halfLenX, py: intY, pz: intZ, plenumW: plenW, runnersX: rotorRunnersX, feedDirX: -1, isBoosted: true, intType, app: intApp, boreScale: wScale }});
                        const isSeq = turboCfg === 'Sequencial';
                        const t1 = this.addTurboUnit(-halfLenX * 0.40, exhY, exhZ - 0.42, isSeq ? 0.76 : 0.92, -1, isSeq ? 'primary' : 'all');
                        const t2 = this.addTurboUnit( halfLenX * 0.40, exhY, exhZ - 0.42, isSeq ? 1.10 : 0.92, -1, isSeq ? 'secondary' : 'all');
                        exhaustAnchors = [t2.downpipeOut];
                        const icX = -halfLenX - 1.18;
                        this.addIntercooler(icX, 0.06, 0, 0.24, 0.74, 1.42);
                        if (isSeq) {{
                            this.addSequentialCrossover(t1.turbOut, t2.chra, -0.14, 0.052);
                        }}
                        this.addPipe(this.staticOpaque, [t1.compOut, [icX + 0.34, 0.18, exhZ - 0.32], [icX, 0.15, -0.64]], 0.068, C_PIPE, [0.62, 52], [0, 1]);
                        this.addPipe(this.staticOpaque, [t2.compOut, [t1.compOut[0], 0.30, exhZ - 0.52], [icX, 0.24, -0.64]], 0.064, C_PIPE, [0.62, 52], [0, 1]);
                        this.addPipe(this.staticOpaque, [[icX, 0.15, 0.64], [icX + 0.32, intY, intZ], [-halfLenX * 0.90, intY, intZ]], 0.084, C_PIPE, [0.62, 52], [0, 1]);
                    }} else if (adm === 'Quad Turbo') {{
                        this.addSideIntakeAssembly({{ halfLenX, py: intY, pz: intZ, plenumW: plenW, runnersX: rotorRunnersX, feedDirX: -1, isBoosted: true, intType, app: intApp, boreScale: wScale }});
                        const icX = -halfLenX - 1.18;
                        this.addIntercooler(icX, 0.06, 0, 0.26, 0.78, 1.50);
                        const isSeq = turboCfg === 'Sequencial';
                        const qUnits = [];
                        for (let qi = 0; qi < 4; qi++) {{
                            const qx = -0.66 * halfLenX + qi * (0.44 * halfLenX);
                            const stg = isSeq ? (qi % 2 === 0 ? 'primary' : 'secondary') : 'all';
                            const qScale = isSeq ? (qi % 2 === 0 ? 0.58 : 0.84) : 0.70;
                            const qt = this.addTurboUnit(qx, exhY, exhZ - 0.42, qScale, -1, stg);
                            qUnits.push(qt);
                            this.addPipe(this.staticOpaque, [qt.compOut, [icX + 0.36, 0.14 + qi * 0.05, exhZ - 0.46], [icX, 0.14 + qi * 0.04, -0.66]], 0.048, C_PIPE, [0.62, 52], [0, 1]);
                        }}
                        exhaustAnchors = [qUnits[3].downpipeOut];
                        if (isSeq) {{
                            this.addSequentialCrossover(qUnits[0].turbOut, qUnits[1].chra, -0.10, 0.040);
                            this.addSequentialCrossover(qUnits[2].turbOut, qUnits[3].chra, -0.10, 0.040);
                        }}
                        this.addPipe(this.staticOpaque, [[icX, 0.15, 0.66], [icX + 0.32, intY, intZ], [-halfLenX * 0.90, intY, intZ]], 0.088, C_PIPE, [0.62, 52], [0, 1]);
                    }} else {{
                        this.addSuperchargerUnit(0, intY + 0.24, intZ, Math.max(0.95, plenW * 0.85), 0.58, -halfLenX - 0.24, intApp, intType);
                        const t = this.addTurboUnit(0.10, exhY, exhZ - 0.42, 1.0, -1);
                        exhaustAnchors = [t.downpipeOut];
                        const icX = -halfLenX - 1.18;
                        this.addIntercooler(icX, 0.06, 0, 0.24, 0.74, 1.38);
                        this.addPipe(this.staticOpaque, [t.compOut, [icX + 0.36, 0.18, exhZ - 0.38], [icX, 0.15, -0.62]], 0.072, C_PIPE, [0.62, 52], [0, 1]);
                        this.addPipe(this.staticOpaque, [[icX, 0.15, 0.62], [icX + 0.28, intY + 0.24, 0.72], [halfLenX * 0.86, intY + 0.24, 0.72], [halfLenX * 0.86, intY + 0.24, intZ], [plenW * 0.45, intY + 0.24, intZ]], 0.076, C_PIPE, [0.62, 52], [0, 2]);
                    }}
                }}

                // Chapa frontal da distribuição + flange traseira da caixa + tubagem de respiro + cambota principal
                if (fmt !== 'WANKEL') {{
                    this.addPart(this.staticTrans, 'bevelBox', this.matTRS(-halfLenX - 0.11, (deckDist - crankR) * 0.36, 0, 0, 0, 0, 0.06, deckDist + crankR + 0.46, Math.max(cylR * 2.5, crankR * 2.5)), C_HEAD, [0.48, 36]);
                }}
                this.addPart(this.staticOpaque, 'cyl', this.matTRS(halfLenX + 0.08, 0, 0, 0, 0, Math.PI * 0.5, 0.42, 0.06, 0.42), C_SUMP, [0.42, 30]);
                this.addPart(this.staticOpaque, 'cyl', this.matTRS(0, 0, 0, 0, 0, Math.PI * 0.5, 0.11, halfLenX * 2.24, 0.11), C_CRANK, [0.68, 58]);
                const damperProfiles = {{
                    'Elastómero OEM':   {{ r: 0.28, thick: 0.105, rim: [0.30, 0.35, 0.42, 1.0], hub: [0.26, 0.44, 0.64, 1.0] }},
                    'Fluido Viscoso':   {{ r: 0.30, thick: 0.130, rim: [0.20, 0.23, 0.28, 1.0], hub: [0.76, 0.80, 0.86, 1.0] }},
                    'ATI Super Damper': {{ r: 0.29, thick: 0.120, rim: [0.15, 0.17, 0.21, 1.0], hub: [0.82, 0.64, 0.28, 1.0] }},
                    'Polia Sólida':     {{ r: 0.23, thick: 0.075, rim: [0.74, 0.78, 0.84, 1.0], hub: [0.72, 0.24, 0.24, 1.0] }}
                }};
                const dProf = damperProfiles[dmpType] || damperProfiles['Elastómero OEM'];
                const dWeight = Math.max(0.1, Math.min(2000.0, Number(this.config.damperWeight) || 3.2));
                const dWScale = Math.max(0.84, Math.min(1.85, 0.88 + Math.log1p(dWeight / 3.2) * 0.16));
                this.dynamicRotors.push({{
                    type: 'pulley',
                    damperStyle: dmpType,
                    cx: -halfLenX - 0.24 - (dWScale - 1.0) * 0.05, cy: 0, cz: 0,
                    r: dProf.r * Math.min(1.42, 0.85 + dWScale * 0.15),
                    thick: dProf.thick * dWScale, speedMult: 1.0,
                    colorRim: dProf.rim,
                    colorHub: dProf.hub
                }});
                const flywheelProfiles = {{
                    'Monomassa Aço':       {{ r: 0.50, thick: 0.110, rim: [0.40, 0.44, 0.50, 1.0], hub: [0.68, 0.72, 0.78, 1.0] }},
                    'Dupla Massa':         {{ r: 0.52, thick: 0.170, rim: [0.32, 0.36, 0.42, 1.0], hub: [0.54, 0.58, 0.65, 1.0] }},
                    'Aligeirado Cromoly':  {{ r: 0.48, thick: 0.082, rim: [0.50, 0.56, 0.64, 1.0], hub: [0.74, 0.64, 0.34, 1.0] }},
                    'Alumínio Billet':     {{ r: 0.49, thick: 0.080, rim: [0.82, 0.86, 0.92, 1.0], hub: [0.66, 0.72, 0.78, 1.0] }},
                    'Carbono Multi-Disco': {{ r: 0.42, thick: 0.075, rim: [0.16, 0.18, 0.21, 1.0], hub: [0.78, 0.60, 0.24, 1.0] }}
                }};
                const fwProf = flywheelProfiles[fwType] || flywheelProfiles['Monomassa Aço'];
                this.dynamicRotors.push({{
                    type: 'flywheel',
                    flywheelStyle: fwType,
                    cx: halfLenX + 0.22, cy: 0, cz: 0,
                    r: fwProf.r, thick: fwProf.thick, speedMult: 1.0,
                    colorRim: fwProf.rim,
                    colorHub: fwProf.hub
                }});

                for (let ci = 0; ci < cylSpecs.length; ci++) {{
                    const c = cylSpecs[ci];
                    const sinA = Math.sin(c.angle), cosA = Math.cos(c.angle);
                    const latY = -sinA, latZ = cosA;
                    const sleeveCenterDist = crankR + rodLen * 0.82;
                    this.addPart(
                        this.staticTrans,
                        'cyl',
                        this.matTRS(c.x, sleeveCenterDist * cosA, c.zOff + sleeveCenterDist * sinA, c.angle, 0, 0, cylR * 1.18, cylLen * 0.96, cylR * 1.18),
                        C_BLOCK,
                        BLK_SPEC
                    );
                    this.addPart(
                        this.staticTrans,
                        'cyl',
                        this.matTRS(c.x, sleeveCenterDist * cosA, c.zOff + sleeveCenterDist * sinA, c.angle, 0, 0, cylR * 1.04, cylLen, cylR * 1.04),
                        [0.34, 0.37, 0.43, 1.0],
                        [0.64, 52]
                    );
                    this.dynamicCyls.push({{
                        x: c.x, zOff: c.zOff, angle: c.angle, phase: c.phase,
                        fireShift: (ci % 2 === 1) ? Math.PI * 2 : 0,
                        cylR, crankR, rodLen, pistonH,
                        cPiston: C_PISTON, cRing: C_RING, cRod: C_ROD, cCrank: C_CRANK
                    }});
                    if (!is2Stroke) {{
                        const xValOffs = valvesCount === 4 ? [-cylR * 0.30, cylR * 0.30] : [0];
                        const vHeadScale = valvesCount === 4 ? 0.19 : 0.27;
                        for (const xOff of xValOffs) {{
                            for (const sideSign of [-1, 1]) {{
                                const latOff = sideSign * (cylR * 0.34);
                                if (!isFreevalve) {{
                                    const seatD = deckDist + 0.105;
                                    const spRad = vType === 'Pneumático' ? 0.048 : 0.040;
                                    this.addPart(
                                        this.staticOpaque,
                                        'cyl',
                                        this.matTRS(c.x + xOff, seatD * cosA + latOff * latY, c.zOff + seatD * sinA + latOff * latZ, c.angle + sideSign * 0.10, 0, 0, spRad * 1.15, 0.012, spRad * 1.15),
                                        C_CRANK,
                                        [0.65, 52]
                                    );
                                    if (camMode !== 'DOHC') {{
                                        const rkD = deckDist + 0.232;
                                        this.addPart(
                                            this.staticOpaque,
                                            'bevelBox',
                                            this.matTRS(c.x + xOff, rkD * cosA + (latOff * 0.55) * latY, c.zOff + rkD * sinA + (latOff * 0.55) * latZ, c.angle, 0, 0, 0.032, 0.024, cylR * 0.42),
                                            C_CRANK,
                                            [0.65, 52]
                                        );
                                    }}
                                }}
                                this.dynamicValves.push({{
                                    x: c.x + xOff, zOff: c.zOff, angle: c.angle,
                                    phase: c.phase * 0.5 + (sideSign > 0 ? 0 : 2.1),
                                    deckDist, cylR, sideSign, vHeadScale,
                                    vType, showSpring: !isFreevalve
                                }});
                            }}
                        }}
                    }}
                }}

                if (isFreevalve && cylSpecs.length) {{
                    const fvOffs = valvesCount === 4 ? [-cylR * 0.30, cylR * 0.30] : [0];
                    this.addFreevalveBank(cylSpecs, fvOffs, deckDist, cylR, halfLenX);
                }}

                if (viewMode === 'all') {{
                    const gbStartX = halfLenX + 0.22 + fwProf.thick * 0.5 + 0.04;
                    const gbInfo = this.addGearboxModel(gbStartX, Math.max(0.56, fwProf.r * 1.14));

                    const {{ exType, tipsMode, exJunc, pipeR, st }} = this.getExhaustParams();
                    const supportsExhJunc = EXHAUST_JUNCTION_FORMATS.includes(fmt);
                    const effExJunc = supportsExhJunc ? exJunc : 'Sem União';
                    const isDualExhaust = exhaustAnchors.length >= 2;
                    const yLine = -0.36;
                    const lanesZ = isDualExhaust
                        ? ((fmt === 'VR' && adm !== 'Biturbo' && adm !== 'Quad Turbo') ? [-0.88, -0.48] : [-0.66, 0.66])
                        : [-0.64];
                    const xMid = gbStartX + 0.28;
                    const xCat = gbStartX + 0.82;
                    const xJunc = gbInfo.xTailEnd + 0.18;
                    const xMuf = xJunc + 0.58;
                    const xTip = xJunc + 1.22;
                    const xStartPipe = [];
                    const pathItems = [];
                    for (let li = 0; li < lanesZ.length; li++) {{
                        const src = exhaustAnchors[li] || [halfLenX + 0.45, yLine, lanesZ[li]];
                        const lz = lanesZ[li];
                        const elbow = [Math.min(src[0] + 0.24, xMid - 0.22), yLine, lz];
                        xStartPipe.push(src);
                        pathItems.push({{ lz, prefixPts: [src, elbow] }});
                    }}
                    this.addExhaustDownstreamSystem({{ lanesZ, yLine, xStartPipe, xMid, xJunc, xCat, xMuf, xTip, pathItems, st, pipeR, exType, tipsMode, exJunc: effExJunc, placeCatBeforeJunc: true }});

                    const xMinAll = -halfLenX - 1.25;
                    const xMaxAll = xTip + 0.38;
                    this.sceneCenterX = (xMinAll + xMaxAll) * 0.5;
                    this.baseDist = Math.max(8.0, (xMaxAll - xMinAll) * 1.04 + maxSpanZ * 1.15);
                }} else {{
                    this.sceneCenterX = 0;
                    this.baseDist = Math.max(5.5, Math.hypot(halfLenX + 0.90, maxSpanZ) * 2.25 + 1.6);
                }}
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

                // Dinâmica de rotação do motor acoplada à curva real de potência/binário, inércia e barra de acelerador (%)
                const inertiaMult = Math.max(0.35, Math.min(12.0, engineSim.inertiaFactor || 1.0));
                const invInertia = 1.0 / inertiaMult;
                if (!engineSim.on) {{
                    if (engineSim.throttlePct !== 0 || engineSim.spaceHeld) {{
                        engineSim.spaceHeld = false;
                        engineSim.preSpaceThrottlePct = 0;
                        setThrottlePercent(0);
                    }}
                    engineSim.currentRpm += (0 - engineSim.currentRpm) * Math.min(1, dt * 5.2 * invInertia);
                    if (engineSim.currentRpm < 15) engineSim.currentRpm = 0;
                }} else {{
                    const thr = Math.max(0, Math.min(1, (engineSim.throttlePct || 0) / 100));
                    const maxR = Math.max(1500, engineSim.maxRpm || 7500);
                    const idle = Math.min(maxR - 200, Math.max(600, engineSim.idleRpm || 950));
                    const idleJitter = idle + Math.sin(now * 0.008) * 18;
                    if (thr <= 0.005) {{
                        if (engineSim.currentRpm > idle + 25) {{
                            const decayFactor = Math.min(1, dt * 5.6 * invInertia);
                            const linearDrop = dt * (950 + engineSim.currentRpm * 0.14) * invInertia * 0.55;
                            const expDrop = engineSim.currentRpm - (engineSim.currentRpm - idleJitter) * decayFactor;
                            engineSim.currentRpm = Math.max(idleJitter, Math.min(expDrop, engineSim.currentRpm - linearDrop));
                        }} else {{
                            engineSim.currentRpm += (idleJitter - engineSim.currentRpm) * Math.min(1, dt * 6.2 * invInertia);
                        }}
                    }} else {{
                        const targetRpm = idle + (maxR - idle) * Math.pow(thr, 0.85);
                        if (engineSim.currentRpm < targetRpm) {{
                            const inst = sampleDynoAtRpm(Math.max(engineSim.currentRpm, idle));
                            const rotJ = Math.max(0.055, engineSim.rotInertia || (0.15 * inertiaMult));
                            const rawDrive = (inst.torqueNm * 2.15 + inst.powerKw * 3.35) / rotJ;
                            const thrGain = 0.18 + 0.82 * thr;
                            const climbRate = Math.max(65, Math.min(22000, rawDrive)) * thrGain;
                            const gap = targetRpm - engineSim.currentRpm;
                            const rawStep = Math.min(gap, climbRate * dt);
                            const step = thr >= 0.98 ? rawStep : Math.min(rawStep, gap * Math.min(1, dt * 11.0));
                            engineSim.currentRpm += step;
                        }} else if (engineSim.currentRpm > targetRpm) {{
                            const decayFactor = Math.min(1, dt * 4.4 * invInertia);
                            const linearDrop = dt * (950 + engineSim.currentRpm * 0.14) * invInertia * 0.55;
                            const expDrop = engineSim.currentRpm - (engineSim.currentRpm - targetRpm) * decayFactor;
                            engineSim.currentRpm = Math.max(targetRpm, Math.min(expDrop, engineSim.currentRpm - linearDrop));
                        }}
                        if (thr >= 0.98 && engineSim.currentRpm >= maxR * 0.985) {{
                            // Oscilação realista de corte de rotação proporcional ao volante e potência
                            engineSim.currentRpm = maxR * (0.975 + 0.025 * Math.sin(now * 0.045));
                        }}
                    }}
                }}

                // Velocidade angular proporcional às RPM reais configuradas (com divisor Slow Mo 1x/2x/5x/10x),
                // com limite anti-aliasing para evitar ilusão estroboscópica em dois sentidos aos 60 Hz
                if (engineSim.currentRpm > 5) {{
                    const rpm = engineSim.currentRpm;
                    const slowDiv = Math.max(1, engineSim.slowMo || 1);
                    const omega = Math.min(48.0, 2.5 + Math.pow(rpm / 100, 0.55) * 3.1);
                    const crankStep = Math.min(0.62, (dt * omega) / slowDiv);
                    this.crankAngle += crankStep;
                    const impMult = 1.0 + Math.min(2.0, Math.max(0, Number(this.config.turboBar) || 0) * 0.25);
                    const uRpm = rpm / Math.max(1, engineSim.maxRpm || 7500);
                    for (const r of this.dynamicRotors) {{
                        const sym = r.symmetry || (r.type === 'impeller' ? 7 : 1);
                        const maxSafeStep = (Math.PI * 0.56) / sym;
                        let mult = r.speedMult;
                        if (r.type === 'impeller') {{
                            let stageFactor = impMult;
                            if (r.stage === 'primary') stageFactor *= 1.18;
                            else if (r.stage === 'secondary') stageFactor *= (0.24 + 0.86 * smoothstep(0.32, 0.58, uRpm));
                            mult = r.speedMult * stageFactor;
                        }}
                        const rotorStep = Math.min(maxSafeStep, crankStep * mult);
                        r.angle = ((r.angle || 0) + rotorStep) % (Math.PI * 2);
                    }}
                    const gasSpeed = 0.45 + Math.min(2.2, (rpm / Math.max(1500, engineSim.maxRpm || 7500)) * 2.0);
                    this.gasFlowPhase = (this.gasFlowPhase + (dt * gasSpeed) / slowDiv) % 1000.0;
                }} else if ((this.config.viewMode || 'engine') === 'exhaust' || (this.config.viewMode || 'engine') === 'all') {{
                    this.gasFlowPhase = (this.gasFlowPhase + dt * 0.16) % 1000.0;
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
                    }} else {{
                        const refRpm = engineSim.hoverRpm !== null ? engineSim.hoverRpm : engineSim.currentRpm;
                        const s = sampleDynoAtRpm(refRpm);
                        dynoLiveReadout.textContent = `${{Math.round(refRpm)}} RPM · ${{formatPowerStr(s.powerKw)}} · ${{formatTorqueStr(s.torqueNm)}}`;
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

                // Pistões, bielas e contrapesos da cambota
                for (const c of this.dynamicCyls) {{
                    const phi = this.crankAngle + c.phase;
                    const yPin = c.crankR * Math.cos(phi);
                    const zPin = c.crankR * Math.sin(phi);
                    const uPin = c.crankR * Math.cos(phi - c.angle);
                    const vPin = c.crankR * Math.sin(phi - c.angle);
                    const uPis = uPin + Math.sqrt(Math.max(0.0001, c.rodLen * c.rodLen - vPin * vPin));

                    const cosA = Math.cos(c.angle), sinA = Math.sin(c.angle);
                    const yPis = uPis * cosA;
                    const zPis = uPis * sinA;
                    const zPinGlobal = c.zOff + zPin;
                    const zPisGlobal = c.zOff + zPis;

                    for (const cheekOff of [-0.088, 0.088]) {{
                        const webM = this.matSpinX(c.x + cheekOff, 0, c.zOff, phi, 0, 0, 0, 0.044, c.crankR, c.crankR);
                        this.drawItem(this.meshes.crankWeb, webM, c.cCrank, [0.64, 52], viewProj);
                        const tungM = this.matSpinX(c.x + cheekOff, -yPin * 0.96, c.zOff - zPin * 0.96, phi, 0, 0, Math.PI * 0.5, 0.048, 0.048, 0.048);
                        this.drawItem(this.meshes.cyl, tungM, [0.76, 0.58, 0.24, 1.0], [0.76, 60], viewProj);
                    }}
                    const pinM = this.matSpinX(c.x, yPin, zPinGlobal, phi, 0, 0, Math.PI * 0.5, 0.075, 0.148, 0.075);
                    this.drawItem(this.meshes.cyl, pinM, c.cCrank, [0.70, 58], viewProj);

                    const rodAngle = Math.atan2(zPisGlobal - zPinGlobal, yPis - yPin);
                    const rodMidY = (yPin + yPis) * 0.5;
                    const rodMidZ = (zPinGlobal + zPisGlobal) * 0.5;
                    const rodDark = [c.cRod[0] * 0.78, c.cRod[1] * 0.78, c.cRod[2] * 0.78, 1.0];
                    const rodWebM = this.matTRS(c.x, rodMidY, rodMidZ, rodAngle, 0, 0, 0.028, c.rodLen * 0.96, 0.056);
                    this.drawItem(this.meshes.bevelBox, rodWebM, rodDark, [0.58, 44], viewProj);
                    const rSin = Math.sin(rodAngle), rCos = Math.cos(rodAngle);
                    for (const fOff of [-0.028, 0.028]) {{
                        const rFlangeM = this.matTRS(c.x, rodMidY - fOff * rSin, rodMidZ + fOff * rCos, rodAngle, 0, 0, 0.058, c.rodLen * 0.94, 0.019);
                        this.drawItem(this.meshes.bevelBox, rFlangeM, c.cRod, [0.70, 56], viewProj);
                    }}
                    const yWrist = 2.0 * rodMidY - yPin;
                    const zWrist = 2.0 * rodMidZ - zPinGlobal;
                    const wristEyeM = this.matSpinX(c.x, yWrist, zWrist, rodAngle, 0, 0, Math.PI * 0.5, 0.068, 0.074, 0.068);
                    this.drawItem(this.meshes.cyl, wristEyeM, [0.80, 0.62, 0.28, 1.0], [0.76, 58], viewProj);
                    // Cabeça da biela bipartida no moente + parafusos hexagonais ARP
                    const bigEndM = this.matSpinX(c.x, yPin, zPinGlobal, rodAngle, 0, 0, Math.PI * 0.5, 0.106, 0.108, 0.106);
                    this.drawItem(this.meshes.cyl, bigEndM, c.cRod, [0.64, 50], viewProj);
                    const shellM = this.matSpinX(c.x, yPin, zPinGlobal, rodAngle, 0, 0, Math.PI * 0.5, 0.088, 0.114, 0.088);
                    this.drawItem(this.meshes.cyl, shellM, [0.78, 0.60, 0.26, 1.0], [0.78, 60], viewProj);
                    for (const bSide of [-0.054, 0.054]) {{
                        const bPosY = yPin - bSide * rSin;
                        const bPosZ = zPinGlobal + bSide * rCos;
                        const boltM = this.matTRS(c.x, bPosY - 0.044 * rCos, bPosZ - 0.044 * rSin, rodAngle, 0, 0, 0.022, 0.072, 0.022);
                        this.drawItem(this.meshes.hex, boltM, [0.84, 0.87, 0.92, 1.0], [0.82, 64], viewProj);
                    }}

                    // Pistão forjado: saia aliviada com patins em grafite + cúpula chanfrada + cavidade + 3 anéis distintos
                    const pisM = this.matTRS(c.x, yPis, zPisGlobal, c.angle, 0, 0, c.cylR * 0.88, c.pistonH * 0.86, c.cylR * 0.88);
                    this.drawItem(this.meshes.cyl, pisM, c.cPiston, [0.78, 64], viewProj);
                    for (const padSide of [-1, 1]) {{
                        const padOff = padSide * (c.cylR * 0.84);
                        const padM = this.matTRS(c.x, yPis - (c.pistonH * 0.12) * cosA - padOff * sinA, zPisGlobal - (c.pistonH * 0.12) * sinA + padOff * cosA, c.angle, 0, 0, c.cylR * 0.95, c.pistonH * 0.42, 0.022);
                        this.drawItem(this.meshes.bevelBox, padM, [0.16, 0.18, 0.22, 1.0], [0.28, 18], viewProj);
                    }}
                    const crownOff = c.pistonH * 0.47;
                    const crownM = this.matTRS(c.x, yPis + crownOff * cosA, zPisGlobal + crownOff * sinA, c.angle, 0, 0, c.cylR * 0.82, 0.042, c.cylR * 0.82);
                    this.drawItem(this.meshes.cone, crownM, [0.90, 0.93, 0.96, 1.0], [0.86, 74], viewProj);
                    const dishM = this.matTRS(c.x, yPis + (crownOff + 0.018) * cosA, zPisGlobal + (crownOff + 0.018) * sinA, c.angle, 0, 0, c.cylR * 0.36, 0.012, c.cylR * 0.36);
                    this.drawItem(this.meshes.cyl, dishM, [0.28, 0.31, 0.36, 1.0], [0.35, 22], viewProj);
                    const wristPinM = this.matTRS(c.x, yPis - (c.pistonH * 0.10) * cosA, zPisGlobal - (c.pistonH * 0.10) * sinA, 0, 0, Math.PI * 0.5, 0.050, c.cylR * 1.50, 0.050);
                    this.drawItem(this.meshes.cyl, wristPinM, c.cCrank, [0.72, 56], viewProj);
                    const ringOffset = c.pistonH * 0.31;
                    const ring1M = this.matTRS(c.x, yPis + ringOffset * cosA, zPisGlobal + ringOffset * sinA, c.angle, 0, 0, c.cylR * 0.905, 0.022, c.cylR * 0.905);
                    this.drawItem(this.meshes.cyl, ring1M, [0.92, 0.95, 0.98, 1.0], [0.86, 72], viewProj);
                    const ring2M = this.matTRS(c.x, yPis + (ringOffset * 0.64) * cosA, zPisGlobal + (ringOffset * 0.64) * sinA, c.angle, 0, 0, c.cylR * 0.902, 0.022, c.cylR * 0.902);
                    this.drawItem(this.meshes.cyl, ring2M, c.cRing, [0.42, 26], viewProj);
                    const ring3M = this.matTRS(c.x, yPis + (ringOffset * 0.28) * cosA, zPisGlobal + (ringOffset * 0.28) * sinA, c.angle, 0, 0, c.cylR * 0.902, 0.028, c.cylR * 0.902);
                    this.drawItem(this.meshes.cyl, ring3M, [0.78, 0.56, 0.24, 1.0], [0.74, 56], viewProj);
                }}

                // Rotores epitrocoidais Wankel, excêntricos e selos de vértice
                for (const w of this.dynamicWankel) {{
                    const phi = this.crankAngle + w.phase;
                    const ey = w.ecc * Math.cos(phi);
                    const ez = w.ecc * Math.sin(phi);
                    const rotorSpin = phi / 3.0;

                    const eccM = this.matSpinX(w.x, ey * 0.72, ez * 0.72, phi, 0, 0, Math.PI * 0.5, w.rotorR * 0.25, w.rotorW * 0.92, w.rotorR * 0.25);
                    this.drawItem(this.meshes.cyl, eccM, w.cShaft, [0.65, 52], viewProj);

                    const rotM = this.matSpinX(w.x, ey, ez, rotorSpin, 0, 0, 0, w.rotorW, w.rotorR, w.rotorR);
                    this.drawItem(this.meshes.wankelRotor, rotM, w.cRotor, [0.76, 62], viewProj);

                    const hubGearM = this.matSpinX(w.x, ey, ez, rotorSpin, 0, 0, Math.PI * 0.5, w.rotorR * 0.34, w.rotorW * 1.06, w.rotorR * 0.34);
                    this.drawItem(this.meshes.gear, hubGearM, w.cGear, [0.76, 60], viewProj);

                    const oilSealM = this.matSpinX(w.x, ey, ez, rotorSpin, 0, 0, Math.PI * 0.5, w.rotorR * 0.46, w.rotorW * 1.04, w.rotorR * 0.46);
                    this.drawItem(this.meshes.cyl, oilSealM, w.cSeal, [0.45, 32], viewProj);

                    for (let k = 0; k < 3; k++) {{
                        const a = rotorSpin + (k * Math.PI * 2) / 3;
                        const ay = ey + Math.cos(a) * w.rotorR;
                        const az = ez + Math.sin(a) * w.rotorR;
                        const sealM = this.matSpinX(w.x, ay, az, a, 0, 0, 0, w.rotorW * 1.02, 0.045, 0.028);
                        this.drawItem(this.meshes.box, sealM, w.cSeal, [0.72, 54], viewProj);
                    }}
                }}

                // Came rotativo interno + Válvulas animadas de admissão e escape
                const camMult = this.config.ciclo === '2T' ? 1.0 : 0.5;
                for (const cam of this.dynamicCams) {{
                    const ang = this.crankAngle * camMult + cam.phase;
                    const lobeM = this.matTRS(cam.x, cam.y, cam.z, ang - Math.PI * 0.5, 0, 0, 0.054, 0.165, 0.165);
                    this.drawItem(this.meshes.camLobe, lobeM, [0.78, 0.82, 0.88, 1.0], [0.76, 62], viewProj);
                }}
                for (const v of this.dynamicValves) {{
                    const camAng = this.crankAngle * camMult + v.phase;
                    const lift = Math.pow(Math.max(0, Math.sin(camAng)), 2) * 0.085;
                    const axY = Math.cos(v.angle), axZ = Math.sin(v.angle);
                    const latY = -axZ, latZ = axY;
                    const latOff = v.sideSign * (v.cylR * 0.34);
                    const tilt = v.angle + v.sideSign * 0.10;
                    const dHead = v.deckDist + 0.035 - lift;
                    const dStem = v.deckDist + 0.15 - lift;
                    const vRadius = v.cylR * (v.vHeadScale || 0.22);
                    const vHeadM = this.matTRS(v.x, dHead * axY + latOff * latY, v.zOff + dHead * axZ + latOff * latZ, tilt, 0, 0, vRadius, 0.022, vRadius);
                    this.drawItem(this.meshes.cyl, vHeadM, [0.85, 0.88, 0.92, 1.0], [0.82, 68], viewProj);
                    const vStemM = this.matTRS(v.x, dStem * axY + latOff * latY, v.zOff + dStem * axZ + latOff * latZ, tilt, 0, 0, 0.019, 0.22, 0.019);
                    this.drawItem(this.meshes.cyl, vStemM, [0.72, 0.76, 0.82, 1.0], [0.75, 60], viewProj);
                    if (v.showSpring) {{
                        const retD = v.deckDist + 0.21 - lift;
                        const seatD = v.deckDist + 0.11;
                        const spH = Math.max(0.024, retD - seatD);
                        const spMidD = seatD + spH * 0.5;
                        const spMesh = v.vType === 'Pneumático' ? this.meshes.cyl : this.meshes.spring;
                        const spCol = v.vType === 'Pneumático'
                            ? [0.62, 0.78, 0.86, 1.0]
                            : (v.vType === 'Desmodrómico' ? [0.72, 0.56, 0.32, 1.0] : [0.78, 0.82, 0.88, 1.0]);
                        const spRad = v.vType === 'Pneumático' ? 0.048 : 0.044;
                        const spM = this.matTRS(v.x, spMidD * axY + latOff * latY, v.zOff + spMidD * axZ + latOff * latZ, tilt, 0, 0, spRad, spH, spRad);
                        this.drawItem(spMesh, spM, spCol, [0.74, 58], viewProj);
                        const retM = this.matTRS(v.x, retD * axY + latOff * latY, v.zOff + retD * axZ + latOff * latZ, tilt, 0, 0, spRad * 1.18, 0.016, spRad * 1.18);
                        this.drawItem(this.meshes.cyl, retM, [0.78, 0.82, 0.88, 1.0], [0.80, 64], viewProj);
                    }}
                }}

                // Rodas/polias multi-raios e compressor 7 pás estáticos na posição e a rodar apenas num sentido em torno do eixo X
                for (const r of this.dynamicRotors) {{
                    const ang = r.angle !== undefined ? r.angle : this.crankAngle * r.speedMult;
                    if (r.type === 'pulley') {{
                        const rimM = this.matSpinX(r.cx, r.cy, r.cz, ang, 0, 0, Math.PI * 0.5, r.r, r.thick, r.r);
                        if (r.damperStyle) {{
                            const isFluid = r.damperStyle === 'Fluido Viscoso';
                            this.drawItem(isFluid ? this.meshes.cyl : this.meshes.gear, rimM, r.colorRim, isFluid ? [0.78, 68] : [0.64, 52], viewProj);
                            if (r.damperStyle === 'Elastómero OEM') {{
                                const elastM = this.matSpinX(r.cx - r.thick * 0.28, r.cy, r.cz, ang, 0, 0, Math.PI * 0.5, r.r * 0.72, r.thick * 0.56, r.r * 0.72);
                                this.drawItem(this.meshes.cyl, elastM, [0.09, 0.10, 0.12, 1.0], [0.15, 10], viewProj);
                            }} else if (isFluid) {{
                                const sealRingM = this.matSpinX(r.cx - r.thick * 0.42, r.cy, r.cz, ang, 0, 0, Math.PI * 0.5, r.r * 0.88, r.thick * 0.26, r.r * 0.88);
                                this.drawItem(this.meshes.cyl, sealRingM, [0.78, 0.82, 0.87, 1.0], [0.85, 72], viewProj);
                            }} else if (r.damperStyle === 'ATI Super Damper') {{
                                for (let b = 0; b < 6; b++) {{
                                    const ba = ang + (b * Math.PI * 2) / 6;
                                    const bRad = r.r * 0.68;
                                    const boltM = this.matSpinX(r.cx - r.thick * 0.52, r.cy + Math.cos(ba) * bRad, r.cz + Math.sin(ba) * bRad, ba, 0, 0, Math.PI * 0.5, 0.022, 0.028, 0.022);
                                    this.drawItem(this.meshes.hex, boltM, [0.86, 0.89, 0.94, 1.0], [0.84, 64], viewProj);
                                }}
                            }} else if (r.damperStyle === 'Polia Sólida') {{
                                for (let s = 0; s < 3; s++) {{
                                    const sa = ang + (s * Math.PI * 2) / 3;
                                    const spM = this.matTRS(r.cx - r.thick * 0.44, r.cy + Math.cos(sa) * (r.r * 0.44), r.cz + Math.sin(sa) * (r.r * 0.44), sa, 0, 0, 0.024, r.r * 0.76, 0.032);
                                    this.drawItem(this.meshes.box, spM, [0.20, 0.23, 0.28, 1.0], [0.55, 42], viewProj);
                                }}
                            }}
                            const hubM = this.matSpinX(r.cx - r.thick * 0.35, r.cy, r.cz, ang, 0, 0, Math.PI * 0.5, r.r * 0.48, r.thick * 0.65, r.r * 0.48);
                            this.drawItem(this.meshes.cyl, hubM, r.colorHub, [0.76, 64], viewProj);
                            const timingBarM = this.matTRS(r.cx - r.thick * 0.54, r.cy + Math.cos(ang) * (r.r * 0.40), r.cz + Math.sin(ang) * (r.r * 0.40), ang, 0, 0, 0.024, r.r * 0.74, 0.038);
                            this.drawItem(this.meshes.box, timingBarM, r.colorHub, [0.72, 58], viewProj);
                        }} else {{
                            this.drawItem(this.meshes.gear, rimM, r.colorRim, [0.64, 52], viewProj);
                            const hubM = this.matSpinX(r.cx - r.thick * 0.35, r.cy, r.cz, ang, 0, 0, Math.PI * 0.5, r.r * 0.44, r.thick * 0.65, r.r * 0.44);
                            this.drawItem(this.meshes.cyl, hubM, r.colorHub, [0.76, 64], viewProj);
                            for (let sp = 0; sp < 4; sp++) {{
                                const sAng = ang + sp * Math.PI * 0.5;
                                const spokeM = this.matTRS(r.cx - r.thick * 0.54, r.cy + Math.cos(sAng) * (r.r * 0.42), r.cz + Math.sin(sAng) * (r.r * 0.42), sAng, 0, 0, 0.024, r.r * 0.72, 0.036);
                                this.drawItem(this.meshes.box, spokeM, sp === 0 ? r.colorHub : [0.56, 0.61, 0.68, 1.0], [0.74, 60], viewProj);
                            }}
                        }}
                        const pinMarkM = this.matTRS(r.cx - r.thick * 0.56, r.cy + Math.cos(ang) * (r.r * 0.74), r.cz + Math.sin(ang) * (r.r * 0.74), ang, 0, 0, 0.034, 0.055, 0.055);
                        this.drawItem(this.meshes.box, pinMarkM, [0.92, 0.34, 0.24, 1.0], [0.7, 56], viewProj);
                        const boltCenterM = this.matSpinX(r.cx - r.thick * 0.62, r.cy, r.cz, ang, 0, 0, Math.PI * 0.5, r.r * 0.20, r.thick * 0.45, r.r * 0.20);
                        this.drawItem(this.meshes.hex, boltCenterM, [0.84, 0.87, 0.92, 1.0], [0.84, 68], viewProj);
                    }} else if (r.type === 'flywheel') {{
                        const fwS = r.flywheelStyle || 'Monomassa Aço';
                        const ringM = this.matSpinX(r.cx, r.cy, r.cz, ang, 0, 0, Math.PI * 0.5, r.r, r.thick, r.r);
                        this.drawItem(this.meshes.cyl, ringM, r.colorRim, fwS === 'Carbono Multi-Disco' ? [0.24, 18] : [0.58, 48], viewProj);
                        const gDelta = this.crankAngle - (r.lastGearCrank !== undefined ? r.lastGearCrank : this.crankAngle);
                        r.lastGearCrank = this.crankAngle;
                        const gStep = gDelta >= 0 ? gDelta : 0;
                        r.gearAngle = ((r.gearAngle || 0) + Math.min(0.11, gStep * (r.speedMult || 1))) % (Math.PI * 2);
                        const teethRingM = this.matSpinX(r.cx - r.thick * 0.25, r.cy, r.cz, r.gearAngle, 0, 0, Math.PI * 0.5, r.r * 1.03, r.thick * 0.30, r.r * 1.03);
                        this.drawItem(this.meshes.gear, teethRingM, [0.56, 0.60, 0.66, 1.0], [0.72, 56], viewProj);
                        const frictionRingM = this.matSpinX(r.cx - r.thick * 0.38, r.cy, r.cz, ang, 0, 0, Math.PI * 0.5, r.r * 0.78, r.thick * 0.18, r.r * 0.78);
                        this.drawItem(this.meshes.cyl, frictionRingM, fwS === 'Alumínio Billet' ? [0.30, 0.34, 0.40, 1.0] : [0.22, 0.25, 0.30, 1.0], [0.42, 32], viewProj);
                        if (fwS === 'Dupla Massa') {{
                            const dmfCoreM = this.matSpinX(r.cx + r.thick * 0.04, r.cy, r.cz, ang, 0, 0, Math.PI * 0.5, r.r * 0.86, r.thick * 0.46, r.r * 0.86);
                            this.drawItem(this.meshes.cyl, dmfCoreM, [0.12, 0.14, 0.18, 1.0], [0.22, 16], viewProj);
                            for (let k = 0; k < 4; k++) {{
                                const ka = ang + (k * Math.PI) / 2;
                                const sprM = this.matTRS(r.cx + r.thick * 0.48, r.cy + Math.cos(ka) * (r.r * 0.56), r.cz + Math.sin(ka) * (r.r * 0.56), ka, 0, 0, 0.025, r.r * 0.26, 0.065);
                                this.drawItem(this.meshes.box, sprM, [0.76, 0.56, 0.22, 1.0], [0.70, 54], viewProj);
                            }}
                        }} else if (fwS === 'Aligeirado Cromoly') {{
                            for (let k = 0; k < 4; k++) {{
                                const ka = ang + (k * Math.PI) / 2;
                                const cutM = this.matTRS(r.cx + r.thick * 0.48, r.cy + Math.cos(ka) * (r.r * 0.56), r.cz + Math.sin(ka) * (r.r * 0.56), ka, 0, 0, 0.028, r.r * 0.34, 0.070);
                                this.drawItem(this.meshes.box, cutM, [0.16, 0.19, 0.24, 1.0], [0.35, 22], viewProj);
                            }}
                        }} else if (fwS === 'Alumínio Billet') {{
                            for (let k = 0; k < 8; k++) {{
                                const ka = ang + (k * Math.PI * 2) / 8;
                                const rPos = r.r * 0.72;
                                const rivM = this.matSpinX(r.cx + r.thick * 0.46, r.cy + Math.cos(ka) * rPos, r.cz + Math.sin(ka) * rPos, ka, 0, 0, Math.PI * 0.5, 0.026, 0.030, 0.026);
                                this.drawItem(this.meshes.hex, rivM, [0.80, 0.62, 0.26, 1.0], [0.80, 62], viewProj);
                            }}
                        }} else if (fwS === 'Carbono Multi-Disco') {{
                            const coverM = this.matSpinX(r.cx + r.thick * 0.42, r.cy, r.cz, ang, 0, 0, Math.PI * 0.5, r.r * 0.84, r.thick * 0.42, r.r * 0.84);
                            this.drawItem(this.meshes.cyl, coverM, [0.78, 0.60, 0.24, 1.0], [0.80, 64], viewProj);
                        }}
                        const hexNutM = this.matSpinX(r.cx + r.thick * 0.56, r.cy, r.cz, ang, 0, 0, Math.PI * 0.5, r.r * 0.18, r.thick * 0.42, r.r * 0.18);
                        this.drawItem(this.meshes.hex, hexNutM, [0.84, 0.87, 0.92, 1.0], [0.84, 66], viewProj);
                        const faceM = this.matSpinX(r.cx + r.thick * 0.32, r.cy, r.cz, ang, 0, 0, Math.PI * 0.5, r.r * 0.78, r.thick * 0.55, r.r * 0.78);
                        this.drawItem(this.meshes.cyl, faceM, r.colorHub, [0.72, 60], viewProj);
                        const bossM = this.matSpinX(r.cx + r.thick * 0.60, r.cy, r.cz, ang, 0, 0, Math.PI * 0.5, r.r * 0.26, r.thick * 0.35, r.r * 0.26);
                        this.drawItem(this.meshes.cyl, bossM, r.colorRim, [0.75, 62], viewProj);
                        const notchM = this.matTRS(r.cx + r.thick * 0.58, r.cy + Math.cos(ang) * (r.r * 0.48), r.cz + Math.sin(ang) * (r.r * 0.48), ang, 0, 0, 0.032, r.r * 0.56, 0.055);
                        this.drawItem(this.meshes.box, notchM, [0.92, 0.34, 0.24, 1.0], [0.6, 48], viewProj);
                    }} else if (r.type === 'impeller') {{
                        const noseM = this.matSpinX(r.cx - 0.02, r.cy, r.cz, ang, 0, 0, Math.PI * 0.5, r.r * 0.26, 0.08, r.r * 0.26);
                        this.drawItem(this.meshes.cone, noseM, r.colorHub, [0.78, 64], viewProj);
                        const wheelM = this.matSpinX(r.cx - 0.01, r.cy, r.cz, ang, 0, 0, Math.PI * 0.5, r.r, 0.075, r.r);
                        this.drawItem(this.meshes.impeller, wheelM, r.colorBlade, [0.86, 74], viewProj);
                    }} else if (r.type === 'clutchAssembly') {{
                        const cs = r.clutchStyle || 'Monodisco Orgânica';
                        const hubM = this.matSpinX(r.cx, r.cy, r.cz, ang, 0, 0, Math.PI * 0.5, r.r * 0.32, 0.18, r.r * 0.32);
                        this.drawItem(this.meshes.cyl, hubM, [0.76, 0.80, 0.86, 1.0], [0.78, 62], viewProj);
                        if (cs === 'Conversor de Binário') {{
                            const convM = this.matSpinX(r.cx, r.cy, r.cz, ang, 0, Math.PI * 0.5, 0, r.r * 0.86, r.r * 0.86, r.r * 0.86);
                            this.drawItem(this.meshes.torus, convM, [0.28, 0.38, 0.52, 1.0], [0.68, 54], viewProj);
                            for (let k = 0; k < 6; k++) {{
                                const ka = ang + (k * Math.PI * 2) / 6;
                                const vaneM = this.matTRS(r.cx, r.cy + Math.cos(ka) * (r.r * 0.48), r.cz + Math.sin(ka) * (r.r * 0.48), ka, 0, 0, 0.08, r.r * 0.34, 0.025);
                                this.drawItem(this.meshes.box, vaneM, [0.78, 0.58, 0.24, 1.0], [0.72, 56], viewProj);
                            }}
                        }} else if (cs === 'Cerâmica Racing') {{
                            const cRim = this.matSpinX(r.cx - 0.04, r.cy, r.cz, ang, 0, 0, Math.PI * 0.5, r.r * 0.94, 0.036, r.r * 0.94);
                            this.drawItem(this.meshes.cyl, cRim, [0.74, 0.22, 0.22, 1.0], [0.70, 56], viewProj);
                            for (let k = 0; k < 6; k++) {{
                                const ka = ang + (k * Math.PI * 2) / 6;
                                const padM = this.matTRS(r.cx + 0.02, r.cy + Math.cos(ka) * (r.r * 0.58), r.cz + Math.sin(ka) * (r.r * 0.58), ka, 0, 0, 0.045, r.r * 0.38, 0.095);
                                this.drawItem(this.meshes.bevelBox, padM, [0.82, 0.50, 0.20, 1.0], [0.76, 60], viewProj);
                            }}
                        }} else if (cs === 'Duplo Disco Aço') {{
                            for (const dOff of [-0.045, 0.045]) {{
                                const discM = this.matSpinX(r.cx + dOff, r.cy, r.cz, ang, 0, 0, Math.PI * 0.5, r.r * 0.88, 0.030, r.r * 0.88);
                                this.drawItem(this.meshes.cyl, discM, [0.48, 0.53, 0.60, 1.0], [0.64, 48], viewProj);
                            }}
                            const midM = this.matSpinX(r.cx, r.cy, r.cz, ang, 0, 0, Math.PI * 0.5, r.r * 0.94, 0.024, r.r * 0.94);
                            this.drawItem(this.meshes.cyl, midM, [0.78, 0.82, 0.88, 1.0], [0.80, 66], viewProj);
                        }} else if (cs === 'Carbono Multi-Disco') {{
                            for (const dOff of [-0.055, 0.0, 0.055]) {{
                                const cDiscM = this.matSpinX(r.cx + dOff, r.cy, r.cz, ang, 0, 0, Math.PI * 0.5, r.r * 0.82, 0.022, r.r * 0.82);
                                this.drawItem(this.meshes.cyl, cDiscM, [0.14, 0.16, 0.20, 1.0], [0.30, 20], viewProj);
                            }}
                            for (let k = 0; k < 6; k++) {{
                                const ka = ang + (k * Math.PI * 2) / 6;
                                const postM = this.matTRS(r.cx + 0.01, r.cy + Math.cos(ka) * (r.r * 0.86), r.cz + Math.sin(ka) * (r.r * 0.86), ka, 0, 0, 0.15, 0.05, 0.06);
                                this.drawItem(this.meshes.bevelBox, postM, [0.84, 0.64, 0.24, 1.0], [0.82, 64], viewProj);
                            }}
                        }} else {{
                            // Monodisco Orgânica
                            const orgM = this.matSpinX(r.cx - 0.02, r.cy, r.cz, ang, 0, 0, Math.PI * 0.5, r.r * 0.90, 0.036, r.r * 0.90);
                            this.drawItem(this.meshes.cyl, orgM, [0.24, 0.22, 0.20, 1.0], [0.24, 16], viewProj);
                            const covM = this.matSpinX(r.cx + 0.04, r.cy, r.cz, ang, 0, 0, -Math.PI * 0.5, r.r * 0.92, 0.09, r.r * 0.92);
                            this.drawItem(this.meshes.cone, covM, [0.64, 0.68, 0.74, 1.0], [0.66, 52], viewProj);
                        }}
                    }} else if (r.type === 'gearboxGear') {{
                        const gDelta = this.crankAngle - (r.lastGearCrank !== undefined ? r.lastGearCrank : this.crankAngle);
                        r.lastGearCrank = this.crankAngle;
                        const gStep = gDelta >= 0 ? gDelta : 0;
                        r.gearAngle = ((r.gearAngle || 0) + Math.max(-0.11, Math.min(0.11, gStep * (r.speedMult || 1)))) % (Math.PI * 2);
                        const gearM = this.matSpinX(r.cx, r.cy, r.cz, r.gearAngle, 0, 0, Math.PI * 0.5, r.r, r.thick, r.r);
                        this.drawItem(this.meshes.gear, gearM, r.colorRim, [0.74, 58], viewProj);
                    }} else if (r.type === 'driveshaft') {{
                        const yokeM = this.matTRS(r.cx, r.cy, r.cz, ang, 0, 0, 0.09, r.r * 1.45, r.r * 1.45);
                        this.drawItem(this.meshes.bevelBox, yokeM, r.colorHub, [0.72, 56], viewProj);
                        const shaftM = this.matSpinX(r.cx + 0.24, r.cy, r.cz, ang, 0, 0, Math.PI * 0.5, r.r * 0.54, 0.52, r.r * 0.54);
                        this.drawItem(this.meshes.cyl, shaftM, r.colorRim, [0.80, 66], viewProj);
                        const stripeM = this.matTRS(r.cx + 0.26, r.cy + Math.cos(ang) * (r.r * 0.55), r.cz + Math.sin(ang) * (r.r * 0.55), ang, 0, 0, 0.36, 0.022, 0.022);
                        this.drawItem(this.meshes.box, stripeM, [0.92, 0.34, 0.24, 1.0], [0.5, 36], viewProj);
                    }}
                }}

                // Fluxo animado dos gases de escape (no modo Escape ou Tudo Junto) + chamas nas ponteiras
                const curViewMode = this.config.viewMode || 'engine';
                if (this.exhaustGasPaths.length && (curViewMode === 'exhaust' || curViewMode === 'all')) {{
                    gl.enable(gl.BLEND);
                    gl.blendFunc(gl.SRC_ALPHA, gl.ONE);
                    gl.depthMask(false);
                    const isActive = engineSim.on && engineSim.currentRpm > 20;
                    const alphaScale = isActive ? 0.92 : 0.34;
                    const rScale = isActive ? (0.95 + 0.35 * (engineSim.currentRpm / Math.max(1500, engineSim.maxRpm || 7500))) : 0.75;
                    const nitroExh = this.config.combustivel === 'Nitrometano';
                    for (const gp of this.exhaustGasPaths) {{
                        for (let k = 0; k < 3; k++) {{
                            const s = (this.gasFlowPhase + gp.phaseOff + k * 0.3333) % 1.0;
                            const pt = this.samplePolyline(gp.pts, s);
                            let gCol;
                            if (s < 0.24) {{
                                gCol = [1.0, 0.72, 0.24, alphaScale];
                            }} else if (s < 0.58) {{
                                gCol = [0.96, 0.42, 0.14, alphaScale * 0.85];
                            }} else if (s < 0.86) {{
                                gCol = nitroExh ? [1.0, 0.55, 0.18, alphaScale * 0.75] : [0.80, 0.30, 0.18, alphaScale * 0.65];
                            }} else {{
                                gCol = [0.46, 0.66, 0.95, alphaScale * 0.55];
                            }}
                            const rad = gp.r * rScale * (s > 0.85 ? 1.25 : 1.0);
                            const gM = this.matTRS(pt[0], pt[1], pt[2], 0, 0, 0, rad, rad, rad);
                            this.drawItem(this.meshes.sphere, gM, gCol, [0.0, 1.0], viewProj);
                        }}
                    }}
                    gl.blendFunc(gl.SRC_ALPHA, gl.ONE_MINUS_SRC_ALPHA);
                    gl.depthMask(true);
                    gl.disable(gl.BLEND);
                }}

                // Chama de combustão na câmara no PMS (visível quando ligado / acentuada em Slow Mo)
                if (engineSim.on && engineSim.currentRpm > 20) {{
                    gl.enable(gl.BLEND);
                    gl.blendFunc(gl.SRC_ALPHA, gl.ONE);
                    gl.depthMask(false);
                    const cycleLen = this.config.ciclo === '2T' ? Math.PI * 2 : Math.PI * 4;
                    const isDieselGlow = this.config.combustivel === 'Diesel' || this.config.combustivel === 'Biodiesel';
                    for (const c of this.dynamicCyls) {{
                        const rawLocal = this.crankAngle + c.phase - c.angle + (this.config.ciclo === '2T' ? 0 : c.fireShift);
                        const cycAng = ((rawLocal % cycleLen) + cycleLen) % cycleLen;
                        if (cycAng < 0.62) {{
                            const intensity = 1.0 - cycAng / 0.62;
                            const phi = this.crankAngle + c.phase;
                            const uPin = c.crankR * Math.cos(phi - c.angle);
                            const vPin = c.crankR * Math.sin(phi - c.angle);
                            const uPis = uPin + Math.sqrt(Math.max(0.0001, c.rodLen * c.rodLen - vPin * vPin));
                            const flashD = uPis + c.pistonH * 0.54 + 0.05;
                            const cosA = Math.cos(c.angle), sinA = Math.sin(c.angle);
                            const flashM = this.matTRS(c.x, flashD * cosA, c.zOff + flashD * sinA, c.angle, 0, 0, c.cylR * 0.78, 0.08 + 0.06 * intensity, c.cylR * 0.78);
                            const col = isDieselGlow
                                ? [1.0, 0.58, 0.16, 0.72 * intensity]
                                : [1.0, 0.46 + 0.36 * intensity, 0.16 + 0.38 * intensity, 0.78 * intensity];
                            this.drawItem(this.meshes.cyl, flashM, col, [0.0, 1.0], viewProj);
                        }}
                    }}
                    for (const w of this.dynamicWankel) {{
                        const phi = this.crankAngle + w.phase;
                        const twoPi = Math.PI * 2;
                        const cycAng = (((phi - Math.PI * 0.42) % twoPi) + twoPi) % twoPi;
                        if (cycAng < 0.72) {{
                            const intensity = 1.0 - cycAng / 0.72;
                            const flashM = this.matTRS(w.x, 0, 0.76 * w.rotorR, 0, 0, 0, w.rotorW * 0.85, 0.28 * w.rotorR * (0.7 + 0.3 * intensity), 0.14 * w.rotorR);
                            const col = isDieselGlow
                                ? [1.0, 0.58, 0.16, 0.74 * intensity]
                                : [1.0, 0.48 + 0.36 * intensity, 0.18 + 0.38 * intensity, 0.80 * intensity];
                            this.drawItem(this.meshes.box, flashM, col, [0.0, 1.0], viewProj);
                        }}
                    }}
                    if (this.exhaustTips.length && (curViewMode === 'exhaust' || curViewMode === 'all')) {{
                        const rpmRatio = engineSim.currentRpm / Math.max(1, engineSim.maxRpm || 7500);
                        const nitro = this.config.combustivel === 'Nitrometano';
                        const thr = nitro ? 0.55 : 0.84;
                        if (rpmRatio > thr) {{
                            const pulse = Math.max(0, Math.sin(this.crankAngle * 1.5) * 0.65 + 0.35);
                            for (const tip of this.exhaustTips) {{
                                const fBoost = tip.hot || nitro ? 1.0 : 0.45;
                                const flLen = (0.16 + 0.28 * pulse) * fBoost;
                                const flM = this.matTRS(tip.x + flLen * 0.45, tip.y, tip.z, 0, 0, -Math.PI * 0.5, tip.r * 0.78, flLen, tip.r * 0.78);
                                const fCol = nitro
                                    ? [1.0, 0.64, 0.16, 0.82 * pulse]
                                    : [0.36, 0.66, 1.0, 0.75 * pulse * fBoost];
                                this.drawItem(this.meshes.cone, flM, fCol, [0.0, 1.0], viewProj);
                            }}
                        }}
                    }}
                    gl.blendFunc(gl.SRC_ALPHA, gl.ONE_MINUS_SRC_ALPHA);
                    gl.depthMask(true);
                    gl.disable(gl.BLEND);
                }}

                if (this.cutaway) {{
                    gl.enable(gl.BLEND);
                    gl.blendFunc(gl.SRC_ALPHA, gl.ONE_MINUS_SRC_ALPHA);
                    gl.depthMask(false);
                    for (const cullFace of [gl.FRONT, gl.BACK]) {{
                        gl.cullFace(cullFace);
                        for (const item of this.staticTrans) {{
                            const col = [item.color[0], item.color[1], item.color[2], 0.25];
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
                ctx.translate(w * 0.35 - this.cam.panX * 40, h * 0.50 - this.cam.panY * 40);
                ctx.scale(this.cam.zoom * 55, this.cam.zoom * 55);
                const cy = Math.cos(this.cam.yaw), sy = Math.sin(this.cam.yaw);
                const cp = Math.cos(this.cam.pitch), sp = Math.sin(this.cam.pitch);
                const proj = (x, y, z) => {{
                    const rx = x * cy + z * sy;
                    const rz = -x * sy + z * cy;
                    const ry = y * cp - rz * sp;
                    return [rx, -ry];
                }};
                ctx.strokeStyle = '#94a3b8';
                ctx.lineWidth = 0.03;
                for (const c of this.dynamicCyls) {{
                    const phi = this.crankAngle + c.phase;
                    const yP = (c.rodLen + c.crankR * Math.cos(phi - c.angle)) * Math.cos(c.angle);
                    const zP = c.zOff + (c.rodLen + c.crankR * Math.cos(phi - c.angle)) * Math.sin(c.angle);
                    const [px, py] = proj(c.x, yP, zP);
                    ctx.beginPath();
                    ctx.arc(px, py, c.cylR * 0.7, 0, Math.PI * 2);
                    ctx.stroke();
                }}
                for (const w of this.dynamicWankel) {{
                    const phi = this.crankAngle + w.phase;
                    const ey = w.ecc * Math.cos(phi);
                    const ez = w.ecc * Math.sin(phi);
                    const rSpin = phi / 3.0;
                    ctx.beginPath();
                    for (let k = 0; k <= 3; k++) {{
                        const a = rSpin + ((k % 3) * Math.PI * 2) / 3;
                        const [px, py] = proj(w.x, ey + Math.cos(a) * w.rotorR, ez + Math.sin(a) * w.rotorR);
                        if (k === 0) ctx.moveTo(px, py);
                        else ctx.lineTo(px, py);
                    }}
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

        // Controlos de Ligar/Desligar e Acelerar
        function updateRpmRedlineVisual(rpm) {{
            if (!telemetryRpmPill || !liveRpmValue) return;
            const maxR = Math.max(1000, engineSim.maxRpm || 7500);
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
                setThrottlePercent(0);
            }} else {{
                setThrottlePercent(engineSim.throttlePct);
            }}
            updateRpmRedlineVisual(engineSim.currentRpm);
            drawDynoChart();
        }}

        btnEnginePower.addEventListener('click', () => {{
            engineSim.on = !engineSim.on;
            if (engineSim.on && engineSim.currentRpm < engineSim.idleRpm) {{
                engineSim.currentRpm = Math.max(engineSim.currentRpm, engineSim.idleRpm * 0.7);
            }}
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
            const rawBore = parseFloat(inputBore.value);
            const rawStroke = parseFloat(inputStroke.value);
            const rawCr = parseFloat(inputCr.value);
            const rawRpm = parseInt(inputRpm.value, 10);
            const rawTurbo = inputTurboBoost ? parseFloat(inputTurboBoost.value) : 0;
            const rawSc = inputScBoost ? parseFloat(inputScBoost.value) : 0;
            const rawDamperWeight = inputDamperWeight ? parseFloat(inputDamperWeight.value) : 3.2;
            const adm = selectAdmissao.value || 'Atmosférico';
            const hasMultiTurbo = adm === 'Biturbo' || adm === 'Quad Turbo';
            const fmtVal = selectFormato.value || 'I';
            const isWankelFmt = fmtVal === 'WANKEL';
            const cicloVal = isWankelFmt ? '4T' : (selectCiclo.value === '2T' ? '2T' : '4T');
            const is2tVal = !isWankelFmt && cicloVal === '2T';
            return {{
                bore: Number.isFinite(rawBore) && rawBore > 0 ? Math.max(10.0, rawBore) : 86.0,
                stroke: Number.isFinite(rawStroke) && rawStroke > 0 ? Math.max(10.0, rawStroke) : 86.0,
                compression_ratio: Number.isFinite(rawCr) && rawCr > 0 ? Math.max(2.0, rawCr) : 10.5,
                max_rpm: Number.isFinite(rawRpm) && rawRpm > 0 ? Math.max(500, rawRpm) : 7500,
                combustivel: selectCombustivel.value || 'Gasolina 95',
                ciclo: cicloVal,
                cilindros: parseInt(selectCilindros.value, 10) || 4,
                admissao: adm,
                turbo_config: (hasMultiTurbo && selectTurboConfig && selectTurboConfig.value === 'Sequencial') ? 'Sequencial' : 'Paralelo',
                intake_type: selectIntakeType ? selectIntakeType.value : 'Plenum OEM',
                intake_material: selectIntakeMaterial ? selectIntakeMaterial.value : 'Alumínio Fundido',
                radiator_type: selectRadiatorType ? selectRadiatorType.value : 'OEM Alumínio',
                flywheel: selectFlywheel ? selectFlywheel.value : 'Monomassa Aço',
                damper: selectDamper ? selectDamper.value : 'Elastómero OEM',
                damper_weight: (Number.isFinite(rawDamperWeight) && rawDamperWeight > 0) ? Math.max(0.1, Math.min(2000.0, rawDamperWeight)) : 3.2,
                gearbox_type: selectGearboxType ? selectGearboxType.value : 'Manual',
                gearbox_speeds: selectGearboxSpeeds ? (parseInt(selectGearboxSpeeds.value, 10) || 6) : 6,
                clutch_type: selectClutchType ? selectClutchType.value : 'Monodisco Orgânica',
                final_drive: selectFinalDrive ? (parseFloat(selectFinalDrive.value) || 3.73) : 3.73,
                exhaust_type: selectExhaustType ? selectExhaustType.value : 'OEM Catalisador',
                exhaust_tips: selectExhaustTips ? selectExhaustTips.value : 'Dupla',
                exhaust_junction: (EXHAUST_JUNCTION_FORMATS.includes(fmtVal) && selectExhaustJunction) ? selectExhaustJunction.value : 'Sem União',
                exhaust_diameter: inputExhaustDiameter ? Math.max(35, Math.min(140, parseFloat(inputExhaustDiameter.value) || 63)) : 63,
                formato: fmtVal,
                v_angle: selectVAngle ? selectVAngle.value : '60',
                material: selectMaterial ? selectMaterial.value : 'Alumínio',
                piston_material: selectPistonMaterial ? selectPistonMaterial.value : 'Alumínio',
                camshaft: selectCamshaft ? selectCamshaft.value : 'DOHC',
                valve_type: is2tVal ? 'Reed Valve' : (selectValveType ? selectValveType.value : 'Molas'),
                num_valvulas: selectValves ? parseInt(selectValves.value, 10) : 4,
                turbo_bar: (inputTurboBoost && !inputTurboBoost.disabled && Number.isFinite(rawTurbo)) ? Math.max(0, rawTurbo) : 0.0,
                sc_bar: (inputScBoost && !inputScBoost.disabled && Number.isFinite(rawSc)) ? Math.max(0, rawSc) : 0.0
            }};
        }}

        function atualizarMotor3D() {{
            const p = readEnginePayload();
            const t = I18N[currentLang];
            const admLabel = (t.admOpts && t.admOpts[p.admissao]) ? t.admOpts[p.admissao] : p.admissao;
            const hasMultiTurbo = p.admissao === 'Biturbo' || p.admissao === 'Quad Turbo';
            const turboCfgLabel = (t.turboCfgOpts && t.turboCfgOpts[p.turbo_config]) ? t.turboCfgOpts[p.turbo_config] : p.turbo_config;
            const fullAdmLabel = hasMultiTurbo ? `${{admLabel}} · ${{turboCfgLabel}}` : admLabel;
            const isWankel = p.formato === 'WANKEL';
            const fmtDisplay = isWankel
                ? `WANKEL ${{p.cilindros}}R`
                : ((p.formato === 'V' || p.formato === 'W') ? `${{p.formato}}${{p.cilindros}} (${{p.v_angle}}°)` : `${{p.formato}}${{p.cilindros}}`);
            const unitCc = (Math.PI / 4.0) * Math.pow(p.bore / 10.0, 2) * (p.stroke / 10.0);
            const litros = ((unitCc * (isWankel ? 1.308 : 1.0) * p.cilindros) / 1000.0).toFixed(2);

            motorNumCilindros.textContent = p.cilindros;
            if (motor3dBadge) {{
                motor3dBadge.textContent = `${{fmtDisplay}} · ${{fullAdmLabel.toUpperCase()}}`;
            }}
            if (motor3dSpec) {{
                motor3dSpec.textContent = isWankel
                    ? `WANKEL · ${{litros}} L · ${{p.cilindros}}R`
                    : `${{p.formato}} · ${{litros}} L · ${{p.bore.toFixed(0)}}×${{p.stroke.toFixed(0)}} mm`;
            }}

            const matLabel = (t.matOpts && t.matOpts[p.material]) ? t.matOpts[p.material] : p.material;
            const pMatLabel = (t.pistonMatOpts && t.pistonMatOpts[p.piston_material]) ? t.pistonMatOpts[p.piston_material] : p.piston_material;
            const fuelLabel = (t.fuelOpts && t.fuelOpts[p.combustivel]) ? t.fuelOpts[p.combustivel] : p.combustivel;
            const fwShort = (t.flywheelShort && t.flywheelShort[p.flywheel]) ? t.flywheelShort[p.flywheel] : p.flywheel;
            const dmpShort = (t.damperShort && t.damperShort[p.damper]) ? t.damperShort[p.damper] : p.damper;
            const is2T = !isWankel && p.ciclo === '2T';
            if (sumArchVal) {{
                if (isWankel) {{
                    sumArchVal.textContent = `${{fmtDisplay}} · ${{t.rotaryWord}}`;
                }} else if (is2T) {{
                    sumArchVal.textContent = `${{fmtDisplay}} · Reed Valve`;
                }} else {{
                    const vtShort = p.camshaft === 'Freevalve' ? 'Freevalve' : `${{p.camshaft}} · ${{p.num_valvulas}}V`;
                    sumArchVal.textContent = `${{fmtDisplay}} · ${{vtShort}}`;
                }}
            }}
            if (sumArchSub) {{
                sumArchSub.textContent = `${{p.ciclo}} · ${{t.compShort}} ${{p.compression_ratio.toFixed(1)}}:1${{!isWankel && (is2T || p.camshaft !== 'Freevalve') ? ` · ${{p.valve_type}}` : ''}}`;
            }}
            if (sumDispVal) sumDispVal.textContent = `${{litros}} L`;
            if (sumGeoSub) sumGeoSub.textContent = `${{p.bore.toFixed(0)}}×${{p.stroke.toFixed(0)}} mm · ${{p.max_rpm}} RPM`;
            const intTypeShort = (t.intakeTypeShort && t.intakeTypeShort[p.intake_type]) ? t.intakeTypeShort[p.intake_type] : p.intake_type;
            const intMatShort = (t.intakeMatShort && t.intakeMatShort[p.intake_material]) ? t.intakeMatShort[p.intake_material] : p.intake_material;
            const hasRadiator = ['Turbo', 'Biturbo', 'Quad Turbo', 'Twincharge'].includes(p.admissao);
            const radShort = (t.radiatorShort && t.radiatorShort[p.radiator_type]) ? t.radiatorShort[p.radiator_type] : p.radiator_type;
            if (sumAdmVal) sumAdmVal.textContent = fullAdmLabel;
            if (sumAdmSub) {{
                let pTxt = '0.0 bar';
                if (p.admissao === 'Supercompressor') pTxt = `+${{p.sc_bar.toFixed(1)}} bar`;
                else if (p.admissao === 'Twincharge') pTxt = `+${{p.turbo_bar.toFixed(1)}} / +${{p.sc_bar.toFixed(1)}} bar`;
                else if (p.admissao !== 'Atmosférico') pTxt = `+${{p.turbo_bar.toFixed(1)}} bar`;
                sumAdmSub.textContent = `${{pTxt}} · ${{intTypeShort}} (${{intMatShort}})${{hasRadiator ? ` · ${{radShort}}` : ''}}`;
            }}
            if (sumBuildVal) sumBuildVal.textContent = matLabel;
            if (sumBuildSub) {{
                const pWord = isWankel ? t.rotorMatWord : t.pistonWord;
                sumBuildSub.textContent = `${{pWord}}: ${{pMatLabel}} · ${{fuelLabel}} · ${{fwShort}} · ${{dmpShort}} (${{p.damper_weight.toFixed(1)}} kg)`;
            }}
            syncDamperSuggestionUI(p);
            if (motor3D) {{
                motor3D.setConfig({{
                    cilindros: p.cilindros,
                    formato: p.formato,
                    admissao: p.admissao,
                    turboConfig: p.turbo_config,
                    intakeType: p.intake_type,
                    intakeMaterial: p.intake_material,
                    flywheel: p.flywheel,
                    damper: p.damper,
                    damperWeight: p.damper_weight,
                    viewMode: viewMode,
                    gearboxType: p.gearbox_type,
                    gearboxSpeeds: p.gearbox_speeds,
                    clutchType: p.clutch_type,
                    finalDrive: p.final_drive,
                    exhaustType: p.exhaust_type,
                    exhaustTips: p.exhaust_tips,
                    exhaustJunction: p.exhaust_junction,
                    exhaustDiameter: p.exhaust_diameter,
                    radiatorType: p.radiator_type,
                    bore: p.bore,
                    stroke: p.stroke,
                    maxRpm: p.max_rpm,
                    ciclo: p.ciclo,
                    combustivel: p.combustivel,
                    vAngle: p.v_angle,
                    material: p.material,
                    pistonMaterial: p.piston_material,
                    camshaft: p.camshaft,
                    valveType: p.valve_type,
                    numValvulas: p.num_valvulas,
                    turboBar: p.turbo_bar,
                    scBar: p.sc_bar
                }});
            }}
        }}

        function aplicarAlertaRpm(alerta, motivos) {{
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
            syncDamperSuggestionUI(payload);
            computeDynoData(payload);

            const t = I18N[currentLang];
            if (window.location.protocol !== 'file:') {{
                try {{
                    const res = await fetch('/api/combustao', {{
                        method: 'POST',
                        headers: {{ 'Content-Type': 'application/json' }},
                        body: JSON.stringify(payload)
                    }});
                    if (res.ok) {{
                        const data = await res.json();
                        const motivos = [];
                        if (data.vel_pistao > data.limite_vm) {{
                            motivos.push(t.warnPiston(Number(data.vel_pistao).toFixed(1), Number(data.limite_vm).toFixed(1)));
                        }}
                        if (payload.compression_ratio > data.limite_cr) {{
                            motivos.push(t.warnCr(data.limite_cr));
                        }}
                        aplicarAlertaRpm(data.alerta_rpm, motivos.length ? motivos : data.motivos_alerta);
                        return;
                    }}
                }} catch (_) {{}}
            }}

            const matTol = {{
                'Alumínio': 0.5, 'Ferro Fundido': -0.5, 'Alumínio Billet': 3.0,
                'Forged': 2.5, 'Forged Heavy': 1.5, 'Billet': 3.8,
                'Magnésio': 1.5, 'Titanium': 4.5, 'Titanium Billet': 6.0, 'Titanium Forged': 5.5
            }};
            const valTol = {{ 'Molas': 0.0, 'VVT': 0.5, 'Desmodrómico': 2.0, 'Pneumático': 4.0, 'Freevalve': 4.5, 'Reed Valve': 3.5 }};
            const pisTol = {{ 'Alumínio': 0.0, 'Forged': 2.5, 'Forged Heavy': 1.5, 'Titânio': 5.0 }};
            const pisCrTol = {{ 'Alumínio': 0.0, 'Forged': 1.0, 'Forged Heavy': 3.0, 'Titânio': 2.0 }};
            const fwTol = {{ 'Monomassa Aço': 0.0, 'Dupla Massa': -0.8, 'Aligeirado Cromoly': 1.0, 'Alumínio Billet': 1.5, 'Carbono Multi-Disco': 2.5 }};
            const dmpTol = {{ 'Elastómero OEM': 0.0, 'Fluido Viscoso': 2.0, 'ATI Super Damper': 3.5, 'Polia Sólida': -2.5 }};
            const isWankel = payload.formato === 'WANKEL';
            const is2T = !isWankel && payload.ciclo === '2T';
            const effValveType = is2T ? 'Reed Valve' : payload.valve_type;
            const isFreevalve = !isWankel && !is2T && (payload.camshaft === 'Freevalve' || effValveType === 'Freevalve');
            const velMediaPistao = isWankel
                ? (2.0 * (payload.stroke / 1000.0) * (payload.max_rpm / 3.0) * 1.55) / 60.0
                : (2.0 * (payload.stroke / 1000.0) * payload.max_rpm) / 60.0;
            const matTVal = matTol[payload.material] !== undefined ? matTol[payload.material] : 0.5;
            const valTVal = isWankel ? 6.0 : (isFreevalve ? 4.5 : (valTol[effValveType] || 0.0));
            const pisTVal = pisTol[payload.piston_material] || 0.0;
            const fwTVal = fwTol[payload.flywheel] !== undefined ? fwTol[payload.flywheel] : 0.0;
            const dmpTVal = dmpTol[payload.damper] !== undefined ? dmpTol[payload.damper] : 0.0;
            const dmpWStats = computeDamperWeightStats(payload);
            const limiteVm = Math.min(30.0, 25.0 + matTVal + valTVal + pisTVal + fwTVal + dmpTVal + dmpWStats.wTol);
            const motivosAlerta = [];
            if (velMediaPistao > limiteVm) {{
                motivosAlerta.push(t.warnPiston(velMediaPistao.toFixed(1), limiteVm.toFixed(1)));
            }}
            const crLimMap = {{
                'Gasolina 91': 11.0, 'Gasolina 95': 12.5, 'Gasolina': 12.5,
                'Gasolina 98': 14.0, 'Gasolina 102': 15.5, 'Gasolina 110': 17.5,
                'Etanol (E85)': 16.5, 'Metanol': 18.0, 'Nitrometano': 14.5,
                'Diesel': 22.0, 'Biodiesel': 21.5
            }};
            const radCrTolMap = {{
                'OEM Alumínio': 0.0, 'Duplo Núcleo': 0.5, 'Triple-Pass Racing': 1.0,
                'Cobre / Latão': 0.4, 'Água-Ar (Charge Cooler)': 1.2
            }};
            const hasRad = ['Turbo', 'Biturbo', 'Quad Turbo', 'Twincharge'].includes(payload.admissao);
            const radCrTol = hasRad ? (radCrTolMap[payload.radiator_type] || 0.0) : 0.0;
            const baseCrLim = crLimMap[payload.combustivel] !== undefined ? crLimMap[payload.combustivel] : 12.5;
            const limiteCr = baseCrLim + (pisCrTol[payload.piston_material] || 0.0) + radCrTol;
            if (payload.compression_ratio > limiteCr) {{
                motivosAlerta.push(t.warnCr(Number(limiteCr.toFixed(1))));
            }}
            aplicarAlertaRpm(motivosAlerta.length > 0, motivosAlerta);
        }}

        async function atualizarDados() {{
            const cilindros = parseInt(selectCilindros.value, 10) || 4;
            const formato = selectFormato.value || 'I';
            const admissao = selectAdmissao.value || 'Atmosférico';
            const turbo_config = (admissao === 'Biturbo' || admissao === 'Quad Turbo') && selectTurboConfig
                ? (selectTurboConfig.value || 'Paralelo')
                : 'Paralelo';
            const radiator_type = selectRadiatorType ? (selectRadiatorType.value || 'OEM Alumínio') : 'OEM Alumínio';

            atualizarMotor3D();

            if (window.location.protocol !== 'file:') {{
                try {{
                    const res = await fetch('/api/ficha', {{
                        method: 'POST',
                        headers: {{ 'Content-Type': 'application/json' }},
                        body: JSON.stringify({{ cilindros, formato, admissao, turbo_config, radiator_type }})
                    }});
                    if (res.ok) {{
                        const data = await res.json();
                        motorNumCilindros.textContent = data.cilindros;
                        atualizarWidget3();
                        return;
                    }}
                }} catch (_) {{}}
            }}

            atualizarWidget3();
        }}

        if (selectFormato) {{
            selectFormato.addEventListener('change', () => {{
                syncCylinderOptionsForFormat();
                syncSubsystemUI();
                atualizarDados();
            }});
        }}
        if (selectCilindros) {{
            selectCilindros.addEventListener('change', () => atualizarDados());
        }}
        if (selectAdmissao) {{
            selectAdmissao.addEventListener('change', () => {{
                syncBoostControls(true);
                atualizarDados();
            }});
        }}
        if (selectTurboConfig) {{
            selectTurboConfig.addEventListener('change', () => atualizarDados());
        }}
        if (selectCamshaft) {{
            selectCamshaft.addEventListener('change', () => {{
                if (selectCamshaft.value === 'Freevalve' && selectValveType) {{
                    selectValveType.value = 'Freevalve';
                }} else if (selectCamshaft.value !== 'Freevalve' && selectValveType && selectValveType.value === 'Freevalve') {{
                    selectValveType.value = 'Molas';
                }}
            }});
        }}
        if (selectValveType) {{
            selectValveType.addEventListener('change', () => {{
                if (selectValveType.value === 'Freevalve' && selectCamshaft) {{
                    selectCamshaft.value = 'Freevalve';
                }} else if (selectValveType.value !== 'Freevalve' && selectCamshaft && selectCamshaft.value === 'Freevalve') {{
                    selectCamshaft.value = 'DOHC';
                }}
            }});
        }}

        function syncSubsystemUI() {{
            const t = I18N[currentLang];
            const gb = selectGearboxType ? selectGearboxType.value : 'Manual';
            const spds = selectGearboxSpeeds ? (parseInt(selectGearboxSpeeds.value, 10) || 6) : 6;
            const isEcvt = gb === 'E-CVT';
            if (selectGearboxSpeeds) {{
                selectGearboxSpeeds.disabled = isEcvt;
                selectGearboxSpeeds.title = isEcvt ? (t.gbSpeedsEcvtTitle || '') : '';
            }}
            const cl = selectClutchType ? selectClutchType.value : 'Monodisco Orgânica';
            const clShort = (t.clutchShort && t.clutchShort[cl]) ? t.clutchShort[cl] : cl;
            const gbSpdSummary = isEcvt ? (t.gbSteplessLabel || 'Stepless') : `${{spds}}M`;
            const gbSpdBtn = isEcvt ? (t.gbSteplessShort || 'Stepless') : `${{spds}}M`;
            if (gearboxSummaryInfo) {{
                gearboxSummaryInfo.textContent = `${{gb}} · ${{gbSpdSummary}} · ${{clShort}}`;
            }}

            const fmtCur = selectFormato ? (selectFormato.value || 'I') : 'I';
            const supportsJunc = EXHAUST_JUNCTION_FORMATS.includes(fmtCur);
            if (selectExhaustJunction) {{
                if (supportsJunc) {{
                    if (selectExhaustJunction.disabled) {{
                        selectExhaustJunction.value = savedDualExhaustJunction || 'X-Pipe';
                        selectExhaustJunction.disabled = false;
                    }} else if (selectExhaustJunction.value) {{
                        savedDualExhaustJunction = selectExhaustJunction.value;
                    }}
                }} else {{
                    if (!selectExhaustJunction.disabled && selectExhaustJunction.value) {{
                        savedDualExhaustJunction = selectExhaustJunction.value;
                    }}
                    selectExhaustJunction.value = 'Sem União';
                    selectExhaustJunction.disabled = true;
                }}
            }}

            const exType = selectExhaustType ? selectExhaustType.value : 'OEM Catalisador';
            const exJunc = (supportsJunc && selectExhaustJunction) ? selectExhaustJunction.value : 'Sem União';
            const juncShort = supportsJunc
                ? ((t.exhJunctionShort && t.exhJunctionShort[exJunc]) ? t.exhJunctionShort[exJunc] : exJunc)
                : t.exhSingleBankLabel;
            const exDiam = inputExhaustDiameter ? Math.max(35, Math.min(140, Math.round(parseFloat(inputExhaustDiameter.value) || 63))) : 63;
            const noteTxt = (t.exhFlowNotes && t.exhFlowNotes[exType]) ? t.exhFlowNotes[exType] : exType;
            if (exhaustSoundNote) {{
                exhaustSoundNote.textContent = `${{noteTxt}} · ${{juncShort}} · ${{exDiam}} mm`;
            }}

            if (btnTopEngine) {{
                btnTopEngine.style.display = viewMode === 'engine' ? 'none' : 'inline-flex';
            }}
            if (btnTopGearbox) {{
                btnTopGearbox.textContent = `${{t.topGearbox}} · ${{gbSpdBtn}}`;
                btnTopGearbox.classList.toggle('ativo', viewMode === 'gearbox' || activeTopPopover === 'gearbox');
                btnTopGearbox.setAttribute('aria-expanded', activeTopPopover === 'gearbox' ? 'true' : 'false');
            }}
            if (btnTopExhaust) {{
                btnTopExhaust.textContent = `${{t.topExhaust}} · ${{exDiam}}mm`;
                btnTopExhaust.classList.toggle('ativo', viewMode === 'exhaust' || activeTopPopover === 'exhaust');
                btnTopExhaust.setAttribute('aria-expanded', activeTopPopover === 'exhaust' ? 'true' : 'false');
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
            if (popoverExhaust) popoverExhaust.classList.toggle('aberto', activeTopPopover === 'exhaust');
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
        if (btnExhBackEngine) btnExhBackEngine.addEventListener('click', () => setViewAndPopover('engine', null));
        if (btnTopGearbox) {{
            btnTopGearbox.addEventListener('click', () => {{
                if (viewMode !== 'gearbox') {{
                    setViewAndPopover('gearbox', 'gearbox');
                }} else {{
                    setViewAndPopover('gearbox', activeTopPopover === 'gearbox' ? null : 'gearbox');
                }}
            }});
        }}
        if (btnTopExhaust) {{
            btnTopExhaust.addEventListener('click', () => {{
                if (viewMode !== 'exhaust') {{
                    setViewAndPopover('exhaust', 'exhaust');
                }} else {{
                    setViewAndPopover('exhaust', activeTopPopover === 'exhaust' ? null : 'exhaust');
                }}
            }});
        }}
        if (btnCloseGearbox) btnCloseGearbox.addEventListener('click', () => setViewAndPopover(null, null));
        if (btnCloseExhaust) btnCloseExhaust.addEventListener('click', () => setViewAndPopover(null, null));

        if (rangeExhaustDiameter && inputExhaustDiameter) {{
            rangeExhaustDiameter.addEventListener('input', () => {{
                inputExhaustDiameter.value = rangeExhaustDiameter.value;
                syncSubsystemUI();
                atualizarMotor3D();
                atualizarWidget3();
            }});
            inputExhaustDiameter.addEventListener('input', () => {{
                const raw = parseFloat(inputExhaustDiameter.value);
                if (Number.isFinite(raw)) {{
                    const clamped = Math.max(35, Math.min(140, Math.round(raw)));
                    rangeExhaustDiameter.value = clamped;
                }}
                syncSubsystemUI();
                atualizarMotor3D();
                atualizarWidget3();
            }});
            inputExhaustDiameter.addEventListener('change', () => {{
                const clamped = Math.max(35, Math.min(140, Math.round(parseFloat(inputExhaustDiameter.value) || 63)));
                inputExhaustDiameter.value = clamped;
                rangeExhaustDiameter.value = clamped;
                syncSubsystemUI();
                atualizarMotor3D();
                atualizarWidget3();
            }});
        }}

        [selectGearboxType, selectGearboxSpeeds, selectClutchType, selectFinalDrive, selectExhaustType, selectExhaustTips, selectExhaustJunction].forEach(el => {{
            if (!el) return;
            el.addEventListener('change', () => {{
                syncSubsystemUI();
                atualizarMotor3D();
                atualizarWidget3();
            }});
        }});

        if (inputDamperWeight) {{
            inputDamperWeight.addEventListener('input', () => {{
                const raw = parseFloat(inputDamperWeight.value);
                if (Number.isFinite(raw) && raw > 2000) {{
                    inputDamperWeight.value = '2000';
                }}
                atualizarMotor3D();
                atualizarWidget3();
            }});
            inputDamperWeight.addEventListener('change', () => {{
                const raw = parseFloat(inputDamperWeight.value);
                const clamped = (Number.isFinite(raw) && raw > 0) ? Math.max(0.1, Math.min(2000.0, raw)) : (engineSim.damperIdealKg || 3.2);
                inputDamperWeight.value = String(Math.round(clamped * 10) / 10);
                atualizarMotor3D();
                atualizarWidget3();
            }});
        }}

        if (btnDamperIdeal) {{
            btnDamperIdeal.addEventListener('click', () => {{
                const p = readEnginePayload();
                const ideal = computeIdealDamperKg(p);
                if (inputDamperWeight) inputDamperWeight.value = ideal.toFixed(1);
                atualizarMotor3D();
                atualizarWidget3();
            }});
        }}

        if (selectCiclo) {{
            selectCiclo.addEventListener('change', () => {{
                syncCycleAndValvetrainUI();
                atualizarMotor3D();
                atualizarWidget3();
            }});
        }}

        [inputBore, inputStroke, inputCr, inputRpm, inputTurboBoost, inputScBoost, selectCombustivel, selectVAngle, selectMaterial, selectPistonMaterial, selectCamshaft, selectValveType, selectValves, selectFlywheel, selectDamper, selectIntakeType, selectIntakeMaterial, selectRadiatorType].forEach(el => {{
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
        syncCylinderOptionsForFormat();
        syncBoostControls(false);
        syncSubsystemUI();
        syncEnginePowerUI();
        setActivePage(0);
        atualizarMotor3D();
        atualizarWidget3();
    </script>
</body>
</html>


"""


def guardar_index_html(
    num_cilindros: int = 4,
    admissao: str = "Atmosférico",
    formato: str = "I",
) -> None:
    """
    Gera primeiro todo o HTML em memória e só depois grava o ficheiro index.html
    (evita que o index.html fique vazio/0 bytes caso ocorra algum erro).
    """
    conteudo_html = gerar_dashboard_html(num_cilindros, admissao, formato)
    caminho_index = os.path.join(BASE_DIR, "index.html")
    with open(caminho_index, "w", encoding="utf-8") as f:
        f.write(conteudo_html)
    print("[OK] Ficheiro index.html gerado com sucesso.")


class DashboardHandler(SimpleHTTPRequestHandler):
    """Servidor HTTP que processa os pedidos dos Widgets 1, 2 e 3 diretamente em Python."""

    def __init__(self, *args, **kwargs):
        kwargs.setdefault("directory", BASE_DIR)
        super().__init__(*args, **kwargs)

    def do_GET(self):
        caminho, _, query = self.path.partition("?")
        if caminho in ("/", "/index.html", "/custom-engine/index.html"):
            destino = f"/custom-engine?{query}" if query else "/custom-engine"
            self.send_response(302)
            self.send_header("Location", destino)
            self.end_headers()
            return
        if caminho in ("/custom-engine", "/custom-engine/"):
            self.path = f"/index.html?{query}" if query else "/index.html"
        return super().do_GET()

    def do_POST(self):
        caminho = self.path.split("?", 1)[0]
        if caminho.startswith("/custom-engine/"):
            caminho = caminho[len("/custom-engine"):]

        tamanho = int(self.headers.get("Content-Length", 0))
        corpo = self.rfile.read(tamanho).decode("utf-8") if tamanho > 0 else "{}"
        try:
            dados = json.loads(corpo)
        except json.JSONDecodeError:
            self.send_error(400, "Invalid JSON")
            return

        if caminho == "/api/ficha":
            fmt = str(dados.get("formato") or "I").upper()
            if fmt not in FORMATOS_MOTOR:
                fmt = "I"
            cil = clamp_cilindros_formato(fmt, int(dados.get("cilindros") or 4))
            adm = str(dados.get("admissao") or "Atmosférico")
            t_cfg = str(dados.get("turbo_config") or "Paralelo")
            rad_t = str(dados.get("radiator_type") or "OEM Alumínio")

            resposta = json.dumps({
                "cilindros": cil,
                "formato": fmt,
                "admissao": adm,
                "turbo_config": t_cfg,
                "radiator_type": rad_t,
                "motor_svg": gerar_svg_motor_inline(cil, fmt, adm, t_cfg, rad_t),
            }).encode("utf-8")

            self.send_response(200)
            self.send_header("Content-Type", "application/json; charset=utf-8")
            self.send_header("Content-Length", str(len(resposta)))
            self.end_headers()
            self.wfile.write(resposta)
            return

        if caminho == "/api/combustao":
            resultado = processar_combustao(
                bore=float(dados.get("bore") or 86.0),
                stroke=float(dados.get("stroke") or 86.0),
                compression_ratio=float(dados.get("compression_ratio") or 10.5),
                max_rpm=int(dados.get("max_rpm") or 7500),
                combustivel=str(dados.get("combustivel") or "Gasolina 95"),
                ciclo=str(dados.get("ciclo") or "4T"),
                num_cilindros=int(dados.get("cilindros") or 4),
                admissao=str(dados.get("admissao") or "Atmosférico"),
                formato=str(dados.get("formato") or "I"),
                v_angle=str(dados.get("v_angle") or "60"),
                material=str(dados.get("material") or "Alumínio"),
                piston_material=str(dados.get("piston_material") or "Alumínio"),
                camshaft=str(dados.get("camshaft") or "DOHC"),
                valve_type=str(dados.get("valve_type") or "Molas"),
                num_valvulas=int(dados.get("num_valvulas") or 4),
                turbo_bar=float(dados.get("turbo_bar") if dados.get("turbo_bar") is not None else 1.5),
                sc_bar=float(dados.get("sc_bar") if dados.get("sc_bar") is not None else 0.8),
                turbo_config=str(dados.get("turbo_config") or "Paralelo"),
                flywheel=str(dados.get("flywheel") or "Monomassa Aço"),
                damper=str(dados.get("damper") or "Elastómero OEM"),
                damper_weight=(float(dados.get("damper_weight")) if dados.get("damper_weight") is not None else None),
                intake_type=str(dados.get("intake_type") or "Plenum OEM"),
                intake_material=str(dados.get("intake_material") or "Alumínio Fundido"),
                gearbox_type=str(dados.get("gearbox_type") or "Manual"),
                gearbox_speeds=int(dados.get("gearbox_speeds") or 6),
                clutch_type=str(dados.get("clutch_type") or "Monodisco Orgânica"),
                exhaust_type=str(dados.get("exhaust_type") or "OEM Catalisador"),
                exhaust_junction=str(dados.get("exhaust_junction") or "X-Pipe"),
                exhaust_diameter=float(dados.get("exhaust_diameter") if dados.get("exhaust_diameter") is not None else 63.0),
                radiator_type=str(dados.get("radiator_type") or "OEM Alumínio"),
            )
            resposta = json.dumps({
                "torque_nm_val": resultado["torque_nm_val"],
                "potencia_kw_val": resultado["potencia_kw_val"],
                "vel_pistao": resultado["velocidade_pistao_mps"],
                "limite_vm": resultado["limite_vm"],
                "limite_cr": resultado["limite_cr"],
                "alerta_rpm": resultado["alerta_rpm"],
                "motivos_alerta": resultado["motivos_alerta"],
                "damper_ideal_kg": resultado["damper_ideal_kg"],
            }, ensure_ascii=False).encode("utf-8")

            self.send_response(200)
            self.send_header("Content-Type", "application/json; charset=utf-8")
            self.send_header("Content-Length", str(len(resposta)))
            self.end_headers()
            self.wfile.write(resposta)
            return

        self.send_error(404)


def iniciar_servidor(porta: int = 8000) -> None:
    """Gera o index.html e inicia o servidor web local em Python."""
    guardar_index_html()
    url = f"http://localhost:{porta}/custom-engine"
    print(f"Servidor ativo em: {url} (Pressiona Ctrl+C para sair)")
    webbrowser.open(url)
    servidor = HTTPServer(("127.0.0.1", porta), DashboardHandler)
    try:
        servidor.serve_forever()
    except KeyboardInterrupt:
        print("\nServidor encerrado.")
        servidor.server_close()


if __name__ == "__main__":
    if "--build-only" in sys.argv:
        guardar_index_html()
    else:
        iniciar_servidor(porta=8000)
