export FROM=bats
export NAME=cats
export SERIAL=pqz4ndnjv223jjqq79yvm2nkzs4n
export PASS=nobby

# Create the Client Key and CSR
openssl genrsa -aes256 -passout pass:xxxx -out ${NAME}.pass.key 4096
openssl rsa -passin pass:xxxx -in ${NAME}.pass.key -out ${NAME}.key
openssl req -new -key ${NAME}.key -out ${NAME}.csr  # asks a bunch of Q's; override w/ -subj
openssl req -new -key ${NAME}.key -out ${NAME}.csr -subj "/C=US/ST=CA/L=San Francisco/O=FlowKarma.Live/OU=${FROM}/CN=${NAME}"
openssl x509 -req -days 3650 -in ${NAME}.csr -CA ca.pem -CAkey ca.key -set_serial ${SERIAL} -out ${NAME}.pem
cat ${NAME}.key ${NAME}.pem ca.pem > ${NAME}.full.pem
openssl pkcs12 -export -out ${NAME}.pfx -inkey ${NAME}.key -in ${NAME}.pem -certfile ca.pem  # wants a password
openssl pkcs12 -export -out ${NAME}.pfx -inkey ${NAME}.key -in ${NAME}.pem -certfile ca.pem -passout env:${PASS}



# suppress password prompt with:  (sets empty password?)
#  -passout pass:

#  other options:  ... env:var
#  https://www.openssl.org/docs/manmaster/man1/openssl-passphrase-options.html

# openssl pkcs12 -export -out sam.pfx -inkey sam.key -in sam.pem -certfile ca.pem -passout env:${PASS}

