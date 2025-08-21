

import graphene
from taskverse.apps.users.schema import Query as UsersQuery, Mutation as UsersMutation
from taskverse.apps.tasks.schema import Query as TasksQuery, Mutation as TasksMutation
from taskverse.apps.monitoring.schema import Query as MonitoringQuery, Mutation as MonitoringMutation

class Query(UsersQuery, TasksQuery, MonitoringQuery, graphene.ObjectType):
    pass

class Mutation(UsersMutation, TasksMutation, MonitoringMutation, graphene.ObjectType):
    pass

schema = graphene.Schema(query=Query, mutation=Mutation)
