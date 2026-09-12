import json
import os
import calendar
from collections import defaultdict
from datetime import datetime, timedelta, timezone

import pandas as pd
import requests
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.font_manager as fm
from matplotlib.patches import FancyBboxPatch

# Caminhos relativos à raiz do repositório (rode o script de lá)
DATA_DIR = "scripts/metricas"
IMG_DIR = "imagens"
RESUMO_PATH = "scripts/metricas/metrics_summary.json"

GITHUB_USER = "thaiveira"
CODEBERG_USER = "thaiveira"
GITHUB_TOKEN = os.environ.get("GITHUB_TOKEN")
MESES_HISTORICO = 6

MESES_PT = ["", "Jan", "Fev", "Mar", "Abr", "Mai", "Jun",
            "Jul", "Ago", "Set", "Out", "Nov", "Dez"]


COR_BG = "#fdfbf6"
COR_INK = "#17151f"
COR_LILAC = "#8a6bd1"
COR_LILAC_SOFT = "#c9b6f2"
COR_PINK = "#ff9fc7"

FONTE_MONO = fm.FontProperties(family="DejaVu Sans Mono", weight="bold")

CAMINHO_VT323 = os.path.join("scripts", "metricas", "fonts", "VT323-Regular.ttf")
if os.path.exists(CAMINHO_VT323):
    fm.fontManager.addfont(CAMINHO_VT323)
    FONTE_TITULO = fm.FontProperties(fname=CAMINHO_VT323)
else:
    print(f"[aviso] VT323 não encontrada em {CAMINHO_VT323} — usando DejaVu Sans Mono no título.")
    FONTE_TITULO = FONTE_MONO

plt.rcParams.update({
    "font.family": "DejaVu Sans Mono",
    "text.color": COR_INK,
    "axes.edgecolor": COR_INK,
    "axes.labelcolor": COR_INK,
    "xtick.color": COR_INK,
    "ytick.color": COR_INK,
    "axes.linewidth": 2,
    "figure.facecolor": COR_BG,
    "axes.facecolor": COR_BG,
    "savefig.facecolor": COR_BG,
})

def desenhar_moldura(fig, cores_canto=(COR_LILAC_SOFT, COR_PINK)):
  
    borda = FancyBboxPatch(
        (0.008, 0.012), 0.984, 0.976,
        boxstyle="round,pad=0,rounding_size=0.03",
        transform=fig.transFigure,
        linewidth=2.5, edgecolor=COR_INK, facecolor="none", zorder=10,
    )
    fig.add_artist(borda)

    n = 6  # tamanho do bloco de pontinhos (n x n) em cada canto
    passo = 0.014
    cantos = [(0.02, 0.965, 1, -1), (0.98, 0.965, -1, -1),
              (0.02, 0.035, 1, 1), (0.98, 0.035, -1, 1)]
    for cx, cy, sx, sy in cantos:
        for i in range(n):
            for j in range(n - i):
                if (i + j) % 2 == 0:
                    continue
                x = cx + sx * i * passo
                y = cy + sy * j * passo
                cor = cores_canto[0] if (i + j) % 3 else cores_canto[1]
                fig.add_artist(plt.Circle((x, y), 0.0028, transform=fig.transFigure,
                                           color=cor, alpha=0.8, zorder=5))


def estilo_eixos(ax):
    ax.set_facecolor(COR_BG)
    for lado in ("top", "right"):
        ax.spines[lado].set_visible(False)
    for lado in ("left", "bottom"):
        ax.spines[lado].set_linewidth(2.2)
        ax.spines[lado].set_color(COR_INK)


# ---------- coleta de dados ----------

def github_headers():
    h = {"Accept": "application/vnd.github+json"}
    if GITHUB_TOKEN:
        h["Authorization"] = f"Bearer {GITHUB_TOKEN}"
    return h


def paginar(url, headers=None, params=None):
    resultados = []
    page = 1
    params = dict(params or {})
    while True:
        params["page"] = page
        resp = requests.get(url, headers=headers, params=params, timeout=20)
        resp.raise_for_status()
        dados = resp.json()
        if not dados:
            break
        resultados.extend(dados)
        page += 1
    return resultados


def fetch_github_repos():
    return paginar(f"https://api.github.com/users/{GITHUB_USER}/repos",
                   headers=github_headers(), params={"per_page": 100, "type": "owner"})


def fetch_codeberg_repos():
    return paginar(f"https://codeberg.org/api/v1/users/{CODEBERG_USER}/repos",
                   params={"limit": 50})


def fetch_github_commits(repo_full_name, desde_iso):
    return paginar(f"https://api.github.com/repos/{repo_full_name}/commits",
                   headers=github_headers(),
                   params={"per_page": 100, "since": desde_iso, "author": GITHUB_USER})


