from dotenv import load_dotenv; load_dotenv(); 
from app.database.session import engine; 
from sqlalchemy import text;
from dotenv import load_dotenv
  
conn = engine.connect(); conn.execute(text('SELECT 1')); print('DB OK'); conn.close()


load_dotenv()

print("=" * 50)
print("DIAGNOSING YOUR TODO APP")
print("=" * 50)

     # Step 1: Test database connection
print("\n[1] Testing database connection...")