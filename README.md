# AskGEO
Project for Data Science (2024-FALL)

1. sample data로 google bigquery newyork citibike_stations 데이터셋 일부 사용
2. semantic search는 일단 간단히 구현하기 위해 chromadb 사용
3. postgis 이용 위해 python으로 local Postgres 연결.
4. 추가로 필요한 구현 내용은 주석으로 달아뒀음 (향후 update 예정)
5. .env file 만들어서 아래 내용 추가해둬야함
6. data 폴도에 html 파일은 지도 출력 결과 (추후 frontend랑 연결)
7. 사용자가 특정 건물 위치(지금은 자전거 정류장 위치)를 물었을 때 좌표와 함께 지도 반환하도록 하는 케이스만 구현
```
OPENAI_API_KEY="YOUR API KEY"

DB_HOST=localhost
DB_PORT=5432
DB_USER=postgres
DB_PASSWORD="PASSWORD"
DB_NAME=postgres
```
main.py 실행시키면 됨. (사용자 질문은 일단 고정해둠)

## feature/nearby
'24.11.27.
