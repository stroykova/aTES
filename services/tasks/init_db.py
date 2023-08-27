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

    create_table('users', ('username unique', 'role'))
    create_table('tasks', ('id INTEGER PRIMARY KEY AUTOINCREMENT', 'description', 'assignee', 'initial_cost', 'done_cost', 'status', 'title', 'jira_id'))
    
    tasks = [
        (1, 'mytask', 'johndoe', 10, 20),
        (2, 'mytask', 'johndoe', 15, 30),
        (3, 'mytask', 'johndoe2', 1, 1),
        (4, 'mytask', 'johndoe2', 2, 2),

    ]
    count = cur.execute('select count(*) from tasks').fetchone()[0]
    print(count)
    if not count:
        for t in tasks:
            statement = f"insert into tasks (id, description, assignee, initial_cost, done_cost, status) values ({t[0]}, '{t[1]}', '{t[2]}', {t[3]}, {t[4]}, null)"
            cur.execute(statement)

    users = [
        ('johndoe', 'parrot'),
        ('johndoe2', 'parrot'),
        ('manager', 'manager'),
    ]
    count = cur.execute('select count(*) from users').fetchone()[0]
    print(count)
    if not count:
        for t in users:
            statement = f"insert into users values ('{t[0]}', '{t[1]}')"
            cur.execute(statement)

    # migrations moved to the initial statement
    # migration1 = f"alter table tasks add column title"
    # migration2 = f"alter table tasks add column jira_id"
    # cur.execute(migration1)
    # cur.execute(migration2)
    
    con.commit()