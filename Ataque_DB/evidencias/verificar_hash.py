import hashlib
password = 'charley'
expected = '8d3533d75ae2c3966d7e0d4fcc69216b'
actual = hashlib.md5(password.encode('utf-8')).hexdigest()
print('Verificacion local del hash del laboratorio SQL_Lab.pcap')
print('Usuario en la respuesta HTTP: 1337')
print('Contrasena candidata: ' + password)
print('MD5 calculado:        ' + actual)
print('Hash de la consigna:  ' + expected)
print('Coinciden: ' + str(actual == expected))
assert actual == expected
