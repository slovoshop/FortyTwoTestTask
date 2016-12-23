#!/bin/sh 

redis-server
sh ../uwsgi/post_deploy.sh 
 
