import warnings
warnings.filterwarnings(action='ignore', module='.*paramiko.*')

from sshtunnel import SSHTunnelForwarder
import pymysql

def list_products_or_departments():
    try:
        print("Establishing SSH tunnel...")
        with SSHTunnelForwarder(
            ('fries.it.uu.se', 22),  # SSH server hostname and port
            ssh_username='XXXX',  # Enter your SSH username
            ssh_password='XXXX',  # Enter your SSH password
            remote_bind_address=('fries.it.uu.se', 3306)  # MySQL server hostname and port
        ) as tunnel:
            print(f"SSH tunnel established successfully! Local port: {tunnel.local_bind_port}")
            print("Connecting to the database...")

            conn = pymysql.connect(
                host='127.0.0.1',  # Always localhost when using the tunnel
                user='ht24_2_group_7',  # MySQL username
                password='pasSWd_7',  # MySQL password
                port=tunnel.local_bind_port,  # Tunnel local port
                database='ht24_2_project_group_7'  # Database name
            )
            print("Database connection established successfully!")

            cursor = conn.cursor()

            department_id = input("\nEnter Department ID: ").strip()
          
            query_check_child = """
            SELECT COUNT(*) AS child_count
            FROM Department
            WHERE Parent_Dept_ID = %s
            """
            cursor.execute(query_check_child, (department_id,))
            result = cursor.fetchone()

            if result and result[0] > 0:
                query_child_departments = """
                SELECT Department_ID, Title
                FROM Department
                WHERE Parent_Dept_ID = %s
                """
                cursor.execute(query_child_departments, (department_id,))
                rows = cursor.fetchall()

                if rows:
                    print("\nChild Departments:")
                    for row in rows:
                        print(f"ID: {row[0]}, Title: {row[1]}")
                else:
                    print("\nNo child departments found.")
            else:
                print("\nNo child departments found.")
                query_products = """
                SELECT ProductID, Title,
                       ROUND(PriceWithoutVAT * (1 + VATPercentage/100) * (1 - DiscountPercentage/100),2) AS RetailPrice
                FROM Product
                WHERE Department_ID = %s
                """
                cursor.execute(query_products, (department_id,))
                rows = cursor.fetchall()

                if rows:
                    print("\nProducts in Department:")
                    for row in rows:
                        print(f"ID: {row[0]}, Title: {row[1]}, Retail Price: {row[2]}")
                else:
                    print("\nNo products found in this department.")

    except pymysql.MySQLError as db_err:
        print(f"Database error: {db_err}")
    except Exception as err:
        print(f"An unexpected error occurred: {err}")
    finally:
        try:
            if 'conn' in locals():
                cursor.close()
                conn.close()
                print()
                print("Database connection closed.")
        except Exception as cleanup_err:
            print(f"Error during cleanup: {cleanup_err}")
        print("SSH tunnel closed.")

if __name__ == "__main__":
    list_products_or_departments()
