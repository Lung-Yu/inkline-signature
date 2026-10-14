#!/usr/bin/env bash
# 下載 12 款簽名字型（Fontsource / Google Fonts，SIL OFL）並轉成 TTF，供 extract_font_skeletons.py 使用。
# 需要：node/npm、python3、fonttools（pip install fonttools）
set -euo pipefail
mkdir -p fonts && cd fonts
for p in mrs-saint-delafield herr-von-muellerhoff monsieur-la-doulaise mr-de-haviland windsong the-nautigal ms-madi allison mr-dafoe hurricane qwigley sacramento; do
  npm pack "@fontsource/$p" --silent >/dev/null
  mkdir -p "_$p" && tar xzf fontsource-$p-*.tgz -C "_$p"
  cp "$(ls _$p/package/files/*latin-400-normal.woff | grep -v ext | head -1)" "$p.woff"
  rm -rf "_$p" fontsource-$p-*.tgz
  python3 -c "from fontTools.ttLib import TTFont;t=TTFont('$p.woff');t.flavor=None;t.save('$p.ttf')"
  echo "ok $p"
done
