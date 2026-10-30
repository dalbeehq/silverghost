# page.tpl.html의 자리표시를 채워 표준 출력으로 낸다.
# --black: 검은 단색(#000) 배경에 제목, 출처, 안내 글을 뺀 판으로 낸다. 달비 2026-10-31 "좌 우 상단 쳐 빼라 그리고 그라데이션 다 빼고 검은 화면에".
# 틀의 {{default}}...{{/default}}는 기본 판에만, {{black}}...{{/black}}는 --black 판에만 들어간다.
import html, re, sys
args = [a for a in sys.argv[1:] if a != '--black']
black = len(args) != len(sys.argv) - 1
tpl, points, title, credit = args
keep, drop = ('black', 'default') if black else ('default', 'black')
s = open(tpl).read()
s = re.sub(r'\{\{%s\}\}.*?\{\{/%s\}\}\n?' % (drop, drop), '', s, flags=re.S)
s = re.sub(r'\{\{/?%s\}\}' % keep, '', s)
s = s.replace('__TITLE__', html.escape(title)).replace('__CREDIT__', html.escape(credit))
print(s.replace('__POINTS__', open(points).read()), end='')
