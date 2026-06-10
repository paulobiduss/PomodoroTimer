# PomodoroTimer

> Aplicativo desktop Pomodoro em PyQt6 com plano de sessões finito, overlay imersivo, histórico de foco diário e execução em bandeja do sistema.

## Funcionalidades

- Timer com progresso circular e contagem regressiva em tempo real
- Plano de sessões finito configurável (foco, pausa curta e pausa longa opcional)
- Encerramento gracioso do ciclo com estado de conclusão e ação "Novo Plano"
- Overlay fullscreen para transições de bloco e conclusão do plano
- Overlay de conclusão com resumo comparativo de foco (hoje x ontem) e total semanal
- Histórico de foco diário persistido, com migração automática do valor acumulado legado
- System tray com ações rápidas (mostrar, pausar/retomar, pular, sair)
- Persistência de configurações e histórico com QSettings
- Ícones SVG programáticos via `IconFactory` para consistência visual
- Arquitetura modular em `core/`, `ui/windows/` e `ui/components/`

## Pré-requisitos

- Windows 10 ou superior
- Python 3.11+
- Pip

## Instalação e execução (modo desenvolvimento)

```bash
git clone https://github.com/paulobiduss/PomodoroTimer.git
cd PomodoroTimer
pip install -r requirements.txt
python main.py
```

## Testes

```bash
python -m unittest discover tests
```

## Gerar o executável (.exe)

```bash
build.bat
```

O script valida Python/PyInstaller, limpa artefatos antigos fora do Google Drive
e gera dois outputs:

- Executável: `C:\tmp\PomodoroTimer_dist\PomodoroTimer\PomodoroTimer.exe`
- Pacote portátil: `C:\tmp\PomodoroTimer_release\PomodoroTimer-portable.zip`

## Estrutura do projeto

```text
pomodoro/
- main.py
- requirements.txt
- build.bat
- README.md
- CHANGELOG.md
- .gitignore
- LICENSE
- assets/
  - icon.png
  - notify.wav
- core/
  - assets.py
  - constants.py
  - focus_history.py
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
- tests/
  - test_focus_history.py
- Docs/
  - AGENTS.md
  - memoria_projeto.md
```

## Arquitetura

- `main.py`: composição de dependências, wiring de sinais e ciclo de vida do app
- `core/focus_history.py`: histórico diário, comparação com ontem e total semanal de foco
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

## Changelog

Veja [CHANGELOG.md](CHANGELOG.md) para o histórico de versões.

## Licença

Distribuído sob a licença MIT. Veja `LICENSE` para mais informações.
