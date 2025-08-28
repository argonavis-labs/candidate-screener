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
5. Create an analytics page that helps me understand the results
    1. Show a table of all ratings for all candidates, along all dimensions and their final score. The first row of this table should always use our human data. each following row should show the ai evaliations we got from our runs. The first column of each row should show the average gap between the AI ratings and human ratings for that run. (e.g. candidate 1 was an AI eval 4, but human 2. candidate 1 was an AI eval 2, but human 4. the diff is calc as (abs(4-2) + abs(2-4))/2 =4). 
    2. Make chart visualizing the human vs ai ratings for all candidates for all runs. choose the best format.
    3. Add another section for other potential relevant metrics. think hard and come up with some on your own

----
## If this doesn't work
1. Imrpove our rubric
2. Increae the numner of example cases
3. Add code signals