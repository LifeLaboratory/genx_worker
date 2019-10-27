from db.base import Sql


class Provider:

    @staticmethod
    def create_task_result(args):
        query = """
            INSERT INTO TaskResult(taskId, data)
            VALUES({task_id}, '{data}')
            returning id
                """
        return Sql.exec(query=query, args=args)
