

import json
import os
from collections import defaultdict
from datetime import datetime, timedelta, timezone

import pandas as pd
import requests
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt


DATA_DIR = "scripts/metricas/data"
IMG_DIR = "imagens"                       
RESUMO_PATH = "scripts/metricas/metrics_summary.json"

GITHUB_USER = "thaiveira"
CODEBERG_USER = "thaiveira"
GITHUB_TOKEN = os.environ.get("GITHUB_TOKEN")  
MESES_HISTORICO = 6


COR_INK = "#17151f"
COR_LILAC = "#8a6bd1"
COR_LILAC_SOFT = "#c9b6f2"
COR_PINK = "#ff9fc7"

plt.rcParams.update({
    "font.family": "monospace",
    "text.color": COR_INK,
    "axes.edgecolor": COR_INK,
    "axes.labelcolor": COR_INK,
    "xtick.color": COR_INK,
    "ytick.color": COR_INK,
    "axes.linewidth": 1.4,
    "figure.facecolor": "none",
    "axes.facecolor": "none",
    "savefig.facecolor": "none",
    "savefig.transparent": True,
})


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
    return paginar(
        f"https://api.github.com/users/{GITHUB_USER}/repos",
        headers=github_headers(),
        params={"per_page": 100, "type": "owner"},
    )


def fetch_codeberg_repos():
    return paginar(
        f"https://codeberg.org/api/v1/users/{CODEBERG_USER}/repos",
        params={"limit": 50},
    )


def fetch_github_commits(repo_full_name, desde_iso):
    return paginar(
        f"https://api.github.com/repos/{repo_full_name}/commits",
        headers=github_headers(),
        params={"per_page": 100, "since": desde_iso, "author": GITHUB_USER},
    )


def fetch_codeberg_commits(repo_full_name, desde_iso):
    return paginar(
        f"https://codeberg.org/api/v1/repos/{repo_full_name}/commits",
        params={"limit": 50, "since": desde_iso},
    )


def fetch_github_linguagens(repo_full_name):
    resp = requests.get(f"https://api.github.com/repos/{repo_full_name}/languages",
                         headers=github_headers(), timeout=20)
    resp.raise_for_status()
    return resp.json()


def fetch_codeberg_linguagens(repo_full_name):
    resp = requests.get(f"https://codeberg.org/api/v1/repos/{repo_full_name}/languages", timeout=20)
    if resp.status_code == 404:
        return {}
    resp.raise_for_status()
    return resp.json()


# ---------- agregação ----------

def coletar_atividade():
   
    desde = (datetime.now(timezone.utc) - timedelta(days=30 * MESES_HISTORICO)).replace(
        day=1, hour=0, minute=0, second=0, microsecond=0
    )
    desde_iso = desde.strftime("%Y-%m-%dT%H:%M:%SZ")

    commits_por_mes = defaultdict(int)
    linguagens_bytes = defaultdict(int)

    for repo in fetch_github_repos():
        if repo.get("fork"):
            continue  # ignora repositórios que são fork de outra pessoa
        nome = repo["full_name"]
        for c in fetch_github_commits(nome, desde_iso):
            data = c["commit"]["author"]["date"][:7]
            commits_por_mes[data] += 1
        for lang, n_bytes in fetch_github_linguagens(nome).items():
            linguagens_bytes[lang] += n_bytes

    for repo in fetch_codeberg_repos():
        if repo.get("fork"):
            continue
        nome = repo["full_name"]
        for c in fetch_codeberg_commits(nome, desde_iso):
            data = c["commit"]["author"]["date"][:7]
            commits_por_mes[data] += 1
        for lang, n_bytes in fetch_codeberg_linguagens(nome).items():
            linguagens_bytes[lang] += n_bytes

    return commits_por_mes, linguagens_bytes


def carregar_json(nome_arquivo):
    with open(os.path.join(DATA_DIR, nome_arquivo), "r", encoding="utf-8") as f:
        return json.load(f)


# ---------- gráficos ----------

