# Laboratório de Experimentação 2 - Análise de Qualidade de Sistemas Java

## Descrição

Este projeto tem como objetivo analisar aspectos da qualidade de repositórios desenvolvidos na linguagem Java, correlacionando-os com características do seu processo de desenvolvimento, sob a perspectiva de métricas de produto calculadas através da ferramenta CK.

## Introdução

No processo de desenvolvimento de sistemas open-source, em que diversos desenvolvedores contribuem em partes diferentes do código, um dos riscos a serem gerenciados diz respeito à evolução dos seus atributos de qualidade interna. Isto é, ao se adotar uma abordagem colaborativa, corre-se o risco de tornar vulnerável aspectos como modularidade, manutenibilidade, ou legibilidade do software produzido. Para tanto, diversas abordagens modernas buscam aperfeiçoar tal processo, através da adoção de práticas relacionadas à revisão de código ou à análise estática através de ferramentas de CI/CD.

Neste contexto, o objetivo deste laboratório é analisar aspectos da qualidade de repositórios desenvolvidos na linguagem Java, correlacionando-os com características do seu processo de desenvolvimento, sob a perspectiva de métricas de produto calculadas através da ferramenta CK.

## Metodologia

### 1. Seleção de Repositórios

Com o objetivo de analisar repositórios relevantes, escritos na linguagem estudada, coletaremos os top-1.000 repositórios Java mais populares do GitHub, calculando cada uma das métricas definidas na Seção 3.

### 2. Questões de Pesquisa

Este laboratório tem o objetivo de responder às seguintes questões de pesquisa:

- **RQ 01**: Qual a relação entre a popularidade dos repositórios e as suas características de qualidade?
- **RQ 02**: Qual a relação entre a maturidade do repositórios e as suas características de qualidade?
- **RQ 03**: Qual a relação entre a atividade dos repositórios e as suas características de qualidade?
- **RQ 04**: Qual a relação entre o tamanho dos repositórios e as suas características de qualidade?

### 3. Definição de Métricas

Para cada questão de pesquisa, realizaremos a comparação entre as características do processo de desenvolvimento dos repositórios e os valores obtidos para as métricas definidas nesta seção.

#### Métricas de Processo:
- **Popularidade**: número de estrelas
- **Tamanho**: linhas de código (LOC) e linhas de comentários
- **Atividade**: número de releases
- **Maturidade**: idade (em anos) de cada repositório coletado

#### Métricas de Qualidade:
- **CBO**: Coupling between objects
- **DIT**: Depth Inheritance Tree
- **LCOM**: Lack of Cohesion of Methods

### 4. Coleta e Análise de Dados

Para análise das métricas de popularidade, atividade e maturidade, serão coletadas informações dos repositórios mais populares em Java, utilizando as APIs REST ou GraphQL do GitHub. Para medição dos valores de qualidade, utilizaremos uma ferramenta de análise estática de código (CK).

**Importante**: a ferramenta CK gera diferentes arquivos .csv com os resultados para níveis de análise diferentes. É importante que você sumarize os dados obtidos.

## Ferramentas Utilizadas

- **CK (Chidamber and Kemerer Java Metrics)**: Ferramenta para análise estática de código Java
- **GitHub API**: Para coleta de dados dos repositórios
- **Linguagens/Tecnologias**: Java, Python (para scripts de automação), CSV (para armazenamento de dados)

## Estrutura do Projeto

```
Lab_experimentacao_2/
├── README.md
├── ck-0.7.1-SNAPSHOT-jar-with-dependencies.jar
├── 
```

## Relatório Final

Para cada uma das questões de pesquisa, faça uma sumarização dos dados obtidos através de valores de medida central (mediana, média e desvio padrão), por repositório.

O documento final deve apresentar:
1. **Introdução simples** com hipóteses informais
2. **Metodologia** utilizada para responder às questões de pesquisa
3. **Resultados obtidos** para cada uma das questões
4. **Discussão** sobre o que você esperava como resultado (suas hipóteses) e os valores obtidos

## Processo de Desenvolvimento

### Sprints e Entregas

- **Lab02S01**: Lista dos 1.000 repositórios Java + Script de Automação de clone e Coleta de Métricas + Arquivo .csv com o resultado das medições de 1 repositório (5 pontos)
- **Lab02S02**: Arquivo .csv com o resultado de todas as medições dos 1.000 repositórios + hipóteses (5 pontos)
- **Análise final**: Análise e visualização de dados + elaboração do relatório final (10 pontos)

### Bônus (+1 ponto)

Para melhor analisar a correlação entre os valores obtidos em cada questão de pesquisa, gere gráficos de correlação que permitam visualizar o comportamento dos dados obtidos. Adicionalmente, utilize um teste estatístico que forneça confiança nas análises apresentadas (por exemplo, teste de correlação de Spearman ou de Pearson).

## Cronograma

Para informações sobre prazos e cronograma detalhado, acesse: [Cronograma do Laboratório](https://github.com/joaopauloaramuni/laboratorio-de-experimentacao-de-software/tree/main/CRONOGRAMA)

## Valor Total

**20 pontos** (+ 1 ponto de bônus)

## Contribuição

Este é um projeto acadêmico desenvolvido como parte do curso de Engenharia de Software. Contribuições são bem-vindas através de pull requests.

## Licença

Este projeto é desenvolvido para fins educacionais.

---

**Nota**: Certifique-se de seguir as boas práticas de desenvolvimento e documentar adequadamente todos os scripts e análises realizadas.