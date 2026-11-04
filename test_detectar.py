import io
import unittest
from pathlib import Path
from detectar import analisar, carregar


class Deteccao(unittest.TestCase):
    def test_ordem_e_evidencia(self):
        with Path(__file__).with_name("demo.jsonl").open() as entrada:
            achados = analisar(carregar(entrada), 30, 2, 3)
        self.assertEqual([a["linhas"] for a in achados], [[2, 3], [2, 3, 1]])

    def test_expiracao(self):
        with Path(__file__).with_name("demo.jsonl").open() as entrada:
            self.assertEqual(analisar(carregar(entrada), 9, 2, 3), [])

    def test_fuso_obrigatorio(self):
        with self.assertRaisesRegex(ValueError, "Linha 1"):
            carregar(io.StringIO('{"hora":"2026-01-01T00:00:01"}'))

    def test_varias_contas_na_mesma_origem(self):
        import json
        linhas = []
        for numero, (origem, conta) in enumerate([("a","um"),("b","dois"),("a","dois"),("a","tres")]):
            linhas.append(json.dumps({"hora":f"2026-01-01T00:00:0{numero}Z",
                                      "origem":origem,"conta":conta,"resultado":"falha"}))
        alertas = analisar(carregar(io.StringIO("\n".join(linhas))), 60, 9, 3)
        self.assertEqual([(a["tipo"], a["linhas"]) for a in alertas], [("várias contas", [1,3,4])])
