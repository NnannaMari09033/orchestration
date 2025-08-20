import graphene
from taskverse.apps.users.schema import Query as UsersQuery
from taskverse.apps.tasks.schema import Query as TasksQuery, Mutation as TasksMutation
from taskverse.apps.monitoring.schema import Query as MonitoringQuery

fix-dockerfile-location
class Query(UsersQuery, TasksQuery, MonitoringQuery, graphene.ObjectType):
    # Main query class combining all app queries
    pass

class Mutation(TasksMutation, graphene.ObjectType):
    # Main mutation class combining all app mutations
    pass



class Query(UsersQuery, TasksQuery, MonitoringQuery, graphene.ObjectType):
    pass


class Mutation(TasksMutation, graphene.ObjectType):
    pass


 main
schema = graphene.Schema(query=Query, mutation=Mutation)
