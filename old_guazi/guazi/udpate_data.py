import pymongo
import pymysql


def to_mysql():
    # 连接 mysql
    conn = pymysql.connect(
            host='192.168.1.94',
            user='dataUser94', 
            password='94dataUser@2020',
            db='usedcar_update',
            charset='utf8',
            cursorclass=pymysql.cursors.DictCursor
        )

    try:
        with conn.cursor() as cursor:
    #         sql = "ALTER TABLE 20201118_autohome_dealer ADD adname CHAR(20);"  # 添加一列
            sql = "SELECT url, registerdate FROM che58_online;"
            cursor.execute(sql)
            conn.commit()
            
            results = [i for i in cursor.fetchall() if not i['registerdate']]
            print(len(results), results[:5])
    #         for res in tqdm(results):
    #             sql_insert = "UPDATE 20201118_autohome_dealer SET adname=%s WHERE location=%s;"
    #             try:
    #                 cursor.execute(sql_insert, (get_adname(res['location']), res['location']))
    #             except Exception as e:
    #                 print(repr(e), res['location'])
                
    #             conn.commit()

    finally:
        conn.close()
        
    print('ok')



if __name__ == '__main__':
    to_mysql()