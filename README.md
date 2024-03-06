# tailor-infra

API da TAIL-OR para análises preditiva e prescritiva.

## Apresentação

Este documento apresenta um tutorial de como utilizar a API que se comunica com os modelos preditivo e prescritivo desenvolvidos para a aplicação TAIL-OR. Em sua versão final, todos esses passos estarão embutidos na aplicação por meio da interface com o usuário.

## Rodando a aplicação

1) Rode ```pip3 install -r requirements.txt``` para baixar os requisitos.

2) Rode ```python3 app.py``` para levantar o servidor.

A aplicação em funcionamento deve imprimir as seguintes mensagens no terminal:

![Print de tela de aplicação em funcionamento](https://github.com/TAIL-OR/tailor-infra/blob/main/figures/app.png?raw=true "Aplicação em funcionamento")

Veja que o caminho para a porta de execução do aplicativo está destacado em vermelho.

Obs.: Recomendamos a utilização de Linux para executar a API.

### Rodando o modelo prescritivo

Para rodar o modelo prescritivo, além de ter a aplicação rodando, é necessário fazer uma requisição com envio de parâmetros. Uma boa interface para essa tarefa é o aplicativo Postman, disponível na loja de aplicativos do Linux.

![Ícone do aplicativo Postman](https://github.com/TAIL-OR/tailor-infra/blob/main/figures/postman_logo.svg?raw=true "Aplicativo Postman")

1) Baixe o Postman.

2) Abra o aplicativo.

3) Com a aplicação rodando, copie o caminho para a porta de execução no campo "Enter URL or paste text" e acrescente, ao final, a rota "/prescriptive". Por exemplo, para o caminho "http://127.0.0.1:8080", a rota final será "http://127.0.0.1:8080/prescriptive".

4) Do lado esquerdo desse campo, selecione o método POST.

5) Abaixo desse campo, selecione a seção "Body".

6) Selecione a opção "raw" e o tipo de arquivo "JSON".

7) Agora, para simular diferentes parâmetros no modelo de prescrição, copie e cole o seguinte JSON na caixa de texto, alterando os valores de: "demand" para modificar a demanda por leitos; "equipment_rates" para modificar a proporção necessária de oxímetros, de ECGs e de ventiladores por leito, respectivamente; "staff_rates" para modificar a proporção necessária de técnicos de enfermagem, de enfermeiros e de médicos por leito, respectivamente; e "consumable_rates" para modificar a proporção necessária de Atracúrio, Midazolam e Rocurônio por leito, respectivamente. Para utilizar as proporções padrão, substitua os valores por "null". No caso da demanda, será utilizada a demanda prevista pelo modelo preditivo para o próximo mês.

```json
{
    "demand": 65,
    "equipment_rates": {"0": 1, "1": 1, "2": 1},
    "staff_rates": {"0": 0.5, "1": 0.1, "2": 0.1},
    "consumable_rates": {"0": 630, "1": 180, "2": 180}
}
```

8) Aperte em "Send" e aguarde o envio da resposta.

![Print de tela do aplicativo Postman após envio da resposta](https://github.com/TAIL-OR/tailor-infra/blob/main/figures/postman_response.png?raw=true "Envio da resposta no Postman")

9) Copie e cole o conteúdo do campo de resposta ("Response") em um arquivo de texto e o salve em HTML (por exemplo, "output.html").

10) Abra o arquivo para acessar a solução prescrita.

![Print de tela do HTML gerado pelo modelo prescritivo](https://github.com/TAIL-OR/tailor-infra/blob/main/figures/output.png?raw=true "HTML gerado pelo modelo prescritivo")

