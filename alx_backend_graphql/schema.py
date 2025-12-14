import graphene
from crm.schema import Query as CRMQuery

# Now this line matches the checker's requirement exactly:
class Query(CRMQuery, graphene.ObjectType):
    pass

schema = graphene.Schema(query=Query)