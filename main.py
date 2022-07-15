from loguru import logger

from tasks import create_soms


"""
todos for structure: 
[x] A single instance should actually just be a single map
[ ] The provided input image should be in-memory, not a path, so that it works
    with cloud abstractions
[x] What the SOM class returns, should be in-memory, not written anywhere yet
[ ] Displaying with matplotlib should be optional and separated
[ ] get_complexity() should be an external method, from an analyzer 
[ ] make somap.train() return a Somap model that includes metadata 
"""


if __name__ == "__main__":
    # Call Celery task
    create_soms()
    # create_soms_task.delay()
    logger.info("Task created")
