sudo docker build -t flask-snpe-app .
sudo docker run -p 5000:5000 --network=host --rm flask-snpe-app

sudo docker run -p 5000:5000 --network=host --rm flask-snpe-app
