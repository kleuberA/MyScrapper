import json
from deepdiff import DeepDiff
from datetime import datetime

# Função para carregar o conteúdo de um arquivo JSON
def carregar_json(arquivo):
    with open(arquivo, 'r', encoding='utf-8') as f:
        return json.load(f)

# Função para gerar um relatório detalhado das modificações
def gerar_relatorio(diferencas):
    # Obter a data atual
    data_atual = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

    # Relatório base com data e resumo das diferenças
    relatorio = {
        "data": data_atual,
        "resumo": "Relatório de diferenças entre os arquivos JSON",
        "diferencas": diferencas,
        "detalhes": []
    }

    # Detalhamento das modificações
    if 'values_changed' in diferencas:
        for chave, diff in diferencas['values_changed'].items():
            detalhe = {
                "chave": chave,
                "valor_antigo": diff['old_value'],
                "valor_novo": diff['new_value']
            }
            relatorio["detalhes"].append(detalhe)

    if 'dictionary_item_added' in diferencas:
        for chave in diferencas['dictionary_item_added']:
            detalhe = {
                "chave": chave,
                "modificacao": "Adicionado",
                "valor": diferencas['dictionary_item_added'][chave]
            }
            relatorio["detalhes"].append(detalhe)

    if 'dictionary_item_removed' in diferencas:
        for chave in diferencas['dictionary_item_removed']:
            detalhe = {
                "chave": chave,
                "modificacao": "Removido",
                "valor": diferencas['dictionary_item_removed'][chave]
            }
            relatorio["detalhes"].append(detalhe)

    return relatorio

# Carregar os dois arquivos JSON
arquivo_json_1 = './Constituicao/constituicao-dados.json'
arquivo_json_2 = './Constituicao/constituicao-dados-teste.json'

dados_json_1 = carregar_json(arquivo_json_1)
dados_json_2 = carregar_json(arquivo_json_2)

# Comparar os dois arquivos JSON
diferencas = DeepDiff(dados_json_1, dados_json_2, ignore_order=True)

# Gerar o relatório detalhado das modificações
relatorio_modificacoes = gerar_relatorio(diferencas)

# Salvar o relatório em um novo arquivo JSON
relatorio_arquivo = './Constituicao/relatorio_modificacoes.json'
with open(relatorio_arquivo, 'w', encoding='utf-8') as f:
    json.dump(relatorio_modificacoes, f, ensure_ascii=False, indent=4)

print(f"Relatório gerado com sucesso: {relatorio_arquivo}")
