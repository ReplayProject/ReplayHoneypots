server_url='http://165.22.11.36'

wget $server_url/static/registration.txt -O registration.sh
chmod 755 registration.sh
# Note: this will export the HPF_* variables
. ./registration.sh $server_url $deploy_key "wordpot"

echo '$HPF_HOST'
echo $HPF_PORT
echo '$HPF_IDENT'
echo '$HPF_SECRET'
echo 'wordpot.events'