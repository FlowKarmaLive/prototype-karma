# Create the Client Key and CSR
openssl genrsa -aes256 -passout pass:xxxx -out ${TMPDIR}/${NAME}.pass.key 4096 && \
openssl rsa -passin pass:xxxx -in ${TMPDIR}/${NAME}.pass.key -out ${TMPDIR}/${NAME}.key && \
openssl req -new -key ${TMPDIR}/${NAME}.key -out ${TMPDIR}/${NAME}.csr -subj "/C=US/ST=CA/L=San Francisco/O=FlowKarma.Live/OU=ou/CN=${NAME}" && \
openssl x509 -req -days 3650 -in ${TMPDIR}/${NAME}.csr -CA ca.pem -CAkey ca.key -set_serial ${SERIAL} -out ${TMPDIR}/${NAME}.pem && \
cat ${TMPDIR}/${NAME}.key ${TMPDIR}/${NAME}.pem ca.pem > ${TMPDIR}/${NAME}.full.pem && \
openssl pkcs12 -export -out ${KEYDIR}/${NAME}.pfx -inkey ${TMPDIR}/${NAME}.key -in ${TMPDIR}/${NAME}.pem -certfile ca.pem -passout env:PW
