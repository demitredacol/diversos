#Copyright (C) 2025 - Demitre Da Col

#Este programa é de software livre; você pode redistribuí-lo e/ou
#modificá-lo sob os termos da Licença Pública Geral GNU
#como publicada pela Free Software Foundation; seja a versão 3
#da licença, ou (a seu critério) qualquer versão posterior.

#Este programa é distribuído na esperança de que seja útil,
#mas SEM NENHUMA GARANTIA; sem sequer a garantia implícita de
#COMERCIALIZAÇÃO ou ADEQUAÇÃO A UMA FINALIDADE ESPECÍFICA.
#Veja a Licença Pública Geral GNU para mais detalhes.

#Você deve ter recebido uma cópia da Licença Pública Geral GNU
#junto com este programa; se não, veja <http://www.gnu.org/licenses/>.


# Programa construído por Demitre Da Col 
# https://www.linkedin.com/in/demitredacol/

from pathlib import Path
import xml.etree.ElementTree as ET

##########################################################################################
def anonimiza_textos(item_xml, lista_subitens, dicionario):
    for sub_item in lista_subitens:
        #campo = item_xml.find(f'nfe:{sub_item}', espaco_nomes)
        campo = item_xml.find(f'{sub_item}')
        if campo is not None:
            campo.text = dicionario[sub_item]

def ler_xml_sem_namespace(arvore_xml, caminho_xml):
    # Faz o parse do XML    
    raix_xml = arvore_xml.getroot()
    
    # Remove os namespaces das tags
    for elem in raix_xml.iter():
        if '}' in elem.tag:
            elem.tag = elem.tag.split('}', 1)[1]  # Remove namespace da tag
        # Remove também namespaces de atributos, se houver
        elem.attrib = {k.split('}', 1)[-1] if '}' in k else k: v for k, v in elem.attrib.items()}

    return raix_xml            

##########################################################################################
caminho_origem  = "PASTA_ORIGEM_ARQUIVOS"
caminho_destino = "PASTA_DESTINO_ARQUIVOS"
espaco_nomes = {'nfe': 'http://www.portalfiscal.inf.br/nfe'}

dados_destinatario = {
    'xNome' : 'DESTINATARIO ALTERADO', 
    'CNPJ' : '00000000000000', 
    'CPF' : '00000000000', 
    'IE' : '', 
    'email' : 'email@dominio.com.br',
    'xLgr' : 'Rua Central',
    'nro' : '123',
    'email' : 'email@dominio.com.br'
}


##########################################################################################
diretorio_origem = Path(caminho_origem)
arquivos_origem = [f.name for f in diretorio_origem.iterdir() if f.is_file()]

for arquivo in arquivos_origem:
    caminho_arquivo_origem = caminho_origem + arquivo

    arvore_xml = ET.parse(caminho_arquivo_origem)
    raiz_xml = ler_xml_sem_namespace(arvore_xml, caminho_arquivo_origem)

    numero_nota_fiscal = raiz_xml.find('.//ide//nNF').text

    # Dados destinatário
    anonimiza_textos(raiz_xml.find('.//dest', espaco_nomes), ['xNome', 'CNPJ', 'CPF', 'IE', 'email'], dados_destinatario )
    anonimiza_textos(raiz_xml.find('.//dest//enderDest', espaco_nomes), ['xLgr'], dados_destinatario )

    # Itens
    valores = {
        'qCom' : '1.0000',
        'vUnCom' : numero_nota_fiscal[:3] + '.0000' ,
        'qTrib' : '1.0000' ,
        'vUnTrib' : numero_nota_fiscal[:3] + '.0000' ,
        'vDesc' : '' ,        
        'vTotTrib' : numero_nota_fiscal[:3] + '.0000',
        'vBC' : numero_nota_fiscal[:3] + '.0000',        
        'vProd' : numero_nota_fiscal[:3] + '.0000',
        'vNF' : numero_nota_fiscal[:3] + '.0000',

        'pICMS' : '17.0000',
        'vICMS' : '0.0000',
        
        'pPIS' : '1.6500',
        'vPIS' : '0.0000',
        
        'pCOFINS' : '7.6000',
        'vCOFINS' : '0.0000'
    }

    # Itens
    for item_det in raiz_xml.findall('.//det'):
        anonimiza_textos(item_det.find('.//prod'), ['qCom', 'vUnCom', 'qTrib', 'vUnTrib'], valores )

        for campo_valor in ['vBC','pICMS', 'vICMS', 'pPIS', 'vPIS', 'pCOFINS', 'vCOFINS', 'vTotTrib']:
            elementos_campo = item_det.findall(f'.//{campo_valor}')
            novo_valor = valores[campo_valor]

            if elementos_campo is not None:
                for elemento_campo in elementos_campo:
                    elemento_campo.text = novo_valor

    # total
    for item_total in raiz_xml.findall('.//total//ICMSTot'):
        for campo_valor in ['vBC','pICMS', 'vICMS', 'pPIS', 'vPIS', 'pCOFINS', 'vCOFINS', 'vTotTrib', 'vDesc', 'vNF', 'vProd']:
            elementos_campo = item_total.findall(f'.//{campo_valor}')
            novo_valor = valores[campo_valor]

            if elementos_campo is not None:
                for elemento_campo in elementos_campo:
                    elemento_campo.text = novo_valor

    # Grava arquivo saida
    numero_nota_fiscal = f'0000000000{numero_nota_fiscal}'
    numero_nota_fiscal = numero_nota_fiscal[-10:]
    caminho_arquivo_destino = caminho_destino + numero_nota_fiscal + '.xml'

    arvore_xml.write(caminho_arquivo_destino, encoding='utf-8', xml_declaration=False, default_namespace='')