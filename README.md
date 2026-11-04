# Login Patterns

Investigue autenticações de uma aplicação própria em um JSON por linha. Eventos fora de ordem são classificados por horário e número da linha. Os achados preservam as linhas originais, inclusive quando a ordem cronológica é diferente da ordem do arquivo.

Use Python 3.11 ou superior, sem pacotes adicionais. Na pasta do projeto:

| Operação | Windows · PowerShell | Linux · Bash |
|---|---|---|
| Analisar a demonstração | `py detectar.py demo.jsonl --falhas 2` | `python3 detectar.py demo.jsonl --falhas 2` |
| Executar testes | `py -m unittest` | `python3 -m unittest` |

Cada linha exige hora ISO 8601 com fuso, conta, origem e resultado (sucesso ou falha). A demonstração produz uma sequência de falhas e um sucesso posterior da mesma origem. O número da linha permite conferir cada evidência.

Ajuste a janela em segundos com --janela, o limiar por conta com --falhas e a quantidade de contas distintas atingidas pela mesma origem com --contas. A borda inicial da janela é inclusiva. Um sucesso encerra a sequência de falhas daquela conta e origem. Origens compartilhadas podem gerar alertas legítimos. A análise mantém os eventos em memória para garantir ordenação.

Licença MIT.
