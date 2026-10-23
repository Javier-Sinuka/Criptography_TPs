FROM httpd:2.4
RUN sed -i 's/^#LoadModule ssl_module/LoadModule ssl_module/' /usr/local/apache2/conf/httpd.conf \
 && sed -i 's/^#LoadModule socache_shmcb_module/LoadModule socache_shmcb_module/' /usr/local/apache2/conf/httpd.conf \
 && printf '\nInclude conf/extra/https-lab.conf\n' >> /usr/local/apache2/conf/httpd.conf
COPY https-lab.conf /usr/local/apache2/conf/extra/https-lab.conf
COPY index.html /usr/local/apache2/htdocs/index.html
