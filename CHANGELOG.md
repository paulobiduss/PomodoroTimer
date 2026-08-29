# Changelog

Todas as mudanças notáveis neste projeto serão documentadas aqui.
Formato baseado em [Keep a Changelog](https://keepachangelog.com/pt-BR/1.0.0/).

## [Não publicado]

### Alterado
- Som de notificação refeito: antes era um tom único de 440 Hz em volume máximo
  (0 dBFS) com ataque instantâneo, que soava alto e assustava. Agora é um sino
  suave de duas notas descendentes (E5 → C5), com ataque gradual, decaimento
  exponencial e pico em -10 dBFS (cerca de 20 dB mais baixo em volume médio).
- Novo script `tools/generate_notify_sound.py` que gera o `assets/notify.wav`,
  permitindo ajustar volume, notas e envelope sem editor de áudio.

## [1.0.1] — 2026-07-18

### Corrigido
- App fechava imediatamente no macOS por causa do `import winsound` (módulo
  exclusivo do Windows). O som de notificação agora é multiplataforma
  (winsound no Windows, `afplay` no macOS, `paplay`/`aplay` no Linux).

### Adicionado
- Assinatura ad-hoc do `.app` no workflow de release, evitando que o macOS
  (Apple Silicon) mate o app por assinatura inválida.

## [1.0.0] — 2026-05-08

### Adicionado
- Plano de sessões finito configurável
- Overlay de conclusão com relógio em tela cheia
- Ícones SVG profissionais via IconFactory
- System tray com ações rápidas
- Persistência de configurações com QSettings
- Arquitetura modular (`core/`, `ui/windows/`, `ui/components/`)
- Resolvedor de assets para dev e build PyInstaller (`core/assets.py`)
