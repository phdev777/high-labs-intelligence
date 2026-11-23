# Publicar em um repositório GitHub próprio

Nome recomendado: `high-labs-intelligence` · Visibilidade: pública · Branch: `main`.

## Publicação inicial pelo site

1. Na conta GitHub desejada, crie um repositório público vazio chamado `high-labs-intelligence`, sem README ou licença automática.
2. Extraia o ZIP e abra um terminal dentro da pasta `high-labs-intelligence`.
3. Execute os comandos abaixo, substituindo `SEU_USUARIO` caso necessário:

```bash
git init
git add .
git commit -m "feat: initial High Labs Intelligence skill"
git branch -M main
git remote add origin https://github.com/SEU_USUARIO/high-labs-intelligence.git
git push -u origin main
```

Use a autenticação normal do GitHub no terminal. **Não coloque token, senha, chaves, arquivos de clientes ou `.env` no commit.**

## Revisão antes de tornar público

```bash
python -m unittest discover -s tests -v
git status --short
git ls-files
```

Confirme que apenas arquivos desta skill estão sendo incluídos. Uma skill pública não deve conter configurações de um cliente específico.

## Repositório existente?

Não execute comandos de `git init` e `git remote add` se estiver dentro de outro projeto. Repositórios de terceiros ou projetos não relacionados não são destino adequado para esta distribuição.