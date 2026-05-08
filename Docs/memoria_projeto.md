# Memória do Projeto: PomodoroTimer

## 1. Visão Geral
O **PomodoroTimer** é um aplicativo desktop escrito em Python utilizando PyQt6. Ele fornece um cronômetro produtivo com tempos configuráveis, progressão visual animada (com renderização crua usando *QPainter*) e um modo imersivo (fullscreen overlay) ao término de cada ciclo de foco ou descanso.

## 2. Histórico de Modificações e Evolução
- **Versão Inicial (Monolítica)**: O aplicativo possuía a lógica quase inteiramente acoplada. As regras de negócio, timers, temas e desenho de interface estavam acumuladas principalmente em arquivos extensos como `timer_window.py`.
- **Refatoração Modular (Maio/2026)**: O projeto foi desmembrado para elevar a coesão e facilitar a manutenção. A arquitetura foi reestruturada de modo a separar claramente a UI das lógicas e estados essenciais.

## 3. Arquitetura Atual e Organização
* `main.py`: Entry point e orquestrador do ciclo de vida da aplicação. Instancia as dependências e amarra os sinais (Signals/Slots).
* **`/core/`**: Lógicas de backend.
  * `constants.py`: Estados do timer (`STATE_FOCUS`, etc) e suas cores.
  * `settings.py`: Persistência de dados locais do usuário com *QSettings*.
* **`/ui/`**: Tudo relacionado à interface.
  * `tray.py`: Lógica do ícone e menu de bandeja do sistema.
  * **`/windows/`**: Telas completas que agrupam widgets maiores.
    * `timer_window.py`: Janela principal com os controles e timer.
    * `overlay_window.py`: Tela cheia com fundo translúcido para notificações visuais potentes.
  * **`/components/`**: Peças atômicas customizadas.
    * `circular_progress.py`: O arco circular e os labels de tempo.
    * `title_bar.py`: Cabeçalho "drag-to-move" das janelas *frameless*.
* **`/assets/`**: Ícones (`icon.png`) e sons (`notify.wav`).

## 4. Próximos Passos Previstos (To-Do Geral)
- [ ] Implementar estatísticas de longo prazo de sessões (relatórios em SQLite ou JSON robusto).
- [ ] Explorar customização mais aprofundada de *Themes* ou modos de notificação silenciosa.
- [ ] Avaliar uma integração futura com uma lista simples de *To-Do* a ser conectada com cada ciclo.

## 5. Histórico de Correções — 07/05/2026

### Bug 1 — Travamento ao mover janela
- **Causa raiz identificada:** lógica de arraste no `DraggableTitleBar` com checagem frágil de botão (`event.buttons() == LeftButton`), suscetível a comportamento inconsistente com flags de mouse no Qt durante o movimento.
- **Correção aplicada:**
  - Ajuste para checagem por bitmask: `event.buttons() & Qt.LeftButton`.
  - `mouseMoveEvent` mantido leve, apenas com cálculo do deslocamento e chamada de `self.window().move(...)`.
  - Reset de `_drag_pos` preservado no `mouseReleaseEvent`.
- **Arquivo alterado:** `ui/components/title_bar.py`

### Bug 2 — Incremento de tempo (+/-) não funcionava
- **Causa raiz identificada:** configuração dependia do comportamento implícito do `QSpinBox` para incremento, sem fluxo explícito de botões dedicados via sinais/slots.
- **Correção aplicada:**
  - Adição de botões dedicados `-` e `+` para **Foco (min)**.
  - Criação de slots explícitos de incremento/decremento com clamp por `minimum()/maximum()`.
  - Política mantida: mudanças durante timer em execução afetam a **próxima sessão**.
- **Arquivo alterado:** `ui/windows/timer_window.py`

### Ajustes adicionais solicitados após validação
- **Warning de geometria no Windows (`QWindowsWindow::setGeometry`):**
  - Causa: conflito entre restrição de `maximumHeight` e altura real necessária do layout.
  - Correção: remoção do limite rígido `setMaximumHeight(700)` na janela principal.
