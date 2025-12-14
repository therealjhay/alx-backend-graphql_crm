import graphene

class Query(graphene.ObjectType):
    # Definition of the field 'hello'
    hello = graphene.String(default_value="Hello, GraphQL!")

    # Logic to resolve the field (technically optional here due to default_value, 
    # but good practice to see how it works)
    def resolve_hello(root, info):
        return "Hello, GraphQL!"

# Create the schema object
schema = graphene.Schema(query=Query)