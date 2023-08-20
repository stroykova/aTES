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
    create_table('users', ('username unique',))
    create_table('tasks', ('id INTEGER PRIMARY KEY', 'description', 'assignee', 'initial_cost', 'done_cost', 'status'))

    migration1 = f"alter table tasks add column title"
    migration2 = f"alter table tasks add column jira_id"
    cur.execute(migration1)
    cur.execute(migration2)

    con.commit()