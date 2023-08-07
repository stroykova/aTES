from main import con, pwd_context


def get_password_hash(password):
    return pwd_context.hash(password)


def table_exists(table_name):
    cur = con.cursor()
    res = cur.execute(f"SELECT name FROM sqlite_master WHERE name='{table_name}'")
    return res.fetchone() is not None


def get_user(username: str):
    cur = con.cursor()
    res = cur.execute(f"SELECT username, hashed_password FROM users WHERE username='{username}'")
    return res.fetchone()
    

if __name__ == '__main__':
   
    cur = con.cursor()

    table_name = 'users'
    fields = ('username', 'hashed_password')
    if not table_exists(table_name):
        statement = f"CREATE TABLE {table_name}({', '.join(fields)})"
        print(statement)
        cur.execute(statement)

    if not get_user('johndoe'):
        password = get_password_hash('secret')
        statement = f"insert into {table_name} values ('johndoe', '{password}')"
        cur.execute(statement)

    cur = con.cursor()
    res = cur.execute(f"SELECT * FROM users")
    print(res.fetchall())

    res = cur.execute("SELECT username, hashed_password FROM users WHERE username='johndoe'")
    result = res.fetchone()
    print(result)
    con.commit()  