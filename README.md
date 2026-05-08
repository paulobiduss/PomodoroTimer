# PomodoroTimer

> Aplicativo desktop Pomodoro em PyQt6 com plano de sess?es finito, overlay imersivo e execu??o em bandeja do sistema.

![screenshot](assets/screenshot.png)

## Funcionalidades

- Timer com progresso circular e contagem regressiva em tempo real
- Plano de sess?es finito configur?vel (foco, pausa curta e pausa longa opcional)
- Encerramento gracioso do ciclo com estado de conclus?o
- Overlay fullscreen para transi??es de bloco e conclus?o do plano
- Overlay de conclus?o com resumo de foco do dia e a??o de novo plano
- System tray com a??es r?pidas (mostrar, pausar/retomar, pular, sair)
- Persist?ncia de configura??es e hist?rico di?rio com QSettings
- ?cones SVG program?ticos via `IconFactory` para consist?ncia visual
- Arquitetura modular em `core/`, `ui/windows/` e `ui/components/`

## Pr?-requisitos

- Windows 10 ou superior
- Python 3.11+
- Pip

## Instala??o e execu??o (modo desenvolvimento)

```bash
git clone https://github.com/seu-usuario/PomodoroTimer.git
cd PomodoroTimer
pip install -r requirements.txt
python main.py
```

## Gerar o execut?vel (.exe)

```bash
build.bat
```

O execut?vel ser? gerado em `dist/PomodoroTimer/`.

## Estrutura do projeto

```text
pomodoro/
??? main.py
??? requirements.txt
??? build.bat
??? README.md
??? PomodoroTimer.spec
??? .gitignore
??? LICENSE
??? assets/
?   ??? icon.png
?   ??? notify.wav
??? core/
?   ??? assets.py
?   ??? constants.py
?   ??? icon_factory.py
?   ??? session_plan.py
?   ??? settings.py
??? ui/
?   ??? tray.py
?   ??? components/
?   ?   ??? circular_progress.py
?   ?   ??? title_bar.py
?   ??? windows/
?       ??? overlay_window.py
?       ??? timer_window.py
??? Docs/
    ??? AGENTS.md
    ??? memoria_projeto.md
```

## Arquitetura

- `main.py`: composi??o de depend?ncias, wiring de sinais e ciclo de vida do app
- `core/session_plan.py`: fonte de verdade da sequ?ncia finita de blocos
- `core/settings.py`: persist?ncia de prefer?ncias e hist?rico do usu?rio
- `core/icon_factory.py`: gera??o de ?cones SVG em runtime
- `core/assets.py`: resolu??o de caminhos de assets para dev e PyInstaller
- `ui/windows/timer_window.py`: janela principal e intera??o do plano com a UI
- `ui/windows/overlay_window.py`: overlays de transi??o e conclus?o
- `ui/tray.py`: integra??o com bandeja do sistema

## Roadmap

Extra?do de `Docs/memoria_projeto.md`:

- [ ] Implementar estat?sticas de longo prazo de sess?es (relat?rios em SQLite ou JSON robusto)
- [ ] Explorar customiza??o mais aprofundada de themes ou modos de notifica??o silenciosa
- [ ] Avaliar integra??o futura com lista simples de To-Do conectada aos ciclos

## Licen?a

Distribu?do sob a licen?a MIT. Veja `LICENSE` para mais informa??es.
