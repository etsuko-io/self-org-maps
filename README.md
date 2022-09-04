# Self Organizing Maps

This app takes an image and transforms it into a new image, containing the original colors of
the input image, but organized by color.



### Example 1

Input

![input-image1](assets/ex1-original.png?raw=true)

Output

![output-image1](assets/ex1-trained.png?raw=true)

### Example 2


Input

![input-image2](assets/ex2-original.jpeg?raw=true)


Output

![output-image2](assets/ex2-trained.png?raw=true)




### Preparing training data
To resize images for training:


    $ python -m som.tooling.resize <path-to-image-dir>



### References
- Implementation based on an article by Mehreen Saeed:
  - https://stackabuse.com/self-organizing-maps-theory-and-implementation-in-python-with-numpy/
- Orignial algorithm by Teuvo Kohonen:
  - https://link.springer.com/article/10.1007/BF00337288
