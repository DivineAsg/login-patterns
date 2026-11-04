"""Correlaciona autenticações de um arquivo JSONL local."""
import argparse
import json
import sys
from collections import defaultdict, deque
from datetime import datetime, timedelta, timezone
from pathlib import Path


def carregar(arquivo):
    eventos = []
    for numero, linha in enumerate(arquivo, 1):
        if not linha.strip():
            continue
        try:
            item = json.loads(linha)
            data = datetime.fromisoformat(item["hora"].replace("Z", "+00:00"))
            if not data.tzinfo:
                raise ValueError("horário sem fuso")
            if item["resultado"] not in ("sucesso", "falha"):
                raise ValueError("resultado desconhecido")
            for campo in ("origem", "conta"):
                if not isinstance(item[campo], str) or not item[campo].strip():
                    raise ValueError(f"{campo} inválido")
            eventos.append((data.astimezone(timezone.utc), numero, item))
        except (KeyError, AttributeError, TypeError, ValueError) as erro:
            raise ValueError(f"Linha {numero} inválida: {erro}") from erro
    return sorted(eventos, key=lambda evento: evento[:2])


def analisar(eventos, segundos, limite, contas):
    janela = timedelta(seconds=segundos)
    historicos = defaultdict(deque)
    alertas = []
    for hora, linha, item in eventos:
        origem, conta = item["origem"], item["conta"]
        fila = historicos[origem]
        while fila and fila[0][0] < hora - janela:
            fila.popleft()
        anteriores = [n for _, n, usuario in fila if usuario == conta]
        distintas = {usuario for _, _, usuario in fila}
        tipo = None
        evidencias = []
        if item["resultado"] == "sucesso":
            if len(anteriores) >= limite:
                tipo, evidencias = "sucesso após falhas", anteriores + [linha]
            historicos[origem] = deque(ev for ev in fila if ev[2] != conta)
        else:
            fila.append((hora, linha, conta))
            if len(anteriores) + 1 == limite:
                tipo, evidencias = "falhas concentradas", anteriores + [linha]
            if conta not in distintas and len(distintas) + 1 == contas:
                alertas.append({"tipo": "várias contas", "origem": origem,
                                "hora": hora.isoformat(), "linhas": [n for _, n, _ in fila]})
        if tipo:
            alertas.append({"tipo": tipo, "origem": origem, "conta": conta,
                            "hora": hora.isoformat(), "linhas": evidencias})
    return alertas


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("arquivo", type=Path, help="eventos JSONL em UTF-8")
    p.add_argument("--janela", type=int, default=300, help="janela em segundos")
    p.add_argument("--falhas", type=int, default=5, help="falhas por origem e conta")
    p.add_argument("--contas", type=int, default=4, help="contas distintas por origem")
    args = p.parse_args()
    if min(args.janela, args.falhas, args.contas) <= 0:
        p.error("os limites devem ser positivos")
    try:
        with args.arquivo.open(encoding="utf-8-sig") as arquivo:
            alertas = analisar(carregar(arquivo), args.janela, args.falhas, args.contas)
        print(json.dumps(alertas, ensure_ascii=False, indent=2))
    except (OSError, ValueError) as erro:
        print(f"Falha ao analisar o arquivo: {erro}", file=sys.stderr)
        return 2
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
