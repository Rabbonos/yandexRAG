#домен который создал: rag4yandex.com. , обязательно нужен для certbot ( можно создать любой другой, 1 $ от яндекса)
# домен который создал 2: yandexragus.duckdns.org
!!!если меняете пути сертификата-ключа-... то в .env поменяйте SSLMODE SSLKEY SSLROOTCERT SSLCERT + учтите что в докере тоже придется указать


НАЧАЛО 
#заходим в coomand promt (в windows в поисковике находим)

#для windows скачиваем от яндекса их cli
@"%SystemRoot%\System32\WindowsPowerShell\v1.0\powershell.exe" -Command "iex ((New-Object System.Net.WebClient).DownloadString('https://storage.yandexcloud.net/yandexcloud-yc/install.ps1'))" && SET "PATH=%PATH%;%USERPROFILE%\yandex-cloud\bin"

#Вводим Y

#запускаем команду, далее следуем базовой инструкции , выбираем нашу папку (1 по дефолту )
yc init

#опять следуем инстуркции , переходим по ссылке, копируем токен который увидили и вставляем :
... (не выходим отсюда и идем дальше по инструкции)


# далее заходим в яндекс VM , запускаем нужный нам VM (достаточно просто), в итоге там должны увидеть что то похожее на 'yc compute ssh --name compute-vm-2-2-20-hdd-1728077926308 --folder-id b1gl42i8kf54i590ma16' , копируете и вставляете в cmd 

#должны были подклюиться к серверу 
теперь вы в линуксе (вашем VM)

#создаём файл
nano backend_fastapi.py

#копируем код что скинул
ctrl+a затем ctrl+c нашего кода в backend_fastapi.py

#вставляем 
ctl + shift + правая кнопка мышьки ( чтобы вставить в созданный файл nano backend_fastapi.py наш код)

#выходим
ctrl+x и enter

#повторяем для всех файлов кроме ( а в .env путь SSLKEY =/etc/nginx/ssl/key.pem   SSLCERT=/etc/nginx/ssl/cert.pem  ) (так же в requirements удалить psycopg2, скачаете несколько по другому )и png (наверное можно было бы через filezilla адекватно закинуть файлы , но тогда надо по ssh подключиться, почему то не выходило нормально)

#у нас есть ещё фотка , её скачиваем по ссылке которую создал ( можно скачать любую фотку естественно)
wget https://i.ibb.co/JdXMC8J/ragyandeximg.png -O ragyandeximg.png

#далее просто вставляйте по очереди команды

sudo apt update       
sudo apt install -y software-properties-common
sudo add-apt-repository ppa:deadsnakes/ppa
sudo apt update
sudo apt install -y python3.10
python3.10 --version - проверяем есть ли пайтон
sudo apt install -y python3.10-venv
python3.10 -m venv myenv - создаем свой энвайронмент
source myenv/bin/activate - активируем
sudo apt install -y python3.10-distutils 
wget https://bootstrap.pypa.io/get-pip.py
  

# для докера, опять просто вставляем по очереди
sudo apt-get update
sudo apt-get install ca-certificates curl
sudo install -m 0755 -d /etc/apt/keyrings
sudo curl -fsSL https://download.docker.com/linux/ubuntu/gpg -o /etc/apt/keyrings/docker.asc
sudo chmod a+r /etc/apt/keyrings/docker.asc

#это одна команда большая
----
echo \
  "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/docker.asc] https://download.docker.com/linux/ubuntu \
  $(. /etc/os-release && echo "$VERSION_CODENAME") stable" | \
  sudo tee /etc/apt/sources.list.d/docker.list > /dev/null
----

sudo apt-get update
sudo apt-get install docker-ce docker-ce-cli containerd.io docker-buildx-plugin docker-compose-plugin


sudo systemctl start docker
sudo docker pull pgvector/pgvector:pg16

#запускаем пока не до конца рабочий фронт
nohup streamlit run front_streamlit.py --server.port 8502 --server.address localhost & #только позволяя локально подключаться к порту 8052 и локальному ip адресу

#certbot (https://certbot.eff.org/instructions?ws=nginx&os=snap) / acme.sh (устанавливаю второе ибо certbot windows не поддерживает больше)
#сертификат и ключ 






#скачиваем nginx 
sudo apt install nginx

#заходим в конфиг 
1 sudo nano /etc/nginx/nginx.conf (LINUX)  ( cd C:\nginx-1.26.2\conf (WINDOWS) ) 
2 CTRL + Shift + ^ - чтобы включить режим \выбирать\ ,далее стрелкой вниз идем в конец файла и CTRL + K(удаляем всё)  
3 копирование ctrl+c ( на своём компе) 
4 вставить shft+ctrl+правая кнопка мыши (сервер) 

