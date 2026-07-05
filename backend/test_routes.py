from main import app

def print_routes(router, prefix=""):
    for route in router.routes:
        if hasattr(route, 'path'):
            print(f"Route: {prefix}{route.path}")
        elif type(route).__name__ == '_IncludedRouter':
            print_routes(route.original_router, prefix + getattr(route.include_context, 'prefix', ''))

print_routes(app.router)
