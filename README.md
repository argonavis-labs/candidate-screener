# Overall goal
We want to feed a model designer portfolio sites (starting with images) and have it determine whether the design is good enough that this person is worth interviewing. We want the model to get as good at portfolio screening as the best senior design hiring managers.

## Todos

1. Create exemplars to feed into the context
    1. Download website screenshots (name the files eg. exemplar_1)
    2. Create JSON of my own rating of them, and attach each object to the file ID. Right now I have a real CSV. Need to turn it into a json.
    3. [P2] Download & compress website
    4. [P2] Run a script that calls Opus on each site to generate code-based supplemental data from the compressed website downloads
2. Create a rubric.json
3. Create test cases
    1. Get 10 screenshots similar to the sites i’ve already ranked. Name them with an ID. (candidate_1)
    2. Create human-ratings.json of my own manual rating on each dimension + final score. Make sure to attach them each object to an ID
    3. [P2] Download and compress each site
    4. [P2] Run a script that calls Opus on each site to generate code-based supplemental data from the compressed website downloads
4. Create a script that calls the model
    1. hook up to the model APIs
    2. Updates the generated-prompt.md by combining core-prompt.md, exemplars.json, rubric.json
    3. Calls the Open AI API on a loop for each screenshot using our final generated-prompt and exemplar images
    4. [P2] implement some prompt caching
    5. [P2] We also feed in our code based supplemental 
    6. Update an ai-ratings.json file after each call finishes. we should keep the IDs consistent with the human-ratings.json
5. Create an evaluation script that loops through the results
    1. Calculate how far off we are on average
    2. Whether there are any systemic biases up or down
    3. Highlights the top 10 sites where there are the most gaps
    4. generates a very simple visualization of the human vs ai scores in a table (can literally be ASCII if needed) so that I can visualize the outcome

----
## If this doesn't work
1. Imrpove our rubric
2. Increae the numner of example cases
3. Add code signals