#делаем папку с сертификатом - ключом 
sudo mkdir ssl

#надо 
sudo apt install socat

wget -O -  https://get.acme.sh | sh -s email=вашмейлтут

source ~/.bashrc ( перезагрузка) 

#надо
acme.sh --set-default-ca --server letsencrypt

#
sudo ~/.acme.sh/acme.sh --issue --standalone -d yandexragus.duckdns.org



# сигнал успеха
Your cert is in: /root/.acme.sh/yandexragus.duckdns.org_ecc/yandexragus.duckdns.org.cer
Your cert key is in: /root/.acme.sh/yandexragus.duckdns.org_ecc/yandexragus.duckdns.or

#запуск nginx
sudo systemctl start nginx

#(скачивает сертификат +  автоматически перезапускает nginx когда надо + обновляет сертификат)
acme.sh --install-cert -d yandexragus.duckdns.org \
--key-file /etc/nginx/ssl/key.pem \
--fullchain-file /etc/nginx/ssl/cert.pem \
--reloadcmd "systemctl reload nginx"

#тест nginx
nginx -t

#########################эту часть с docker можно пропустить, она нужна была только чтобы вручную всё делать, теперь надо просто запустить скрипт который в git указан#####################################
#UPDATE делать всё автоматически слишком запарно... ( надо cron job скрипту сделать будет)
#теперь запускаем базу данных (через докер) и даём пароль и тд ей, подключаем ssl, ... 
DOCKER 
-----------------------------------------------------------------
sudo docker run -d --name SSL_POSTGR \
  -p 5432:5432 \
  -e POSTGRES_PASSWORD=experiment\
  pgvector/pgvector:pg16

#тут надо скопировать наш ключ и сертфикат в докер
sudo docker cp /etc/nginx/ssl/key.pem SSL_POSTGR:/var/lib/postgresql/
sudo docker cp /etc/nginx/ssl/cert.pem SSL_POSTGR:/var/lib/postgresql/

sudo docker exec -it SSL_POSTGR bash -c "chown postgres:postgres /var/lib/postgresql/key.pem && chmod 600 /var/lib/postgresql/key.pem"

sudo docker exec -it SSL_POSTGR bash -c "chown postgres:postgres /var/lib/postgresql/cert.pem && chmod 644 /var/lib/postgresql/cert.pem"


sudo docker exec -it SSL_POSTGR bash -c "sed -i 's|^#ssl = .*|ssl = '\''on'\''|' /var/lib/postgresql/data/postgresql.conf"


sudo docker exec -it SSL_POSTGR bash -c "sed -i 's|^#ssl_cert_file = .*|ssl_cert_file = '\''/var/lib/postgresql/cert.pem'\''|' /var/lib/postgresql/data/postgresql.conf"

sudo docker exec -it SSL_POSTGR bash -c "sed -i 's|^#ssl_key_file = .*|ssl_key_file = '\''/var/lib/postgresql/key.pem'\''|' /var/lib/postgresql/data/postgresql.conf"

sudo docker exec -it SSL_POSTGR bash -c "sed -i 's|^hostssl all all all|hostssl all all all scram-sha-256|' /var/lib/postgresql/data/pg_hba.conf"

sudo docker restart SSL_POSTGR
----------------------------------------------------------------

cd home/X ( Х папка начальная где вы были) например y4gpt


source myenv/bin/activate - активируем (опять ибо возможно до этого выходили уже)

sudo apt-get update
sudo apt-get install -y libpq-dev python3-dev build-essential
pip install --upgrade pip
pip install --upgrade setuptools
pip install psycopg2-binary
pip install wheel
pip install -r requirements.txt

sudo chmod 644 /etc/nginx/ssl/cert.pem
sudo chmod 600 /etc/nginx/ssl/key.pem

sudo su
source /home/y4gpt/myenv/bin/activate


#запускаем бэк
nohup uvicorn backend_fastapi:app --host localhost --port 8000 & #только позволяя локально подключаться к порту 8052 и локальному ip адресу

#создаём таблицы
python -m database_setup.py

#(если у вас несколько streamlit работает то закройте , если только 1 то всё, больше нет иснтуркций)

ps 

kill X

#последний шаг если было несколько streamlit
nohup streamlit run front_streamlit.py --server.port 8502 --server.address localhost &

#( ещё возможно: sudo ufw deny 8052 sudo ufw allow from <nginx_ip_address> to any port 8502, что то же самое должно быть  )




