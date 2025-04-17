#!/bin/bash

# Check the operating system
OS=$(uname -s)

if [[ "$OS" == "Linux" ]]; then
  # Linux installation
  echo "Installing on Linux..."

  # Root detection
  if [ "$(id -u)" != "0" ]; then
    echo "This script must be run as root" 2>&1
    exit 1
  fi

  # Run uninstall script first
  sh uninstall.sh

  # Package manager detection
  APT_CMD=$(which apt)
  PACMAN_CMD=$(which pacman)

  # Python version detection
  PYTHON_VER="3"

  # Install dependencies
  if [[ ! -z $APT_CMD ]]; then
    if [ $PYTHON_VER -eq 3 ]; then
      sudo apt -y install python3-gi gir1.2-gtk-3.0 gir1.2-wnck-3.0 python3-xlib python3-pil scrot
    else
      sudo apt -y install python-gi gir1.2-gtk-3.0 gir1.2-wnck-3.0 python-xlib python-pil scrot
    fi
  elif [[ ! -z $PACMAN_CMD ]]; then
    sudo pacman -S python-gobject gtk3 libwnck3 python-xlib python-pillow scrot
  else
    echo "error can't install dependencies"
    exit 1
  fi

  # Get script path
  SCRIPT_PATH="$( cd "$(dirname "$0")" >/dev/null 2>&1 ; pwd -P )"

  # Create symlink
  ln -s $SCRIPT_PATH/bot.py /usr/local/bin/dindo-bot
  chmod 755 /usr/local/bin/dindo-bot

  # Copy & update desktop files
  cp dindo-bot.desktop /usr/share/applications/dindo-bot.desktop
  sed -i 's/^Exec=.*$/Exec=dindo-bot/g' /usr/share/applications/dindo-bot.desktop
  chmod 755 /usr/share/applications/dindo-bot.desktop

  cp dindo-bot-dev.desktop /usr/share/applications/dindo-bot-dev.desktop
  sed -i 's/^Exec=.*$/Exec=dindo-bot --dev/g' /usr/share/applications/dindo-bot-dev.desktop
  chmod 755 /usr/share/applications/dindo-bot-dev.desktop

  # Copy icons
  cp icons/logo.png /usr/share/icons/hicolor/128x128/apps/dindo-bot.png
  chmod 644 /usr/share/icons/hicolor/128x128/apps/dindo-bot.png

  # Refresh icons cache
  gtk-update-icon-cache
elif [[ "$OS" == "MINGW64_NT-10.0-19045" || "$OS" == "Windows" ]]; then
  # Windows installation
  echo "Installing on Windows..."

  # Check if Python 3 and pip are installed
  if ! command -v python3 &> /dev/null; then
    echo "Python 3 is not installed. Please install it and ensure it's in your PATH."
    exit 1
  fi

  if ! command -v pip3 &> /dev/null; then
    echo "pip3 is not installed. Please install it."
    exit 1
  fi

  # Install Python dependencies using pip
  pip3 install -r dependencies.txt
  echo "Dependencies installed."
  echo "Please run bot.py to start the application"
else
  echo "Unsupported operating system: $OS"
  exit 1
fi