def fetch_codeberg_commits(repo_full_name, desde_iso):
    return paginar(f"https://codeberg.org/api/v1/repos/{repo_full_name}/commits",
                   params={"limit": 50, "since": desde_iso})


def fetch_github_linguagens(repo_full_name):
    r = requests.get(f"https://api.github.com/repos/{repo_full_name}/languages",
                      headers=github_headers(), timeout=20)
    r.raise_for_status()
    return r.json()


def fetch_codeberg_linguagens(repo_full_name):
    r = requests.get(f"https://codeberg.org/api/v1/repos/{repo_full_name}/languages", timeout=20)
    if r.status_code == 404:
        return {}
    r.raise_for_status()
    return r.json()


def meses_da_janela(n=MESES_HISTORICO):
    hoje = datetime.now(timezone.utc)
    y, m = hoje.year, hoje.month
    meses = []
    for _ in range(n):
        meses.append(f"{y:04d}-{m:02d}")
        m -= 1
        if m == 0:
            m, y = 12, y - 1
    return list(reversed(meses))


def coletar_atividade():
    janela = meses_da_janela()
    desde = datetime.strptime(janela[0] + "-01", "%Y-%m-%d").replace(tzinfo=timezone.utc)
    desde_iso = desde.strftime("%Y-%m-%dT%H:%M:%SZ")

    commits_por_mes = defaultdict(int)
    linguagens_bytes = defaultdict(int)

    for repo in fetch_github_repos():
        if repo.get("fork"):
            continue
        nome = repo["full_name"]
        for c in fetch_github_commits(nome, desde_iso):
            commits_por_mes[c["commit"]["author"]["date"][:7]] += 1
        for lang, n_bytes in fetch_github_linguagens(nome).items():
            linguagens_bytes[lang] += n_bytes

    for repo in fetch_codeberg_repos():
        if repo.get("fork"):
            continue
        nome = repo["full_name"]
        for c in fetch_codeberg_commits(nome, desde_iso):
            commits_por_mes[c["commit"]["author"]["date"][:7]] += 1
        for lang, n_bytes in fetch_codeberg_linguagens(nome).items():
            linguagens_bytes[lang] += n_bytes


    for mes in janela:
        commits_por_mes.setdefault(mes, 0)
    commits_por_mes = {m: commits_por_mes[m] for m in janela}

    return commits_por_mes, linguagens_bytes


def carregar_json(nome_arquivo):
    with open(os.path.join(DATA_DIR, nome_arquivo), "r", encoding="utf-8") as f:
        return json.load(f)


def rotulo_mes(aaaa_mm):
    ano, mes = aaaa_mm.split("-")
    return f"{MESES_PT[int(mes)]} {ano}"


# ---------- gráficos ----------

def grafico_commits(commits_por_mes):
    df = pd.DataFrame(list(commits_por_mes.items()), columns=["mes", "commits"])
    df["rotulo"] = df["mes"].map(rotulo_mes)

    fig, ax = plt.subplots(figsize=(8.6, 5.6))
    fig.subplots_adjust(top=0.8, bottom=0.16, left=0.1, right=0.96)
    estilo_eixos(ax)

    idx_max = df["commits"].idxmax() if df["commits"].max() > 0 else None
    cores = [COR_PINK if i == idx_max else COR_LILAC for i in df.index]
    ax.bar(df["rotulo"], df["commits"], color=cores, edgecolor=COR_INK, linewidth=2, width=0.62, zorder=3)

    ax.set_title("commits por mês", fontproperties=FONTE_TITULO, fontsize=32, pad=34)
    ax.text(0.0, 1.06, "commits", transform=ax.transAxes, fontproperties=FONTE_TITULO, fontsize=16)
    ax.set_xlabel("mês", fontproperties=FONTE_MONO, fontsize=13, labelpad=10)
    ax.grid(axis="y", color=COR_LILAC_SOFT, linewidth=1.1, linestyle=(0, (2, 3)), zorder=0)
    ax.set_axisbelow(True)
    plt.setp(ax.get_xticklabels(), fontproperties=FONTE_MONO, fontsize=11)
    plt.setp(ax.get_yticklabels(), fontproperties=FONTE_MONO, fontsize=11)

    desenhar_moldura(fig, (COR_LILAC_SOFT, COR_PINK))
    fig.savefig(os.path.join(IMG_DIR, "commits.svg"))
    plt.close(fig)

    return {
        "total_commits": int(df["commits"].sum()),
        "media_mensal": round(df["commits"].mean(), 1),
        "mes_mais_ativo": df.loc[idx_max, "rotulo"] if idx_max is not None else None,
    }


