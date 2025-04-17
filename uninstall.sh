#!/bin/bash -e

# Determine the operating system
OS=$(uname -s)

# Function to display an error message and exit
error_exit() {
  echo "Error: $1" >&2
  exit 1
}

if [[ "$OS" == "Linux" ]]; then
  if [[ "$(id -u)" -ne 0 ]]; then
    error_exit "This script must be run as root on Linux."
  fi

  # remove symlink
  rm -f /usr/local/bin/dindo-bot

  # remove desktop files
  rm -f /usr/share/applications/dindo-bot.desktop
  rm -f /usr/share/applications/dindo-bot-dev.desktop

  # remove icons
  rm -f /usr/share/icons/hicolor/128x128/apps/dindo-bot.png
elif [[ "$OS" == "MINGW"* || "$OS" == "CYGWIN"* ]]; then
    echo "Uninstallation on Windows is currently a manual process."
    echo "Please manually delete the application directory and any created shortcuts."
else
  error_exit "Unsupported operating system: $OS"
fi
