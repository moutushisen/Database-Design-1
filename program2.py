import warnings
warnings.filterwarnings(action='ignore', module='.*paramiko.*')

from sshtunnel import SSHTunnelForwarder
import pymysql

def update_product_discount():
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
            print()
            product_id = input("Enter Product ID: ").strip()

            query_current_discount = """
            SELECT DiscountPercentage 
            FROM Product 
            WHERE ProductID = %s
            """
            cursor.execute(query_current_discount, (product_id,))
            result = cursor.fetchone()

            if result:
                print(f"Current Discount: {result[0]}%")
                new_discount = float(input("Enter New Discount Percentage: "))

                query_update_discount = """
                UPDATE Product 
                SET DiscountPercentage = %s 
                WHERE ProductID = %s
                """
                cursor.execute(query_update_discount, (new_discount, product_id))
                conn.commit()

                print("Discount updated successfully!")
            else:
                print("Product not found.")

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
    update_product_discount()