def grafico_linguagens(linguagens_bytes):
    linguagens_bytes = dict(linguagens_bytes)
    if "Jupyter Notebook" in linguagens_bytes:
        linguagens_bytes["Python"] = linguagens_bytes.get("Python", 0) + linguagens_bytes.pop("Jupyter Notebook")

    total = sum(linguagens_bytes.values()) or 1
    df = pd.DataFrame(
        [(lang, round(n * 100 / total, 1)) for lang, n in linguagens_bytes.items()],
        columns=["linguagem", "porcentagem"],
    ).sort_values("porcentagem", ascending=False).head(8)
    df = df.sort_values("porcentagem", ascending=True)

    fig, ax = plt.subplots(figsize=(8.6, 5.6))
    fig.subplots_adjust(top=0.82, bottom=0.12, left=0.22, right=0.86)
    estilo_eixos(ax)

    cores = [COR_LILAC if v == df["porcentagem"].max() else COR_LILAC_SOFT for v in df["porcentagem"]]
    barras = ax.barh(df["linguagem"], df["porcentagem"], color=cores, edgecolor=COR_INK, linewidth=2, height=0.6, zorder=3)

    ax.set_title("distribuição de linguagens", fontproperties=FONTE_TITULO, fontsize=30, pad=34)
    ax.text(0.0, 1.06, "linguagem", transform=ax.transAxes, fontproperties=FONTE_TITULO, fontsize=16)
    ax.set_xlabel("%", fontproperties=FONTE_MONO, fontsize=13, labelpad=10)
    for rect, v in zip(barras, df["porcentagem"]):
        ax.text(rect.get_width() + total * 0 + 1.2, rect.get_y() + rect.get_height() / 2,
                f"{v}%", va="center", fontproperties=FONTE_MONO, fontsize=11)
    plt.setp(ax.get_xticklabels(), fontproperties=FONTE_MONO, fontsize=11)
    plt.setp(ax.get_yticklabels(), fontproperties=FONTE_MONO, fontsize=11)

    desenhar_moldura(fig, (COR_LILAC_SOFT, COR_LILAC))
    fig.savefig(os.path.join(IMG_DIR, "linguagens.svg"))
    plt.close(fig)

    return {"linguagem_principal": df.iloc[-1]["linguagem"] if not df.empty else None}


def grafico_estudos(dados):
    df = pd.DataFrame(dados["horas_por_topico"]).sort_values("horas", ascending=True)

    fig, ax = plt.subplots(figsize=(8.6, 5.6))
    fig.subplots_adjust(top=0.82, bottom=0.12, left=0.22, right=0.86)
    estilo_eixos(ax)

    barras = ax.barh(df["topico"], df["horas"], color=COR_PINK, edgecolor=COR_INK, linewidth=2, height=0.6, zorder=3)

    ax.set_title("horas de estudo por tópico", fontproperties=FONTE_TITULO, fontsize=30, pad=34)
    ax.text(0.0, 1.06, "tópico", transform=ax.transAxes, fontproperties=FONTE_TITULO, fontsize=16)
    ax.set_xlabel("horas", fontproperties=FONTE_MONO, fontsize=13, labelpad=10)
    for rect, v in zip(barras, df["horas"]):
        ax.text(rect.get_width() + df["horas"].max() * 0.02, rect.get_y() + rect.get_height() / 2,
                f"{v}h", va="center", fontproperties=FONTE_MONO, fontsize=11)
    plt.setp(ax.get_xticklabels(), fontproperties=FONTE_MONO, fontsize=11)
    plt.setp(ax.get_yticklabels(), fontproperties=FONTE_MONO, fontsize=11)

    desenhar_moldura(fig, (COR_PINK, COR_LILAC_SOFT))
    fig.savefig(os.path.join(IMG_DIR, "estudos.svg"))
    plt.close(fig)

    return {"total_horas": int(df["horas"].sum()), "topico_principal": df.iloc[-1]["topico"]}


def main():
    os.makedirs(IMG_DIR, exist_ok=True)

    commits_por_mes, linguagens_bytes = coletar_atividade()
    estudos = carregar_json("study_log.json")

    resumo = {}
    resumo.update(grafico_commits(commits_por_mes))
    resumo.update(grafico_linguagens(linguagens_bytes))
    resumo.update(grafico_estudos(estudos))
    resumo["janela"] = meses_da_janela()
    resumo["gerado_em"] = datetime.now(timezone.utc).strftime("%Y-%m-%d")

    with open(RESUMO_PATH, "w", encoding="utf-8") as f:
        json.dump(resumo, f, ensure_ascii=False, indent=2)

    print("Gráficos gerados em imagens/. Resumo:")
    print(json.dumps(resumo, ensure_ascii=False, indent=2))
    print("\nAgora confira os SVGs e faça o commit manualmente:")
    print("  git add imagens/commits.svg imagens/linguagens.svg imagens/estudos.svg scripts/metricas/metrics_summary.json")
    print('  git commit -m "Atualiza métricas (mensal)"')
    print("  git push")


if __name__ == "__main__":
    main()
