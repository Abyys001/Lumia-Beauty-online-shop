#!/usr/bin/env bash
# =============================================================================
# One-time Let's Encrypt bootstrap for lumiabeauty.ir.
# Run ON THE SERVER, from the repo root, AFTER `docker compose pull`:
#   ./scripts/init-letsencrypt.sh
#
# It creates a throwaway self-signed cert so nginx can start, brings nginx up,
# then swaps in a real Let's Encrypt cert obtained via the HTTP-01 challenge.
# Requires ports 80/443 open and DNS for the domains pointing at this server.
# =============================================================================
set -e

domains=(lumiabeauty.ir www.lumiabeauty.ir)
email="siavash0darvishi@gmail.com"     # for expiry notices; "" to skip
rsa_key_size=4096
data_path="./certbot"
staging=0                              # set to 1 to test without hitting rate limits

compose="docker compose -f docker-compose.yml -f docker-compose.prod.yml"

if ! command -v docker >/dev/null 2>&1; then
  echo "Error: docker is not installed." >&2; exit 1
fi

if [ -d "$data_path/conf/live/${domains[0]}" ]; then
  read -p "Existing certificate for ${domains[0]} found. Replace it? (y/N) " decision
  if [ "$decision" != "Y" ] && [ "$decision" != "y" ]; then exit; fi
fi

echo "### Creating a dummy certificate so nginx can boot ..."
live_path="/etc/letsencrypt/live/${domains[0]}"
mkdir -p "$data_path/conf/live/${domains[0]}"
$compose run --rm --entrypoint "\
  openssl req -x509 -nodes -newkey rsa:$rsa_key_size -days 1 \
    -keyout '$live_path/privkey.pem' \
    -out '$live_path/fullchain.pem' \
    -subj '/CN=localhost'" certbot

echo "### Starting nginx ..."
$compose up --force-recreate -d nginx

echo "### Removing the dummy certificate ..."
$compose run --rm --entrypoint "\
  rm -Rf /etc/letsencrypt/live/${domains[0]} && \
  rm -Rf /etc/letsencrypt/archive/${domains[0]} && \
  rm -Rf /etc/letsencrypt/renewal/${domains[0]}.conf" certbot

echo "### Requesting the real Let's Encrypt certificate ..."
domain_args=""
for domain in "${domains[@]}"; do domain_args="$domain_args -d $domain"; done

case "$email" in
  "") email_arg="--register-unsafely-without-email" ;;
  *)  email_arg="--email $email" ;;
esac
[ $staging != "0" ] && staging_arg="--staging" || staging_arg=""

$compose run --rm --entrypoint "\
  certbot certonly --webroot -w /var/www/certbot \
    $staging_arg $email_arg $domain_args \
    --rsa-key-size $rsa_key_size \
    --agree-tos --no-eff-email \
    --force-renewal" certbot

echo "### Reloading nginx with the real certificate ..."
$compose exec nginx nginx -s reload

echo "### Done. Now bring the whole stack up:"
echo "    $compose up -d"
