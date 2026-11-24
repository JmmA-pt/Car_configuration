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
        linhas = ""
        for k in range(1, 4):
            if vertical:
                ly = y + k * (h / 4.0)
                linhas += f'<line x1="{x + 4:.1f}" y1="{ly:.1f}" x2="{x + w - 4:.1f}" y2="{ly:.1f}" stroke="#475569" stroke-width="1" />\n'
            else:
                lx = x + k * (w / 4.0)
                linhas += f'<line x1="{lx:.1f}" y1="{y + 4:.1f}" x2="{lx:.1f}" y2="{y + h - 4:.1f}" stroke="#475569" stroke-width="1" />\n'
        return (
            f'<rect x="{x:.1f}" y="{y:.1f}" width="{w:.1f}" height="{h:.1f}" rx="4" fill="#090c12" stroke="#94a3b8" stroke-width="1.3" />\n'
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
            turbo_wankel = desenhar_turbo(152.0, 206.0, 1.18) + desenhar_turbo(266.0, 206.0, 1.18)
        elif adm == "Quad Turbo":
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
            admissao_svg = (
                f'<path d="M 30,190 L 30,47 L 78,47" fill="none" stroke="url(#eng-pipe)" stroke-width="4.5" stroke-linejoin="round" />\n'
                f'<path d="M 68,210 L 266,210" fill="none" stroke="url(#eng-pipe)" stroke-width="4.5" />\n'
                f'{desenhar_intercooler(16.0, 194.0, 50.0, 26.0)}'
                f'<rect x="78" y="40" width="248" height="14" rx="5" fill="#121620" stroke="#94a3b8" stroke-width="1.3" />\n'
                f'<rect x="90" y="45.5" width="224" height="3" rx="1.5" fill="url(#eng-accent)" />\n'
                f'<rect x="82" y="191" width="240" height="8" rx="4" fill="#1a100e" stroke="#ea580c" stroke-width="1.1" />\n'
                f'{desenhar_turbo(146.0, 211.0, 1.24)}'
                f'{desenhar_turbo(282.0, 211.0, 1.24)}'
            )
        elif adm == "Quad Turbo":
            admissao_svg = (
                f'<path d="M 30,190 L 30,47 L 78,47" fill="none" stroke="url(#eng-pipe)" stroke-width="4.5" stroke-linejoin="round" />\n'
                f'<path d="M 68,210 L 326,210" fill="none" stroke="url(#eng-pipe)" stroke-width="4.5" />\n'
                f'{desenhar_intercooler(16.0, 194.0, 50.0, 26.0)}'
                f'<rect x="78" y="40" width="248" height="14" rx="5" fill="#121620" stroke="#94a3b8" stroke-width="1.3" />\n'
                f'<rect x="90" y="45.5" width="224" height="3" rx="1.5" fill="url(#eng-accent)" />\n'
                f'<rect x="82" y="191" width="240" height="8" rx="4" fill="#1a100e" stroke="#ea580c" stroke-width="1.1" />\n'
                f'{desenhar_turbo(112.0, 211.0, 1.05)}'
                f'{desenhar_turbo(178.0, 211.0, 1.05)}'
                f'{desenhar_turbo(244.0, 211.0, 1.05)}'
                f'{desenhar_turbo(310.0, 211.0, 1.05)}'
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
            admissao_vw = (
                f'<path d="M 185,24 L 24,24 L 24,86" fill="none" stroke="url(#eng-pipe)" stroke-width="4.5" stroke-linejoin="round" />\n'
                f'<path d="M 185,222 L 24,222 L 24,160" fill="none" stroke="url(#eng-pipe)" stroke-width="4.5" stroke-linejoin="round" />\n'
                f'<line x1="34" y1="123" x2="82" y2="123" stroke="url(#eng-pipe)" stroke-width="4.5" />\n'
                f'{desenhar_intercooler(14.0, 86.0, 20.0, 74.0, True)}'
                f'<rect x="78" y="109" width="250" height="28" rx="6" fill="#121620" stroke="#94a3b8" stroke-width="1.3" />\n'
                f'<rect x="94" y="121.5" width="218" height="3" rx="1.5" fill="url(#eng-accent)" />\n'
                f'{desenhar_turbo(212.0, 24.0, 1.22)}'
                f'{desenhar_turbo(212.0, 222.0, 1.22)}'
            )
        elif adm == "Quad Turbo":
            admissao_vw = (
                f'<path d="M 120,24 L 24,24 L 24,86" fill="none" stroke="url(#eng-pipe)" stroke-width="4.5" stroke-linejoin="round" />\n'
                f'<path d="M 272,24 L 180,24" fill="none" stroke="url(#eng-pipe)" stroke-width="4.2" />\n'
                f'<path d="M 120,222 L 24,222 L 24,160" fill="none" stroke="url(#eng-pipe)" stroke-width="4.5" stroke-linejoin="round" />\n'
                f'<path d="M 272,222 L 180,222" fill="none" stroke="url(#eng-pipe)" stroke-width="4.2" />\n'
                f'<line x1="34" y1="123" x2="82" y2="123" stroke="url(#eng-pipe)" stroke-width="4.5" />\n'
                f'{desenhar_intercooler(14.0, 86.0, 20.0, 74.0, True)}'
                f'{desenhar_turbo(150.0, 24.0, 1.05)}'
                f'{desenhar_turbo(272.0, 24.0, 1.05)}'
                f'{desenhar_turbo(150.0, 222.0, 1.05)}'
                f'{desenhar_turbo(272.0, 222.0, 1.05)}'
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
                        <button type="button" class="btn-engine-ctrl" id="btn-engine-throttle" disabled title="Manter premido (ou barra de espaço) para acelerar">
                            <span id="btn-engine-throttle-label">Acelerar</span>
                        </button>
                        <button type="button" class="btn-engine-ctrl" id="btn-slow-mo" aria-pressed="false" title="Alternar câmara lenta: 1x → 2x → 5x → 10x → Desligado">
                            <span id="btn-slow-mo-label">Slow Mo</span>
                        </button>
                    </div>
                    <div class="engine-dock-telemetry">
                        <div class="telemetry-pill">
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
def processar_combustao(
    bore: float = 86.0,
    stroke: float = 86.0,
    compression_ratio: float = 10.5,
    max_rpm: int = 7500,
    combustivel: str = "Gasolina",
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
) -> dict:
    """
    Calcula automaticamente em Python os parâmetros do motor (potência em kW,
    binário em Nm, cilindrada e alertas mecânicos) para o Dyno Curves.
    """
    bore = max(10.0, float(bore))
    stroke = max(10.0, float(stroke))
    cr = max(2.0, float(compression_ratio))
    max_rpm = max(500, int(max_rpm))
    ciclo = "2T" if str(ciclo).upper() == "2T" else "4T"
    formato_valido = str(formato).upper() if str(formato).upper() in FORMATOS_MOTOR else "I"
    num_cilindros = clamp_cilindros_formato(formato_valido, num_cilindros)
    admissao_valida = admissao if admissao in PERFIS_ADMISSAO else "Atmosférico"
    turbo_b = max(0.0, min(6.0, float(turbo_bar)))
    sc_b = max(0.0, min(4.0, float(sc_bar)))

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
        "Gasolina": {"torque": 1.00, "power": 1.00},
        "Etanol (E85)": {"torque": 1.08, "power": 1.08},
        "Metanol": {"torque": 1.12, "power": 1.12},
        "Diesel": {"torque": 1.14, "power": 0.78},
    }
    perfil_comb = fatores_combustivel.get(combustivel, fatores_combustivel["Gasolina"])

    is_freevalve = camshaft == "Freevalve" or valve_type == "Freevalve"
    perfis_cam = {
        "DOHC": {"tq": 1.00, "hp": 1.00},
        "SOHC": {"tq": 1.01, "hp": 0.96},
        "OHV": {"tq": 1.04, "hp": 0.91},
        "Freevalve": {"tq": 1.06, "hp": 1.10},
    }
    p_cam = perfis_cam["Freevalve"] if is_freevalve else perfis_cam.get(camshaft, perfis_cam["DOHC"])

    perfis_valvulas = {
        "Molas": {"tq": 1.00, "hp": 1.00, "tol": 0.0},
        "VVT": {"tq": 1.03, "hp": 1.03, "tol": 0.5},
        "Desmodrómico": {"tq": 1.01, "hp": 1.05, "tol": 2.0},
        "Pneumático": {"tq": 1.00, "hp": 1.08, "tol": 4.0},
        "Freevalve": {"tq": 1.00, "hp": 1.00, "tol": 4.5},
    }
    p_val = perfis_valvulas["Freevalve"] if is_freevalve else perfis_valvulas.get(valve_type, perfis_valvulas["Molas"])

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

    is_wankel = formato_valido == "WANKEL"
    n_val = 2 if int(num_valvulas) == 2 else 4
    val_tq = 1.00 if is_wankel else (1.02 if n_val == 2 else 1.00)
    val_hp = 1.00 if is_wankel else (0.93 if n_val == 2 else 1.00)
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
        * p_cam["tq"]
        * p_val["tq"]
        * val_tq
        * p_pis["tq"]
    ))

    fator_rpm_potencia = 0.93 if is_wankel else (0.88 if ciclo == "4T" else 0.94)
    potencia_cv = (
        ((torque_nm * max_rpm * fator_rpm_potencia) / 7121.0)
        * (adm_mp / adm_mb)
        * (perfil_comb["power"] / perfil_comb["torque"])
        * (p_cam["hp"] / p_cam["tq"])
        * (p_val["hp"] / p_val["tq"])
        * (val_hp / val_tq)
        * p_mat["hp"]
        * (p_pis["hp"] / p_pis["tq"])
        * 1.01387
    )
    potencia_kw = int(round(potencia_cv * 0.73549875))

    # 3. Validação da velocidade média do pistão / rotor e taxa de compressão
    if is_wankel:
        velocidade_pistao_mps = (2.0 * (stroke / 1000.0) * (max_rpm / 3.0) * 1.55) / 60.0
    else:
        velocidade_pistao_mps = (2.0 * (stroke / 1000.0) * max_rpm) / 60.0
    limite_vm = 25.0 + p_mat["tol"] + p_val["tol"] + p_pis["tol"]
    limite_cr = (22.0 if combustivel == "Diesel" else 15.0) + p_pis["cr_tol"]
    motivos_alerta = []
    if velocidade_pistao_mps > limite_vm:
        motivos_alerta.append(f"Vel. média do pistão elevada ({velocidade_pistao_mps:.1f} m/s > {limite_vm:.1f} m/s)")
    if cr > limite_cr:
        motivos_alerta.append(f"Taxa de compressão > {limite_cr:.0f}:1")
    alerta_rpm = len(motivos_alerta) > 0

    return {
        "tipo_motor": f"{formato_valido}{num_cilindros} · {admissao_valida} ({ciclo})",
        "cilindrada_litros": f"{cilindrada_litros:.2f} L",
        "pressao_bar": pressao_str,
        "torque_nm": f"{torque_nm} Nm",
        "potencia_kw": f"{potencia_kw} kW",
        "torque_nm_val": torque_nm,
        "potencia_kw_val": potencia_kw,
        "velocidade_pistao_mps": round(velocidade_pistao_mps, 2),
        "limite_vm": round(limite_vm, 1),
        "limite_cr": int(limite_cr),
        "alerta_rpm": alerta_rpm,
        "motivos_alerta": motivos_alerta,
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

            <!-- Página 2: Distribuição & Válvulas -->
            <div class="config-page" id="cfg-page-1" data-page="1">
                <div class="config-page-grid grid-cols-4">
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
                </div>
            </div>

            <!-- Página 3: Admissão & Combustão -->
            <div class="config-page" id="cfg-page-2" data-page="2">
                <div class="config-page-grid grid-cols-6">
                    <div class="campo-grupo">
                        <label for="select-admissao" id="lbl-admissao">TIPO DE ADMISSÃO</label>
                        <select id="select-admissao" class="input-cyber">
                            {options_adm_html}
                        </select>
                    </div>
                    <div class="campo-grupo">
                        <label for="select-combustivel" id="lbl-combustivel">COMBUSTÍVEL</label>
                        <select id="select-combustivel" class="input-cyber">
                            <option value="Gasolina" selected>Gasolina</option>
                            <option value="Etanol (E85)">Etanol (E85)</option>
                            <option value="Metanol">Metanol</option>
                            <option value="Diesel">Diesel</option>
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
                        <small id="sum-adm-sub">{dados_iniciais["pressao_bar"]}</small>
                    </div>
                    <div class="summary-pill">
                        <span id="lbl-sum-build">BLOCO &amp; COMBUSTÍVEL</span>
                        <strong id="sum-build-val">Alumínio</strong>
                        <small id="sum-build-sub">Pistão: Alumínio · Gasolina</small>
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
        .widget-card,
        .engine-action-dock,
        .motor-3d-hint {{
            pointer-events: auto;
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

        .btn-engine-ctrl.acelerando {{
            background: var(--btn-hover-grad);
            border-color: #ef4444;
            color: #ffffff;
            box-shadow: 0 6px 18px -4px rgba(220, 38, 38, 0.65);
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
            background: var(--btn-hover-grad);
            border-color: #ef4444;
            color: #ffffff;
            transform: translateY(-1px);
            box-shadow: 0 6px 18px -6px rgba(220, 38, 38, 0.65);
        }}

        .btn-engine-ctrl:not(:disabled):active {{
            transform: translateY(0);
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

        .config-page-grid.grid-cols-4 {{
            grid-template-columns: repeat(4, minmax(0, 1fr));
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
            .config-page-grid.grid-cols-7 {{
                grid-template-columns: repeat(4, minmax(0, 1fr));
            }}
            .config-page-grid.grid-cols-6,
            .summary-stats-grid {{
                grid-template-columns: repeat(3, minmax(0, 1fr));
            }}
        }}

        @media (max-width: 1020px) {{
            .dashboard-topbar {{
                align-self: stretch;
                justify-content: center;
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
            .config-page-grid.grid-cols-7,
            .config-page-grid.grid-cols-6,
            .config-page-grid.grid-cols-4,
            .summary-stats-grid {{
                grid-template-columns: repeat(2, minmax(0, 1fr));
            }}
            .dyno-canvas-wrap {{
                height: 195px;
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
        <header class="dashboard-topbar">
            <div class="topbar-right">
                <span class="widget-badge badge-live" id="motor-3d-badge">{formato_clean}{num_cilindros} · {adm_clean.upper()}</span>
                <button type="button" class="btn-3d-ctrl ativo" id="btn-3d-cutaway" aria-pressed="true" title="Alternar vista de corte transparente">Vista Corte</button>
                <button type="button" class="btn-3d-ctrl" id="btn-3d-autorotate" aria-pressed="false" title="Rodar o modelo automaticamente">Auto-Rodar</button>
                <button type="button" class="btn-3d-ctrl" id="btn-3d-reset" title="Repor ângulo inicial da câmara">Repor Vista</button>
                <button type="button" class="btn-3d-ctrl btn-lang-toggle" id="btn-lang-toggle" aria-pressed="false" title="Mudar idioma (Português / English)">PT → EN</button>
            </div>
        </header>

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
        const inputTurboBoost = document.getElementById('input-turbo-boost');
        const inputScBoost = document.getElementById('input-sc-boost');
        const rpmAlertaMsg = document.getElementById('rpm-alerta-msg');

        const btnEnginePower = document.getElementById('btn-engine-power');
        const btnEnginePowerLabel = document.getElementById('btn-engine-power-label');
        const btnEngineThrottle = document.getElementById('btn-engine-throttle');
        const btnSlowMo = document.getElementById('btn-slow-mo');
        const btnSlowMoLabel = document.getElementById('btn-slow-mo-label');
        const btnLangToggle = document.getElementById('btn-lang-toggle');
        const btnCutaway = document.getElementById('btn-3d-cutaway');
        const btnAutoRotate3D = document.getElementById('btn-3d-autorotate');
        const btnReset3D = document.getElementById('btn-3d-reset');
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
                throttle: 'Acelerar',
                throttleTitle: 'Manter premido (ou barra de espaço) para acelerar',
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
                lblAdmissao: 'TIPO DE ADMISSÃO',
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
                vTypeOpts: {{ 'Molas': 'Molas Helicoidais', 'VVT': 'VVT (Variável)', 'Desmodrómico': 'Desmodrómico', 'Pneumático': 'Pneumático', 'Freevalve': 'Freevalve (Eletropneumático)' }},
                admOpts: {{ 'Atmosférico': 'Atmosférico', 'Turbo': 'Turbo', 'Supercompressor': 'Supercompressor', 'Biturbo': 'Biturbo', 'Quad Turbo': 'Quad Turbo', 'Twincharge': 'Twincharge' }},
                fuelOpts: {{ 'Gasolina': 'Gasolina', 'Etanol (E85)': 'Etanol (E85)', 'Metanol': 'Metanol', 'Diesel': 'Diesel' }},
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
                throttle: 'Throttle',
                throttleTitle: 'Hold down (or Spacebar) to throttle',
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
                lblAdmissao: 'INDUCTION',
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
                vTypeOpts: {{ 'Molas': 'Coil Springs', 'VVT': 'VVT (Variable)', 'Desmodrómico': 'Desmodromic', 'Pneumático': 'Pneumatic', 'Freevalve': 'Freevalve (Electro-Pneumatic)' }},
                admOpts: {{ 'Atmosférico': 'Nat. Aspirated', 'Turbo': 'Turbocharged', 'Supercompressor': 'Supercharged', 'Biturbo': 'Twin-Turbo', 'Quad Turbo': 'Quad-Turbo', 'Twincharge': 'Twincharged' }},
                fuelOpts: {{ 'Gasolina': 'Gasoline', 'Etanol (E85)': 'Ethanol (E85)', 'Metanol': 'Methanol', 'Diesel': 'Diesel' }},
                warnPiston: (v, lim) => `High mean piston speed (${{v}} m/s > ${{lim}} m/s)`,
                warnCr: lim => `Compression ratio > ${{lim}}:1`
            }}
        }};

        /* ----------------------------------------------------------------------
           ESTADO DE SIMULAÇÃO EM TEMPO REAL (Ligar/Desligar + Acelerar + Dyno)
           ---------------------------------------------------------------------- */
        const engineSim = {{
            on: false,
            throttleHeld: false,
            blipTimer: 0,
            currentRpm: 0,
            idleRpm: 950,
            maxRpm: 7500,
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
            if (selectCamshaft) selectCamshaft.disabled = isWankel;
            if (selectValveType) selectValveType.disabled = isWankel;
            if (selectValves) selectValves.disabled = isWankel;
        }}

        function syncBoostControls(resetToDefaults = false) {{
            if (!selectAdmissao) return;
            const adm = selectAdmissao.value || 'Atmosférico';
            const hasTurbo = ['Turbo', 'Biturbo', 'Quad Turbo', 'Twincharge'].includes(adm);
            const hasSc = ['Supercompressor', 'Twincharge'].includes(adm);
            const defs = DEFAULT_BOOST_BY_ADM[adm] || DEFAULT_BOOST_BY_ADM['Atmosférico'];
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
            if (dashboardMain) dashboardMain.classList.toggle('dyno-hidden', !isLast);
            if (motor3D && typeof motor3D.setRightPanelVisible === 'function') {{
                motor3D.setRightPanelVisible(isLast);
            }}
            if (isLast) {{
                drawDynoChart();
            }}
        }}

        function applyLanguage() {{
            const t = I18N[currentLang];
            document.documentElement.lang = currentLang;
            const setTxt = (id, val) => {{ const el = document.getElementById(id); if (el) el.textContent = val; }};
            setTxt('btn-3d-autorotate', t.autoRotate);
            setTxt('btn-3d-reset', t.resetView);
            setTxt('motor-3d-hint', t.hint);
            setTxt('btn-engine-throttle-label', t.throttle);
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
            setTxt('lbl-admissao', t.lblAdmissao);
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
            if (btnEngineThrottle) btnEngineThrottle.title = t.throttleTitle;
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
            mapOpts(selectAdmissao, t.admOpts);
            mapOpts(selectCombustivel, t.fuelOpts);
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

        function computeDynoData(params) {{
            const fatoresComb = {{
                'Gasolina': {{ tq: 1.00, hp: 1.00 }},
                'Etanol (E85)': {{ tq: 1.08, hp: 1.08 }},
                'Metanol': {{ tq: 1.12, hp: 1.12 }},
                'Diesel': {{ tq: 1.14, hp: 0.78 }}
            }};
            const admKey = ['Atmosférico', 'Turbo', 'Supercompressor', 'Biturbo', 'Quad Turbo', 'Twincharge'].includes(params.admissao)
                ? params.admissao
                : 'Atmosférico';
            const turboBar = Math.max(0, Math.min(6, Number(params.turbo_bar) || 0));
            const scBar = Math.max(0, Math.min(4, Number(params.sc_bar) || 0));
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

            const perfilComb = fatoresComb[params.combustivel] || fatoresComb['Gasolina'];
            const isDiesel = params.combustivel === 'Diesel';
            const isWankel = params.formato === 'WANKEL';
            const isFreevalve = !isWankel && (params.camshaft === 'Freevalve' || params.valve_type === 'Freevalve');

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
                'Freevalve': {{ tq: 1.00, hp: 1.00 }}
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
            const pCam = isWankel ? {{ tq: 1.00, hp: 1.00 }} : (isFreevalve ? camMap['Freevalve'] : (camMap[params.camshaft] || camMap['DOHC']));
            const pVal = isWankel ? {{ tq: 1.00, hp: 1.00 }} : (isFreevalve ? valMap['Freevalve'] : (valMap[params.valve_type] || valMap['Molas']));
            const pMatHp = matHpMap[params.material] || 1.00;
            const pPis = pisMap[params.piston_material] || pisMap['Alumínio'];
            const nVal = parseInt(params.num_valvulas, 10) === 2 ? 2 : 4;
            const valTq = isWankel ? 1.00 : (nVal === 2 ? 1.02 : 1.00);
            const valHp = isWankel ? 1.00 : (nVal === 2 ? 0.93 : 1.00);

            const fatorCr = 1.0 + Math.max(-0.25, Math.min(0.35, (params.compression_ratio - 10.0) * 0.025));
            const fatorCicloTq = isWankel ? 1.42 : (params.ciclo === '2T' ? 1.25 : 1.00);
            const peakTorqueNm = Math.round(litros * 105.0 * fatorCr * perfilComb.tq * fatorCicloTq * admMb * pCam.tq * pVal.tq * valTq * pPis.tq);
            const fatorRpmHp = isWankel ? 0.93 : (params.ciclo === '4T' ? 0.88 : 0.94);
            const peakPowerCv = ((peakTorqueNm * params.max_rpm * fatorRpmHp) / 7121.0) * (admMp / admMb) * (perfilComb.hp / perfilComb.tq) * (pCam.hp / pCam.tq) * (pVal.hp / pVal.tq) * (valHp / valTq) * pMatHp * (pPis.hp / pPis.tq) * 1.01387;
            const peakPowerKw = Math.round(peakPowerCv * 0.73549875);

            const maxRpm = Math.max(1500, params.max_rpm);
            const startRpm = Math.min(1000, Math.round(maxRpm * 0.15));
            const steps = 48;
            const strokeRatio = Math.max(0.75, Math.min(1.25, params.stroke / Math.max(1, params.bore)));
            const lowEndBias = (strokeRatio - 1.0) * 0.14 + (isDiesel ? 0.12 : 0.0) + (params.camshaft === 'OHV' && !isWankel ? 0.04 : 0.0) + (params.valve_type === 'VVT' && !isWankel ? 0.05 : 0.0) + (isFreevalve ? 0.06 : 0.0) + (nVal === 2 && !isWankel ? 0.04 : 0.0);

            const raw = [];
            let maxRawT = 1e-6;
            for (let i = 0; i <= steps; i++) {{
                const rpm = startRpm + (maxRpm - startRpm) * (i / steps);
                const u = rpm / maxRpm;
                let tShape = 1.0;

                if (admKey === 'Atmosférico') {{
                    const rise = Math.sin(Math.min(1, u / (isDiesel ? 0.48 : 0.70)) * (Math.PI * 0.5));
                    const drop = Math.max(0, u - (isDiesel ? 0.58 : (isWankel ? 0.78 : 0.72))) * (isDiesel ? 0.76 : (isWankel ? 0.42 : 0.56));
                    tShape = (0.70 + lowEndBias) + 0.30 * rise - drop;
                }} else if (admKey === 'Turbo') {{
                    const spoolRpm = Math.min(maxRpm * (isDiesel ? 0.34 : 0.44), (isDiesel ? 2000 : 2700) + turboBar * 240);
                    const spool = smoothstep(spoolRpm * 0.42, spoolRpm * 1.05, rpm);
                    tShape = ((isDiesel ? 0.56 : 0.46) + (isDiesel ? 0.44 : 0.54) * spool) * (1.0 - Math.max(0, u - (isDiesel ? 0.62 : 0.78)) * (isDiesel ? 0.78 : 0.54));
                }} else if (admKey === 'Biturbo') {{
                    const spoolRpm = Math.min(maxRpm * (isDiesel ? 0.30 : 0.40), (isDiesel ? 1850 : 2500) + turboBar * 180);
                    const spool = smoothstep(spoolRpm * 0.40, spoolRpm * 1.02, rpm);
                    tShape = ((isDiesel ? 0.60 : 0.50) + (isDiesel ? 0.40 : 0.50) * spool) * (1.0 - Math.max(0, u - (isDiesel ? 0.68 : 0.82)) * (isDiesel ? 0.62 : 0.42));
                }} else if (admKey === 'Quad Turbo') {{
                    const spoolRpm = Math.min(maxRpm * (isDiesel ? 0.28 : 0.38), (isDiesel ? 1750 : 2400) + turboBar * 160);
                    const spool = smoothstep(spoolRpm * 0.36, spoolRpm * 0.98, rpm);
                    tShape = ((isDiesel ? 0.62 : 0.52) + (isDiesel ? 0.38 : 0.48) * spool) * (1.0 - Math.max(0, u - (isDiesel ? 0.72 : 0.86)) * (isDiesel ? 0.54 : 0.32));
                }} else if (admKey === 'Supercompressor') {{
                    const rise = Math.sin(Math.min(1, u / 0.62) * (Math.PI * 0.5));
                    tShape = (0.83 + lowEndBias * 0.5) + 0.17 * rise - Math.max(0, u - (isDiesel ? 0.60 : 0.72)) * (isDiesel ? 0.72 : 0.50);
                }} else {{
                    // Twincharge: compressor em baixa + turbo em alta
                    tShape = 0.86 + 0.14 * smoothstep(0.16, 0.54, u) - Math.max(0, u - (isDiesel ? 0.70 : 0.84)) * (isDiesel ? 0.60 : 0.38);
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

            engineSim.maxRpm = maxRpm;
            engineSim.idleRpm = Math.min(1150, Math.max(750, Math.round(maxRpm * 0.13)));
            engineSim.dynoPoints = points;
            engineSim.peakPowerKw = peakPowerKw;
            engineSim.peakPowerRpm = Math.round(bestP.rpm);
            engineSim.peakTorqueNm = peakTorqueNm;
            engineSim.peakTorqueRpm = Math.round(bestT.rpm);

            syncUnitDisplays();
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

            const padL = 40, padR = 40, padT = 18, padB = 34;
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
            ctx.font = '600 9.5px "JetBrains Mono", monospace';
            ctx.fillStyle = 'rgba(248, 113, 113, 0.90)';
            ctx.textAlign = 'right';
            ctx.fillText(powerUnitLabel(), padL - 6, padT - 5);
            ctx.fillStyle = 'rgba(212, 155, 75, 0.92)';
            ctx.textAlign = 'left';
            ctx.fillText(torqueUnitLabel(), padL + pw + 6, padT - 5);

            ctx.font = '600 10px "JetBrains Mono", monospace';
            for (let g = 0; g <= 4; g++) {{
                const gy = padT + (ph * g) / 4;
                ctx.beginPath();
                ctx.moveTo(padL, gy);
                ctx.lineTo(padL + pw, gy);
                ctx.stroke();

                const pVal = Math.round(maxPowerAxis * (1 - g / 4));
                const tVal = Math.round(maxTorqueAxis * (1 - g / 4));
                ctx.fillStyle = 'rgba(248, 113, 113, 0.82)';
                ctx.textAlign = 'right';
                ctx.fillText(String(pVal), padL - 6, gy + 3);

                ctx.fillStyle = 'rgba(212, 155, 75, 0.85)';
                ctx.textAlign = 'left';
                ctx.fillText(String(tVal), padL + pw + 6, gy + 3);
            }}

            // Eixo X simplificado (×1000 RPM: 1K -> 1, 2K -> 2...)
            const stepRpm = maxRpm > 16000 ? 4000 : (maxRpm > 9000 ? 2000 : 1000);
            const firstTick = Math.max(stepRpm, Math.ceil(minRpm / stepRpm) * stepRpm);
            ctx.fillStyle = '#9ca3af';
            ctx.textAlign = 'center';
            for (let rVal = firstTick; rVal <= maxRpm; rVal += stepRpm) {{
                const gx = xOf(rVal);
                ctx.beginPath();
                ctx.moveTo(gx, padT);
                ctx.lineTo(gx, padT + ph);
                ctx.stroke();
                ctx.fillText(String(Math.round(rVal / 1000)), gx, padT + ph + 13);
            }}
            ctx.font = '600 9px "JetBrains Mono", monospace';
            ctx.fillStyle = '#6b7280';
            ctx.fillText('RPM (×1000)', padL + pw * 0.5, ch - 4);

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
            ctx.lineWidth = 2.2;
            ctx.stroke();

            // Curva de Potência
            ctx.beginPath();
            pts.forEach((p, idx) => {{
                const x = xOf(p.rpm), y = yPower(convertPower(p.powerKw));
                if (idx === 0) ctx.moveTo(x, y); else ctx.lineTo(x, y);
            }});
            ctx.strokeStyle = '#ef4444';
            ctx.lineWidth = 2.5;
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
                ctx.beginPath(); ctx.arc(mx, ty, 4.2, 0, Math.PI * 2); ctx.fill();
                ctx.strokeStyle = '#07090d'; ctx.lineWidth = 1.5; ctx.stroke();

                ctx.fillStyle = '#ef4444';
                ctx.beginPath(); ctx.arc(mx, py, 4.6, 0, Math.PI * 2); ctx.fill();
                ctx.strokeStyle = '#07090d'; ctx.lineWidth = 1.5; ctx.stroke();
            }}

            ctx.restore();
        }}

        if (dynoCanvas) {{
            dynoCanvas.addEventListener('pointermove', e => {{
                const rect = dynoCanvas.getBoundingClientRect();
                const pts = engineSim.dynoPoints;
                if (!pts.length || !rect.width) return;
                const padL = 40, padR = 40;
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
                    combustivel: 'Gasolina',
                    vAngle: '60',
                    material: 'Alumínio',
                    pistonMaterial: 'Alumínio',
                    camshaft: 'DOHC',
                    valveType: 'Molas',
                    numValvulas: 4,
                    turboBar: 0.0,
                    scBar: 0.0
                }};

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
                        vec3 L1 = normalize(vec3(0.55, 0.88, 0.65));
                        vec3 L2 = normalize(vec3(-0.78, 0.35, -0.55));
                        vec3 L3 = normalize(vec3(0.15, -0.65, 0.72));
                        float hemi = 0.5 + 0.5 * N.y;
                        vec3 ambient = mix(vec3(0.28, 0.31, 0.37), vec3(0.74, 0.78, 0.84), hemi);
                        float diff1 = max(dot(N, L1), 0.0);
                        float diff2 = max(dot(N, L2), 0.0);
                        float diff3 = max(dot(N, L3), 0.0);
                        vec3 H1 = normalize(L1 + V);
                        vec3 H2 = normalize(L2 + V);
                        float spec1 = pow(max(dot(N, H1), 1e-4), max(1.0, uSpec.y)) * uSpec.x * 1.15;
                        float spec2 = pow(max(dot(N, H2), 1e-4), max(1.0, uSpec.y * 0.7)) * uSpec.x * 0.45;
                        float fres = pow(clamp(1.0 - max(dot(N, V), 0.0), 1e-4, 1.0), 2.8);
                        float metal = clamp((uSpec.x - 0.34) / 0.56, 0.0, 1.0);
                        float studioBand = smoothstep(0.14, 0.86, diff1 * 0.72 + fres * 0.68) * metal;
                        vec3 studioTint = mix(vec3(0.74, 0.84, 0.96), vec3(1.0, 0.95, 0.88), clamp(diff2 * 1.4, 0.0, 1.0));
                        float rim = fres * (0.15 + 0.22 * uSpec.x);
                        float diffGain = mix(1.0, 0.80, metal);
                        vec3 specTint = mix(vec3(1.0), uColor.rgb * 0.55 + vec3(0.45), metal);
                        vec3 col = uColor.rgb * (ambient * 0.44 + (diff1 * 0.74 + diff2 * 0.34 + diff3 * 0.18) * diffGain)
                                 + specTint * vec3(spec1 * 1.16 + spec2 * 1.06)
                                 + studioTint * (studioBand * 0.15)
                                 + vec3(rim * 0.74, rim * 0.84, rim);
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
                    cyl: this.makeMesh(this.buildCylinderData(32, 1.0, 1.0)),
                    cone: this.makeMesh(this.buildCylinderData(32, 1.0, 0.54)),
                    hex: this.makeMesh(this.buildCylinderData(6, 1.0, 1.0)),
                    camLobe: this.makeMesh(this.buildCamLobeData(32)),
                    gear: this.makeMesh(this.buildGearData(20, 0.88, 1.04)),
                    torus: this.makeMesh(this.buildTorusData(32, 16, 0.42)),
                    sphere: this.makeMesh(this.buildSphereData(12, 16)),
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
                        const bulge = 0.12 * Math.sin(Math.PI * u);
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

            addPipe(targetList, points, radius, color, spec = [0.62, 52], couplerIndices = []) {{
                const C_COUPLER = [0.16, 0.20, 0.28, 1.0];
                for (let i = 0; i < points.length - 1; i++) {{
                    const p1 = points[i], p2 = points[i + 1];
                    const dx = p2[0] - p1[0], dy = p2[1] - p1[1], dz = p2[2] - p1[2];
                    const len = Math.hypot(dx, dy, dz);
                    if (len < 0.001) continue;
                    const ux = dx / len, uy = dy / len, uz = dz / len;
                    const mx = (p1[0] + p2[0]) * 0.5;
                    const my = (p1[1] + p2[1]) * 0.5;
                    const mz = (p1[2] + p2[2]) * 0.5;
                    const ax = uz, az = -ux;
                    const axisLen = Math.hypot(ax, az);
                    let m;
                    if (axisLen < 1e-4) {{
                        m = this.matTRS(mx, my, mz, uy < 0 ? Math.PI : 0, 0, 0, radius, len, radius);
                    }} else {{
                        const ang = Math.acos(Math.max(-1, Math.min(1, uy)));
                        m = this.matAxisAngle(mx, my, mz, ax, 0, az, ang, radius, len, radius);
                    }}
                    this.addPart(targetList, 'cyl', m, color, spec);
                    if (i > 0) {{
                        this.addPart(targetList, 'sphere', this.matTRS(p1[0], p1[1], p1[2], 0, 0, 0, radius * 1.02, radius * 1.02, radius * 1.02), color, spec);
                    }}
                    if (couplerIndices.includes(i) && len > 0.16) {{
                        let cm;
                        if (axisLen < 1e-4) {{
                            cm = this.matTRS(mx, my, mz, uy < 0 ? Math.PI : 0, 0, 0, radius * 1.24, 0.12, radius * 1.24);
                        }} else {{
                            const ang = Math.acos(Math.max(-1, Math.min(1, uy)));
                            cm = this.matAxisAngle(mx, my, mz, ax, 0, az, ang, radius * 1.24, 0.12, radius * 1.24);
                        }}
                        this.addPart(targetList, 'cyl', cm, C_COUPLER, [0.25, 16]);
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
                    this.addPart(this.staticOpaque, 'box', this.matTRS(x, dTop * cosA, z + dTop * sinA, tiltAngle, 0, 0, 0.095, 0.06, 0.11), C_CAP, [0.45, 34]);
                    // Linha metálica de alta pressão Common Rail para cada injetor
                    const dSide = y + 0.04;
                    this.addPart(this.staticOpaque, 'cyl', this.matTRS(x, dSide * cosA - 0.06 * sinA, z + dSide * sinA + 0.06 * cosA, tiltAngle + 0.6, 0, 0, 0.018, 0.14, 0.018), [0.80, 0.84, 0.88, 1.0], [0.8, 64]);
                }} else {{
                    const C_COIL = [0.68, 0.22, 0.22, 1.0];
                    const C_BOOT = [0.18, 0.20, 0.24, 1.0];
                    this.addPart(this.staticOpaque, 'cyl', this.matTRS(x, dBase * cosA, z + dBase * sinA, tiltAngle, 0, 0, 0.055, 0.13, 0.055), C_BOOT, [0.3, 18]);
                    const dTop = y + 0.08;
                    this.addPart(this.staticOpaque, 'box', this.matTRS(x, dTop * cosA, z + dTop * sinA, tiltAngle, 0, 0, 0.12, 0.075, 0.14), C_COIL, [0.55, 40]);
                    this.addPart(this.staticOpaque, 'box', this.matTRS(x, (dTop + 0.045) * cosA, z + (dTop + 0.045) * sinA, tiltAngle, 0, 0, 0.06, 0.025, 0.08), C_BOOT, [0.4, 24]);
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

            addTurboUnit(cx, cy, cz, scale, flipZ = 1) {{
                const s = scale;
                const C_COMP = [0.78, 0.82, 0.87, 1.0];
                const C_TURB = [0.50, 0.36, 0.28, 1.0];
                const C_CART = [0.34, 0.38, 0.44, 1.0];
                const C_HUB  = [0.24, 0.41, 0.60, 1.0];
                const C_BLADE = [0.90, 0.93, 0.96, 1.0];
                const C_WASTE = [0.58, 0.62, 0.68, 1.0];

                // Center bearing housing (CHRA) + oil feed/drain bosses + V-band clamp rings
                this.addPart(this.staticOpaque, 'cyl', this.matTRS(cx, cy, cz, 0, 0, Math.PI * 0.5, 0.14 * s, 0.32 * s, 0.14 * s), C_CART, [0.55, 40]);
                this.addPart(this.staticOpaque, 'cyl', this.matTRS(cx, cy + 0.17 * s, cz, 0, 0, 0, 0.038 * s, 0.14 * s, 0.038 * s), [0.72, 0.60, 0.32, 1.0], [0.65, 52]);
                this.addPart(this.staticOpaque, 'cyl', this.matTRS(cx, cy - 0.16 * s, cz, 0, 0, 0, 0.042 * s, 0.12 * s, 0.042 * s), C_CART, [0.5, 36]);
                this.addPart(this.staticOpaque, 'cyl', this.matTRS(cx - 0.09 * s, cy, cz, 0, 0, Math.PI * 0.5, 0.21 * s, 0.03 * s, 0.21 * s), C_COMP, [0.75, 62]);
                this.addPart(this.staticOpaque, 'cyl', this.matTRS(cx + 0.09 * s, cy, cz, 0, 0, Math.PI * 0.5, 0.19 * s, 0.03 * s, 0.19 * s), C_WASTE, [0.65, 52]);
                // Compressor snail + intake bellmouth + blow-off valve (BOV)
                this.addPart(this.staticOpaque, 'torus', this.matTRS(cx - 0.17 * s, cy, cz, 0, Math.PI * 0.5, 0, 0.25 * s, 0.25 * s, 0.25 * s), C_COMP, [0.78, 68]);
                this.addPart(this.staticOpaque, 'cyl', this.matTRS(cx - 0.25 * s, cy, cz, 0, 0, Math.PI * 0.5, 0.19 * s, 0.15 * s, 0.19 * s), C_COMP, [0.72, 60]);
                this.addPart(this.staticOpaque, 'cone', this.matTRS(cx - 0.34 * s, cy, cz, 0, 0, Math.PI * 0.5, 0.21 * s, 0.09 * s, 0.21 * s), C_COMP, [0.76, 64]);
                this.addPart(this.staticOpaque, 'cyl', this.matTRS(cx - 0.17 * s, cy + 0.26 * s, cz - 0.14 * s * flipZ, 0, 0, 0, 0.065 * s, 0.14 * s, 0.065 * s), [0.72, 0.24, 0.24, 1.0], [0.68, 54]);
                // Turbine snail + exhaust outlet flange + downpipe + O2 sensor
                this.addPart(this.staticOpaque, 'torus', this.matTRS(cx + 0.17 * s, cy, cz, 0, Math.PI * 0.5, 0, 0.22 * s, 0.22 * s, 0.22 * s), C_TURB, [0.40, 28]);
                this.addPart(this.staticOpaque, 'cyl', this.matTRS(cx + 0.26 * s, cy, cz, 0, 0, Math.PI * 0.5, 0.15 * s, 0.16 * s, 0.15 * s), C_TURB, [0.35, 24]);
                this.addPipe(this.staticOpaque, [[cx + 0.33 * s, cy, cz], [cx + 0.62 * s, cy - 0.08 * s, cz], [cx + 0.78 * s, cy - 0.36 * s, cz]], 0.115 * s, C_TURB, [0.42, 30]);
                this.addPart(this.staticOpaque, 'cyl', this.matTRS(cx + 0.55 * s, cy + 0.05 * s, cz, -0.35, 0, -0.35, 0.028 * s, 0.14 * s, 0.028 * s), C_WASTE, [0.7, 56]);
                // Wastegate actuator canister + rod
                this.addPart(this.staticOpaque, 'cyl', this.matTRS(cx - 0.04 * s, cy + 0.26 * s, cz + 0.16 * s * flipZ, 0, 0, Math.PI * 0.5, 0.08 * s, 0.16 * s, 0.08 * s), C_WASTE, [0.6, 48]);
                this.addPart(this.staticOpaque, 'cyl', this.matTRS(cx + 0.10 * s, cy + 0.21 * s, cz + 0.10 * s * flipZ, 0.3, 0, Math.PI * 0.5, 0.018 * s, 0.24 * s, 0.018 * s), C_COMP, [0.7, 56]);

                this.dynamicRotors.push({{
                    type: 'impeller',
                    cx: cx - 0.35 * s, cy, cz,
                    r: 0.145 * s,
                    speedMult: 2.2,
                    colorHub: C_HUB,
                    colorBlade: C_BLADE
                }});

                return {{
                    inlet: [cx - 0.36 * s, cy, cz],
                    compOut: [cx - 0.17 * s, cy + 0.25 * s, cz],
                    turbOut: [cx + 0.34 * s, cy, cz]
                }};
            }}

            addSuperchargerUnit(x, y, z, lenX, widthZ, pulleyX) {{
                const C_BODY = [0.35, 0.40, 0.47, 1.0];
                const C_RIB  = [0.60, 0.65, 0.72, 1.0];
                const C_SNOUT = [0.68, 0.73, 0.79, 1.0];
                const C_BELT = [0.15, 0.17, 0.20, 1.0];

                this.addPart(this.staticOpaque, 'box', this.matTRS(x, y, z, 0, 0, 0, lenX, 0.42, widthZ), C_BODY, [0.55, 44]);
                this.addPart(this.staticOpaque, 'cyl', this.matTRS(x, y + 0.08, z - widthZ * 0.22, 0, 0, Math.PI * 0.5, 0.18, lenX * 0.98, 0.18), C_RIB, [0.68, 58]);
                this.addPart(this.staticOpaque, 'cyl', this.matTRS(x, y + 0.08, z + widthZ * 0.22, 0, 0, Math.PI * 0.5, 0.18, lenX * 0.98, 0.18), C_RIB, [0.68, 58]);
                for (let k = -3; k <= 3; k++) {{
                    this.addPart(this.staticOpaque, 'box', this.matTRS(x + k * (lenX * 0.13), y + 0.25, z, 0, 0, 0, 0.045, 0.055, widthZ * 0.94), C_RIB, [0.62, 50]);
                }}
                // Billet blower snout & flange
                const snoutLen = Math.max(0.25, (x - lenX * 0.5) - pulleyX);
                const snoutCx = pulleyX + snoutLen * 0.5;
                this.addPart(this.staticOpaque, 'cyl', this.matTRS(snoutCx, y, z, 0, 0, Math.PI * 0.5, 0.098, snoutLen + 0.14, 0.098), C_SNOUT, [0.72, 62]);
                this.addPart(this.staticOpaque, 'box', this.matTRS(x - lenX * 0.5, y, z, 0, 0, 0, 0.07, 0.30, 0.32), C_RIB, [0.65, 52]);
                // Bypass actuator valve on side
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
                const C_CORE = [0.74, 0.78, 0.84, 1.0];
                const C_TANK = [0.42, 0.47, 0.54, 1.0];
                const C_FIN  = [0.48, 0.52, 0.58, 1.0];
                this.addPart(this.staticOpaque, 'box', this.matTRS(cx, cy, cz, 0, 0, 0, wX, hY, dZ * 0.76), C_CORE, [0.65, 50]);
                this.addPart(this.staticOpaque, 'box', this.matTRS(cx, cy, cz - dZ * 0.48, 0, 0, 0, wX * 1.06, hY * 1.04, dZ * 0.20), C_TANK, [0.5, 40]);
                this.addPart(this.staticOpaque, 'box', this.matTRS(cx, cy, cz + dZ * 0.48, 0, 0, 0, wX * 1.06, hY * 1.04, dZ * 0.20), C_TANK, [0.5, 40]);
                // Cooling fin rows + top mounting brackets
                for (let k = -3; k <= 3; k++) {{
                    this.addPart(this.staticOpaque, 'box', this.matTRS(cx, cy + k * (hY * 0.13), cz, 0, 0, 0, wX * 1.05, 0.020, dZ * 0.73), C_FIN, [0.4, 24]);
                }}
                this.addPart(this.staticOpaque, 'box', this.matTRS(cx, cy + hY * 0.54, cz - dZ * 0.3, 0, 0, 0, wX * 0.6, 0.06, 0.08), C_TANK, [0.5, 36]);
                this.addPart(this.staticOpaque, 'box', this.matTRS(cx, cy + hY * 0.54, cz + dZ * 0.3, 0, 0, 0, wX * 0.6, 0.06, 0.08), C_TANK, [0.5, 36]);
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

                const n = Math.max(1, Math.min(16, parseInt(this.config.cilindros, 10) || 4));
                const fmt = ['I', 'V', 'VR', 'W', 'B', 'WANKEL'].includes(this.config.formato) ? this.config.formato : 'I';
                const adm = this.config.admissao || 'Atmosférico';
                const isDiesel = this.config.combustivel === 'Diesel';
                const vAngOpt = this.config.vAngle === '90' ? '90' : '60';
                const matOpt = this.config.material || 'Alumínio';
                const pMatOpt = this.config.pistonMaterial || 'Alumínio';
                const camMode = ['DOHC', 'SOHC', 'OHV', 'Freevalve'].includes(this.config.camshaft) ? this.config.camshaft : 'DOHC';
                const vType = this.config.valveType || 'Molas';
                const isFreevalve = fmt !== 'WANKEL' && (camMode === 'Freevalve' || vType === 'Freevalve');
                const valvesCount = parseInt(this.config.numValvulas, 10) === 2 ? 2 : 4;
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
                const C_GASKET  = [0.76, 0.45, 0.22, 1.0];
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
                const C_INTAKE  = [0.46, 0.51, 0.58, 1.0];
                const C_RUNNER  = [0.58, 0.63, 0.69, 1.0];
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
                    // Cárter detalhado + aletas de arrefecimento + bujão sextavado em latão
                    this.addPart(this.staticOpaque, 'box', this.matTRS(0, -crankR - 0.14, 0, 0, 0, 0, blockW * 1.03, 0.10, blockZ * 1.02), C_SUMP, [0.4, 24]);
                    this.addPart(this.staticOpaque, 'box', this.matTRS(0, -crankR - 0.30, 0, 0, 0, 0, blockW * 0.96, 0.28, blockZ * 0.90), C_SUMP, [0.35, 20]);
                    this.addPart(this.staticOpaque, 'cyl', this.matTRS(halfLenX * 0.60, -crankR - 0.43, 0, 0, 0, 0, 0.048, 0.05, 0.048), [0.76, 0.62, 0.28, 1.0], [0.7, 52]);
                    for (let f = -2; f <= 2; f++) {{
                        this.addPart(this.staticOpaque, 'box', this.matTRS(0, -crankR - 0.45, f * (blockZ * 0.16), 0, 0, 0, blockW * 0.88, 0.03, 0.03), C_BLOCK, [0.5, 32]);
                    }}

                    // Bloco, saia do cárter a cobrir a cambota, nervuras estruturais, capas de mancal, relas, arranque e filtro
                    const blockY = deckDist * 0.46;
                    const blockH = deckDist * 0.92;
                    const skirtBot = -crankR - 0.10;
                    const skirtH = 0.04 - skirtBot;
                    const skirtZ = Math.max(blockZ * 1.02, crankR * 2.55);
                    this.addPart(this.staticTrans, 'box', this.matTRS(0, blockY, 0, 0, 0, 0, blockW, blockH, blockZ), C_BLOCK, BLK_SPEC);
                    this.addPart(this.staticTrans, 'box', this.matTRS(0, skirtBot + skirtH * 0.5, 0, 0, 0, 0, blockW * 1.01, skirtH, skirtZ), C_BLOCK, BLK_SPEC);
                    this.addPart(this.staticTrans, 'box', this.matTRS(halfLenX + 0.03, skirtBot + skirtH * 0.5, 0, 0, 0, 0, 0.06, skirtH, skirtZ * 0.98), C_BLOCK, BLK_SPEC);
                    // Junta MLS da colaça em cobre-bronze + nervuras estruturais laterais + vareta do óleo + termóstato
                    this.addPart(this.staticOpaque, 'box', this.matTRS(0, deckDist - 0.012, 0, 0, 0, 0, blockW * 1.018, 0.024, blockZ * 1.018), C_GASKET, [0.72, 54]);
                    this.addPart(this.staticOpaque, 'box', this.matTRS(-halfLenX - 0.11, deckDist - 0.012, blockZ * 0.36, 0, 0, 0, 0.09, 0.026, 0.12), C_GASKET, [0.75, 56]);
                    for (const ribSide of [-1, 1]) {{
                        for (let rIdx = 0; rIdx < n; rIdx++) {{
                            const rx = cylSpecs[rIdx].x;
                            this.addPart(this.staticOpaque, 'box', this.matTRS(rx, blockY, ribSide * (blockZ * 0.51), 0, 0, 0, 0.042, blockH * 0.78, 0.036), C_BLOCK, BLK_SPEC);
                            this.addPart(this.staticOpaque, 'hex', this.matTRS(rx, deckDist + 0.415, ribSide * (blockZ * 0.34), 0, 0, 0, 0.032, 0.024, 0.032), C_BOLT, [0.78, 60]);
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
                    this.addPart(this.staticOpaque, 'box', this.matTRS(0, blockY - 0.10, blockZ * 0.50, 0, 0, 0, blockW * 0.96, 0.045, 0.045), C_BLOCK, [0.5, 32]);
                    this.addPart(this.staticOpaque, 'box', this.matTRS(0, blockY - 0.10, -blockZ * 0.50, 0, 0, 0, blockW * 0.96, 0.045, 0.045), C_BLOCK, [0.5, 32]);
                    for (let i = 0; i < n; i++) {{
                        const cx = cylSpecs[i].x;
                        this.addPart(this.staticOpaque, 'cyl', this.matTRS(cx, blockY, blockZ * 0.51, Math.PI * 0.5, 0, 0, 0.075, 0.03, 0.075), C_BOLT, [0.7, 56]);
                        this.addPart(this.staticOpaque, 'cyl', this.matTRS(cx, blockY, -blockZ * 0.51, Math.PI * 0.5, 0, 0, 0.075, 0.03, 0.075), C_BOLT, [0.7, 56]);
                        this.addPart(this.staticOpaque, 'box', this.matTRS(cx, -0.05, 0, 0, 0, 0, 0.12, 0.24, 0.28), C_CRANK, [0.48, 34]);
                    }}
                    // Filtro de óleo + sensor de pressão + motor de arranque traseiro
                    this.addPart(this.staticOpaque, 'cyl', this.matTRS(-halfLenX * 0.32, -0.06, blockZ * 0.64, 0.65, 0, 0, 0.12, 0.28, 0.12), C_FILTER, [0.55, 44]);
                    this.addPart(this.staticOpaque, 'cyl', this.matTRS(-halfLenX * 0.05, 0.08, blockZ * 0.55, Math.PI * 0.5, 0, 0, 0.032, 0.08, 0.032), [0.76, 0.62, 0.28, 1.0], [0.7, 54]);
                    this.addStarterMotor(halfLenX * 0.62, -0.06, blockZ * 0.56 + 0.16);

                    // Cabeça, tampa de válvulas sólida de largura integral, tampa de óleo e pernos de cabeça
                    this.addPart(this.staticTrans, 'box', this.matTRS(0, deckDist + 0.16, 0, 0, 0, 0, blockW * 1.01, 0.28, blockZ * 1.04), C_HEAD, [0.46, 36]);
                    this.addPart(this.staticOpaque, 'box', this.matTRS(0, deckDist + 0.37, 0, 0, 0, 0, blockW * 1.02, 0.14, blockZ * 1.02), C_VALVE, [0.55, 48]);
                    this.addPart(this.staticOpaque, 'box', this.matTRS(0, deckDist + 0.445, -blockZ * 0.24, 0, 0, 0, blockW * 0.92, 0.035, 0.06), C_BOLT, [0.7, 54]);
                    this.addPart(this.staticOpaque, 'box', this.matTRS(0, deckDist + 0.445,  blockZ * 0.24, 0, 0, 0, blockW * 0.92, 0.035, 0.06), C_BOLT, [0.7, 54]);
                    this.addPart(this.staticOpaque, 'cyl', this.matTRS(-halfLenX * 0.70, deckDist + 0.46, 0.06, 0, 0, 0, 0.095, 0.06, 0.095), C_BOLT, [0.7, 54]);

                    // Distribuição DOHC / SOHC / OHV / Freevalve + capas + calha elétrica + bobinas/injetores
                    const camZIn = blockZ * 0.22;
                    const camZEx = -blockZ * 0.22;
                    const tx = -halfLenX - 0.24;
                    this.addPart(this.staticOpaque, 'box', this.matTRS(0, deckDist + 0.46, 0.14, 0, 0, 0, blockW * 0.88, 0.04, 0.045), C_BELT, [0.25, 16]);
                    if (isFreevalve) {{
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
                    if (isFreevalve) {{
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
                        this.addPipe(this.staticOpaque, [
                            [cx, portY, blockZ * 0.45],
                            [cx, portY + 0.11, intZ * 0.84],
                            [cx, portY + 0.02, intZ]
                        ], 0.072 * boreScale, C_RUNNER);
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

                    const plenumW = halfLenX * 1.88;
                    if (adm === 'Atmosférico') {{
                        this.addPart(this.staticOpaque, 'cyl', this.matTRS(0, portY + 0.02, intZ + 0.10, 0, 0, Math.PI * 0.5, 0.19, plenumW, 0.19), C_INTAKE, [0.55, 48]);
                        for (let r = -2; r <= 2; r++) {{
                            this.addPart(this.staticOpaque, 'cyl', this.matTRS(r * (plenumW * 0.18), portY + 0.02, intZ + 0.10, 0, 0, Math.PI * 0.5, 0.205, 0.032, 0.205), C_RUNNER, [0.65, 52]);
                        }}
                        this.addThrottleBody(-halfLenX * 0.98, portY + 0.02, intZ + 0.10);
                        this.addPipe(this.staticOpaque, [[-halfLenX * 0.94, portY + 0.02, intZ + 0.10], [-halfLenX - 0.34, portY + 0.02, intZ + 0.10]], 0.11, C_PIPE, [0.62, 52], [0]);
                        this.addConeFilter(-halfLenX - 0.56, portY + 0.02, intZ + 0.10, -1);
                    }} else if (adm === 'Turbo') {{
                        this.addPart(this.staticOpaque, 'cyl', this.matTRS(0, portY + 0.02, intZ + 0.10, 0, 0, Math.PI * 0.5, 0.19, plenumW, 0.19), C_INTAKE, [0.55, 48]);
                        const t = this.addTurboUnit(-0.1, portY - 0.45, exhZ - 0.44, 1.05, -1);
                        const icX = -halfLenX - 1.15;
                        this.addIntercooler(icX, 0.05, 0, 0.24, 0.72, 1.25);
                        this.addPipe(this.staticOpaque, [t.compOut, [t.compOut[0] - 0.25, 0.25, exhZ - 0.45], [icX, 0.15, -0.58]], 0.075, C_PIPE, [0.62, 52], [0, 1]);
                        this.addPipe(this.staticOpaque, [[icX, 0.15, 0.58], [icX + 0.3, portY + 0.02, intZ + 0.10], [-halfLenX * 0.94, portY + 0.02, intZ + 0.10]], 0.08, C_PIPE, [0.62, 52], [0, 1]);
                    }} else if (adm === 'Supercompressor') {{
                        this.addSuperchargerUnit(0, deckDist + 0.68, 0.05, halfLenX * 1.55, 0.58, -halfLenX - 0.24);
                        this.addPipe(this.staticOpaque, [[halfLenX * 0.78, deckDist + 0.68, 0.05], [halfLenX + 0.28, deckDist + 0.68, 0.05]], 0.11, C_PIPE, [0.62, 52], [0]);
                        this.addConeFilter(halfLenX + 0.50, deckDist + 0.68, 0.05, 1);
                    }} else if (adm === 'Biturbo') {{
                        this.addPart(this.staticOpaque, 'cyl', this.matTRS(0, portY + 0.02, intZ + 0.10, 0, 0, Math.PI * 0.5, 0.19, plenumW, 0.19), C_INTAKE, [0.55, 48]);
                        const t1 = this.addTurboUnit(-halfLenX * 0.45, portY - 0.45, exhZ - 0.44, 0.92, -1);
                        const t2 = this.addTurboUnit(halfLenX * 0.45, portY - 0.45, exhZ - 0.44, 0.92, -1);
                        const icX = -halfLenX - 1.15;
                        this.addIntercooler(icX, 0.05, 0, 0.24, 0.74, 1.35);
                        this.addPipe(this.staticOpaque, [t1.compOut, [icX + 0.35, 0.18, exhZ - 0.35], [icX, 0.15, -0.62]], 0.068, C_PIPE, [0.62, 52], [0, 1]);
                        this.addPipe(this.staticOpaque, [t2.compOut, [t1.compOut[0], 0.35, exhZ - 0.55], [icX, 0.25, -0.62]], 0.064, C_PIPE, [0.62, 52], [0, 1]);
                        this.addPipe(this.staticOpaque, [[icX, 0.15, 0.62], [icX + 0.3, portY + 0.02, intZ + 0.10], [-halfLenX * 0.94, portY + 0.02, intZ + 0.10]], 0.082, C_PIPE, [0.62, 52], [0, 1]);
                    }} else if (adm === 'Quad Turbo') {{
                        this.addPart(this.staticOpaque, 'cyl', this.matTRS(0, portY + 0.02, intZ + 0.10, 0, 0, Math.PI * 0.5, 0.19, plenumW, 0.19), C_INTAKE, [0.55, 48]);
                        const icX = -halfLenX - 1.18;
                        this.addIntercooler(icX, 0.05, 0, 0.26, 0.78, 1.48);
                        const qXs = [-0.72 * halfLenX, -0.24 * halfLenX, 0.24 * halfLenX, 0.72 * halfLenX];
                        for (let qi = 0; qi < qXs.length; qi++) {{
                            const qt = this.addTurboUnit(qXs[qi], portY - 0.45, exhZ - 0.42, 0.72, -1);
                            this.addPipe(this.staticOpaque, [qt.compOut, [icX + 0.36, 0.15 + qi * 0.05, exhZ - 0.46], [icX, 0.15 + qi * 0.04, -0.64]], 0.048, C_PIPE, [0.62, 52], [0, 1]);
                        }}
                        this.addPipe(this.staticOpaque, [[icX, 0.15, 0.64], [icX + 0.3, portY + 0.02, intZ + 0.10], [-halfLenX * 0.94, portY + 0.02, intZ + 0.10]], 0.088, C_PIPE, [0.62, 52], [0, 1]);
                    }} else {{
                        this.addSuperchargerUnit(0, deckDist + 0.68, 0.05, halfLenX * 1.55, 0.58, -halfLenX - 0.24);
                        const t = this.addTurboUnit(0.15, portY - 0.45, exhZ - 0.44, 1.0, -1);
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
                    this.addPart(this.staticTrans, 'box', this.matTRS(0, -0.02, 0, 0, 0, 0, blockW * 1.01, bankH * 1.06, bCaseZ), C_BLOCK, BLK_SPEC);
                    this.addPart(this.staticOpaque, 'box', this.matTRS(0, bankH * 0.50, 0, 0, 0, 0, blockW * 0.96, 0.08, bCaseZ * 0.94), C_HEAD, [0.46, 36]);
                    this.addPart(this.staticOpaque, 'box', this.matTRS(0, -bankH * 0.54, 0, 0, 0, 0, blockW * 0.98, 0.11, bCaseZ * 1.08), C_SUMP, [0.4, 24]);
                    this.addPart(this.staticOpaque, 'box', this.matTRS(0, -bankH * 0.70, 0, 0, 0, 0, blockW * 0.88, 0.24, bCaseZ * 0.92), C_SUMP, [0.35, 20]);
                    for (let f = -2; f <= 2; f++) {{
                        this.addPart(this.staticOpaque, 'box', this.matTRS(0, -bankH * 0.83, f * 0.11, 0, 0, 0, blockW * 0.80, 0.03, 0.03), C_BLOCK, [0.5, 32]);
                    }}
                    this.addPart(this.staticOpaque, 'cyl', this.matTRS(-halfLenX * 0.62, bankH * 0.56, bCaseZ * 0.42, 0.2, 0, 0, 0.11, 0.24, 0.11), C_FILTER, [0.55, 44]);

                    // Bancadas horizontais opostas (-Z e +Z)
                    const vvtColorB = vType === 'VVT' ? [0.76, 0.60, 0.24, 1.0] : [0.26, 0.44, 0.64, 1.0];
                    for (const side of [-1, 1]) {{
                        const ang = side * Math.PI * 0.5;
                        const blockMidZ = side * deckDist * 0.48;
                        this.addPart(this.staticTrans, 'box', this.matTRS(0, 0, blockMidZ, ang, 0, 0, blockW, deckDist * 0.88, bankH), C_BLOCK, BLK_SPEC);
                        this.addPart(this.staticOpaque, 'box', this.matTRS(0, 0, side * (deckDist - 0.011), ang, 0, 0, blockW * 1.018, 0.022, bankH * 1.04), C_GASKET, [0.72, 54]);
                        this.addPart(this.staticTrans, 'box', this.matTRS(0, 0, side * (deckDist + 0.14), ang, 0, 0, blockW * 1.01, 0.26, bankH * 1.04), C_HEAD, [0.45, 36]);
                        for (const boltSide of [-1, 1]) {{
                            for (const c of cylSpecs) {{
                                this.addPart(this.staticOpaque, 'hex', this.matTRS(c.x, boltSide * bankH * 0.36, side * (deckDist + 0.39), ang, 0, 0, 0.028, 0.022, 0.028), C_BOLT, [0.78, 60]);
                            }}
                        }}
                        this.addPart(this.staticOpaque, 'box', this.matTRS(0, 0, side * (deckDist + 0.35), ang, 0, 0, blockW * 1.02, 0.14, bankH * 1.02), C_VALVE, [0.55, 48]);
                        this.addPart(this.staticOpaque, 'box', this.matTRS(0, 0, side * (deckDist + 0.425), ang, 0, 0, blockW * 0.90, 0.03, bankH * 0.26), C_BOLT, [0.7, 54]);

                        const camZ = side * (deckDist + 0.20);
                        if (isFreevalve) {{
                            // Atuadores eletro-pneumáticos adicionados via addFreevalveBank
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
                    if (!isFreevalve && camMode === 'OHV') {{
                        this.addPart(this.staticOpaque, 'cyl', this.matTRS(0, 0.24, 0, 0, 0, Math.PI * 0.5, 0.052, blockW * 1.02, 0.052), C_CRANK, [0.65, 52]);
                        this.dynamicRotors.push({{ type: 'pulley', cx: -halfLenX - 0.24, cy: 0.24, cz: 0, r: 0.18, thick: 0.07, speedMult: this.config.ciclo === '2T' ? 1.0 : 0.5, colorRim: [0.36, 0.41, 0.48, 1.0], colorHub: [0.72, 0.48, 0.26, 1.0] }});
                    }}

                    // Motor de arranque traseiro + capas de mancal + cames/varetas + bobinas/injetores Boxer
                    this.addStarterMotor(halfLenX * 0.62, bankH * 0.48 + 0.14, 0.24);
                    for (const c of cylSpecs) {{
                        if (!isFreevalve) {{
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
                    if (isFreevalve) {{
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
                    this.addPipe(this.staticOpaque, [
                        [halfLenX * 0.90, exhY, -exhZOut],
                        [halfLenX + 0.35, exhY - 0.05, 0],
                        [halfLenX * 0.90, exhY, exhZOut]
                    ], 0.095, C_EXHAUST, [0.4, 28]);

                    // Admissão superior aranha (spider) + rampas de injeção
                    const intTopY = bankH * 0.52 + 0.46;
                    const plenumW = halfLenX * 1.82;
                    for (const c of cylSpecs) {{
                        const portZ = c.bank * (deckDist + 0.06);
                        this.addPipe(this.staticOpaque, [
                            [c.x, bankH * 0.45, portZ],
                            [c.x, intTopY - 0.08, c.bank * (deckDist * 0.48)],
                            [c.x, intTopY, 0]
                        ], 0.064 * boreScale, C_RUNNER);
                    }}
                    this.addPart(this.staticOpaque, 'cyl', this.matTRS(0, bankH * 0.52 + 0.08, -deckDist * 0.78, 0, 0, Math.PI * 0.5, 0.036, plenumW * 0.94, 0.036), C_RAIL, [0.65, 52]);
                    this.addPart(this.staticOpaque, 'cyl', this.matTRS(0, bankH * 0.52 + 0.08,  deckDist * 0.78, 0, 0, Math.PI * 0.5, 0.036, plenumW * 0.94, 0.036), C_RAIL, [0.65, 52]);

                    if (adm === 'Atmosférico') {{
                        this.addPart(this.staticOpaque, 'box', this.matTRS(0, intTopY + 0.12, 0, 0, 0, 0, plenumW, 0.26, 0.52), C_INTAKE, [0.55, 48]);
                        this.addThrottleBody(halfLenX * 0.96, intTopY + 0.12, 0);
                        this.addPipe(this.staticOpaque, [[halfLenX * 0.90, intTopY + 0.12, 0], [halfLenX + 0.34, intTopY + 0.12, 0]], 0.11, C_PIPE, [0.62, 52], [0]);
                        this.addConeFilter(halfLenX + 0.56, intTopY + 0.12, 0, 1);
                    }} else if (adm === 'Turbo') {{
                        this.addPart(this.staticOpaque, 'box', this.matTRS(0, intTopY + 0.12, 0, 0, 0, 0, plenumW, 0.26, 0.52), C_INTAKE, [0.55, 48]);
                        const t = this.addTurboUnit(0, exhY - 0.04, -exhZOut - 0.36, 1.02, -1);
                        const icX = -halfLenX - 1.18;
                        this.addIntercooler(icX, 0.08, 0, 0.24, 0.72, 1.38);
                        this.addPipe(this.staticOpaque, [t.compOut, [icX + 0.35, 0.12, -exhZOut - 0.28], [icX, 0.12, -0.62]], 0.076, C_PIPE, [0.62, 52], [0, 1]);
                        this.addPipe(this.staticOpaque, [[icX, 0.12, 0.62], [icX + 0.30, intTopY + 0.12, 0.36], [-halfLenX * 0.90, intTopY + 0.12, 0]], 0.082, C_PIPE, [0.62, 52], [0, 1]);
                    }} else if (adm === 'Supercompressor') {{
                        this.addSuperchargerUnit(0, intTopY + 0.28, 0, halfLenX * 1.55, 0.62, -halfLenX - 0.24);
                        this.addPipe(this.staticOpaque, [[halfLenX * 0.78, intTopY + 0.28, 0], [halfLenX + 0.30, intTopY + 0.28, 0]], 0.11, C_PIPE, [0.62, 52], [0]);
                        this.addConeFilter(halfLenX + 0.52, intTopY + 0.28, 0, 1);
                    }} else if (adm === 'Biturbo') {{
                        this.addPart(this.staticOpaque, 'box', this.matTRS(0, intTopY + 0.12, 0, 0, 0, 0, plenumW, 0.26, 0.52), C_INTAKE, [0.55, 48]);
                        const tL = this.addTurboUnit(0, exhY - 0.04, -exhZOut - 0.34, 0.94, -1);
                        const tR = this.addTurboUnit(0, exhY - 0.04,  exhZOut + 0.34, 0.94,  1);
                        const icX = -halfLenX - 1.18;
                        this.addIntercooler(icX, 0.08, 0, 0.24, 0.74, 1.48);
                        this.addPipe(this.staticOpaque, [tL.compOut, [icX + 0.32, 0.12, -exhZOut - 0.20], [icX, 0.12, -0.68]], 0.070, C_PIPE, [0.62, 52], [0, 1]);
                        this.addPipe(this.staticOpaque, [tR.compOut, [icX + 0.32, 0.12,  exhZOut + 0.20], [icX, 0.12,  0.68]], 0.070, C_PIPE, [0.62, 52], [0, 1]);
                        this.addPipe(this.staticOpaque, [[icX, 0.26, 0], [-halfLenX * 0.90, intTopY + 0.12, 0]], 0.085, C_PIPE, [0.62, 52], [0]);
                    }} else if (adm === 'Quad Turbo') {{
                        this.addPart(this.staticOpaque, 'box', this.matTRS(0, intTopY + 0.12, 0, 0, 0, 0, plenumW, 0.26, 0.52), C_INTAKE, [0.55, 48]);
                        const icX = -halfLenX - 1.18;
                        this.addIntercooler(icX, 0.08, 0, 0.26, 0.78, 1.56);
                        for (const qx of [-halfLenX * 0.46, halfLenX * 0.46]) {{
                            const tL = this.addTurboUnit(qx, exhY - 0.04, -exhZOut - 0.34, 0.74, -1);
                            const tR = this.addTurboUnit(qx, exhY - 0.04,  exhZOut + 0.34, 0.74,  1);
                            this.addPipe(this.staticOpaque, [tL.compOut, [icX + 0.34, 0.12, -exhZOut - 0.24], [icX, 0.12, -0.72]], 0.052, C_PIPE, [0.62, 52], [0, 1]);
                            this.addPipe(this.staticOpaque, [tR.compOut, [icX + 0.34, 0.12,  exhZOut + 0.24], [icX, 0.12,  0.72]], 0.052, C_PIPE, [0.62, 52], [0, 1]);
                        }}
                        this.addPipe(this.staticOpaque, [[icX, 0.26, 0], [-halfLenX * 0.90, intTopY + 0.12, 0]], 0.088, C_PIPE, [0.62, 52], [0]);
                    }} else {{
                        this.addSuperchargerUnit(0, intTopY + 0.28, 0, halfLenX * 1.55, 0.62, -halfLenX - 0.24);
                        const t = this.addTurboUnit(0, exhY - 0.04, -exhZOut - 0.36, 0.96, -1);
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

                    // Cárter detalhado + saia do bloco cobrindo toda a cambota + tampa central do vale + filtro
                    const skirtBotV = -crankR - 0.10;
                    const vCaseH = 0.28 - skirtBotV;
                    const vCaseZ = Math.max(cylR * 2.85, crankR * 2.55);
                    this.addPart(this.staticOpaque, 'box', this.matTRS(0, -crankR - 0.14, 0, 0, 0, 0, blockW * 1.03, 0.10, vCaseZ * 1.04), C_SUMP, [0.4, 24]);
                    this.addPart(this.staticOpaque, 'box', this.matTRS(0, -crankR - 0.30, 0, 0, 0, 0, blockW * 0.96, 0.28, vCaseZ * 0.92), C_SUMP, [0.35, 20]);
                    for (let f = -2; f <= 2; f++) {{
                        this.addPart(this.staticOpaque, 'box', this.matTRS(0, -crankR - 0.45, f * 0.14, 0, 0, 0, blockW * 0.88, 0.03, 0.03), C_BLOCK, [0.5, 32]);
                    }}
                    this.addPart(this.staticTrans, 'box', this.matTRS(0, skirtBotV + vCaseH * 0.5, 0, 0, 0, 0, blockW * 1.01, vCaseH, vCaseZ), C_BLOCK, BLK_SPEC);
                    this.addPart(this.staticOpaque, 'box', this.matTRS(0, deckDist * 0.52, 0, 0, 0, 0, blockW * 0.98, 0.08, Math.max(0.32, cylR * 1.1)), C_HEAD, [0.46, 36]);
                    this.addPart(this.staticOpaque, 'cyl', this.matTRS(-halfLenX * 0.45, -0.05, cylR * 1.38, 0.7, 0, 0, 0.12, 0.26, 0.12), C_FILTER, [0.55, 44]);
                    this.addStarterMotor(halfLenX * 0.62, -0.14, cylR * 1.48);

                    for (const side of [-1, 1]) {{
                        const ang = side * baseBankAng;
                        const sinA = Math.sin(ang), cosA = Math.cos(ang);
                        this.addPart(this.staticTrans, 'box', this.matTRS(0, bankMidDist * cosA, bankMidDist * sinA, ang, 0, 0, blockW, bankH, bankZWidth), C_BLOCK, BLK_SPEC);
                        const gskD = deckDist - 0.011;
                        this.addPart(this.staticOpaque, 'box', this.matTRS(0, gskD * cosA, gskD * sinA, ang, 0, 0, blockW * 1.018, 0.022, bankZWidth * 1.02), C_GASKET, [0.72, 54]);
                        const outerSideZ = ang >= 0 ? bankZWidth * 0.52 : -bankZWidth * 0.52;
                        const bankCylSpecs = cylSpecs.filter(c => c.bank === side);
                        for (const c of bankCylSpecs) {{
                            const rx = c.x;
                            const ribY = bankMidDist * cosA - outerSideZ * sinA;
                            const ribZ = bankMidDist * sinA + outerSideZ * cosA;
                            this.addPart(this.staticOpaque, 'box', this.matTRS(rx, ribY, ribZ, ang, 0, 0, 0.040, bankH * 0.72, 0.034), C_BLOCK, BLK_SPEC);
                            const boltD = deckDist + 0.39;
                            const boltY = boltD * cosA - (outerSideZ * 0.65) * sinA;
                            const boltZ = boltD * sinA + (outerSideZ * 0.65) * cosA;
                            this.addPart(this.staticOpaque, 'hex', this.matTRS(rx, boltY, boltZ, ang, 0, 0, 0.030, 0.022, 0.030), C_BOLT, [0.78, 60]);
                        }}
                        const headD = deckDist + 0.14;
                        this.addPart(this.staticTrans, 'box', this.matTRS(0, headD * cosA, headD * sinA, ang, 0, 0, blockW * 1.01, 0.26, bankZWidth * 1.03), C_HEAD, [0.45, 36]);
                        const vcD = deckDist + 0.35;
                        this.addPart(this.staticOpaque, 'box', this.matTRS(0, vcD * cosA, vcD * sinA, ang, 0, 0, blockW * 1.02, 0.14, bankZWidth * 1.02), C_VALVE, [0.55, 48]);
                        const ribD = deckDist + 0.425;
                        this.addPart(this.staticOpaque, 'box', this.matTRS(0, ribD * cosA, ribD * sinA, ang, 0, 0, blockW * 0.90, 0.03, bankZWidth * 0.28), C_BOLT, [0.7, 54]);

                        const vvtColor = vType === 'VVT' ? [0.76, 0.60, 0.24, 1.0] : [0.26, 0.44, 0.64, 1.0];
                        if (isFreevalve) {{
                            // Atuadores eletro-pneumáticos adicionados via addFreevalveBank
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
                    if (!isFreevalve && camMode === 'OHV') {{
                        const valleyCamY = 0.26;
                        this.addPart(this.staticOpaque, 'cyl', this.matTRS(0, valleyCamY, 0, 0, 0, Math.PI * 0.5, 0.055, blockW * 1.02, 0.055), C_CRANK, [0.65, 52]);
                        this.dynamicRotors.push({{ type: 'pulley', cx: -halfLenX - 0.24, cy: valleyCamY, cz: 0, r: 0.20, thick: 0.075, speedMult: this.config.ciclo === '2T' ? 1.0 : 0.5, colorRim: [0.36, 0.41, 0.48, 1.0], colorHub: [0.72, 0.48, 0.26, 1.0] }});
                    }}
                    // Bobinas/injetores + cames + varetas OHV + capas de mancal em cada cilindro
                    for (const c of cylSpecs) {{
                        if (!isFreevalve) {{
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
                    if (isFreevalve) {{
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

                    const valleyY = deckDist * 0.85 + 0.16;
                    const plenumW = halfLenX * 1.82;
                    for (const c of cylSpecs) {{
                        const portY = (deckDist + 0.08) * Math.cos(c.angle);
                        const portZ = (deckDist + 0.08) * Math.sin(c.angle) - c.bank * (bankZWidth * 0.35);
                        this.addPipe(this.staticOpaque, [[c.x, valleyY, 0], [c.x, portY, portZ]], 0.064 * boreScale, C_RUNNER);
                    }}
                    // Rampas de injeção no vale central
                    this.addPart(this.staticOpaque, 'cyl', this.matTRS(0, valleyY + 0.06, -0.32, 0, 0, Math.PI * 0.5, 0.036, plenumW * 0.94, 0.036), C_RAIL, [0.65, 52]);
                    this.addPart(this.staticOpaque, 'cyl', this.matTRS(0, valleyY + 0.06,  0.32, 0, 0, Math.PI * 0.5, 0.036, plenumW * 0.94, 0.036), C_RAIL, [0.65, 52]);

                    if (adm === 'Atmosférico') {{
                        this.addPart(this.staticOpaque, 'box', this.matTRS(0, valleyY + 0.14, 0, 0, 0, 0, plenumW, 0.28, 0.52), C_INTAKE, [0.55, 48]);
                        this.addThrottleBody(halfLenX * 0.96, valleyY + 0.14, 0);
                        this.addPipe(this.staticOpaque, [[halfLenX * 0.90, valleyY + 0.14, 0], [halfLenX + 0.34, valleyY + 0.14, 0]], 0.11, C_PIPE, [0.62, 52], [0]);
                        this.addConeFilter(halfLenX + 0.56, valleyY + 0.14, 0, 1);
                    }} else if (adm === 'Turbo') {{
                        this.addPart(this.staticOpaque, 'box', this.matTRS(0, valleyY + 0.14, 0, 0, 0, 0, plenumW, 0.28, 0.52), C_INTAKE, [0.55, 48]);
                        const t = this.addTurboUnit(0, exhY - 0.20, -exhZOut - 0.42, 1.05, -1);
                        const icX = -halfLenX - 1.18;
                        this.addIntercooler(icX, 0.06, 0, 0.24, 0.74, 1.45);
                        this.addPipe(this.staticOpaque, [t.compOut, [icX + 0.35, 0.20, -exhZOut - 0.35], [icX, 0.15, -0.68]], 0.078, C_PIPE, [0.62, 52], [0, 1]);
                        this.addPipe(this.staticOpaque, [[icX, 0.15, 0.68], [icX + 0.32, valleyY + 0.14, 0.40], [-halfLenX * 0.90, valleyY + 0.14, 0]], 0.082, C_PIPE, [0.62, 52], [0, 1]);
                    }} else if (adm === 'Supercompressor') {{
                        this.addSuperchargerUnit(0, valleyY + 0.30, 0, halfLenX * 1.55, 0.62, -halfLenX - 0.24);
                        this.addPipe(this.staticOpaque, [[halfLenX * 0.78, valleyY + 0.30, 0], [halfLenX + 0.30, valleyY + 0.30, 0]], 0.11, C_PIPE, [0.62, 52], [0]);
                        this.addConeFilter(halfLenX + 0.52, valleyY + 0.30, 0, 1);
                    }} else if (adm === 'Biturbo') {{
                        this.addPart(this.staticOpaque, 'box', this.matTRS(0, valleyY + 0.14, 0, 0, 0, 0, plenumW, 0.28, 0.52), C_INTAKE, [0.55, 48]);
                        const tL = this.addTurboUnit(-0.1, exhY - 0.20, -exhZOut - 0.40, 0.96, -1);
                        const tR = this.addTurboUnit(-0.1, exhY - 0.20,  exhZOut + 0.40, 0.96,  1);
                        const icX = -halfLenX - 1.18;
                        this.addIntercooler(icX, 0.06, 0, 0.24, 0.76, 1.55);
                        this.addPipe(this.staticOpaque, [tL.compOut, [icX + 0.30, 0.18, -exhZOut - 0.2], [icX, 0.15, -0.72]], 0.07, C_PIPE, [0.62, 52], [0, 1]);
                        this.addPipe(this.staticOpaque, [tR.compOut, [icX + 0.30, 0.18,  exhZOut + 0.2], [icX, 0.15,  0.72]], 0.07, C_PIPE, [0.62, 52], [0, 1]);
                        this.addPipe(this.staticOpaque, [[icX, 0.30, 0], [-halfLenX * 0.90, valleyY + 0.14, 0]], 0.085, C_PIPE, [0.62, 52], [0]);
                    }} else if (adm === 'Quad Turbo') {{
                        this.addPart(this.staticOpaque, 'box', this.matTRS(0, valleyY + 0.14, 0, 0, 0, 0, plenumW, 0.28, 0.52), C_INTAKE, [0.55, 48]);
                        const icX = -halfLenX - 1.18;
                        this.addIntercooler(icX, 0.06, 0, 0.26, 0.80, 1.62);
                        for (const qx of [-halfLenX * 0.46, halfLenX * 0.46]) {{
                            const tL = this.addTurboUnit(qx, exhY - 0.20, -exhZOut - 0.40, 0.76, -1);
                            const tR = this.addTurboUnit(qx, exhY - 0.20,  exhZOut + 0.40, 0.76,  1);
                            this.addPipe(this.staticOpaque, [tL.compOut, [icX + 0.32, 0.18, -exhZOut - 0.22], [icX, 0.15, -0.74]], 0.052, C_PIPE, [0.62, 52], [0, 1]);
                            this.addPipe(this.staticOpaque, [tR.compOut, [icX + 0.32, 0.18,  exhZOut + 0.22], [icX, 0.15,  0.74]], 0.052, C_PIPE, [0.62, 52], [0, 1]);
                        }}
                        this.addPipe(this.staticOpaque, [[icX, 0.30, 0], [-halfLenX * 0.90, valleyY + 0.14, 0]], 0.088, C_PIPE, [0.62, 52], [0]);
                    }} else {{
                        this.addSuperchargerUnit(0, valleyY + 0.30, 0, halfLenX * 1.55, 0.62, -halfLenX - 0.24);
                        const t = this.addTurboUnit(0, exhY - 0.20, -exhZOut - 0.40, 0.98, -1);
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

                    // Placas laterais e intermédias (Irons) + carcaças epitrocoidais + rotores
                    for (let i = 0; i <= nRotors; i++) {{
                        const px = startRx - pitchX * 0.5 + i * pitchX;
                        const isEnd = (i === 0 || i === nRotors);
                        const targetPlate = isEnd ? this.staticOpaque : this.staticTrans;
                        this.addPart(targetPlate, 'box', this.matTRS(px, 0, 0, 0, 0, 0, ironW, 2.38 * rotorR, 2.02 * rotorR), isEnd ? C_HEAD : C_BLOCK, BLK_SPEC);
                        this.addPart(targetPlate, 'cyl', this.matTRS(px, 1.04 * rotorR, 0, 0, 0, Math.PI * 0.5, 0.92 * rotorR, ironW * 0.98, 0.92 * rotorR), isEnd ? C_HEAD : C_BLOCK, BLK_SPEC);
                        this.addPart(targetPlate, 'cyl', this.matTRS(px, -1.04 * rotorR, 0, 0, 0, Math.PI * 0.5, 0.92 * rotorR, ironW * 0.98, 0.92 * rotorR), isEnd ? C_HEAD : C_BLOCK, BLK_SPEC);
                    }}

                    for (let rIdx = 0; rIdx < nRotors; rIdx++) {{
                        const rx = startRx + rIdx * pitchX;
                        this.addPart(this.staticTrans, 'wankelHousing', this.matTRS(rx, 0, 0, 0, 0, 0, housingW, rotorR, rotorR), C_BLOCK, BLK_SPEC);
                        // Velas Leading & Trailing no lado +Z (câmara de combustão) + bobinas vermelhas
                        for (const spY of [-0.20 * rotorR, 0.20 * rotorR]) {{
                            this.addPart(this.staticOpaque, 'cyl', this.matTRS(rx, spY, 1.02 * rotorR, Math.PI * 0.5, 0, 0, 0.042, 0.16, 0.042), C_BOLT, [0.76, 60]);
                            this.addPart(this.staticOpaque, 'cyl', this.matTRS(rx, spY, 1.13 * rotorR, Math.PI * 0.5, 0, 0, 0.052, 0.10, 0.052), [0.72, 0.22, 0.22, 1.0], [0.55, 42]);
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
                    this.addPart(this.staticTrans, 'box', this.matTRS(0, sumpY + 0.12, 0, 0, 0, 0, stackW * 0.98, 0.26, 1.72 * rotorR), C_BLOCK, BLK_SPEC);
                    this.addPart(this.staticOpaque, 'box', this.matTRS(0, sumpY - 0.06, 0, 0, 0, 0, stackW * 1.02, 0.12, 1.85 * rotorR), C_SUMP, [0.4, 24]);
                    this.addPart(this.staticOpaque, 'box', this.matTRS(0, sumpY - 0.22, 0, 0, 0, 0, stackW * 0.94, 0.24, 1.65 * rotorR), C_SUMP, [0.35, 20]);
                    for (let f = -2; f <= 2; f++) {{
                        this.addPart(this.staticOpaque, 'box', this.matTRS(0, sumpY - 0.35, f * 0.18 * rotorR, 0, 0, 0, stackW * 0.86, 0.03, 0.03), C_BLOCK, [0.5, 32]);
                    }}
                    this.addPart(this.staticOpaque, 'box', this.matTRS(0, 1.32 * rotorR, 0, 0, 0, 0, stackW * 0.96, 0.12, 1.24 * rotorR), C_VALVE, [0.55, 48]);
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
                    for (let rIdx = 0; rIdx < nRotors; rIdx++) {{
                        const rx = startRx + rIdx * pitchX;
                        this.addPipe(this.staticOpaque, [[rx, -0.35 * rotorR, -0.98 * rotorR], [rx, exhY, exhZ]], 0.088 * wScale, C_EXHAUST, [0.4, 28]);
                        this.addPipe(this.staticOpaque, [[rx, 0.48 * rotorR, -0.96 * rotorR], [rx, 1.15 * rotorR, -0.82 * rotorR], [rx, intY, intZ]], 0.082 * wScale, C_RUNNER);
                        this.addPart(this.staticOpaque, 'cyl', this.matTRS(rx, 0.95 * rotorR, -0.58 * rotorR, -0.45, 0, 0, 0.030, 0.14, 0.030), C_BOLT, [0.6, 48]);
                    }}
                    this.addPart(this.staticOpaque, 'cyl', this.matTRS(0, exhY, exhZ, 0, 0, Math.PI * 0.5, 0.12, plenW, 0.12), C_EXHAUST, [0.4, 28]);
                    this.addPart(this.staticOpaque, 'cyl', this.matTRS(0, 1.04 * rotorR, -0.54 * rotorR, 0, 0, Math.PI * 0.5, 0.040, plenW, 0.040), C_RAIL, [0.65, 52]);
                    this.addPipe(this.staticOpaque, [[halfLenX * 0.88, exhY, exhZ], [halfLenX + 0.42, exhY - 0.12, exhZ]], 0.105, C_EXHAUST, [0.4, 28]);

                    if (adm === 'Atmosférico') {{
                        this.addPart(this.staticOpaque, 'cyl', this.matTRS(0, intY, intZ, 0, 0, Math.PI * 0.5, 0.19, plenW, 0.19), C_INTAKE, [0.55, 48]);
                        this.addThrottleBody(-halfLenX * 0.92, intY, intZ);
                        this.addPipe(this.staticOpaque, [[-halfLenX * 0.92, intY, intZ], [-halfLenX - 0.34, intY, intZ]], 0.11, C_PIPE, [0.62, 52], [0]);
                        this.addConeFilter(-halfLenX - 0.56, intY, intZ, -1);
                    }} else if (adm === 'Turbo') {{
                        this.addPart(this.staticOpaque, 'cyl', this.matTRS(0, intY, intZ, 0, 0, Math.PI * 0.5, 0.19, plenW, 0.19), C_INTAKE, [0.55, 48]);
                        const t = this.addTurboUnit(0, exhY, exhZ - 0.42, 1.08, -1);
                        const icX = -halfLenX - 1.18;
                        this.addIntercooler(icX, 0.06, 0, 0.24, 0.74, 1.38);
                        this.addPipe(this.staticOpaque, [t.compOut, [icX + 0.34, 0.16, exhZ - 0.35], [icX, 0.15, -0.62]], 0.078, C_PIPE, [0.62, 52], [0, 1]);
                        this.addPipe(this.staticOpaque, [[icX, 0.15, 0.62], [icX + 0.32, intY, intZ], [-halfLenX * 0.90, intY, intZ]], 0.082, C_PIPE, [0.62, 52], [0, 1]);
                    }} else if (adm === 'Supercompressor') {{
                        this.addSuperchargerUnit(0, intY + 0.24, intZ, Math.max(0.95, plenW * 0.85), 0.58, -halfLenX - 0.24);
                        this.addPipe(this.staticOpaque, [[plenW * 0.46, intY + 0.24, intZ], [halfLenX + 0.30, intY + 0.24, intZ]], 0.11, C_PIPE, [0.62, 52], [0]);
                        this.addConeFilter(halfLenX + 0.52, intY + 0.24, intZ, 1);
                    }} else if (adm === 'Biturbo') {{
                        this.addPart(this.staticOpaque, 'cyl', this.matTRS(0, intY, intZ, 0, 0, Math.PI * 0.5, 0.19, plenW, 0.19), C_INTAKE, [0.55, 48]);
                        const t1 = this.addTurboUnit(-halfLenX * 0.40, exhY, exhZ - 0.42, 0.92, -1);
                        const t2 = this.addTurboUnit( halfLenX * 0.40, exhY, exhZ - 0.42, 0.92, -1);
                        const icX = -halfLenX - 1.18;
                        this.addIntercooler(icX, 0.06, 0, 0.24, 0.74, 1.42);
                        this.addPipe(this.staticOpaque, [t1.compOut, [icX + 0.34, 0.18, exhZ - 0.32], [icX, 0.15, -0.64]], 0.068, C_PIPE, [0.62, 52], [0, 1]);
                        this.addPipe(this.staticOpaque, [t2.compOut, [t1.compOut[0], 0.30, exhZ - 0.52], [icX, 0.24, -0.64]], 0.064, C_PIPE, [0.62, 52], [0, 1]);
                        this.addPipe(this.staticOpaque, [[icX, 0.15, 0.64], [icX + 0.32, intY, intZ], [-halfLenX * 0.90, intY, intZ]], 0.084, C_PIPE, [0.62, 52], [0, 1]);
                    }} else if (adm === 'Quad Turbo') {{
                        this.addPart(this.staticOpaque, 'cyl', this.matTRS(0, intY, intZ, 0, 0, Math.PI * 0.5, 0.19, plenW, 0.19), C_INTAKE, [0.55, 48]);
                        const icX = -halfLenX - 1.18;
                        this.addIntercooler(icX, 0.06, 0, 0.26, 0.78, 1.50);
                        for (let qi = 0; qi < 4; qi++) {{
                            const qx = -0.66 * halfLenX + qi * (0.44 * halfLenX);
                            const qt = this.addTurboUnit(qx, exhY, exhZ - 0.42, 0.70, -1);
                            this.addPipe(this.staticOpaque, [qt.compOut, [icX + 0.36, 0.14 + qi * 0.05, exhZ - 0.46], [icX, 0.14 + qi * 0.04, -0.66]], 0.048, C_PIPE, [0.62, 52], [0, 1]);
                        }}
                        this.addPipe(this.staticOpaque, [[icX, 0.15, 0.66], [icX + 0.32, intY, intZ], [-halfLenX * 0.90, intY, intZ]], 0.088, C_PIPE, [0.62, 52], [0, 1]);
                    }} else {{
                        this.addSuperchargerUnit(0, intY + 0.24, intZ, Math.max(0.95, plenW * 0.85), 0.58, -halfLenX - 0.24);
                        const t = this.addTurboUnit(0.10, exhY, exhZ - 0.42, 1.0, -1);
                        const icX = -halfLenX - 1.18;
                        this.addIntercooler(icX, 0.06, 0, 0.24, 0.74, 1.38);
                        this.addPipe(this.staticOpaque, [t.compOut, [icX + 0.36, 0.18, exhZ - 0.38], [icX, 0.15, -0.62]], 0.072, C_PIPE, [0.62, 52], [0, 1]);
                        this.addPipe(this.staticOpaque, [[icX, 0.15, 0.62], [icX + 0.28, intY + 0.24, 0.72], [halfLenX * 0.86, intY + 0.24, 0.72], [halfLenX * 0.86, intY + 0.24, intZ], [plenW * 0.45, intY + 0.24, intZ]], 0.076, C_PIPE, [0.62, 52], [0, 2]);
                    }}
                }}

                // Chapa frontal da distribuição + flange traseira da caixa + tubagem de respiro + cambota principal
                if (fmt !== 'WANKEL') {{
                    this.addPart(this.staticTrans, 'box', this.matTRS(-halfLenX - 0.11, (deckDist - crankR) * 0.36, 0, 0, 0, 0, 0.06, deckDist + crankR + 0.46, Math.max(cylR * 2.5, crankR * 2.5)), C_HEAD, [0.48, 36]);
                }}
                this.addPart(this.staticOpaque, 'cyl', this.matTRS(halfLenX + 0.08, 0, 0, 0, 0, Math.PI * 0.5, 0.42, 0.06, 0.42), C_SUMP, [0.42, 30]);
                this.addPart(this.staticOpaque, 'cyl', this.matTRS(0, 0, 0, 0, 0, Math.PI * 0.5, 0.11, halfLenX * 2.24, 0.11), C_CRANK, [0.65, 56]);
                this.dynamicRotors.push({{
                    type: 'pulley',
                    cx: -halfLenX - 0.24, cy: 0, cz: 0,
                    r: 0.28, thick: 0.105, speedMult: 1.0,
                    colorRim: [0.30, 0.35, 0.42, 1.0],
                    colorHub: [0.26, 0.44, 0.64, 1.0]
                }});
                this.dynamicRotors.push({{
                    type: 'flywheel',
                    cx: halfLenX + 0.22, cy: 0, cz: 0,
                    r: 0.50, thick: 0.11, speedMult: 1.0,
                    colorRim: [0.40, 0.44, 0.50, 1.0],
                    colorHub: [0.68, 0.72, 0.78, 1.0]
                }});

                for (let ci = 0; ci < cylSpecs.length; ci++) {{
                    const c = cylSpecs[ci];
                    const sinA = Math.sin(c.angle), cosA = Math.cos(c.angle);
                    const latY = -sinA, latZ = cosA;
                    const sleeveCenterDist = crankR + rodLen * 0.82;
                    this.addPart(
                        this.staticTrans,
                        'cyl',
                        this.matTRS(c.x, sleeveCenterDist * cosA, c.zOff + sleeveCenterDist * sinA, c.angle, 0, 0, cylR * 1.06, cylLen, cylR * 1.06),
                        C_LINER,
                        [0.5, 42]
                    );
                    this.dynamicCyls.push({{
                        x: c.x, zOff: c.zOff, angle: c.angle, phase: c.phase,
                        fireShift: (ci % 2 === 1) ? Math.PI * 2 : 0,
                        cylR, crankR, rodLen, pistonH,
                        cPiston: C_PISTON, cRing: C_RING, cRod: C_ROD, cCrank: C_CRANK
                    }});
                    const xValOffs = valvesCount === 4 ? [-cylR * 0.30, cylR * 0.30] : [0];
                    const vHeadScale = valvesCount === 4 ? 0.19 : 0.27;
                    for (const xOff of xValOffs) {{
                        for (const sideSign of [-1, 1]) {{
                            const latOff = sideSign * (cylR * 0.34);
                            if (!isFreevalve) {{
                                const springD = deckDist + 0.16;
                                const spCol = vType === 'Pneumático'
                                    ? [0.62, 0.78, 0.86, 1.0]
                                    : (vType === 'Desmodrómico' ? [0.72, 0.56, 0.32, 1.0] : C_RING);
                                const spRad = vType === 'Pneumático' ? 0.048 : 0.040;
                                this.addPart(
                                    this.staticOpaque,
                                    'cyl',
                                    this.matTRS(c.x + xOff, springD * cosA + latOff * latY, c.zOff + springD * sinA + latOff * latZ, c.angle + sideSign * 0.10, 0, 0, spRad, 0.095, spRad),
                                    spCol,
                                    [0.55, 36]
                                );
                                const retD = springD + 0.048;
                                this.addPart(
                                    this.staticOpaque,
                                    'cyl',
                                    this.matTRS(c.x + xOff, retD * cosA + latOff * latY, c.zOff + retD * sinA + latOff * latZ, c.angle + sideSign * 0.10, 0, 0, spRad * 1.18, 0.016, spRad * 1.18),
                                    C_BOLT,
                                    [0.76, 58]
                                );
                                if (camMode !== 'DOHC') {{
                                    const rkD = springD + 0.072;
                                    this.addPart(
                                        this.staticOpaque,
                                        'box',
                                        this.matTRS(c.x + xOff, rkD * cosA + (latOff * 0.55) * latY, c.zOff + rkD * sinA + (latOff * 0.55) * latZ, c.angle, 0, 0, 0.032, 0.022, cylR * 0.42),
                                        C_CRANK,
                                        [0.65, 52]
                                    );
                                }}
                            }}
                            this.dynamicValves.push({{
                                x: c.x + xOff, zOff: c.zOff, angle: c.angle,
                                phase: c.phase * 0.5 + (sideSign > 0 ? 0 : 2.1),
                                deckDist, cylR, sideSign, vHeadScale
                            }});
                        }}
                    }}
                }}

                if (isFreevalve && cylSpecs.length) {{
                    const fvOffs = valvesCount === 4 ? [-cylR * 0.30, cylR * 0.30] : [0];
                    this.addFreevalveBank(cylSpecs, fvOffs, deckDist, cylR, halfLenX);
                }}

                this.baseDist = Math.max(5.5, Math.hypot(halfLenX + 0.9, maxSpanZ) * 2.25 + 1.6);
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

            setRightPanelVisible(visible) {{
                const isDesktop = window.innerWidth > 1020;
                const prevPanX = this.defaultCam.panX;
                const nextPanX = (visible && isDesktop) ? 0.78 : 0.0;
                const nextPanY = isDesktop ? (visible ? -0.05 : 0.04) : 0.12;
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
                this.defaultCam.panX = (rightVis && isDesktop) ? 0.78 : 0.0;
                this.defaultCam.panY = isDesktop ? (rightVis ? -0.05 : 0.04) : 0.12;
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

                // Dinâmica de rotação do motor (Ligar/Desligar + Acelerar)
                if (engineSim.blipTimer > 0) {{
                    engineSim.blipTimer = Math.max(0, engineSim.blipTimer - dt);
                }}
                const revActive = engineSim.on && (engineSim.throttleHeld || engineSim.blipTimer > 0);
                if (!engineSim.on) {{
                    engineSim.currentRpm += (0 - engineSim.currentRpm) * Math.min(1, dt * 4.2);
                    if (engineSim.currentRpm < 15) engineSim.currentRpm = 0;
                }} else if (revActive) {{
                    const target = engineSim.maxRpm;
                    const rate = Math.max(2500, (target - engineSim.idleRpm) * 1.35);
                    engineSim.currentRpm = Math.min(target, engineSim.currentRpm + rate * dt);
                    if (engineSim.currentRpm >= target * 0.985) {{
                        // Oscilação realista de corte de rotação
                        engineSim.currentRpm = target * (0.975 + 0.025 * Math.sin(now * 0.045));
                    }}
                }} else {{
                    const idleJitter = engineSim.idleRpm + Math.sin(now * 0.008) * 18;
                    engineSim.currentRpm += (idleJitter - engineSim.currentRpm) * Math.min(1, dt * 3.8);
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
                    for (const r of this.dynamicRotors) {{
                        const sym = r.symmetry || (r.type === 'impeller' ? 5 : 1);
                        const maxSafeStep = (Math.PI * 0.56) / sym;
                        const mult = r.type === 'impeller' ? r.speedMult * impMult : r.speedMult;
                        const rotorStep = Math.min(maxSafeStep, crankStep * mult);
                        r.angle = ((r.angle || 0) + rotorStep) % (Math.PI * 2);
                    }}
                }}

                if (liveRpmValue) {{
                    liveRpmValue.textContent = `${{Math.round(engineSim.currentRpm)}} RPM`;
                }}
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
                const tx = this.cam.panX * rightX;
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

                    for (const cheekOff of [-0.074, 0.074]) {{
                        const cheekM = this.matSpinX(c.x + cheekOff, -yPin * 0.40, c.zOff - zPin * 0.40, phi, 0, 0, Math.PI * 0.5, c.crankR * 0.64, 0.034, c.crankR * 0.92);
                        this.drawItem(this.meshes.cyl, cheekM, c.cCrank, [0.62, 48], viewProj);
                    }}
                    const cwM = this.matTRS(c.x, -yPin * 0.46, c.zOff - zPin * 0.46, phi, 0, 0, 0.076, c.crankR * 1.04, 0.155);
                    this.drawItem(this.meshes.box, cwM, c.cCrank, [0.55, 42], viewProj);
                    const cwBrassM = this.matTRS(c.x, -yPin * 0.88, c.zOff - zPin * 0.88, phi, 0, 0, 0.066, 0.026, 0.12);
                    this.drawItem(this.meshes.box, cwBrassM, [0.76, 0.58, 0.24, 1.0], [0.74, 58], viewProj);
                    const armM = this.matTRS(c.x, yPin * 0.5, c.zOff + zPin * 0.5, phi, 0, 0, 0.062, c.crankR, 0.105);
                    this.drawItem(this.meshes.box, armM, c.cCrank, [0.55, 42], viewProj);
                    const pinM = this.matSpinX(c.x, yPin, zPinGlobal, phi, 0, 0, Math.PI * 0.5, 0.075, 0.14, 0.075);
                    this.drawItem(this.meshes.cyl, pinM, c.cCrank, [0.65, 52], viewProj);

                    const rodAngle = Math.atan2(zPisGlobal - zPinGlobal, yPis - yPin);
                    const rodMidY = (yPin + yPis) * 0.5;
                    const rodMidZ = (zPinGlobal + zPisGlobal) * 0.5;
                    const rodDark = [c.cRod[0] * 0.78, c.cRod[1] * 0.78, c.cRod[2] * 0.78, 1.0];
                    const rodWebM = this.matTRS(c.x, rodMidY, rodMidZ, rodAngle, 0, 0, 0.028, c.rodLen * 0.96, 0.056);
                    this.drawItem(this.meshes.box, rodWebM, rodDark, [0.54, 40], viewProj);
                    const rSin = Math.sin(rodAngle), rCos = Math.cos(rodAngle);
                    for (const fOff of [-0.028, 0.028]) {{
                        const rFlangeM = this.matTRS(c.x, rodMidY - fOff * rSin, rodMidZ + fOff * rCos, rodAngle, 0, 0, 0.056, c.rodLen * 0.94, 0.018);
                        this.drawItem(this.meshes.box, rFlangeM, c.cRod, [0.68, 54], viewProj);
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

                    // Pistão + coroa chanfrada + cavilhão + anéis de segmento
                    const pisM = this.matTRS(c.x, yPis, zPisGlobal, c.angle, 0, 0, c.cylR * 0.88, c.pistonH, c.cylR * 0.88);
                    this.drawItem(this.meshes.cyl, pisM, c.cPiston, [0.78, 64], viewProj);
                    const crownOff = c.pistonH * 0.54;
                    const crownM = this.matTRS(c.x, yPis + crownOff * cosA, zPisGlobal + crownOff * sinA, c.angle, 0, 0, c.cylR * 0.72, 0.032, c.cylR * 0.72);
                    this.drawItem(this.meshes.cyl, crownM, [0.90, 0.93, 0.96, 1.0], [0.85, 72], viewProj);
                    const wristPinM = this.matTRS(c.x, yPis - (c.pistonH * 0.10) * cosA, zPisGlobal - (c.pistonH * 0.10) * sinA, 0, 0, Math.PI * 0.5, 0.048, c.cylR * 1.48, 0.048);
                    this.drawItem(this.meshes.cyl, wristPinM, c.cCrank, [0.7, 54], viewProj);
                    const ringOffset = c.pistonH * 0.28;
                    const ringM = this.matTRS(c.x, yPis + ringOffset * cosA, zPisGlobal + ringOffset * sinA, c.angle, 0, 0, c.cylR * 0.90, 0.036, c.cylR * 0.90);
                    this.drawItem(this.meshes.cyl, ringM, c.cRing, [0.4, 24], viewProj);
                    const ringM2 = this.matTRS(c.x, yPis + (ringOffset * 0.5) * cosA, zPisGlobal + (ringOffset * 0.5) * sinA, c.angle, 0, 0, c.cylR * 0.90, 0.030, c.cylR * 0.90);
                    this.drawItem(this.meshes.cyl, ringM2, c.cRing, [0.4, 24], viewProj);
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
                }}

                // Rodas/polias e volante estáticos na posição e a rodar apenas num sentido em torno do eixo X
                for (const r of this.dynamicRotors) {{
                    const ang = r.angle !== undefined ? r.angle : this.crankAngle * r.speedMult;
                    if (r.type === 'pulley') {{
                        const rimM = this.matSpinX(r.cx, r.cy, r.cz, ang, 0, 0, Math.PI * 0.5, r.r, r.thick, r.r);
                        this.drawItem(this.meshes.cyl, rimM, r.colorRim, [0.6, 48], viewProj);
                        const hubM = this.matSpinX(r.cx - r.thick * 0.35, r.cy, r.cz, ang, 0, 0, Math.PI * 0.5, r.r * 0.52, r.thick * 0.6, r.r * 0.52);
                        this.drawItem(this.meshes.cyl, hubM, r.colorHub, [0.75, 64], viewProj);
                        const timingBarM = this.matTRS(r.cx - r.thick * 0.54, r.cy + Math.cos(ang) * (r.r * 0.40), r.cz + Math.sin(ang) * (r.r * 0.40), ang, 0, 0, 0.026, r.r * 0.78, 0.044);
                        this.drawItem(this.meshes.box, timingBarM, r.colorHub, [0.7, 56], viewProj);
                        const pinMarkM = this.matTRS(r.cx - r.thick * 0.56, r.cy + Math.cos(ang) * (r.r * 0.72), r.cz + Math.sin(ang) * (r.r * 0.72), ang, 0, 0, 0.034, 0.055, 0.055);
                        this.drawItem(this.meshes.box, pinMarkM, [0.92, 0.34, 0.24, 1.0], [0.7, 56], viewProj);
                        const boltCenterM = this.matSpinX(r.cx - r.thick * 0.62, r.cy, r.cz, ang, 0, 0, Math.PI * 0.5, r.r * 0.22, r.thick * 0.45, r.r * 0.22);
                        this.drawItem(this.meshes.cyl, boltCenterM, [0.80, 0.84, 0.89, 1.0], [0.82, 68], viewProj);
                    }} else if (r.type === 'flywheel') {{
                        const ringM = this.matSpinX(r.cx, r.cy, r.cz, ang, 0, 0, Math.PI * 0.5, r.r, r.thick, r.r);
                        this.drawItem(this.meshes.cyl, ringM, r.colorRim, [0.55, 44], viewProj);
                        const gDelta = this.crankAngle - (r.lastGearCrank !== undefined ? r.lastGearCrank : this.crankAngle);
                        r.lastGearCrank = this.crankAngle;
                        const gStep = gDelta >= 0 ? gDelta : 0;
                        r.gearAngle = ((r.gearAngle || 0) + Math.min(0.11, gStep * (r.speedMult || 1))) % (Math.PI * 2);
                        const teethRingM = this.matSpinX(r.cx - r.thick * 0.25, r.cy, r.cz, r.gearAngle, 0, 0, Math.PI * 0.5, r.r * 1.03, r.thick * 0.30, r.r * 1.03);
                        this.drawItem(this.meshes.gear, teethRingM, [0.56, 0.60, 0.66, 1.0], [0.72, 56], viewProj);
                        const hexNutM = this.matSpinX(r.cx + r.thick * 0.56, r.cy, r.cz, ang, 0, 0, Math.PI * 0.5, r.r * 0.18, r.thick * 0.42, r.r * 0.18);
                        this.drawItem(this.meshes.hex, hexNutM, [0.84, 0.87, 0.92, 1.0], [0.84, 66], viewProj);
                        if (r.type === 'flywheel') {{
                            const frictionRingM = this.matSpinX(r.cx - r.thick * 0.38, r.cy, r.cz, ang, 0, 0, Math.PI * 0.5, r.r * 0.78, r.thick * 0.18, r.r * 0.78);
                            this.drawItem(this.meshes.cyl, frictionRingM, [0.22, 0.25, 0.30, 1.0], [0.42, 32], viewProj);
                        }}
                        const faceM = this.matSpinX(r.cx + r.thick * 0.32, r.cy, r.cz, ang, 0, 0, Math.PI * 0.5, r.r * 0.78, r.thick * 0.55, r.r * 0.78);
                        this.drawItem(this.meshes.cyl, faceM, r.colorHub, [0.72, 60], viewProj);
                        const bossM = this.matSpinX(r.cx + r.thick * 0.60, r.cy, r.cz, ang, 0, 0, Math.PI * 0.5, r.r * 0.26, r.thick * 0.35, r.r * 0.26);
                        this.drawItem(this.meshes.cyl, bossM, r.colorRim, [0.75, 62], viewProj);
                        const notchM = this.matTRS(r.cx + r.thick * 0.58, r.cy + Math.cos(ang) * (r.r * 0.48), r.cz + Math.sin(ang) * (r.r * 0.48), ang, 0, 0, 0.032, r.r * 0.56, 0.055);
                        this.drawItem(this.meshes.box, notchM, [0.92, 0.34, 0.24, 1.0], [0.6, 48], viewProj);
                    }} else if (r.type === 'impeller') {{
                        const hubM = this.matSpinX(r.cx, r.cy, r.cz, ang, 0, 0, Math.PI * 0.5, r.r * 0.36, 0.06, r.r * 0.36);
                        this.drawItem(this.meshes.cyl, hubM, r.colorHub, [0.7, 56], viewProj);
                        for (let b = 0; b < 5; b++) {{
                            const bAng = ang + (b * Math.PI * 2) / 5;
                            const bM = this.matTRS(r.cx - 0.02, r.cy + Math.cos(bAng) * (r.r * 0.45), r.cz + Math.sin(bAng) * (r.r * 0.45), bAng, 0, 0, 0.024, r.r * 0.90, 0.032);
                            this.drawItem(this.meshes.box, bM, r.colorBlade, [0.8, 64], viewProj);
                        }}
                    }}
                }}

                // Chama de combustão na câmara no PMS (visível quando ligado / acentuada em Slow Mo)
                if (engineSim.on && engineSim.currentRpm > 20) {{
                    gl.enable(gl.BLEND);
                    gl.blendFunc(gl.SRC_ALPHA, gl.ONE);
                    gl.depthMask(false);
                    const cycleLen = this.config.ciclo === '2T' ? Math.PI * 2 : Math.PI * 4;
                    const isDieselGlow = this.config.combustivel === 'Diesel';
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
        function syncEnginePowerUI() {{
            const t = I18N[currentLang];
            btnEnginePower.classList.toggle('ligado', engineSim.on);
            btnEnginePower.setAttribute('aria-pressed', engineSim.on ? 'true' : 'false');
            btnEnginePowerLabel.textContent = engineSim.on ? t.stopEngine : t.startEngine;
            btnEngineThrottle.disabled = !engineSim.on;
            if (!engineSim.on) {{
                engineSim.throttleHeld = false;
                engineSim.blipTimer = 0;
                btnEngineThrottle.classList.remove('acelerando');
            }}
            drawDynoChart();
        }}

        btnEnginePower.addEventListener('click', () => {{
            engineSim.on = !engineSim.on;
            if (engineSim.on && engineSim.currentRpm < engineSim.idleRpm) {{
                engineSim.currentRpm = Math.max(engineSim.currentRpm, engineSim.idleRpm * 0.7);
            }}
            syncEnginePowerUI();
        }});

        const startThrottle = e => {{
            if (!engineSim.on) return;
            if (e && e.cancelable) e.preventDefault();
            engineSim.throttleHeld = true;
            engineSim.blipTimer = 0.55;
            btnEngineThrottle.classList.add('acelerando');
        }};
        const stopThrottle = () => {{
            engineSim.throttleHeld = false;
            btnEngineThrottle.classList.remove('acelerando');
        }};

        btnEngineThrottle.addEventListener('pointerdown', startThrottle);
        window.addEventListener('pointerup', stopThrottle);
        window.addEventListener('pointercancel', stopThrottle);
        window.addEventListener('blur', stopThrottle);
        btnEngineThrottle.addEventListener('keydown', e => {{
            if (e.code === 'Space' || e.code === 'Enter') startThrottle(e);
        }});
        btnEngineThrottle.addEventListener('keyup', e => {{
            if (e.code === 'Space' || e.code === 'Enter') stopThrottle();
        }});
        window.addEventListener('keydown', e => {{
            if (e.code !== 'Space' || !engineSim.on) return;
            const active = document.activeElement;
            if (active && active !== document.body && active !== btnEngineThrottle && active !== motorCanvas && active.id !== 'motor-bg-stage') return;
            startThrottle(e);
        }});
        window.addEventListener('keyup', e => {{
            if (e.code !== 'Space') return;
            if (engineSim.throttleHeld) stopThrottle();
        }});

        function readEnginePayload() {{
            const rawBore = parseFloat(inputBore.value);
            const rawStroke = parseFloat(inputStroke.value);
            const rawCr = parseFloat(inputCr.value);
            const rawRpm = parseInt(inputRpm.value, 10);
            const rawTurbo = inputTurboBoost ? parseFloat(inputTurboBoost.value) : 0;
            const rawSc = inputScBoost ? parseFloat(inputScBoost.value) : 0;
            return {{
                bore: Number.isFinite(rawBore) && rawBore > 0 ? Math.max(10.0, rawBore) : 86.0,
                stroke: Number.isFinite(rawStroke) && rawStroke > 0 ? Math.max(10.0, rawStroke) : 86.0,
                compression_ratio: Number.isFinite(rawCr) && rawCr > 0 ? Math.max(2.0, rawCr) : 10.5,
                max_rpm: Number.isFinite(rawRpm) && rawRpm > 0 ? Math.max(500, rawRpm) : 7500,
                combustivel: selectCombustivel.value || 'Gasolina',
                ciclo: selectCiclo.value || '4T',
                cilindros: parseInt(selectCilindros.value, 10) || 4,
                admissao: selectAdmissao.value || 'Atmosférico',
                formato: selectFormato.value || 'I',
                v_angle: selectVAngle ? selectVAngle.value : '60',
                material: selectMaterial ? selectMaterial.value : 'Alumínio',
                piston_material: selectPistonMaterial ? selectPistonMaterial.value : 'Alumínio',
                camshaft: selectCamshaft ? selectCamshaft.value : 'DOHC',
                valve_type: selectValveType ? selectValveType.value : 'Molas',
                num_valvulas: selectValves ? parseInt(selectValves.value, 10) : 4,
                turbo_bar: (inputTurboBoost && !inputTurboBoost.disabled && Number.isFinite(rawTurbo)) ? Math.max(0, rawTurbo) : 0.0,
                sc_bar: (inputScBoost && !inputScBoost.disabled && Number.isFinite(rawSc)) ? Math.max(0, rawSc) : 0.0
            }};
        }}

        function atualizarMotor3D() {{
            const p = readEnginePayload();
            const t = I18N[currentLang];
            const admLabel = (t.admOpts && t.admOpts[p.admissao]) ? t.admOpts[p.admissao] : p.admissao;
            const isWankel = p.formato === 'WANKEL';
            const fmtDisplay = isWankel
                ? `WANKEL ${{p.cilindros}}R`
                : ((p.formato === 'V' || p.formato === 'W') ? `${{p.formato}}${{p.cilindros}} (${{p.v_angle}}°)` : `${{p.formato}}${{p.cilindros}}`);
            const unitCc = (Math.PI / 4.0) * Math.pow(p.bore / 10.0, 2) * (p.stroke / 10.0);
            const litros = ((unitCc * (isWankel ? 1.308 : 1.0) * p.cilindros) / 1000.0).toFixed(2);

            motorNumCilindros.textContent = p.cilindros;
            if (motor3dBadge) {{
                motor3dBadge.textContent = `${{fmtDisplay}} · ${{admLabel.toUpperCase()}}`;
            }}
            if (motor3dSpec) {{
                motor3dSpec.textContent = isWankel
                    ? `WANKEL · ${{litros}} L · ${{p.cilindros}}R`
                    : `${{p.formato}} · ${{litros}} L · ${{p.bore.toFixed(0)}}×${{p.stroke.toFixed(0)}} mm`;
            }}

            const matLabel = (t.matOpts && t.matOpts[p.material]) ? t.matOpts[p.material] : p.material;
            const pMatLabel = (t.pistonMatOpts && t.pistonMatOpts[p.piston_material]) ? t.pistonMatOpts[p.piston_material] : p.piston_material;
            const fuelLabel = (t.fuelOpts && t.fuelOpts[p.combustivel]) ? t.fuelOpts[p.combustivel] : p.combustivel;
            if (sumArchVal) {{
                if (isWankel) {{
                    sumArchVal.textContent = `${{fmtDisplay}} · ${{t.rotaryWord}}`;
                }} else {{
                    const vtShort = p.camshaft === 'Freevalve' ? 'Freevalve' : `${{p.camshaft}} · ${{p.num_valvulas}}V`;
                    sumArchVal.textContent = `${{fmtDisplay}} · ${{vtShort}}`;
                }}
            }}
            if (sumArchSub) {{
                sumArchSub.textContent = `${{p.ciclo}} · ${{t.compShort}} ${{p.compression_ratio.toFixed(1)}}:1${{!isWankel && p.camshaft !== 'Freevalve' ? ` · ${{p.valve_type}}` : ''}}`;
            }}
            if (sumDispVal) sumDispVal.textContent = `${{litros}} L`;
            if (sumGeoSub) sumGeoSub.textContent = `${{p.bore.toFixed(0)}}×${{p.stroke.toFixed(0)}} mm · ${{p.max_rpm}} RPM`;
            if (sumAdmVal) sumAdmVal.textContent = admLabel;
            if (sumAdmSub) {{
                if (p.admissao === 'Atmosférico') sumAdmSub.textContent = '0.0 bar';
                else if (p.admissao === 'Supercompressor') sumAdmSub.textContent = `+${{p.sc_bar.toFixed(1)}} bar`;
                else if (p.admissao === 'Twincharge') sumAdmSub.textContent = `+${{p.turbo_bar.toFixed(1)}} / +${{p.sc_bar.toFixed(1)}} bar`;
                else sumAdmSub.textContent = `+${{p.turbo_bar.toFixed(1)}} bar`;
            }}
            if (sumBuildVal) sumBuildVal.textContent = matLabel;
            if (sumBuildSub) {{
                const pWord = isWankel ? t.rotorMatWord : t.pistonWord;
                sumBuildSub.textContent = `${{pWord}}: ${{pMatLabel}} · ${{fuelLabel}}`;
            }}
            if (motor3D) {{
                motor3D.setConfig({{
                    cilindros: p.cilindros,
                    formato: p.formato,
                    admissao: p.admissao,
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
            const valTol = {{ 'Molas': 0.0, 'VVT': 0.5, 'Desmodrómico': 2.0, 'Pneumático': 4.0, 'Freevalve': 4.5 }};
            const pisTol = {{ 'Alumínio': 0.0, 'Forged': 2.5, 'Forged Heavy': 1.5, 'Titânio': 5.0 }};
            const pisCrTol = {{ 'Alumínio': 0.0, 'Forged': 1.0, 'Forged Heavy': 3.0, 'Titânio': 2.0 }};
            const isWankel = payload.formato === 'WANKEL';
            const isFreevalve = !isWankel && (payload.camshaft === 'Freevalve' || payload.valve_type === 'Freevalve');
            const velMediaPistao = isWankel
                ? (2.0 * (payload.stroke / 1000.0) * (payload.max_rpm / 3.0) * 1.55) / 60.0
                : (2.0 * (payload.stroke / 1000.0) * payload.max_rpm) / 60.0;
            const matTVal = matTol[payload.material] !== undefined ? matTol[payload.material] : 0.5;
            const valTVal = isWankel ? 6.0 : (isFreevalve ? 4.5 : (valTol[payload.valve_type] || 0.0));
            const pisTVal = pisTol[payload.piston_material] || 0.0;
            const limiteVm = 25.0 + matTVal + valTVal + pisTVal;
            const motivosAlerta = [];
            if (velMediaPistao > limiteVm) {{
                motivosAlerta.push(t.warnPiston(velMediaPistao.toFixed(1), limiteVm.toFixed(1)));
            }}
            const limiteCr = (payload.combustivel === 'Diesel' ? 22 : 15) + (pisCrTol[payload.piston_material] || 0.0);
            if (payload.compression_ratio > limiteCr) {{
                motivosAlerta.push(t.warnCr(limiteCr));
            }}
            aplicarAlertaRpm(motivosAlerta.length > 0, motivosAlerta);
        }}

        async function atualizarDados() {{
            const cilindros = parseInt(selectCilindros.value, 10) || 4;
            const formato = selectFormato.value || 'I';
            const admissao = selectAdmissao.value || 'Atmosférico';

            atualizarMotor3D();

            if (window.location.protocol !== 'file:') {{
                try {{
                    const res = await fetch('/api/ficha', {{
                        method: 'POST',
                        headers: {{ 'Content-Type': 'application/json' }},
                        body: JSON.stringify({{ cilindros, formato, admissao }})
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

        [inputBore, inputStroke, inputCr, inputRpm, inputTurboBoost, inputScBoost, selectCombustivel, selectCiclo, selectVAngle, selectMaterial, selectPistonMaterial, selectCamshaft, selectValveType, selectValves].forEach(el => {{
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

            resposta = json.dumps({
                "cilindros": cil,
                "formato": fmt,
                "admissao": adm,
                "motor_svg": gerar_svg_motor_inline(cil, fmt, adm),
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
                combustivel=str(dados.get("combustivel") or "Gasolina"),
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
            )
            resposta = json.dumps({
                "torque_nm_val": resultado["torque_nm_val"],
                "potencia_kw_val": resultado["potencia_kw_val"],
                "vel_pistao": resultado["velocidade_pistao_mps"],
                "limite_vm": resultado["limite_vm"],
                "limite_cr": resultado["limite_cr"],
                "alerta_rpm": resultado["alerta_rpm"],
                "motivos_alerta": resultado["motivos_alerta"],
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
