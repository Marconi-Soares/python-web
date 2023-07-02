import sqlite3


create_task_table = (
"""
CREATE TABLE IF NOT EXISTS tasks(
    id INTEGER PRIMARY KEY AUTOINCREMENT, 
    title TEXT, 
    is_complete INTEGER DEFAULT 0 CHECK( is_complete IN (0, 1))
)
""")

class DB_conn:
    db_name = 'db.sqlite3'
    @classmethod
    def connect(cls):
        conn = sqlite3.connect(cls.db_name)
        cursor = conn.cursor()
        return conn, cursor

    @classmethod
    def close(cls, *args):
        for arg in args: arg.close()

    @classmethod
    def migrate(cls):
        conn, cursor = cls.connect()
        cursor.execute(create_task_table)
        conn.commit()
        cls.close(cursor, conn)
 

class TaskWriteMixin(DB_conn):
    @classmethod
    def add(cls, title, is_complete=False):
        conn, cursor = cls.connect()

        if is_complete: is_complete = 1
        else: is_complete = 0

        cursor.execute(
            "INSERT INTO tasks (title, is_complete) VALUES (?, ?)", 
            (title, is_complete)
        )
        conn.commit()
        cls.close(cursor, conn)
    
    @classmethod
    def update(cls, title, id):
        conn, cursor = cls.connect()
        cursor.execute("UPDATE tasks SET title = ? WHERE id = ?", (title, id))
        conn.commit()
        task = cls.get(id, cursor=cursor, conn=conn)
        return task

    @classmethod
    def complete(cls, id):
        conn, cursor = cls.connect()
        cursor.execute("UPDATE tasks SET is_complete = 1 WHERE id = ?", (id,))
        conn.commit()
        task = cls.get(id, cursor=cursor, conn=conn)
        return task

    @classmethod
    def delete(cls, id):
        conn, cursor = cls.connect()
        cursor.execute("DELETE FROM tasks WHERE id = ?", (id,))
        conn.commit()
        cls.close(cursor, conn)


class TaskReadMixin(DB_conn):
    @classmethod
    def get(cls, id, cursor=None, conn=None):
        if conn is None:
            conn, cursor = cls.connect()

        cursor.execute("SELECT * FROM tasks WHERE id = ?", (id,)) 
        task = cursor.fetchall()
        cls.close(cursor, conn)
        return cls.to_dict(task)[0]

    @classmethod
    def all(cls):
        conn, cursor = cls.connect()
        conn.row_factory = sqlite3.Row
        cursor.execute("SELECT * FROM tasks ORDER BY -is_complete")
        rows = cursor.fetchall()
        tasks = cls.to_dict(rows)
        cls.close(cursor, conn)
        return tasks 

    @classmethod
    def filter(cls, title):
        conn, cursor = cls.connect()
        query = (
            "SELECT * FROM tasks WHERE title LIKE ? COLLATE NOCASE" +
            " ORDER BY -is_complete"
        )
        cursor.execute(query, (F'%{title}%',))
        tasks = cursor.fetchall()
        cls.close(cursor, conn)
        return cls.to_dict(tasks)

   
class Tasks(TaskWriteMixin, TaskReadMixin):
    @classmethod
    def to_dict(cls, rows):
        tasks = list()
        for row in rows:
            task = dict()
            task.setdefault('is_complete', False)
            task['id'] = row[0]
            task['title'] = row[1]

            if row[2] == 1:
                task['is_complete'] = True
            
            tasks.append(task)
        return tasks

