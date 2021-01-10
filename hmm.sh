export FROM=bats
export NAME=cats
export SERIAL=pqz4ndnjv223jjqq79yvm2nkzs4n

# Create the Client Key and CSR
openssl genrsa -aes256 -passout pass:xxxx -out ${NAME}.pass.key 4096
openssl rsa -passin pass:xxxx -in ${NAME}.pass.key -out ${NAME}.key
openssl req -new -key ${NAME}.key -out ${NAME}.csr  # asks a bunch of Q's; override w/ -subj
openssl x509 -req -days 3650 -in ${NAME}.csr -CA ca.pem -CAkey ca.key -set_serial ${SERIAL} -out ${NAME}.pem
cat ${NAME}.key ${NAME}.pem ca.pem > ${NAME}.full.pem
openssl pkcs12 -export -out ${NAME}.pfx -inkey ${NAME}.key -in ${NAME}.pem -certfile ca.pem  # wants a password


 openssl req -new -subj "/C=US/ST=CA/L=San Francisco/O=FlowKarma.Live/OU=${FROM}/CN=${NAME}" -key ${NAME}.key -out ${NAME}.csr