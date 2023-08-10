from main import con


def table_exists(table_name):
    cur = con.cursor()
    res = cur.execute(f"SELECT name FROM sqlite_master WHERE name='{table_name}'")
    return res.fetchone() is not None


def create_table(table_name, fields):
    cur = con.cursor()
    if not table_exists(table_name):
        statement = f"CREATE TABLE {table_name}({', '.join(fields)})"
        print(statement)
        cur.execute(statement)
    con.commit()


if __name__ == '__main__':
    
    cur = con.cursor()

    create_table('users', ('username', 'role'))
    create_table('tasks', ('description', 'assignee', 'initial_cost', 'done_cost'))
    
    tasks = [
        ('mytask', 'johndoe', 10, 20),
        ('mytask', 'johndoe', 15, 30),
        ('mytask', 'johndoe2', 1, 1),
        ('mytask', 'johndoe2', 2, 2),

    ]
    count = cur.execute('select count(*) from tasks').fetchone()[0]
    print(count)
    if not count:
        for t in tasks:
            statement = f"insert into tasks values ('{t[0]}', '{t[1]}', {t[2]}, {t[3]})"
            cur.execute(statement)

    con.commit()