# Autoclicker para Linux (X11)

Um autoclicker simples para Linux, feito em **Python puro**, usando apenas bibliotecas padrão do sistema (`libX11` e `libXtst`).  
Não usa `pip`, não depende de pacotes externos e funciona apenas em ambientes **X11**.

---

## 📌 Requisitos

- Linux rodando **X11**  
  Verifique com:
  ```bash
  echo $XDG_SESSION_TYPE

Deve retornar x11.

## Bibliotecas do sistema:

libX11.so.6

libXtst.so.6

Essas libs já vêm instaladas na maioria das distros baseadas em Ubuntu/Mint.

## ▶️ Como rodar

No terminal, dentro da pasta do projeto:

python3 autoclicker_linux.py

## 🎮 Como usar

F9 → ativa/desativa o autoclicker

F10 → encerra o programa

O autoclick funciona em qualquer janela do sistema.

## 🧱 Estrutura e tecnologias usadas

Python 3

ctypes (biblioteca padrão)

X11 para leitura global de teclado

Xtst para simular eventos de clique do mouse

Obs: Nenhuma instalação adicional é necessária além do Python já presente no sistema.
