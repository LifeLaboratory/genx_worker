from db.base import Sql


class Provider:

    @staticmethod
    def get_tasks(args):
        query = """
            SELECT * FROM TaskResult
            join Tasks t on t.id = TaskResult.taskid
                """
        return Sql.exec(query=query, args=args)

    @staticmethod
    def create_task(args):
        query = """
            INSERT INTO tasks (nodeId, status)
            VALUES({nodeId}, '{status}')
            returning id
        """

        return Sql.exec(query=query, args=args)
