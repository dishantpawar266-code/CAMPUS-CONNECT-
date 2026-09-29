def get_connection():
    try:
        if IS_CLOUD:
            conn = mysql.connector.connect(
                host=DB_HOST,
                port=DB_PORT,
                user=DB_USER,
                password=DB_PASSWORD,
                database=DB_NAME,
                ssl_verify_cert=True,
                ssl_verify_identity=True
            )
        else:
            conn = mysql.connector.connect(
                host=DB_HOST,
                port=DB_PORT,
                user=DB_USER,
                password=DB_PASSWORD,
                database=DB_NAME
            )

        if conn.is_connected():
            return conn

    except Error as e:
        error_message = f"Database Connection Failed: {e}"

        print(error_message)

        if IS_CLOUD:
            st.error(error_message)

        return None

    return None