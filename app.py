import vyper

v = vyper.Vyper()

v.set('winter', {'k':{'v':'i'}})
print('!', v.get('winter.k.v'))
