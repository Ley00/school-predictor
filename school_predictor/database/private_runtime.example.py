"""
Arquivo de referência para a camada privada local.

Copie este arquivo para:
    school_predictor/database/private_runtime.py

Esse arquivo local deve permanecer fora do Git e concentrar:
1. a preparação local dos insumos usados na versão pública
2. a extração dos CSVs e a geração de dados falsos compatíveis com o contrato público

O repositório público mantém apenas os wrappers e o contrato das entradas.
"""


def prepare_private_database(user: str = "Warley", source_database: str | None = None) -> str:
    raise NotImplementedError(
        "Implemente aqui a rotina local de preparação dos insumos e geração dos dados falsos usados pela versão pública."
    )


def extract_private_school_data(
    session,
    project_root=".",
    student_name=None,
    academic_period=None,
    specific=False,
):
    raise NotImplementedError(
        "Implemente aqui a extração local de CSVs e a geração dos registros artificiais necessários para a versão pública."
    )
