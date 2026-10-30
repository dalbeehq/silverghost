#!/bin/sh
# 빌드한 dist/를 website 저장소의 public/silverghost/ 로 옮긴다. 사용: sync-site.sh <website 폴더>
set -e
root=$(cd "$(dirname "$0")/.." && pwd)
site=${1:?website 폴더를 준다}
python3 -I "$root/tools/build.py"
rm -rf "$site/public/silverghost"
mkdir -p "$site/public/silverghost"
cp -R "$root/dist/." "$site/public/silverghost/"
echo "$site/public/silverghost"
