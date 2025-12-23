import re
p='templates/restaurants/restaurant_detail.html'
s=open(p,encoding='utf-8').read()
pattern=re.compile(r'{%\s*(if|elif|else|endif|for|endfor|block|endblock|comment|endcomment)\b[^%]*%}')
stack=[]
line_map=lambda pos: s.count('\n',0,pos)+1
for m in pattern.finditer(s):
    tag=m.group(0)
    name=m.group(1)
    ln=line_map(m.start())
    print(f"{ln}: {tag.strip()}")
    if name=='if':
        stack.append(('if',ln))
    elif name=='for':
        stack.append(('for',ln))
    elif name=='block':
        stack.append(('block',ln))
    elif name=='endif':
        if stack and stack[-1][0]=='if':
            stack.pop()
        else:
            print(f"Unmatched endif at {ln}")
    elif name=='endfor':
        if stack and stack[-1][0]=='for':
            stack.pop()
        else:
            print(f"Unmatched endfor at {ln}")
    elif name=='endblock':
        if stack and stack[-1][0]=='block':
            stack.pop()
        else:
            print(f"Unmatched endblock at {ln}")

print('\nRemaining stack (unclosed tags):')
for t,ln in stack:
    print(t,ln)
