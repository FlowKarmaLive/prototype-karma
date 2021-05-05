# Use Cloudflare's "Family" DNS to check hostnames.
# https://cloudflare-dns.com/family/
import dns.resolver as DNS

dns = DNS.Resolver()
dns.cache = DNS.LRUCache()
dns.nameservers = ['1.1.1.3', '1.0.0.3']

def check_domain(domain):
    return ['0.0.0.0'] != list(map(str, dns.resolve(domain)))


# E.g.:
a = dns.resolve('google.com')
print(list(map(str, a)))
b = dns.resolve('porno.com')
print(list(map(str, b)))

