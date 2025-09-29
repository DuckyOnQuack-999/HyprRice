"""
Package Options Dialog for HyprRice

Provides package management options and installation scripts for different distributions.
Inspired by ML4W Dotfiles and end-4 dots-hyprland patterns.
"""

import os
import sys
from pathlib import Path
from typing import Dict, List, Optional
from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QTabWidget, QWidget,
    QTextEdit, QPushButton, QLabel, QComboBox, QFormLayout,
    QGroupBox, QMessageBox, QScrollArea, QFrame, QSplitter,
    QListWidget, QListWidgetItem, QCheckBox, QSpinBox,
    QLineEdit, QFileDialog, QProgressBar, QTreeWidget,
    QTreeWidgetItem, QHeaderView, QTableWidget, QTableWidgetItem
)
from PyQt6.QtCore import Qt, pyqtSignal, QThread, pyqtSlot, QTimer
from PyQt6.QtGui import QFont, QPalette, QColor, QIcon, QPixmap
import logging


class PackageOptionsDialog(QDialog):
    """Dialog for displaying package management options and installation scripts."""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("HyprRice Package Options")
        self.setMinimumSize(900, 700)
        self.resize(1200, 800)
        
        self.logger = logging.getLogger(__name__)
        
        self._setup_ui()
        self._load_package_templates()
    
    def _setup_ui(self):
        """Setup the user interface."""
        layout = QVBoxLayout(self)
        
        # Create tab widget for different package types
        self.tab_widget = QTabWidget()
        layout.addWidget(self.tab_widget)
        
        # Create tabs for different package managers
        self._create_arch_tab()
        self._create_fedora_tab()
        self._create_ubuntu_tab()
        self._create_flatpak_tab()
        self._create_snap_tab()
        self._create_nix_tab()
        self._create_docker_tab()
        self._create_homebrew_tab()
        
        # Create bottom buttons
        button_layout = QHBoxLayout()
        
        self.copy_button = QPushButton("Copy to Clipboard")
        self.copy_button.clicked.connect(self._copy_to_clipboard)
        button_layout.addWidget(self.copy_button)
        
        self.save_button = QPushButton("Save to File")
        self.save_button.clicked.connect(self._save_to_file)
        button_layout.addWidget(self.save_button)
        
        self.close_button = QPushButton("Close")
        self.close_button.clicked.connect(self.accept)
        button_layout.addWidget(self.close_button)
        
        layout.addLayout(button_layout)
    
    def _create_arch_tab(self):
        """Create Arch Linux package tab."""
        tab = QWidget()
        layout = QVBoxLayout(tab)
        
        # Description
        desc_label = QLabel(
            "Arch Linux package options for HyprRice. Choose from AUR package, "
            "PKGBUILD, or manual installation script."
        )
        desc_label.setWordWrap(True)
        layout.addWidget(desc_label)
        
        # Package type selector
        type_group = QGroupBox("Package Type")
        type_layout = QFormLayout(type_group)
        
        self.arch_type_combo = QComboBox()
        self.arch_type_combo.addItems([
            "AUR Package (yay/paru)",
            "PKGBUILD",
            "Manual Installation Script",
            "Setup Script"
        ])
        self.arch_type_combo.currentTextChanged.connect(self._update_arch_content)
        type_layout.addRow("Type:", self.arch_type_combo)
        
        layout.addWidget(type_group)
        
        # Content display
        self.arch_content = QTextEdit()
        self.arch_content.setFont(QFont("JetBrainsMono Nerd Font", 10))
        self.arch_content.setReadOnly(True)
        layout.addWidget(self.arch_content)
        
        self.tab_widget.addTab(tab, "Arch Linux")
    
    def _create_fedora_tab(self):
        """Create Fedora package tab."""
        tab = QWidget()
        layout = QVBoxLayout(tab)
        
        # Description
        desc_label = QLabel(
            "Fedora package options for HyprRice. Choose from RPM spec, "
            "COPR repository, or manual installation script."
        )
        desc_label.setWordWrap(True)
        layout.addWidget(desc_label)
        
        # Package type selector
        type_group = QGroupBox("Package Type")
        type_layout = QFormLayout(type_group)
        
        self.fedora_type_combo = QComboBox()
        self.fedora_type_combo.addItems([
            "RPM Spec",
            "COPR Repository",
            "Manual Installation Script",
            "Setup Script"
        ])
        self.fedora_type_combo.currentTextChanged.connect(self._update_fedora_content)
        type_layout.addRow("Type:", self.fedora_type_combo)
        
        layout.addWidget(type_group)
        
        # Content display
        self.fedora_content = QTextEdit()
        self.fedora_content.setFont(QFont("JetBrainsMono Nerd Font", 10))
        self.fedora_content.setReadOnly(True)
        layout.addWidget(self.fedora_content)
        
        self.tab_widget.addTab(tab, "Fedora")
    
    def _create_ubuntu_tab(self):
        """Create Ubuntu package tab."""
        tab = QWidget()
        layout = QVBoxLayout(tab)
        
        # Description
        desc_label = QLabel(
            "Ubuntu/Debian package options for HyprRice. Choose from PPA, "
            "DEB package, or manual installation script."
        )
        desc_label.setWordWrap(True)
        layout.addWidget(desc_label)
        
        # Package type selector
        type_group = QGroupBox("Package Type")
        type_layout = QFormLayout(type_group)
        
        self.ubuntu_type_combo = QComboBox()
        self.ubuntu_type_combo.addItems([
            "PPA Repository",
            "DEB Package",
            "Manual Installation Script",
            "Setup Script"
        ])
        self.ubuntu_type_combo.currentTextChanged.connect(self._update_ubuntu_content)
        type_layout.addRow("Type:", self.ubuntu_type_combo)
        
        layout.addWidget(type_group)
        
        # Content display
        self.ubuntu_content = QTextEdit()
        self.ubuntu_content.setFont(QFont("JetBrainsMono Nerd Font", 10))
        self.ubuntu_content.setReadOnly(True)
        layout.addWidget(self.ubuntu_content)
        
        self.tab_widget.addTab(tab, "Ubuntu/Debian")
    
    def _create_flatpak_tab(self):
        """Create Flatpak package tab."""
        tab = QWidget()
        layout = QVBoxLayout(tab)
        
        # Description
        desc_label = QLabel(
            "Flatpak package options for HyprRice. Includes manifest file "
            "and installation instructions."
        )
        desc_label.setWordWrap(True)
        layout.addWidget(desc_label)
        
        # Content display
        self.flatpak_content = QTextEdit()
        self.flatpak_content.setFont(QFont("JetBrainsMono Nerd Font", 10))
        self.flatpak_content.setReadOnly(True)
        layout.addWidget(self.flatpak_content)
        
        self.tab_widget.addTab(tab, "Flatpak")
    
    def _create_snap_tab(self):
        """Create Snap package tab."""
        tab = QWidget()
        layout = QVBoxLayout(tab)
        
        # Description
        desc_label = QLabel(
            "Snap package options for HyprRice. Includes snapcraft.yaml "
            "and installation instructions."
        )
        desc_label.setWordWrap(True)
        layout.addWidget(desc_label)
        
        # Content display
        self.snap_content = QTextEdit()
        self.snap_content.setFont(QFont("JetBrainsMono Nerd Font", 10))
        self.snap_content.setReadOnly(True)
        layout.addWidget(self.snap_content)
        
        self.tab_widget.addTab(tab, "Snap")
    
    def _create_nix_tab(self):
        """Create Nix package tab."""
        tab = QWidget()
        layout = QVBoxLayout(tab)
        
        # Description
        desc_label = QLabel(
            "Nix package options for HyprRice. Includes Nix derivation "
            "and installation instructions."
        )
        desc_label.setWordWrap(True)
        layout.addWidget(desc_label)
        
        # Content display
        self.nix_content = QTextEdit()
        self.nix_content.setFont(QFont("JetBrainsMono Nerd Font", 10))
        self.nix_content.setReadOnly(True)
        layout.addWidget(self.nix_content)
        
        self.tab_widget.addTab(tab, "Nix")
    
    def _create_docker_tab(self):
        """Create Docker package tab."""
        tab = QWidget()
        layout = QVBoxLayout(tab)
        
        # Description
        desc_label = QLabel(
            "Docker container options for HyprRice. Includes Dockerfile "
            "and container usage instructions."
        )
        desc_label.setWordWrap(True)
        layout.addWidget(desc_label)
        
        # Content display
        self.docker_content = QTextEdit()
        self.docker_content.setFont(QFont("JetBrainsMono Nerd Font", 10))
        self.docker_content.setReadOnly(True)
        layout.addWidget(self.docker_content)
        
        self.tab_widget.addTab(tab, "Docker")
    
    def _create_homebrew_tab(self):
        """Create Homebrew package tab."""
        tab = QWidget()
        layout = QVBoxLayout(tab)
        
        # Description
        desc_label = QLabel(
            "Homebrew package options for HyprRice. Includes formula "
            "and installation instructions for macOS."
        )
        desc_label.setWordWrap(True)
        layout.addWidget(desc_label)
        
        # Content display
        self.homebrew_content = QTextEdit()
        self.homebrew_content.setFont(QFont("JetBrainsMono Nerd Font", 10))
        self.homebrew_content.setReadOnly(True)
        layout.addWidget(self.homebrew_content)
        
        self.tab_widget.addTab(tab, "Homebrew")
    
    def _load_package_templates(self):
        """Load package templates and populate content."""
        self._update_arch_content()
        self._update_fedora_content()
        self._update_ubuntu_content()
        self._update_flatpak_content()
        self._update_snap_content()
        self._update_nix_content()
        self._update_docker_content()
        self._update_homebrew_content()
    
    def _update_arch_content(self):
        """Update Arch Linux content based on selected type."""
        content_type = self.arch_type_combo.currentText()
        
        if content_type == "AUR Package (yay/paru)":
            content = """# Install HyprRice from AUR
yay -S hyprrice

# Or with paru
paru -S hyprrice

# Verify installation
hyprrice --version
hyprrice doctor
"""
        elif content_type == "PKGBUILD":
            content = """# PKGBUILD for HyprRice
pkgname=hyprrice
pkgver=1.0.0
pkgrel=1
pkgdesc="Comprehensive Hyprland Ecosystem Ricing Tool"
arch=('any')
url="https://github.com/DuckyOnQuack-999/HyprRice"
license=('MIT')
depends=('python-pyqt6' 'python-pillow' 'python-yaml' 'python-gobject' 'qt6-wayland')
makedepends=('python-setuptools' 'python-wheel')
source=("$pkgname-$pkgver.tar.gz::https://github.com/DuckyOnQuack-999/HyprRice/archive/v$pkgver.tar.gz")
sha256sums=('SKIP')

build() {
  cd "$pkgname-$pkgver"
  python setup.py build
}

package() {
  cd "$pkgname-$pkgver"
  python setup.py install --root="$pkgdir" --optimize=1
}
"""
        elif content_type == "Manual Installation Script":
            content = """#!/bin/bash
# HyprRice Manual Installation Script for Arch Linux

echo "Installing HyprRice dependencies..."

# Update system
sudo pacman -Syu

# Install dependencies
sudo pacman -S --needed \\
    hyprland \\
    waybar \\
    rofi \\
    dunst \\
    swww \\
    grim \\
    slurp \\
    cliphist \\
    hyprlock \\
    python-pyqt6 \\
    python-pillow \\
    python-yaml \\
    python-gobject \\
    qt6-wayland

# Install HyprRice
pip install --user hyprrice

# Verify installation
hyprrice doctor
hyprrice gui
"""
        else:  # Setup Script
            content = """#!/bin/bash
# HyprRice Setup Script for Arch Linux

set -e

echo "Setting up HyprRice on Arch Linux..."

# Check if running as root
if [[ $EUID -eq 0 ]]; then
   echo "This script should not be run as root" 
   exit 1
fi

# Install dependencies
sudo pacman -S --needed \\
    hyprland \\
    waybar \\
    rofi \\
    dunst \\
    swww \\
    grim \\
    slurp \\
    cliphist \\
    hyprlock \\
    python-pyqt6 \\
    python-pillow \\
    python-yaml \\
    python-gobject \\
    qt6-wayland

# Install HyprRice
pip install --user hyprrice

# Create necessary directories
mkdir -p ~/.config/hyprrice
mkdir -p ~/.hyprrice/{themes,plugins,backups,logs}

# Run initial setup
hyprrice doctor
hyprrice gui --setup-wizard

echo "HyprRice setup complete!"
echo "Run 'hyprrice gui' to start the configuration tool."
"""
        
        self.arch_content.setPlainText(content)
    
    def _update_fedora_content(self):
        """Update Fedora content based on selected type."""
        content_type = self.fedora_type_combo.currentText()
        
        if content_type == "RPM Spec":
            content = """# hyprrice.spec
Name:           hyprrice
Version:        1.0.0
Release:        1%{?dist}
Summary:        Comprehensive Hyprland Ecosystem Ricing Tool

License:        MIT
URL:            https://github.com/DuckyOnQuack-999/HyprRice
Source0:        https://github.com/DuckyOnQuack-999/HyprRice/archive/v%{version}.tar.gz

BuildArch:      noarch
BuildRequires:  python3-devel python3-setuptools python3-wheel
Requires:       python3-qt6 python3-pillow python3-pyyaml python3-gobject qt6-qtwayland

%description
HyprRice is a comprehensive ricing tool for the Hyprland Wayland compositor ecosystem.
It provides a modern GUI, deep integration with Hyprland and related tools, theme management,
plugin support, and robust configuration handling.

%prep
%setup -q

%build
python3 setup.py build

%install
python3 setup.py install --root %{buildroot}

%files
%{python3_sitelib}/hyprrice/
%{_bindir}/hyprrice

%changelog
* $(date +'%a %b %d %Y') HyprRice Team <hyprrice@example.com> - 1.0.0-1
- Initial package
"""
        elif content_type == "COPR Repository":
            content = """# COPR Repository Setup
# Add COPR repository
sudo dnf copr enable hyprrice/hyprrice

# Install HyprRice
sudo dnf install hyprrice

# Verify installation
hyprrice --version
hyprrice doctor
"""
        elif content_type == "Manual Installation Script":
            content = """#!/bin/bash
# HyprRice Manual Installation Script for Fedora

echo "Installing HyprRice dependencies..."

# Update system
sudo dnf update

# Install dependencies
sudo dnf install \\
    hyprland \\
    waybar \\
    rofi \\
    dunst \\
    swww \\
    grim \\
    slurp \\
    cliphist \\
    hyprlock \\
    python3-qt6 \\
    python3-pillow \\
    python3-pyyaml \\
    python3-gobject \\
    qt6-qtwayland

# Install HyprRice
pip3 install --user hyprrice

# Verify installation
hyprrice doctor
hyprrice gui
"""
        else:  # Setup Script
            content = """#!/bin/bash
# HyprRice Setup Script for Fedora

set -e

echo "Setting up HyprRice on Fedora..."

# Check if running as root
if [[ $EUID -eq 0 ]]; then
   echo "This script should not be run as root" 
   exit 1
fi

# Install dependencies
sudo dnf install \\
    hyprland \\
    waybar \\
    rofi \\
    dunst \\
    swww \\
    grim \\
    slurp \\
    cliphist \\
    hyprlock \\
    python3-qt6 \\
    python3-pillow \\
    python3-pyyaml \\
    python3-gobject \\
    qt6-qtwayland

# Install HyprRice
pip3 install --user hyprrice

# Create necessary directories
mkdir -p ~/.config/hyprrice
mkdir -p ~/.hyprrice/{themes,plugins,backups,logs}

# Run initial setup
hyprrice doctor
hyprrice gui --setup-wizard

echo "HyprRice setup complete!"
echo "Run 'hyprrice gui' to start the configuration tool."
"""
        
        self.fedora_content.setPlainText(content)
    
    def _update_ubuntu_content(self):
        """Update Ubuntu content based on selected type."""
        content_type = self.ubuntu_type_combo.currentText()
        
        if content_type == "PPA Repository":
            content = """# Add PPA repository
sudo add-apt-repository ppa:hyprrice/ppa
sudo apt update

# Install HyprRice
sudo apt install hyprrice

# Verify installation
hyprrice --version
hyprrice doctor
"""
        elif content_type == "DEB Package":
            content = """# Download and install DEB package
wget https://github.com/DuckyOnQuack-999/HyprRice/releases/download/v1.0.0/hyprrice_1.0.0-1_amd64.deb
sudo dpkg -i hyprrice_1.0.0-1_amd64.deb
sudo apt-get install -f  # Fix dependencies

# Verify installation
hyprrice --version
hyprrice doctor
"""
        elif content_type == "Manual Installation Script":
            content = """#!/bin/bash
# HyprRice Manual Installation Script for Ubuntu/Debian

echo "Installing HyprRice dependencies..."

# Update system
sudo apt update

# Install dependencies
sudo apt install \\
    hyprland \\
    waybar \\
    rofi \\
    dunst \\
    swww \\
    grim \\
    slurp \\
    cliphist \\
    hyprlock \\
    python3-pyqt6 \\
    python3-pil \\
    python3-yaml \\
    python3-gi \\
    qt6-wayland

# Install HyprRice
pip3 install --user hyprrice

# Verify installation
hyprrice doctor
hyprrice gui
"""
        else:  # Setup Script
            content = """#!/bin/bash
# HyprRice Setup Script for Ubuntu/Debian

set -e

echo "Setting up HyprRice on Ubuntu/Debian..."

# Check if running as root
if [[ $EUID -eq 0 ]]; then
   echo "This script should not be run as root" 
   exit 1
fi

# Install dependencies
sudo apt update
sudo apt install \\
    hyprland \\
    waybar \\
    rofi \\
    dunst \\
    swww \\
    grim \\
    slurp \\
    cliphist \\
    hyprlock \\
    python3-pyqt6 \\
    python3-pil \\
    python3-yaml \\
    python3-gi \\
    qt6-wayland

# Install HyprRice
pip3 install --user hyprrice

# Create necessary directories
mkdir -p ~/.config/hyprrice
mkdir -p ~/.hyprrice/{themes,plugins,backups,logs}

# Run initial setup
hyprrice doctor
hyprrice gui --setup-wizard

echo "HyprRice setup complete!"
echo "Run 'hyprrice gui' to start the configuration tool."
"""
        
        self.ubuntu_content.setPlainText(content)
    
    def _update_flatpak_content(self):
        """Update Flatpak content."""
        content = """# Flatpak Manifest for HyprRice
{
  "app-id": "com.hyprrice.HyprRice",
  "runtime": "org.kde.Platform",
  "runtime-version": "5.15-22.08",
  "sdk": "org.kde.Sdk",
  "command": "hyprrice",
  "finish-args": [
    "--share=ipc",
    "--socket=wayland",
    "--socket=x11",
    "--device=dri",
    "--filesystem=home",
    "--filesystem=host"
  ],
  "modules": [
    {
      "name": "hyprrice",
      "buildsystem": "python",
      "sources": [
        {
          "type": "git",
          "url": "https://github.com/DuckyOnQuack-999/HyprRice.git",
          "tag": "v1.0.0"
        }
      ]
    }
  ]
}

# Installation Instructions:
# 1. Install Flatpak if not already installed
sudo apt install flatpak  # Ubuntu/Debian
sudo dnf install flatpak  # Fedora
sudo pacman -S flatpak    # Arch

# 2. Add Flathub repository
flatpak remote-add --if-not-exists flathub https://flathub.org/repo/flathub.flatpakrepo

# 3. Install HyprRice
flatpak install flathub com.hyprrice.HyprRice

# 4. Run HyprRice
flatpak run com.hyprrice.HyprRice
"""
        self.flatpak_content.setPlainText(content)
    
    def _update_snap_content(self):
        """Update Snap content."""
        content = """# snapcraft.yaml for HyprRice
name: hyprrice
version: '1.0.0'
summary: Comprehensive Hyprland Ecosystem Ricing Tool
description: |
  HyprRice is a comprehensive ricing tool for the Hyprland Wayland compositor ecosystem.
  It provides a modern GUI, deep integration with Hyprland and related tools, theme management,
  plugin support, and robust configuration handling.

grade: stable
confinement: strict

parts:
  hyprrice:
    plugin: python
    source: .
    python-version: python3
    build-packages:
      - python3-dev
      - python3-setuptools
      - python3-wheel
    stage-packages:
      - python3-pyqt6
      - python3-pil
      - python3-yaml
      - python3-gi
      - qt6-wayland

apps:
  hyprrice:
    command: hyprrice
    plugs:
      - home
      - x11
      - wayland
      - network
      - desktop

# Installation Instructions:
# 1. Install Snap if not already installed
sudo apt install snapd  # Ubuntu/Debian
sudo dnf install snapd  # Fedora
sudo pacman -S snapd    # Arch

# 2. Install HyprRice
sudo snap install hyprrice

# 3. Run HyprRice
hyprrice
"""
        self.snap_content.setPlainText(content)
    
    def _update_nix_content(self):
        """Update Nix content."""
        content = """# Nix derivation for HyprRice
{ lib, python3Packages, hyprland, waybar, rofi, dunst, swww, grim, slurp, cliphist, hyprlock, qt6 }:

python3Packages.buildPythonApplication rec {
  pname = "hyprrice";
  version = "1.0.0";

  src = ./.;

  propagatedBuildInputs = with python3Packages; [
    pyqt6
    pillow
    pyyaml
    pygobject3
  ];

  buildInputs = [
    hyprland
    waybar
    rofi
    dunst
    swww
    grim
    slurp
    cliphist
    hyprlock
    qt6.qtwayland
  ];

  meta = with lib; {
    description = "Comprehensive Hyprland Ecosystem Ricing Tool";
    homepage = "https://github.com/DuckyOnQuack-999/HyprRice";
    license = licenses.mit;
    maintainers = [ ];
    platforms = platforms.linux;
  };
}

# Installation Instructions:
# 1. Add to your Nix configuration
# Add this to your configuration.nix or home.nix

# 2. Install with nix-env
nix-env -iA nixpkgs.hyprrice

# 3. Or add to your system configuration
# Add hyprrice to environment.systemPackages

# 4. Run HyprRice
hyprrice
"""
        self.nix_content.setPlainText(content)
    
    def _update_docker_content(self):
        """Update Docker content."""
        content = """# Dockerfile for HyprRice
FROM python:3.11-slim

# Install system dependencies
RUN apt-get update && apt-get install -y \\
    hyprland \\
    waybar \\
    rofi \\
    dunst \\
    swww \\
    grim \\
    slurp \\
    cliphist \\
    hyprlock \\
    python3-pyqt6 \\
    python3-pil \\
    python3-yaml \\
    python3-gi \\
    qt6-wayland \\
    && rm -rf /var/lib/apt/lists/*

# Install HyprRice
COPY . /app
WORKDIR /app
RUN pip install -e .

# Set up user
RUN useradd -m -s /bin/bash hyprrice
USER hyprrice
WORKDIR /home/hyprrice

# Expose port for web interface (if implemented)
EXPOSE 8080

# Default command
CMD ["hyprrice", "gui"]

# Build and run instructions:
# 1. Build the image
docker build -t hyprrice .

# 2. Run the container
docker run -it --rm \\
    -e DISPLAY=$DISPLAY \\
    -v /tmp/.X11-unix:/tmp/.X11-unix \\
    -v $HOME/.config:/home/hyprrice/.config \\
    hyprrice

# 3. For Wayland support
docker run -it --rm \\
    -e WAYLAND_DISPLAY=$WAYLAND_DISPLAY \\
    -v $XDG_RUNTIME_DIR:$XDG_RUNTIME_DIR \\
    -v $HOME/.config:/home/hyprrice/.config \\
    hyprrice
"""
        self.docker_content.setPlainText(content)
    
    def _update_homebrew_content(self):
        """Update Homebrew content."""
        content = """# Homebrew formula for HyprRice
class Hyprrice < Formula
  desc "Comprehensive Hyprland Ecosystem Ricing Tool"
  homepage "https://github.com/DuckyOnQuack-999/HyprRice"
  url "https://github.com/DuckyOnQuack-999/HyprRice/archive/v1.0.0.tar.gz"
  sha256 "SKIP"
  license "MIT"

  depends_on "python@3.11"
  depends_on "pyqt6"
  depends_on "pillow"
  depends_on "pyyaml"
  depends_on "pygobject3"

  def install
    system "python3", "-m", "pip", "install", *std_pip_args, "."
  end

  test do
    system "#{bin}/hyprrice", "--version"
  end
end

# Installation Instructions:
# 1. Install Homebrew if not already installed
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"

# 2. Add the tap (if using a custom tap)
brew tap hyprrice/hyprrice

# 3. Install HyprRice
brew install hyprrice

# 4. Run HyprRice
hyprrice
"""
        self.homebrew_content.setPlainText(content)
    
    def _copy_to_clipboard(self):
        """Copy current content to clipboard."""
        current_tab = self.tab_widget.currentIndex()
        
        if current_tab == 0:  # Arch
            content = self.arch_content.toPlainText()
        elif current_tab == 1:  # Fedora
            content = self.fedora_content.toPlainText()
        elif current_tab == 2:  # Ubuntu
            content = self.ubuntu_content.toPlainText()
        elif current_tab == 3:  # Flatpak
            content = self.flatpak_content.toPlainText()
        elif current_tab == 4:  # Snap
            content = self.snap_content.toPlainText()
        elif current_tab == 5:  # Nix
            content = self.nix_content.toPlainText()
        elif current_tab == 6:  # Docker
            content = self.docker_content.toPlainText()
        elif current_tab == 7:  # Homebrew
            content = self.homebrew_content.toPlainText()
        else:
            content = ""
        
        if content:
            clipboard = QApplication.clipboard()
            clipboard.setText(content)
            QMessageBox.information(self, "Copied", "Content copied to clipboard!")
        else:
            QMessageBox.warning(self, "Error", "No content to copy!")
    
    def _save_to_file(self):
        """Save current content to file."""
        current_tab = self.tab_widget.currentIndex()
        
        if current_tab == 0:  # Arch
            content = self.arch_content.toPlainText()
            default_name = "hyprrice-arch-install.sh"
        elif current_tab == 1:  # Fedora
            content = self.fedora_content.toPlainText()
            default_name = "hyprrice-fedora-install.sh"
        elif current_tab == 2:  # Ubuntu
            content = self.ubuntu_content.toPlainText()
            default_name = "hyprrice-ubuntu-install.sh"
        elif current_tab == 3:  # Flatpak
            content = self.flatpak_content.toPlainText()
            default_name = "hyprrice-flatpak.json"
        elif current_tab == 4:  # Snap
            content = self.snap_content.toPlainText()
            default_name = "hyprrice-snapcraft.yaml"
        elif current_tab == 5:  # Nix
            content = self.nix_content.toPlainText()
            default_name = "hyprrice-nix.nix"
        elif current_tab == 6:  # Docker
            content = self.docker_content.toPlainText()
            default_name = "hyprrice-dockerfile"
        elif current_tab == 7:  # Homebrew
            content = self.homebrew_content.toPlainText()
            default_name = "hyprrice-homebrew.rb"
        else:
            content = ""
            default_name = "hyprrice-package.txt"
        
        if content:
            file_path, _ = QFileDialog.getSaveFileName(
                self, "Save Package File",
                os.path.expanduser(f"~/Downloads/{default_name}"),
                "All Files (*)"
            )
            
            if file_path:
                try:
                    with open(file_path, 'w', encoding='utf-8') as f:
                        f.write(content)
                    QMessageBox.information(self, "Saved", f"File saved to {file_path}")
                except Exception as e:
                    QMessageBox.critical(self, "Error", f"Failed to save file: {e}")
        else:
            QMessageBox.warning(self, "Error", "No content to save!")
