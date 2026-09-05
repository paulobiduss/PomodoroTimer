# Changelog

Todas as mudanças notáveis neste projeto serão documentadas aqui.
Formato baseado em [Keep a Changelog](https://keepachangelog.com/pt-BR/1.0.0/).

## [Não lançado]

### Alterado
- Build do Windows agora embute metadados de versão (`version_info.txt`) no
  `.exe` (nome do produto, empresa, descrição) e desativa a compressão UPX
  (`--noupx`), reduzindo falsos positivos comuns de antivírus em executáveis
  gerados por PyInstaller.
- `version_info.txt` passou a ser gerado dinamicamente a partir da tag do
  release (`tools/render_version_info.py`) no job `build-windows`, evitando
  que o `FileVersion` do `.exe` fique dessincronizado da versão publicada
  (aconteceu no teste do v1.0.3: o `.exe` saiu com `FileVersion 1.0.2.0`
  porque o arquivo era mantido manualmente).
- O release no GitHub Actions passou a publicar um arquivo `.sha256` junto de
  cada pacote (Windows e macOS), para o usuário verificar a integridade do
  download.
- README ampliado com instruções passo a passo de como abrir o app com
  segurança no Windows (SmartScreen) e no macOS (Gatekeeper/quarentena), já
  que o projeto não possui certificado de assinatura de código pago.

## [1.0.2] — 2026-08-29

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
