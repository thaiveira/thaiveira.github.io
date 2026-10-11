# thaiveira.com.br

Meu site, portfólio e blog que é um playground que cresce e muda comigo. Feito com HTML, CSS, JavaScript, um pouco de Python e café.

🌐 **[thaiveira.com.br](https://thaiveira.com.br)**

![HTML5](https://img.shields.io/badge/HTML5-E34F26?logo=html5&logoColor=white)
![CSS3](https://img.shields.io/badge/CSS3-1572B6?logo=css3&logoColor=white)
![JavaScript](https://img.shields.io/badge/JavaScript-F7DF1E?logo=javascript&logoColor=black)
![Python](https://img.shields.io/badge/Python-3776AB?logo=python&logoColor=white)
![GitHub Pages](https://img.shields.io/badge/GitHub%20Pages-222?logo=github&logoColor=white)
  
## O que tem aqui

- **Visual pixel art**: estrelas, lua, separadores, ícones e fontes em pixel art.
- **Tema claro e escuro**: botão no canto superior da tela, com a escolha salva no navegador e mantida entre as páginas.
- **Galeria com lightbox**: `<dialog>` nativo, setas e teclado, swipe no celular e transição suave (View Transitions API).
- **Métricas automáticas**: gráficos de commits e linguagens do meu [GitHub](https://github.com/thaiveira) e [Codeberg](https://codeberg.org/thaiveira), gerados em Python e atualizados todo mês por uma GitHub Action.
- **Sem frameworks**: HTML, CSS e JS puros, sem build.

![tela inicio tema escuro](imagens/tema-escuro.png)
![tela inicio tema claro](imagens/tema-claro.png)

## Estrutura

```
.
├── .github/workflows/metricas.yml   # Action das métricas
├── imagens/                         # imagens do visual do site
├── js/                              # tema, galeria e efeitos
├── posts/                           # blog, um .html por post (+ imagens/ dos posts)
├── scripts/metricas/                # gerar_metricas.py, fontes e requirements.txt
├── style/style.css
├── *.html                           # index, sobre, portfolio, metricas, blog...
├── feed.xml                         # RSS do blog
└── CNAME                            # domínio personalizado
```

## Métricas

`scripts/metricas/gerar_metricas.py` busca commits dos últimos 6 meses e a distribuição de linguagens aqui no meu GiHub e lá no meu Codeberg. As horas de estudo vêm de `study_log.json`, que atualizo à mão.

**Automático:** o workflow roda todo fim de mês e abre um **pull request** para eu revisar e aceitar.

## Deploy

GitHub Pages, via VScodium.