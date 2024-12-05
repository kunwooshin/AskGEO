import os

from openai import OpenAI
from sqlalchemy import create_engine, text
from sqlalchemy.exc import SQLAlchemyError

# Initialize OpenAI

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
llm = OpenAI(api_key=OPENAI_API_KEY)

# Initialize postgres

HOST = os.getenv('DB_HOST')
PORT = os.getenv('DB_PORT')
USER = os.getenv('DB_USER')
PASSWORD = os.getenv('DB_PASSWORD')
DATABASE = os.getenv('DB_NAME')
DATABASE_URI = f'postgresql+psycopg2://{USER}:{PASSWORD}@{HOST}:{PORT}/{DATABASE}'

INSTRUCTION = """
You are a SQL query generator. Based on the user's question and the database structure, generate a SQL query. 
The query will be run on a PostgreSQL database containing OpenStreetMap (OSM) data with the following structure:

1. `planet_osm_point`: Contains point features (e.g., POIs like restaurants, ATMs, bus stops).
   - Columns: `osm_id`, `name`, `amenity`, `shop`, `tourism`, `way` (geometry), `tags`.
   - The `tags` column stores additional key-value pairs as hstore data, representing detailed metadata for each feature. Use this column to filter specific features when the standard columns (e.g., `amenity`) don't suffice.

2. `planet_osm_line`: Contains linear features (e.g., roads, rivers, walking paths).
   - Columns: `osm_id`, `name`, `highway`, `waterway`, `way` (geometry).

3. `planet_osm_polygon`: Contains polygon features (e.g., buildings, parks, land use areas).
   - Columns: `osm_id`, `name`, `building`, `landuse(farmland, grass, meadow, industrial, government, construction, religious, residential, forest,)`, `way` (geometry).

4. `planet_osm_roads`: A subset of `planet_osm_line` with only road features.
   - Columns: `osm_id`, `name`, `highway`, `way` (geometry).

5. `planet_osm_nodes`: Contains raw node data (points) for all elements in OSM.
   - Columns: `id`, `lat`, `lon`, `tags`.
   - The `tags` column stores additional key-value pairs as hstore data. Use this table when you need precise latitude and longitude for specific nodes, such as landmarks, intersections, or utility points.

Your goal is to generate SQL queries to extract specific geographic features or perform analysis. For each query, include:
1. A brief description of the query’s purpose.
2. The complete SQL query.
3. If it's not asking query, provide the answer.

**Examples**
User Question: Show me the buildings within 300 meters of the Cultural Center
SQL Query: SELECT p.osm_id, p.name, p.building, ST_AsText(p.way) AS geometry FROM planet_osm_polygon p JOIN planet_osm_polygon c ON ST_DWithin(p.way, c.way, 300) WHERE c.name = '문화관';

User Question: Tell me the coordinate of KWANJEONG Library
SQL Query: SELECT name, ST_AsText(way) AS location FROM planet_osm_polygon WHERE name = '관정도서관';

**Names:**
names from planet_osm_polygon

101동
102동
103동
105동
106동
107동
108동
109동
110동
111동
113동
114동
115동
116동
117동
16-A동
1단지상가
201동
202동
203동
204동
205동
206동
207동
230동
231동
232동
24동
25-1동
25동
26동
27동
2단지상가
302
303
304
312 정밀기계설계 실험동
42-1동
45동
503동
504동
505동
506동
507동
508동
509동
510동
511동
512동
513동
516동
517동
518동
519동
520동
521동
522동
523동
615 남북공동선언 기념공원
900
901
902
903
904
905
906
918
919A
919B
919C
919D
920
921
922
923
924
925
926
931
932
933
934
935
A
B
BK국제관
C
CJ인터내셔널센터
D
E
F
G
GS25
H
I
IBK 커뮤니케이션센터
LG전자 서울대연구소
SK텔레콤 연구동
SPC 농생명과학 및 기초과학연구동
제1공학관
제2공학관
제2파워플랜트
제3식당 (전망대)
제4식당
마당
정자
총장 공관
물이 고여있는 연못(건물뒤편)
단지 콘크리트 경계옹벽
미림 어린이공원
신림 동마아파트
신림 주공아파트 1단지
신림 주공아파트 2단지
신림 벽산블루밍 아파트
주공2300프라자
신림3구역 재개발
강당동
경비실
급식실
꿈담길
농구장
문화관
버들골
수영장
예술관
자하연
정보관
창조관
천문대
청룡산
체육관
행정관
관악사 (가족생활관)
관악사 (학부생활관)
관악사 (대학원생활관)
코웨이 R&D 센터
저류조 입구
서울대 정문 예술 공원
삼성산 뜨란채 아파트
버들골 풍산마당
관악산 벽산타운 1단지 아파트
관악산 벽산타운 2단지 아파트
관악산 벽산타운 3단지 아파트
관악산 벽산타운 5단지 아파트
관악산 벽산타운 5단지 아파트 1상가
관악산 벽산타운 6단지 아파트
서울대 교수아파트
신림동 현대아파트
우정원 글로벌사회공헌센터(153동)
공과대학
공대폭포
광신학원
교수회관
단지화단
대운동장
대학신문
도성교회
동궁빌라
동신교회
동일학원
미림학원
미술대학
법과대학
사범대학
샘말공원
약학대학
연구공원
영선공장
으뜸공원
은정교회
음악대학
인문대학
입학본부
중앙광장
코사마트
호암동관
호암서관
경영대학 (SK경영관)
테니스장 1-3
테니스장 12-14
테니스장 4-6
테니스장 7-8
테니스장 9-11
신양교회 입구
"주민쉼터 공원(정자, 풀)"
국제산장 아파트
느티나무 어린이집
파스쿠찌 서울대점
공과대학 테니스장 A
공과대학 테니스장 B&C
보성운수 난곡영업소
약학대학 신약개발센터
학생회관(63)
관악구제2구민운동장
신림건영3차아파트
관리사무소
관악아파트
관정도서관
광신중학교
교육정보관
국제대학원
난우중학교
대림국제관
동원생활관
두산인문관
보건대학원
사회과학관
삼성산성당
삼성중학교
수의과대학
신림변전소
언어교육원
예림유치원
우천법학관
유재기념관
자하연식당
전파천문대
종합체육관
주영광교회
중앙도서관
지진관측소
직원아파트
차량정비고
청광아파트
태흥아파트
파워플랜트
해동학술관
환경대학원
환경안전원
"법학도서관 (국산도서관, 서암관)"
언어교육원 CJ어학관
서울대학교 정문
서울대학교 미술관
서울대학교 박물관
수의대부속 동물병원
서울대학교 관악캠퍼스
정보화본부(102동)
행정대학원(57-1동)
행정대학원(57동)
풍동실험동2
게스트하우스
공대간이식당
광신고등학교
백학어린이집
삼성고등학교
생활과학대학
시각디자인실
신림주공상가
신림현대맨션
아시아연구소
어린이놀이터
위험물저장고
자연과학대학
컴퓨터연구소
폐기물보관소
합실어린이집
호암교수회관
자연과학대학 (502)
근대법학교육100주년기념관
신림푸르지오2차
건설환경공학부
국제백신연구소
기초전력연구원
난곡공영차고지
난우어린이공원
난향어린이공원
대기환경관측소
대형구조실험동
두레학생문예관
롯데국제교육관
상산수리과학관
생명공학연구동
생물공학연구소
선박실험공장동
엔지니어하우스
유전공학연구소
종합교육연구동
태양어린이공원
학생군사교육단
합실어린이공원
호암컨벤션센터
경영전문대학원 (LG경영관)
관악산휴먼시아 1단지
관악산휴먼시아 2단지
관악산휴먼시아 3단지
신양학술정보관 I
신양학술정보관 Ⅱ
신양학술정보관 Ⅲ
신림동금호타운1차아파트
관악도시농업공원
관악산야외식물원
농업생명과학대학
미림여자고등학교
반도체공동연구소
사우촌어린이공원
서울난곡초등학교
서울난향초등학교
서울삼성초등학교
서울신우초등학교
서울원신초등학교
신소재공동연구소
포스코스포츠센터
유회진학술정보관 (300동)
멀티미디어강의동 (이공계)
멀티미디어강의동 (인문사회계)
교수학습개발센터 및 기초교육원
반도체공동연구소 교육관
글로벌학생생활관(915)
글로벌학생생활관(916)
글로벌학생생활관(917)
규장각한국학연구원
글로벌공학교육센터
기초과학공동기기원
서울매그넷고등학교
선형수조실험공장동
실험동물자원관리원
체육문화교육연구동(71-1동)
광신방송예술고등학교
기초사범교육협력센터
난곡공영차고지관리동
농생명과학공동기기원
삼성전자서울대연구소
예술계복합교육연구동
화학공정신기술연구소
관악서울대학교치과병원
뉴미디어통신공동연구소
신동아종건블루아아파트
에너지자원신기술연구소
정밀기계설계공동연구소
미림여자정보과학고등학교
차세대자동차기술연구센터
방사선동위원소폐기물보관소

names from planet_osm_point

(주)포포인
(주)포포인 파란코끼리
100주년 기념비
201동.동산교회
203동앞
24/7 Lab
24시 뼈다귀 전주식당
2단지종합상가
301동 식당
301동 교수식당
302동 식당
3단지종합상가
49동 디자인연구동
51장국밥
B5 벙커
BBQ Cafe
BK국제관
CU
EMETH(에메트)커피
GS25
Gate
Gate G
Hotcup(핫컵)
MOTIVE BOON SHIK CAFE(모티브분식카페)
Parking (underground)
SNU Hair
Shinhan Bank
Underground parking
k82 만년약수
홈
그 녀석의 직화쭈꾸미
컵&커피
眞(진)갈비
제1야영장
제2공학관
제2야영장
제2파워플랜트
겐지
농협
다빈
돌산
뒷돈
사계
샘물
알럽
일미
정자
진스
쿠모
톡톡
파란
플랙
호야
집밥 e선생
효의 초밥
가비 사랑방
돌산 국기봉
배떡 신림점
겐지 비어캔치킨
해랑 종합어시장
루나(Luna)
법대.사회대입구
벽산1단지입구
벽산6단지입구
관악IC
사당IC
메가MGC커피
가네샤
고향집
관악산
관악정
난곡사
농생대
당나귀
더푸드
도어즈
락구정
모꼬지
모자봉
묵은지
보덕사
봉덕사
사르샤
상하이
성불암
성주암
신소재
썰카페
씬차호
아워홈
약수터
예술애
옥이네
왕짜장
용암천
인아랑
자부심
자운암
장군봉
전망대
조망점
차이홍
콩숙이
티에스
편의점
핫푸드
행정관
호압사
홍타코
구시아 (300동 식당)
보미네 식당
스누샤 카페
요달의 찜닭
도림천 상류 저류죠
당신과 나의 귀한만남
칼바위 국기봉
콩부리 관악점
베트남 쌀국수 전문점 포포인
꿀단지 탕후루(신림본점)
최가네 김치찌개
관악사 체력단련실
현대옥 신림녹두거리점
낙원정(15호)
아카샤(Akasha)
코지바(Cozy bar)
리멤버(Remember)
호암산(민주동산 국기봉)
국기봉(돌산바위)
"호압산, 관악산생태공원,삼성동"
경영대.행정대학원
자연대.행정관입구
"호압사0.8km, 선우공원1.8km, 관악구민방위교육장2km, 휴먼시아아파트"
이마트24
서울대76동 나인온스버거
낙성대JC
쓰리팝PC방
간식대장
공대입구
관악교회
관악구청
국수나무
굽고굽고
기사식당
김밥천국
난곡종점
난향면옥
노천강당
다온푸드
더오믈렛
더테이블
돼지마을
뚝딱이찬
라쿠치나
라테라스
롯데리아
맘스치킨
메밀쟁이
명가식당
미니스톱
미소김밥
민주동산
본가짜장
봉자한끼
비밀부엌
비울김밥
산복터널
산장교회
삼성산장
삼성전자
성림교회
성장교회
세광운수
소담마루
소담포차
수원갈비
수중동산
신대성각
신림운수
신양교회
신토불이
신한은행
심야술상
아니이맛
아지사이
양천운수
옛날짜장
오삼숙이
우리은행
원부동산
윤머리방
이라운지
이레축산
장어나라
착한덮밥
철스뮤직
카페그랑
카페드림
카페안녕
퀴즈노스
탁배기집
테마분식
텐카이핀
페리카나
포차종점
한국순대
핫도리탕
햇빛식당
호박족발
푸디스트 (주)아름드리
관악산역 1번출구
미쳐버린 파닭
칼국수랑 김밥
캐리비안 회적
멕시카나 치킨 신림대학동점
기력장어 관악점
바로반점 신림점
스톡홀름 샐러드
통닭신사 신림점
통큰갈비 난곡점
포엠쓰리 신림점
피자먹다 난곡점
라운지오 서울대점
이라운지 서울대점
박군치킨 서울대학교점
관악교통 전기버스충전소
금별맥주 신림녹두거리점
타코라미 수제왕타코야끼&캔커피
옛날순대(12호)
자연식구(박자연 착한음식이야기)
오븐마루(난향점)
유완약국.성림교회
미림고개.고시촌입구
미림여고.미림여자정보과학고
가마로강정
가비사랑방
가족생활동
고기사이소
고시칼국수
공동기기원
국제대학원
기숙사식당
난향삼거리
농대도서관
다케돈까스
만년약수터
맛들의잔치
맥시칸치킨
먹거리코너
면류관교회
모모루덴스
몽실이푸드
문화관입구
미랑컬헤어
배드민턴장
봉봉돈까스
붕어빵창고
산장아파트
산장약수터
삼성산성지
상봉약수터
서울대입구
서울대정문
서울대학교
세븐일레븐
쇼랜드치킨
신림왕꼬치
쎄븐일레븐
어느멋진날
어울림마을
오뚝이분식
오렌지포차
우리집밥상
이디야커피
이승철스시
인헌아파트
작당민센터
전주현대옥
지하주차장
착한도시락
천지부동산
파고다쉼터
파리바게뜨
파리바게트
패밀리치킨
포크앤누들
푸짐한밥상
프레드피자
하얀테이블
학부생활관
한고을식당
한마음스넥
헤어스케치
현대문방구
현대주유소
호압사입구
서울대학교 정문
서울대학교 후문
요다드래곤 김밥
두마리찜닭 두찜 관악신림점
이나닭강정 신림1호점
골뱅이소면 이야기
라오니피자 관악점
토마토김밥 난곡점
서울대학교 학생식당 (SNU student union restaurant)
가마로강정 녹두거리점
쇼랜드치킨 서울남부직영1호점
남파김삼준 문화복지기념관
고산매운탕(4호)
부리또리꼬(BURRITO RICO)
옐로우타운(Yellow Town)
"서울둘레길(석수역), 서울둘레길(사당역), 금천체육공원, 삼성공원"
서울대후문.연구공원
관악산입구.관악아트홀·중앙도서관
수의대입구.보건대학원앞
벽산아파트102동
벽산아파트106동
벽산아파트112동
벽산아파트113동
벽산아파트1단지.호압사입구
삼성산주공307동앞
벽산아파트5단지
가마솥도시락
관악사삼거리
광신고교입구
교수회관입구
기숙사삼거리
나인온스버거
다인고시부페
대가왕돈카츠
대학동노인정
대학동이모네
대학원생활관
럭키할인마트
마리아쥬제이
마약타코야키
미르보드카페
미림성중국성
미림여고입구
박효신닭꼬치
벽산모아치과
봉구스밥버거
봉이숯불갈비
봉천로사거리
사계절세탁소
삼성치안센터
서울핫뼈구이
신동아아파트
신림복지관앞
신우초등학교
엄마손칼국수
원당초교입구
이가네감자탕
지은이네맛집
청아람독서실
청춘김치찌개
포크플레이트
하륜일만족발
호암교수회관
호압사갈림길
황비홍마라탕
파주대찬닭발 feat.IZAKAYA 신림녹두거리점
신동아아파트 전기차 충전소
투썸플레이스 서울대점
호암교수회관 크리스탈
박효신닭꼬치 신림녹두점
삼성초등학교 병설유치원
호암교수회관 컨벤션센터
국수나무그린 신림녹두거리점
나인온스버거(서울대점)
광신고등학교.주공1단지
금호타운아파트
난곡공영차고지
난우중학교입구
난향동주민센터
내친구김밥본점
대학동샘말공원
보성운수기종점
서울대교수회관
연세베스트의원
욕망오므라이스
은행나무사거리
이화온누리약국
찌개가맛있는집
캐리비안의회적
통영장어잡는날
호프가맛있는집
해랑종합어시장 신림녹두점
전설의옛날통닭(신림점)
관악산휴먼시아.신림푸르지오2차
유전공학연구소.반도체공동연구소
고기택배가는남자
관악문화관도서관
난향동공영차고지
병천가마솥순대국
삼성산주공아파트
서울대학교우체국
스타일리스트헤어
신림근린공원입구
에너지자원연구소
도로시파스타연정 신림점
관악문화원도서관 구내식당
"유회진학술정보관, 제1공학관"
"호암로녹지연결로, 호압사, 관악산둘레길, 삼성산"
"호암로녹지연결로, 호압사, 관악산둘레길, 삼성산성지"
서울난향초등학교.난향동주민센터
건설환경종합연구소
서울대호암교수회관
신림종합사회복지관
우리동네아이스크림
건설환경종합연구소앞
보성운수차고지맞은편
삼성산주공아파트정문
관악산휴먼시아아파트1단지입구
디딤돌공인중개사사무소
또래오래관악신림중앙점
전준수명품청기와감자탕
서울관악삼성동우편취급국


**Notes:**
1. Use PostGIS spatial functions (e.g., `ST_Distance`, `ST_Intersects`, `ST_DWithin`) for spatial queries.
2. Use the `ST_AsText` function to convert geometry to human-readable form when necessary.
3. If you fail to retrieve data from planet_osm_point, try planet_osm_polygon.
4. All of the place is described in Korean. Please use the Korean name to search the place.
    """

