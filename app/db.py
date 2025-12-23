from django.db import connection

def test_db_connection():
    try:
        with connection.cursor() as cursor:
            cursor.execute("SELECT * from users")
            row = cursor.fetchone()
        print("✅ DB 연결 성공:", row)
    except Exception as e:
        print("❌ DB 연결 실패:", e)