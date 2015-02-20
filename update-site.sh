# Update remote site to the git master
# and restart the supervisor
ssh reftag.rmcgibbo.org \
    'cd /home/rmcgibbo/reftagger/  &&
    git pull origin master &&
    cd /home/rmcgibbo/ &&
    supervisorctl restart tornado-5000'
