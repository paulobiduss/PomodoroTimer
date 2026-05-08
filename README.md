# PomodoroTimer
Feito com IA, Codex e Claude.
Claude para melhorar o prompt.
Codex para codigo. 

> Aplicativo desktop Pomodoro em PyQt6 com plano de sessões finito, overlay imersivo e execução em bandeja do sistema.

## Funcionalidades

- Timer com progresso circular e contagem regressiva em tempo real
- Plano de sessões finito configurável (foco, pausa curta e pausa longa opcional)
- Encerramento gracioso do ciclo com estado de conclusão
- Overlay fullscreen para transições de bloco e conclusão do plano
- Overlay de conclusão com resumo de foco do dia e ação de novo plano
- System tray com ações rápidas (mostrar, pausar/retomar, pular, sair)
- Persistência de configurações e histórico diário com QSettings
- Ícones SVG programáticos via `IconFactory` para consistência visual
- Arquitetura modular em `core/`, `ui/windows/` e `ui/components/`

## Pré-requisitos

- Windows 10 ou superior
- Python 3.11+
- Pip

## Instalação e execução (modo desenvolvimento)

```bash
git clone https://github.com/seu-usuario/PomodoroTimer.git
cd PomodoroTimer
pip install -r requirements.txt
python main.py
```

## Gerar o executável (.exe)

```bash
build.bat
```

O executável será gerado em `dist/PomodoroTimer/`.

## Estrutura do projeto

```text
pomodoro/
- main.py
- requirements.txt
- build.bat
- README.md
- PomodoroTimer.spec
- .gitignore
- LICENSE
- assets/
  - icon.png
  - notify.wav
- core/
  - assets.py
  - constants.py
  - icon_factory.py
  - session_plan.py
  - settings.py
- ui/
  - tray.py
  - components/
    - circular_progress.py
    - title_bar.py
  - windows/
    - overlay_window.py
    - timer_window.py
- Docs/
  - AGENTS.md
  - memoria_projeto.md
```

## Arquitetura

- `main.py`: composição de dependências, wiring de sinais e ciclo de vida do app
- `core/session_plan.py`: fonte de verdade da sequência finita de blocos
- `core/settings.py`: persistência de preferências e histórico do usuário
- `core/icon_factory.py`: geração de ícones SVG em runtime
- `core/assets.py`: resolução de caminhos de assets para dev e PyInstaller
- `ui/windows/timer_window.py`: janela principal e interação do plano com a UI
- `ui/windows/overlay_window.py`: overlays de transição e conclusão
- `ui/tray.py`: integração com bandeja do sistema

## Roadmap

Extraído de `Docs/memoria_projeto.md`:

- [ ] Implementar estatísticas de longo prazo de sessões (relatórios em SQLite ou JSON robusto)
- [ ] Explorar customização mais aprofundada de themes ou modos de notificação silenciosa
- [ ] Avaliar integração futura com lista simples de To-Do conectada aos ciclos

## Licença

Distribuído sob a licença MIT. Veja `LICENSE` para mais informações.
