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
    

def create_table(table_name, fields, additional=''):
    cur = con.cursor()
    if not table_exists(table_name):
        statement = f"CREATE TABLE {table_name}({', '.join(fields)}) {additional}"
        print(statement)
        cur.execute(statement)
    con.commit()


users = [
    ('johndoe', get_password_hash('secret'), 'parrot'),
    ('johndoe2', get_password_hash('secret'), 'parrot'),
    ('manager', get_password_hash('secret'), 'manager'),
]


if __name__ == '__main__':
   
    cur = con.cursor()

    table_name = 'users'
    create_table(table_name, ('username unique', 'hashed_password', 'role'))

    if not get_user('johndoe'):
        for u in users:
            statement = f"insert into {table_name} values ('{u[0]}', '{u[1]}', '{u[2]}')"
            cur.execute(statement)

    cur = con.cursor()
    res = cur.execute(f"SELECT * FROM users")
    print(res.fetchall())
    con.commit()  