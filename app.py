import vyper

v = vyper.Vyper()

v.set('winter', {'k': 'v'})
print(v.get('winter.k'))
