"""Gravação de registros enviados pelo site (avaliações, sugestões) em arquivos JSON.

Cada arquivo guarda uma lista de objetos. Não há banco de dados (SPEC §8): os
registros são lidos depois, à mão, para o relatório do projeto.
"""

import json
import threading
import uuid
from pathlib import Path

# Uma trava só para todos os arquivos: o volume de envios é pequeno, e assim
# duas requisições ao mesmo tempo nunca leem e regravam o mesmo arquivo juntas.
_trava_arquivos = threading.Lock()


def anexar_registro(destino: Path, registro: dict) -> None:
    """Acrescenta `registro` ao fim da lista guardada em `destino`.

    A gravação é atômica: o conteúdo novo vai para um arquivo temporário na
    mesma pasta, que depois substitui o original de uma vez. Se a API cair no
    meio, o arquivo antigo continua inteiro. Um arquivo ausente, vazio ou
    corrompido é tratado como lista vazia.
    """
    destino.parent.mkdir(parents=True, exist_ok=True)

    with _trava_arquivos:
        registros: list[dict] = []
        if destino.exists():
            try:
                conteudo = destino.read_text(encoding="utf-8").strip()
                if conteudo:
                    dados = json.loads(conteudo)
                    if isinstance(dados, list):
                        registros = dados
            except (json.JSONDecodeError, OSError):
                registros = []

        registros.append(registro)

        caminho_temporario = destino.with_name(f"{destino.name}.{uuid.uuid4().hex}.tmp")
        try:
            with caminho_temporario.open("w", encoding="utf-8") as arquivo:
                json.dump(registros, arquivo, ensure_ascii=False, indent=2)
            caminho_temporario.replace(destino)
        finally:
            if caminho_temporario.exists():
                try:
                    caminho_temporario.unlink()
                except OSError:
                    pass