def grafico_commits(commits_por_mes):
    df = pd.DataFrame(sorted(commits_por_mes.items()), columns=["mes", "commits"])
    fig, ax = plt.subplots(figsize=(6.4, 3.4))
    ax.bar(df["mes"], df["commits"], color=COR_LILAC, edgecolor=COR_INK, linewidth=1.4, width=0.55)
    ax.set_title("Commits por mês (GitHub + Codeberg)", fontsize=13, fontweight="bold", pad=12)
    ax.spines[["top", "right"]].set_visible(False)
    ax.set_axisbelow(True)
    ax.grid(axis="y", color=COR_LILAC_SOFT, linewidth=0.8, alpha=0.6)
    plt.xticks(rotation=20)
    fig.tight_layout()
    fig.savefig(os.path.join(IMG_DIR, "commits.svg"))
    plt.close(fig)
    return {
        "total_commits": int(df["commits"].sum()) if not df.empty else 0,
        "media_mensal": round(df["commits"].mean(), 1) if not df.empty else 0,
        "mes_mais_ativo": df.loc[df["commits"].idxmax(), "mes"] if not df.empty else None,
    }


def grafico_linguagens(linguagens_bytes):
    total = sum(linguagens_bytes.values()) or 1
    df = pd.DataFrame(
        [(lang, round(n * 100 / total, 1)) for lang, n in linguagens_bytes.items()],
        columns=["linguagem", "porcentagem"],
    ).sort_values("porcentagem", ascending=True).tail(6)  # top 6
    cores = [COR_LILAC, COR_PINK, COR_LILAC_SOFT, COR_INK] * 2
    fig, ax = plt.subplots(figsize=(6.4, 3.2))
    ax.barh(df["linguagem"], df["porcentagem"], color=cores[:len(df)], edgecolor=COR_INK, linewidth=1.4, height=0.55)
    ax.set_title("Linguagens mais usadas (por volume de código)", fontsize=13, fontweight="bold", pad=12)
    ax.spines[["top", "right"]].set_visible(False)
    for i, v in enumerate(df["porcentagem"]):
        ax.text(v + 1, i, f"{v}%", va="center", fontsize=10)
    fig.tight_layout()
    fig.savefig(os.path.join(IMG_DIR, "linguagens.svg"))
    plt.close(fig)
    return {"linguagem_principal": df.iloc[-1]["linguagem"] if not df.empty else None}


def grafico_estudos(dados):
    df = pd.DataFrame(dados["horas_por_topico"]).sort_values("horas", ascending=True)
    fig, ax = plt.subplots(figsize=(6.4, 3.6))
    ax.barh(df["topico"], df["horas"], color=COR_PINK, edgecolor=COR_INK, linewidth=1.4, height=0.55)
    ax.set_title("Horas de estudo autodidata por tópico", fontsize=13, fontweight="bold", pad=12)
    ax.spines[["top", "right"]].set_visible(False)
    for i, v in enumerate(df["horas"]):
        ax.text(v + 1, i, f"{v}h", va="center", fontsize=10)
    fig.tight_layout()
    fig.savefig(os.path.join(IMG_DIR, "estudos.svg"))
    plt.close(fig)
    return {
        "total_horas": int(df["horas"].sum()),
        "topico_principal": df.iloc[-1]["topico"],
    }


def main():
    os.makedirs(IMG_DIR, exist_ok=True)

    commits_por_mes, linguagens_bytes = coletar_atividade()
    estudos = carregar_json("study_log.json")

    resumo = {}
    resumo.update(grafico_commits(commits_por_mes))
    resumo.update(grafico_linguagens(linguagens_bytes))
    resumo.update(grafico_estudos(estudos))
    resumo["gerado_em"] = datetime.now(timezone.utc).strftime("%Y-%m-%d")

    with open(RESUMO_PATH, "w", encoding="utf-8") as f:
        json.dump(resumo, f, ensure_ascii=False, indent=2)

    print("Gráficos gerados em imagens/. Resumo salvo em metrics_summary.json:")
    print(json.dumps(resumo, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
