# Maintainer: DuckyOnQuack-999 <your-email@example.com>

pkgname=hyprrice
pkgver=1.0.0
pkgrel=1
pkgdesc="Comprehensive Hyprland Ecosystem Ricing Tool (PyQt5 GUI, themes, plugins, backup, and more)"
arch=('any')
url="https://github.com/DuckyOnQuack-999/HyprRice"
license=('GPL2')
depends=('python' 'python-pyqt5' 'python-pyyaml' 'python-pillow' 'python-psutil' 'python-pydbus' 'python-configparser' 'python-requests' 'python-colorama' 'python-rich')
makedepends=('python-setuptools')
source=("$pkgname-$pkgver.tar.gz::$url/archive/refs/tags/v$pkgver.tar.gz")
sha256sums=('SKIP')

build() {
  cd "$srcdir/$pkgname-$pkgver"
  python setup.py build
}

package() {
  cd "$srcdir/$pkgname-$pkgver"
  python setup.py install --root="$pkgdir" --optimize=1
}