ERROR_PROMPT = "This occurs error.\n"
NO_ANSWER_PROMPT = "This gives nothing.\n"

EXTRACT_SQL_PROMPT = "Extract SQL query from the generated text. Respond with pure sql query only.\n"

VERIFICATION_PROMPT = "Is this a valid result? Just YES/NO.\n"
INVALID_PROMPT = "This does not look valid. Please try again.\n"


# Create SQLAlchemy database engine
def create_db_engine():
    return create_engine(DATABASE_URI)


# Function to execute the generated SQL query
def execute_query(engine, query):
    try:
        with engine.connect() as connection:
            result = connection.execute(text(query)).fetchall()
            if not result:
                return NO_ANSWER_PROMPT, None
            else:
                return None, result
    except SQLAlchemyError as e:
        return ERROR_PROMPT + f" Details: {str(e)}", None


# Function to refine the GPT query
def generate_response(prompt):
    response = llm.chat.completions.create(
        model='gpt-4o-mini',
        messages=[
            {"role": "user", "content": prompt},
        ],
        temperature=0
    )

    return response.choices[0].message.content.strip()


# Main function
def main():
    # Example user question
    question = "Tell me the coordinate of KWANJEONG Library"
    iteration = 0

    # Create initial prompt
    prompt = INSTRUCTION + "\nQuestion: " + question
    print(f"User Question: {question}")

    # Create database engine
    engine = create_db_engine()

    while iteration < 5:
        print(f"Iteration {iteration + 1}")

        # Get GPT-generated SQL query
        response = generate_response(prompt)
        print("GPT Response:", response)
        sql_query = generate_response(EXTRACT_SQL_PROMPT + response)

        # Execute the query
        print("SQL Query:", sql_query)
        message, result = execute_query(engine, sql_query.replace('```sql', '').replace('```', ''))

        # Handle query results
        appended_text = ""  # Store only the appended part
        if message == NO_ANSWER_PROMPT:
            appended_text = f"\n\n{NO_ANSWER_PROMPT}: {sql_query}\n"
        elif message and message.startswith(ERROR_PROMPT):
            appended_text = f"\n\n{sql_query}\n{message}"
        else:
            # Valid result
            print("Final Result:", result)

            p = f"Question: {question}, Answer:{result}\n{VERIFICATION_PROMPT}"
            valid = generate_response(p)
            if "NO" in valid:
                appended_text = f"\n{sql_query}\n{result}\n{INVALID_PROMPT}"
            else:
                print("Valid Answer")
                return

        # Print only the appended part
        print("Appended to prompt:", appended_text.strip())

        # Append to the prompt
        prompt += appended_text
        iteration += 1

    print("Max iterations reached. Unable to refine query.")


if __name__ == "__main__":
    main()
