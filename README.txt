#заходим в coomand promt (в windows в поисковике находим)

#для windows скачиваем от яндекса их cli
@"%SystemRoot%\System32\WindowsPowerShell\v1.0\powershell.exe" -Command "iex ((New-Object System.Net.WebClient).DownloadString('https://storage.yandexcloud.net/yandexcloud-yc/install.ps1'))" && SET "PATH=%PATH%;%USERPROFILE%\yandex-cloud\bin"

#Вводим Y

#запускаем команду, далее следуем базовой инструкции , выбираем нашу папку (1 по дефолту )
yc init

#опять следуем инстуркции , переходим по ссылке, копируем токен который увидили и вставляем :
...


# далее вставляем по инструкции яндекса следующее:
yc compute ssh --name compute-vm-2-2-20-hdd-1728077926308 --folder-id b1gl42i8kf54i590ma16

#должны были подклюиться к серверу 
теперь вы в линуксе 

#создаём файл
nano backend_fastapi.py

#копируем код что скинул
ctrl+a затем ctrl+c нашего кода в backend_fastapi.py

#вставляем 
ctl + shift + правая кнопка мышьки ( чтобы вставить в созданный файл nano backend_fastapi.py наш код)

#выходим
ctrl+x и enter

#повторяем для всех файлов кроме png (наверное можно было бы через filezilla адекватно закинуть файлы , но тогда надо по ssh подключиться, почему то не выходило нормально)

#у нас есть ешё фотка , её скачиваем по ссылке которую создал
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
pip install -r requirements.txt   

# для докера, опять просто вставляем по очереди
sudo apt install -y apt-transport-https ca-certificates curl software-properties-common
sudo install -m 0755 -d /etc/apt/keyrings
sudo curl -fsSL https://download.docker.com/linux/ubuntu/gpg -o /etc/apt/keyrings/docker.asc

#это одна команда большая
sudo chmod a+r /etc/apt/keyrings/docker.asc
echo \
  "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/docker.asc] https://download.docker.com/linux/ubuntu \
  $(. /etc/os-release && echo "$VERSION_CODENAME") stable" | \
  sudo tee /etc/apt/sources.list.d/docker.list > /dev/null

sudo apt-get update
sudo apt-get install docker-ce docker-ce-cli containerd.io docker-buildx-plugin docker-compose-plugin

sudo systemctl start docker
sudo docker pull pgvector/pgvector:pg16

#теперь запускаем базу данных (через докер) и даём пароль и тд ей, postgres- название базы данных, experiment - пароль ...
sudo docker run -d \
  --name pgvector-container \
  -e POSTGRES_USER=postgres \
  -e POSTGRES_PASSWORD=experiment \
  -p 5432:5432 \
  pgvector/pgvector:16

#заходим в докер
docker exec -it <название/id докера> bash
# надо перейти в cd /var/lib/postgresql/data
cd /var/lib/postgresql/data

#для ssl для базы данных
#модифицируем файл postgresql.conf чтобы было :( 
ssl = on
ssl_cert_file = 'C:/path/to/your/cert.pem'
ssl_key_file = 'C:/path/to/your/key.pem'
) 
nano postgresql.conf # и дальше меняем то что выше указано

sudo apt-get update
sudo apt-get install -y libpq-dev python3-dev build-essential
pip install --upgrade pip
pip install --upgrade setuptools
pip install psycopg2-binary
pip install wheel
pip install -r requirements.txt

#скачиваем nginx 
...

#заходим в конфиг Х и меняем на конфиг что указал
...

#наконец то запуск

nohup streamlit run front_streamlit.py --server.port 8502 --server.address localhost & #только позволяя локально подключаться к порту 8052 и локальному ip адресу
nohup uvicorn backend_fastapi:app --host localhost --port 8000 & #только позволяя локально подключаться к порту 8052 и локальному ip адресу

#( ещё возможно: sudo ufw deny 8502 sudo ufw allow from <nginx_ip_address> to any port 8502, что то же самое должно быть  )

#запуск nginx
...