- **Layout de botões dos campos numéricos:**
  - Remoção visual de setas internas dos `QSpinBox` (`NoButtons`) para manter somente os botões externos `+/-`.
  - Inclusão de botões `+/-` também para **Repouso curto (min)**.
- **Persistência modular de repouso curto:**
  - `short_break_minutes` passou a ter getter/setter persistidos em `AppSettings` com fallback compatível para usuários antigos sem chave salva.
- **Arquivos alterados:**
  - `ui/windows/timer_window.py`
  - `core/settings.py`

### Validação técnica registrada
- Compilação de sintaxe sem erros via `python -m py_compile` nos módulos alterados.
- Inicialização via `python main.py` realizada (processo GUI ativo em loop de eventos, sem erro imediato de startup).


## 6. Feature Nova ? Plano Finito de Sess?es (08/05/2026)

### Objetivo funcional
- Permitir que o usu?rio configure um ciclo finito com:
  - quantidade de focos,
  - dura??o de foco,
  - dura??o de pausa curta,
  - pausa longa opcional e dura??o.
- Encerrar o ciclo de forma graciosa ao final, sem rein?cio autom?tico.

### Mudan?as de arquitetura
- **Core como fonte de verdade**:
  - `SessionPlan` concentra toda a regra de sequ?ncia de blocos.
  - `TimerWindow` deixa de decidir o pr?ximo estado diretamente e passa a consumir o bloco atual do plano.
- **Inje??o de depend?ncia em `main.py`**:
  - O plano ? instanciado no entry point e injetado na janela principal.
  - O rebuild de plano ocorre por sinais, mantendo desacoplamento entre m?dulos.
- **Estados e persist?ncia**:
  - Inclus?o de `STATE_COMPLETED` e manuten??o de `STATE_LONG_BREAK` para pausa longa final.
  - Persist?ncia no `AppSettings` para: `focus_count`, `break_duration`, `long_break_enabled`, `long_break_duration`.

### Atualiza??o da arquitetura (complemento)
- **`/core/`**:
  - `session_plan.py`: orquestrador do plano finito e emissor de `plan_finished`.
- **`/ui/windows/`**:
  - `timer_window.py`: consome blocos do `SessionPlan`, exibe progresso linear do plano e estado textual (sess?o/pausa).
  - `overlay_window.py`: mant?m overlay de transi??o e adiciona modo de conclus?o com ?Novo Plano? e ?Fechar?.
- **`main.py`**:
  - centraliza inje??o do plano e conex?es de sinais de ciclo/conclus?o.

### Fluxo de sinais (desacoplamento)
- `session_finished` (TimerWindow) ? overlay de transi??o.
- `plan_finished` (SessionPlan) ? `TimerWindow.on_plan_finished` + overlay de conclus?o.
- `new_plan_clicked` (overlay de conclus?o) ? reconstru??o/inje??o de novo plano no `main.py`.

### Comportamento funcional final
- Fluxo de execu??o segue o plano definido pelo usu?rio (foco/pausas).
- Ao concluir todos os blocos:
  - timer para,
  - controles de execu??o ficam desabilitados,
  - label de estado indica plano conclu?do,
  - overlay final mostra resumo de foco acumulado do dia.
- O ciclo s? volta a iniciar por a??o expl?cita em **Novo Plano**.

### Limita??o observada (n?o corrigida)
- H? mistura de encoding legada em partes do projeto/documenta??o (acentua??o inconsistente em alguns ambientes/terminais). O ponto foi registrado e n?o corrigido nesta etapa por n?o ser escopo da feature.

## 7. Status de Publicacao
- Reposit?rio p?blico no GitHub: [ ] (usu?rio deve preencher a URL)
- Vers?o publicada: 1.0.0
- Execut?vel dispon?vel em Releases: [ ] (fazer upload manual do .exe)
