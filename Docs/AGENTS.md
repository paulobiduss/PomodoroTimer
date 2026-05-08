# Agent Directives: PomodoroTimer

> [!WARNING]
> Olá, IA Assistente. Se você estiver lendo este repositório, você **DEVE** aderir estritamente a estas diretrizes antes de modificar qualquer código ou responder ao usuário.

## 1. Princípios de Design e Arquitetura (O Vibe-Check)
Qualquer nova funcionalidade adicionada a este projeto deve respeitar:
* **Minimalismo de Atrito:** Código resiliente, sem exageros verbosos. Crie logs descritivos e *fallback* limpos.
* **Composição Modular:** Funções e componentes de UI são construídos independentes (desacoplados). Se for criar um novo widget, coloque-o isolado em `ui/components/`. 
* **Prioridade Narrativa:** A legibilidade humana vem antes da eficiência extrema da máquina. Trate o código como uma história lógica bem documentada.

## 2. Regras de Ouro na Resposta (Mediação Verbal)
* **Explicação Lógica Primeiro:** Nunca cuspa código sem antes explicar a **lógica funcional** (o "porquê" e o "como") da refatoração/criação através de uma narrativa em tópicos ou bullet points.
* **Estrutura Top-Down:** Inicie pela visão de alto nível (arquitetura/conceito) antes de entrar nos detalhes técnicos minúsculos (variáveis e imports).
* **Formatação (Leitura Bionic):** Utilize formatações de destaque (**negrito** nas keywords) para guiar o olhar do usuário durante o texto explicativo.

## 3. Padrões Práticos de Código
* **UI e Core Isolados:** Não deixe as regras de estado cruas habitarem a UI. Injete configurações via classes (como `AppSettings`) e utilize o ecossistema de *Signals/Slots* (`pyqtSignal`) do PyQt6 para enviar eventos inter-telas.
* **Caminho Relativo Robusto para Assets:** Sempre utilize *helpers* ou manipulações compatíveis com `sys._MEIPASS` para encontrar arquivos que residem na pasta `assets/`. O aplicativo final será compilado com PyInstaller (ver `build.bat`).

## 4. Docstring Padrão (Template)
Todo novo script ou módulo centralizado deve ter no cabeçalho o seguinte formato de Programação Literária:

```python
"""
[nome_do_arquivo.py] — [Breve Descrição do Componente]

Objetivo Macro:
    [Qual é o problema real que este script/classe resolve?]

Fluxo Lógico:
    1. Origem: [Quem envia o dado / De onde nasce o gatilho?]
    2. Transformação: [Qual a regra de negócio/renderização aqui executada?]
    3. Destino: [Qual o output ou os sinais emitidos ao final?]
"""
```

## 5. Estado do Reposit?rio (Publica??o)
- Vers?o atual: 1.0.0
- Licen?a: MIT
- Status: P?blico ? qualquer contribui??o externa deve respeitar todas as se??es deste documento.
- Para contribuidores: abra uma Issue antes de submeter um Pull Request com novas features.
