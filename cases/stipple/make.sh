#!/bin/sh
# 사진 한 장을 점묘 페이지로 만든다.
# 사용: make.sh <사진> <이름> <제목> <출처 한 줄> [점 개수=24000]
# BLACK=1 make.sh ...: 검은 단색 배경에 글자 없는 판으로 만든다(fill.py --black).
# 결과: cases/stipple/<이름>.html, <이름>.points.json. 오려낸 그림과 마스크는 src/<이름>-cut.png, src/<이름>-mask.png
set -e
here=$(cd "$(dirname "$0")" && pwd)
root=$(cd "$here/../.." && pwd)
img=$1; name=$2; title=$3; credit=$4; n=${5:-24000}
[ -n "$credit" ] || { echo "사용: make.sh <사진> <이름> <제목> <출처 한 줄> [점 개수]"; exit 64; }
"${CUTOUT:-$HOME/ws/skills/media-use/scripts/vision-cutout.sh}" "$img" "$root/src/$name-cut.png" "$root/src/$name-mask.png"
python3 -I "$here/stipple.py" "$img" "$root/src/$name-mask.png" "$here/$name.points.json" "$n"
python3 -I "$here/fill.py" "$here/page.tpl.html" "$here/$name.points.json" "$title" "$credit" ${BLACK:+--black} > "$here/$name.html"
echo "$here/$name.html"
