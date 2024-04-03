Crawler implementation is in crawler.py
Database is implemented inside a docker container using postgresql running on port 5431, where POSTGRES_USER=user and POSTGRES_PASSWORD=SecretPassword
The exported database dump is located at https://drive.google.com/drive/folders/1FFJezEFauKXiC3eLXoPJ3EjCTg7-wk9D?usp=drive_link

The following libraries are required:
urllib 1.26.4
selenium 3.141.0
beautifulsoup4 4.12.2  
concurrent.futures
psycopg2 2.9.9