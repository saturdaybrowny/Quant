import win32com.client  # win32com 모듈 import
import psycopg2 # postgreSQL 연동 모듈 import


# Connect to an existing database
host = 'localhost'
dbname = 'sbt'
user = 'sbt'
pwd = 'sbt'
conn = psycopg2.connect('host={0} dbname={1} user={2} password={3}'.format(host, dbname, user, pwd))

# 연결 여부 체크
objCpCybos = win32com.client.Dispatch("CpUtil.CpCybos")
bConnect = objCpCybos.IsConnect
print(bConnect)
if (bConnect == 0):
    print("PLUS가 정상적으로 연결되지 않음. ")
    exit()

# 종목코드 리스트 구하기
objCpCodeMgr = win32com.client.Dispatch("CpUtil.CpCodeMgr")
codeList = objCpCodeMgr.GetStockListByMarket(1)  # 거래소
codeList2 = objCpCodeMgr.GetStockListByMarket(2)  # 코스닥

item_code = {}

print("거래소 종목코드", len(codeList))
for i, code in enumerate(codeList[:10]):
    secondCode = objCpCodeMgr.GetStockSectionKind(code)
    name = objCpCodeMgr.CodeToName(code)
    stdPrice = objCpCodeMgr.GetStockStdPrice(code)
    if name in ['우리은행']:  # -->> 원하는 종목(기업) 이름 입력하면 됨
        item_code[name] = code
        print(i, code, secondCode, stdPrice, name)

print("코스닥 종목코드", len(codeList2))
for i, code in enumerate(codeList2):
    secondCode = objCpCodeMgr.GetStockSectionKind(code)
    name = objCpCodeMgr.CodeToName(code)
    stdPrice = objCpCodeMgr.GetStockStdPrice(code)
    if name in ['우리은행']:  # -->> 원하는 종목(기업) 이름 입력하면 됨
        item_code[name] = code
        print(i, code, secondCode, stdPrice, name)

# 전체 종목코드 개수
# print("거래소 + 코스닥 종목코드 ",len(codeList) + len(codeList2))
print(item_code)

'''결과
거래소 종목코드 1363
0 A000020 1 9270 동화약품
1 A000030 1 17000 우리은행
2 A000040 1 396 KR모터스
3 A000050 1 13900 경방
4 A000060 1 26300 메리츠화재
코스닥 종목코드 1257
603 A068270 1 178300 셀트리온
1109 A215600 1 60200 신라젠
{'신라젠': 'A215600', '셀트리온': 'A068270'}
'''


# 일자별 데이터 호출 함수
def ReqeustData(obj, name, code):
    # 데이터 요청
    obj.BlockRequest()

    # 통신 결과 확인
    rqStatus = obj.GetDibStatus()
    rqRet = obj.GetDibMsg1()
    #     print("통신상태", rqStatus, rqRet)
    if rqStatus != 0:
        return False

    # 일자별 정보 데이터 처리
    count = obj.GetHeaderValue(1)  # 데이터 개수

    temp_data = []
    for i in range(count):
        date = obj.GetDataValue(0, i)  # 일자
        open = obj.GetDataValue(1, i)  # 시가
        high = obj.GetDataValue(2, i)  # 고가
        low = obj.GetDataValue(3, i)  # 저가
        close = obj.GetDataValue(4, i)  # 종가
        diff = obj.GetDataValue(5, i)  #
        vol = obj.GetDataValue(6, i)  # 거래량

        year = slice(0, 4)
        month = slice(4, 6)
        day = slice(6, 8)
        date = str(date)
        date_time = '{0}-{1}-{2}'.format(date[year], date[month], date[day])

        #         print(date, open, high, low, close, diff, vol)
        stock_data.append((code, name, date_time, open, high, low, close, diff, vol))
    return temp_data


stock_data = []

# 일자별 object 구하기
objStockWeek = win32com.client.Dispatch("DsCbo1.StockWeek")

for name, code in item_code.items():
    objStockWeek.SetInputValue(0, code)  # 종목 코드 - 셀트리온:A068270, 신라젠:A215600
    # 최초 데이터 요청
    ret = ReqeustData(objStockWeek, name, code)
    stock_data += ret
    # 연속 데이터 요청
    # 예제는 5번만 연속 통신 하도록 함.
    NextCount = 1
    while objStockWeek.Continue:  # 연속 조회처리
        NextCount += 1;
        if NextCount > 6:
            break
        ret = ReqeustData(objStockWeek, name, code)
        stock_data += ret
        if ret == False:
            exit()


#conn = _mysql.connect(host="localhost", user="sbt", passwd="sbtisgood", db="sbt")
cur = conn.cursor()

cur.executemany("INSERT INTO daily_stock_price(code, name, date, open, high, low, close, diff, volume) \
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)", stock_data)

conn.commit()

cur.execute("SELECT * FROM daily_stock_price WHERE name='셀트리온'")

for row in cur.fetchall():
    print(row)
