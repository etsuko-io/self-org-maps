from som.api.fastapi import create_app


"""
todos for structure:
[ ] The provided input image should be in-memory, not a path, so that it works
    with cloud abstractions
[ ] Bring matplotlib back
[ ] get_complexity() should be an external method, from an analyzer
[ ] make somap.train() return a Somap model that includes metadata
"""
app = create_app()
