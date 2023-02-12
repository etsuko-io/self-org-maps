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


# Project Architecture

## Overview
The project is comprised of two main components: an API and Celery for processing. It is designed to be deployed to AWS and can be interacted with through the API to process images.

## Components
- API: The entry point for interacting with the project.
- Celery: Used for processing images.
- SQS: Used for queue management in Celery.

## Workflow
1. A user makes a request to the API to process an image.
2. The API offloads the processing to Celery.
3. Celery processes the image and stores the result in an S3 bucket.
4. Once processing is complete, the API sends an email with a link to the result.

## Example Request
An example of a request can be found in the `quickstart` folder.


# Development
- Run pre-commit install to install the pre-commit hook

# References
- Implementation based on an article by Mehreen Saeed:
  - https://stackabuse.com/self-organizing-maps-theory-and-implementation-in-python-with-numpy/
- Orignial algorithm by Teuvo Kohonen:
  - https://link.springer.com/article/10.1007/BF00337288
