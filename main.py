from tasks import create_soms


"""
todos for structure: 
[x] A single instance should actually just be a single map
[ ] The provided input should be in-memory, not a path
[ ] What the SOM class returns, should be in-memory, not written anywhere yet
[ ] Displaying with matplotlib should be optional and separated
[ ] get_complexity() should be an external method, from an analyzer 
[ ] make somap.train() return a Somap model that includes metadata 
"""


if __name__ == "__main__":
    create_soms.delay()
