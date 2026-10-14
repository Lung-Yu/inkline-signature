"""把 hanzi-writer-data 轉成網站使用的分片檔 site/hz/h{0..96}.json。

用法：
  npm pack hanzi-writer-data && mkdir src && tar xzf hanzi-writer-data-*.tgz -C src
  python3 -I tools/build_hanzi_shards.py src/package site/hz

每個字存成 [中線, [筆畫輪廓 SVG path...]]。
中線以 4 個 base64 字元編一點：x、y 各 12 bit，座標除以 2 並把 y 翻轉（900 - y）。
分片依 codePoint % 97，網頁只下載名字用到的分片。
"""
import glob, json, os, re, sys

B = 'ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789-_'

def enc(v):
    v = max(0, min(4095, v + 256))
    return B[v >> 6] + B[v & 63]

def main(src, out):
    os.makedirs(out, exist_ok=True)
    shards = {}
    for f in glob.glob(os.path.join(src, '*.json')):
        ch = os.path.basename(f)[:-5]
        if len(ch) != 1 or not ('一' <= ch <= '鿿' or '㐀' <= ch <= '䶿'):
            continue
        d = json.load(open(f, encoding='utf-8'))
        med = ','.join(''.join(enc(round(x / 2)) + enc(round((900 - y) / 2)) for x, y in s) for s in d['medians'])
        outs = [re.sub(r' ?([A-Za-z]) ?', r'\1', re.sub(r'\s+', ' ', s).strip()) for s in d['strokes']]
        shards.setdefault(ord(ch) % 97, {})[ch] = [med, outs]
    for k, v in shards.items():
        with open(os.path.join(out, f'h{k}.json'), 'w', encoding='utf-8') as fh:
            json.dump(v, fh, ensure_ascii=False, separators=(',', ':'))
    print(sum(len(v) for v in shards.values()), 'characters in', len(shards), 'shards')

if __name__ == '__main__':
    main(sys.argv[1], sys.argv[2])
