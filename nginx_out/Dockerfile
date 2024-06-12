FROM nginx
WORKDIR /var/www/medml_front/
# COPY ./front_server .

# RUN mkdir -p /usr/src/web/static_files/front/
# COPY ./front_server/static/ /usr/src/web/static_files/front/
RUN rm /etc/nginx/conf.d/default.conf
COPY ./nginx.conf /etc/nginx/conf.d/default.conf
