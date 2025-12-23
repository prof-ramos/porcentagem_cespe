# Diretrizes do Repositório

## Estrutura do Projeto e Organização de Módulos
Este repositório é focado em dados. Os arquivos principais ficam na raiz e são planilhas `.xlsx` (ex.: `AFO.xlsx`, `Etica.xlsx`, `DireitoAdm.xlsx`). Há um diretório `direito_administrativo/`, atualmente vazio. Não há código-fonte, testes automatizados ou scripts complexos neste momento.

## Comandos de Build, Teste e Desenvolvimento
Não existem comandos de build/teste registrados. Para inspecionar o conteúdo, abra as planilhas no Excel/LibreOffice ou utilize uma ferramenta de análise de dados.

## Estilo de Código e Convenções de Nomenclatura
- **Formato de Arquivo**: Arquivos de dados devem permanecer em `.xlsx`.
- **Nomenclatura**: Utilize nomes curtos, **sem espaços e sem acentos (apenas caracteres ASCII)**, alinhados ao tema do arquivo (ex.: `DireitoConstitucional.xlsx` em vez de `Direito Constitucional.xlsx`).
- **Histórico**: Evite renomear arquivos existentes sem necessidade, pois isso dificulta o rastreamento do histórico.

## Diretrizes de Teste
Não há suíte de testes automatizada. A validação deve ser manual:
- Abra a planilha e verifique se as abas e colunas esperadas existem.
- Confirme que os dados não foram truncados ou deslocados.
- Se fizer edições em lote, compare amostras antes e depois.

## Diretrizes de Commit e Pull Request
O histórico deve ser limpo e descritivo. Sugestões:
- Commits curtos e objetivos (ex.: "Atualiza AFO.xlsx com novas questões").
- Em PRs, descreva o motivo das alterações e liste os arquivos afetados.
- **Evidências de Validação**: Inclua provas concretas de que os dados estão corretos, tais como:
    - Capturas de tela (screenshots) das planilhas abertas.
    - Diffs de commit mostrando as linhas alteradas.
    - Comparações de amostras de linhas (antes vs. depois).
    - Breve descrição dos passos de validação realizados (ex.: "Abri no Excel, filtrei pela coluna X e conferi o total").

## Integridade de Dados e Segurança
Não inclua dados sensíveis (PII) nas planilhas. Caso precise compartilhar exemplos, use dados anonimizados ou sintéticos.
