from main import con


def table_exists(table_name):
    cur = con.cursor()
    res = cur.execute(f"SELECT name FROM sqlite_master WHERE name='{table_name}'")
    return res.fetchone() is not None

if __name__ == '__main__':
    
    cur = con.cursor()

    table_name = 'users'
    fields = ('email', 'hashed_password')
    if not table_exists(table_name):
        statement = f"CREATE TABLE {table_name}({', '.join(fields)})"
        print(statement)
        cur.execute(statement)
