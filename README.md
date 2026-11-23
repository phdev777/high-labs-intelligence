# High Labs Intelligence

**Inteligência operacional para qualquer negócio.**

Skill independente de setor e de plataforma para apoiar análise de operações, planilhas Excel/CSV, orçamento, custos, produção, capacidade, manutenção, compras, estoque, ERP, KPIs e relatórios gerenciais.

> **Versão:** 0.1.0 (pré-lançamento técnico) · **Idioma-base:** português brasileiro · **Execução:** conforme ferramentas disponíveis na IA do usuário.

## O que entrega

- Método de análise rastreável, com checagem de completude, duplicidade, reconciliação, granularidade e fontes.
- Guias especializados de produção, custos, orçamento, estoque, manutenção, anomalias e indicadores.
- Templates de relatório diário, fechamento mensal e investigação de desvios.
- Scripts opcionais e locais para perfil de CSV/XLSX e variação orçado x realizado; sem conexão automática a ERP ou dados de clientes.
- Estrutura multiempresa: contexto individual sempre separado da skill pública.

## Organização

```text
high-labs-intelligence/
├── SKILL.md                      # Ponto de entrada da skill
├── references/                  # Módulos de conhecimento sob demanda
├── templates/                   # Modelos reutilizáveis
├── scripts/                     # Auxiliares opcionais e locais (somente leitura)
├── examples/                    # Dados integralmente sintéticos
├── tests/                       # Verificações básicas
└── .github/workflows/validate.yml
```

## Instalar no Claude

No `claude.ai`, se sua assinatura e configuração permitirem skills personalizadas e execução de código, importe o arquivo ZIP da skill nas configurações de Skills. O ZIP inclui um diretório que contém `SKILL.md`. A plataforma valida o pacote e decide quando carregar a skill. Consulte a [documentação oficial](https://platform.claude.com/docs/en/agents-and-tools/agent-skills/overview).

## Instalar no ChatGPT

Onde o recurso Skills estiver disponível para sua conta/workspace: **Plugins → Skills → Criar → Carregar do computador**, e envie o pacote ZIP. A disponibilidade depende do plano e das permissões da organização. Consulte a [documentação oficial](https://help.openai.com/en/articles/20001066-skills-in-chatgpt).

**Alternativa:** use `SKILL.md` e os guias relevantes como instruções/contexto em uma conversa ou projeto, conforme os recursos do produto. Apenas anexar arquivos não equivale necessariamente a instalar uma skill automaticamente ativável.

## Exemplos de pedidos

```text
Analise os custos deste trimestre por centro de custo. Aponte variações
relevantes e possíveis causas, validando duplicidades e valores ausentes.

Consolide estas planilhas de produção e elabore um relatório diário,
respeitando as regras de turno definidas neste negócio.

Concilie compras, recebimentos e notas fiscais, listando divergências,
mas sem alterar o ERP.

Simule três cenários do orçamento anual por unidade, com premissas
explicitadas e comparação com o histórico informado.
```

## Executar os auxiliares opcionais

Requer Python 3.10+. O perfil de XLSX requer `openpyxl` instalado no ambiente local (`pip install openpyxl`). Não é necessário para uso textual da skill. Os scripts não alteram arquivos nem transmitem dados pela rede.

```bash
python scripts/profile_tabular.py examples/producao-sintetica.csv --key evento_id
python scripts/budget_variance.py examples/custos-sinteticos.csv --group-by categoria,periodo --locale br
python -m unittest discover -s tests -v
```

O perfil XLSX analisa células e fórmulas sem recalcular ou validar os valores das fórmulas. `budget_variance.py` **recusa linhas com valores ausentes/inválidos**, a menos que `--allow-partial` seja informado; nesse caso o relatório indica a cobertura e as rejeições. Os exemplos são fictícios.

## Limitações e princípios de segurança

- Não substitui profissional contábil, engenheiro responsável ou auditoria independente.
- Nenhuma integração externa ocorre automaticamente. Acesso a OneDrive, ERP, banco ou BI depende de conectores autorizados e das ferramentas da plataforma.
- Nenhum lançamento/alteração é realizado sem autorização específica.
- Empresas diferentes devem manter **contextos, credenciais e bases isolados**; nunca coloque informações de clientes nesta distribuição pública.
- **Não considera uma análise completa se houver linhas rejeitadas, cobertura parcial ou conflitos de fontes sem validação.**
- Versão experimental: teste com dados sintéticos e ambiente controlado antes de usar resultados em decisões materiais.

## Evolução e contribuição

O núcleo metodológico é independente de ChatGPT, Claude e do futuro assistente nativo High Labs. O comportamento e a instalação podem variar conforme a plataforma. Sugestões, testes e correções podem ser propostos por pull request quando o repositório for publicado.

## Licença

**Todos os direitos reservados.** Uma licença de código e de distribuição ainda não foi definida. Publicar este repositório não concede automaticamente autorização para reproduzir, modificar ou redistribuir a skill. Este projeto não é afiliado à OpenAI ou à Anthropic.