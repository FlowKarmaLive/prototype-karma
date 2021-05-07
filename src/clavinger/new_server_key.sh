# As per: https://gist.github.com/mtigas/952344
# Generate key file with password (because you has to.)
openssl genrsa -aes256 -passout pass:xxxx -out ca.pass.key 4096
# Strip the password out.
openssl rsa -passin pass:xxxx -in ca.pass.key -out ca.key
# Get rid of the passowrd'd key file.
rm ca.pass.key
# Create the PEM file.
openssl req -new -x509 -days 3650 -key ca.key -out ca.pem


