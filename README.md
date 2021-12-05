# Modelo de memoria episódica para assistentes robóticos

## Sobre

Trabalho de conclusão de curso 

Departamento de Engenharia Mecatrônica

Escola Politécnica da USP

Autores:
- Felipe Sinyee Tsai
- Jiahao Zhao

Orientador: Professor Dr. Marcos Ribeiro Pereira Barretto

Ano 2021

Esse trabalho tem como objetivo desenvolver um módulo de memória episódica em um assistente virtual robótico capaz de aprender as preferências de restaurantes de um indivíduo e sugerí-los. O trabalho consiste do desenvolvimento da arquitetura do módulo e a sua implementação.


## Implementação do modelo

O módulo pode ser analisado em duas partes:
- Captura e Inserção das Memórias
- Requisição das Memórias

## Banco de dados

Para esse trabalho foi utilizado um banco de dados orientado a grafos. O banco escolhido foi o [GraphDB](https://graphdb.ontotext.com/documentation/free/), que possui uma versão paga e uma grátis.

A url de acesso ao banco de dados está localizado em `Constraint.py` na variável `DB_Url`. 



## Módulos

O modelo possui 12 módulos:
- *Assistant*
- *TakePicture*
- *GetCoordinates* (Simulação)
- *RecognizeFace*
- *RecognizePerson*
- *RecognizeEmotion*
- *CreateAtimo*
- *InsertAtimo*
- *GetIntention* (Simulação)
- *RequestMemory* 
- *SelectMemory* 
- *SendResponse* (Simulação)

O primeiro módulo *Assistant* é responsável pela comunicação entre os outros módulos.

Os próximos sete (*TakePicture* até *InsertAtimo*) são responsáveis pela Captura e Inserção das Memórias.

Já os quatro últimos (*GetIntention* até *SendResponse*) são responsáveis pela Requisição das Memórias

Cada um dos módulos esta em um arquivo diferente e precisa de um terminal único para rodar.


## Funcionamento

### Captura e Inserção das Memórias

Após acionar os módulos responsáveis por essa parte (*Assistant* a *InsertAtimo*) o módulo *TakePicture* abrirá a câmera do computador.

Para tirar uma foto basta apertar `space`. Após tirar a foto, ela será enviada ao *Assistant* e posteriormente aos próximos módulos.

Após o término de um átimo ele será inserido no banco

### Requisição das Memórias

Acionar os módulos responsáveis (*Assistant*, *GetIntention* a *SendResponse*).

Pedir solicitação através do terminal no módulo *GetIntention*. 

Uma lista de restaurantes será requisitado do banco. Em seguida selecionado e apresentado ao usuário.
